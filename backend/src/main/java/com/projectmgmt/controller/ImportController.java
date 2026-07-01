package com.projectmgmt.controller;

import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import javax.sql.DataSource;
import java.io.*;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.*;
import java.util.concurrent.TimeUnit;

@RestController
@RequestMapping("/api/import")
@RequiredArgsConstructor
public class ImportController {

    private static final Logger log = LoggerFactory.getLogger(ImportController.class);

    private final DataSource dataSource;

    /** Lệnh python trong container (override bằng env IMPORT_PYTHON_BIN nếu cần). */
    @Value("${import.python-bin:python3}")
    private String pythonBin;

    /**
     * GET /api/import/template
     * Tải file Excel mẫu (đúng cấu trúc các sheet mà import yêu cầu).
     */
    @GetMapping("/template")
    public ResponseEntity<Resource> downloadTemplate() throws Exception {
        Resource resource = new ClassPathResource("templates/Resource_Allocation_Template.xlsx");
        if (!resource.exists()) {
            return ResponseEntity.notFound().build();
        }
        String fileName = "Resource_Allocation_Template.xlsx";
        String encoded = URLEncoder.encode(fileName, StandardCharsets.UTF_8).replace("+", "%20");
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION,
                        "attachment; filename=\"" + fileName + "\"; filename*=UTF-8''" + encoded)
                .contentType(MediaType.parseMediaType(
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
                .body(resource);
    }

    /**
     * POST /api/import/excel
     * Nhận file Excel (multipart), chạy extract_excel.py, rồi thực thi SQL vào DB.
     */
    @PostMapping(value = "/excel", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public Map<String, Object> importExcel(@RequestParam("file") MultipartFile file) throws Exception {
        Map<String, Object> result = new LinkedHashMap<>();

        if (file.isEmpty()) {
            result.put("success", false);
            result.put("message", "File rỗng");
            return result;
        }

        String originalName = file.getOriginalFilename();
        if (originalName == null || (!originalName.endsWith(".xlsx") && !originalName.endsWith(".xls"))) {
            result.put("success", false);
            result.put("message", "Chỉ hỗ trợ file .xlsx / .xls");
            return result;
        }

        // 1. Lưu file vào temp directory
        Path tempDir = Files.createTempDirectory("qt175_import_");
        Path excelPath  = tempDir.resolve(originalName);
        Path sqlPath    = tempDir.resolve("import_data.sql");
        Path scriptPath = tempDir.resolve("extract_excel.py");

        try {
            file.transferTo(excelPath.toFile());
            log.info("Saved uploaded Excel to: {}", excelPath);

            // 2. Giải nén script từ classpath (đóng gói trong jar) ra file tạm
            Resource scriptRes = new ClassPathResource("scripts/extract_excel.py");
            if (!scriptRes.exists()) {
                result.put("success", false);
                result.put("message", "Không tìm thấy script extract_excel.py trong ứng dụng");
                return result;
            }
            try (InputStream in = scriptRes.getInputStream()) {
                Files.copy(in, scriptPath, StandardCopyOption.REPLACE_EXISTING);
            }

            // 3. Chạy Python extract script
            ProcessBuilder pb = new ProcessBuilder(
                pythonBin, scriptPath.toString(),
                "--xlsx", excelPath.toString(),
                "--out",  sqlPath.toString()
            );
            pb.redirectErrorStream(true);
            pb.environment().put("PYTHONIOENCODING", "utf-8");

            Process process;
            try {
                process = pb.start();
            } catch (IOException e) {
                log.error("Không khởi chạy được Python ('{}'): {}", pythonBin, e.getMessage());
                result.put("success", false);
                result.put("message", "Máy chủ chưa cài đặt Python để xử lý Excel");
                result.put("detail", e.getMessage());
                return result;
            }
            String pyOutput = new String(process.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
            boolean finished = process.waitFor(120, TimeUnit.SECONDS);

            if (!finished) {
                // Đừng để tiến trình python treo ngốn tài nguyên
                process.destroyForcibly();
                result.put("success", false);
                result.put("message", "Xử lý Excel quá thời gian (timeout)");
                result.put("detail", pyOutput);
                return result;
            }
            if (process.exitValue() != 0) {
                result.put("success", false);
                result.put("message", "Python script thất bại");
                result.put("detail", pyOutput);
                return result;
            }

            log.info("Python output: {}", pyOutput);

            // Parse stats từ output (Milestones: X | Tasks: Y)
            String milestonesStr = extractStat(pyOutput, "Milestones: (\\d+)");
            String tasksStr      = extractStat(pyOutput, "Tasks: (\\d+)");

            // 4. Đọc SQL và thực thi từng statement
            String sqlContent = Files.readString(sqlPath, StandardCharsets.UTF_8);
            int stmtCount = executeSqlFile(sqlContent);

            result.put("success", true);
            result.put("message", "Import thành công");
            result.put("fileName", originalName);
            result.put("milestones", milestonesStr.isEmpty() ? "?" : milestonesStr);
            result.put("tasks", tasksStr.isEmpty() ? "?" : tasksStr);
            result.put("sqlStatements", stmtCount);
            result.put("pythonOutput", pyOutput);

        } finally {
            // Dọn dẹp temp files
            try {
                Files.deleteIfExists(excelPath);
                Files.deleteIfExists(sqlPath);
                Files.deleteIfExists(scriptPath);
                Files.deleteIfExists(tempDir);
            } catch (Exception e) {
                log.warn("Cleanup temp files failed: {}", e.getMessage());
            }
        }

        return result;
    }

    /**
     * Thực thi file SQL (nhiều statements, phân tách bằng ';').
     *
     * QUAN TRỌNG: chạy TẤT CẢ statement trên MỘT connection duy nhất trong MỘT
     * transaction. File SQL tự chứa `SET FOREIGN_KEY_CHECKS=0` ở đầu và `=1` ở cuối;
     * vì cùng một connection nên việc tắt FK có hiệu lực cho toàn bộ DELETE/INSERT.
     *
     * Trước đây mỗi câu chạy qua một connection khác nhau của pool (HikariCP), nên
     * `SET FOREIGN_KEY_CHECKS=0` không áp dụng cho các câu DELETE/INSERT ở connection
     * khác → khi import lần 2 (bảng đã có dữ liệu) sinh ra tham chiếu khoá ngoại lệch
     * (product trỏ tới project_group không tồn tại) làm API sản phẩm sập 500.
     *
     * Lỗi cấp connection -> rollback toàn bộ (giữ nguyên dữ liệu cũ thay vì làm hỏng).
     * Lỗi ở một câu lẻ (dữ liệu bẩn) -> bỏ qua câu đó và tiếp tục (InnoDB chỉ rollback
     * đúng câu lỗi, không huỷ cả transaction).
     */
    private int executeSqlFile(String sqlContent) throws SQLException {
        String[] rawStatements = sqlContent.split("(?<=;)\\s*\\n");
        int count = 0;
        try (Connection conn = dataSource.getConnection()) {
            boolean prevAutoCommit = conn.getAutoCommit();
            conn.setAutoCommit(false);
            try (Statement st = conn.createStatement()) {
                for (String stmt : rawStatements) {
                    String s = stmt.trim();
                    if (s.isEmpty() || s.startsWith("--")) continue;
                    // Bỏ dấu ';' cuối
                    if (s.endsWith(";")) {
                        s = s.substring(0, s.length() - 1).trim();
                    }
                    if (s.isEmpty() || s.startsWith("--")) continue;
                    try {
                        st.execute(s);
                        count++;
                    } catch (SQLException e) {
                        log.warn("SQL error (skipped): {} | stmt: {}",
                            e.getMessage(), s.length() > 80 ? s.substring(0, 80) + "..." : s);
                    }
                }
                conn.commit();
            } catch (SQLException e) {
                conn.rollback();
                log.error("Import thất bại ở tầng transaction, đã rollback: {}", e.getMessage());
                throw e;
            } finally {
                // Đảm bảo FK checks bật lại và trả connection về pool ở trạng thái sạch
                try (Statement reset = conn.createStatement()) {
                    reset.execute("SET FOREIGN_KEY_CHECKS=1");
                } catch (SQLException ignore) { /* best effort */ }
                conn.setAutoCommit(prevAutoCommit);
            }
        }
        return count;
    }

    private String extractStat(String text, String pattern) {
        java.util.regex.Matcher m = java.util.regex.Pattern.compile(pattern).matcher(text);
        return m.find() ? m.group(1) : "";
    }
}
