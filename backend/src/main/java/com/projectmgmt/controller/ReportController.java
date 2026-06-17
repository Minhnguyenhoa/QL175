package com.projectmgmt.controller;

import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.InputStreamResource;
import org.springframework.core.io.Resource;
import org.springframework.http.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.*;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.TimeUnit;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@RestController
@RequestMapping("/api/report")
@RequiredArgsConstructor
public class ReportController {

    private static final Logger log = LoggerFactory.getLogger(ReportController.class);
    private final JdbcTemplate jdbc;

    /** Lệnh python trong container (override bằng env IMPORT_PYTHON_BIN nếu cần). */
    @Value("${import.python-bin:python3}")
    private String pythonBin;

    @Value("${spring.datasource.url}")
    private String datasourceUrl;
    @Value("${spring.datasource.username}")
    private String dbUser;
    @Value("${spring.datasource.password}")
    private String dbPwd;

    /** Các script cần giải nén cùng thư mục (generate_* import report_data). */
    private static final String[] REPORT_SCRIPTS = {
        "report_data.py", "generate_report_pdf.py", "generate_report_slides.py"
    };

    private static final Pattern JDBC_URL =
        Pattern.compile("jdbc:mysql://([^:/]+)(?::(\\d+))?/([^?;]+)");

    /** GET /api/report/project-groups — trả về danh sách nhóm dự án để chọn khi xuất PDF */
    @GetMapping("/project-groups")
    public List<Map<String, Object>> getProjectGroups() {
        return jdbc.queryForList(
            "SELECT id, code, name FROM project_groups ORDER BY id");
    }

    @GetMapping("/summary")
    public Map<String, Object> getSummary() {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("reportDate", LocalDate.now().toString());

        // ── 1. TỔNG QUAN MILESTONE ────────────────────────────────────────────
        Long total = jdbc.queryForObject("SELECT COUNT(*) FROM milestones", Long.class);

        // Status derived: remind='Quá hạn' → overdue, actualEndDate NOT NULL → done,
        // currentPhase IS NOT NULL → in-progress, else not-started
        Long done       = jdbc.queryForObject(
            "SELECT COUNT(*) FROM milestones WHERE actual_end_date IS NOT NULL", Long.class);
        Long inProgress = jdbc.queryForObject(
            "SELECT COUNT(*) FROM milestones WHERE actual_end_date IS NULL AND current_phase IS NOT NULL", Long.class);
        Long overdue    = jdbc.queryForObject(
            "SELECT COUNT(*) FROM milestones WHERE remind='Quá hạn'", Long.class);
        Long notStarted = total - done - inProgress;
        if (notStarted < 0) notStarted = 0L;

        Map<String, Object> overview = new LinkedHashMap<>();
        overview.put("total", total);
        overview.put("done", done);
        overview.put("inProgress", inProgress);
        overview.put("notStarted", notStarted);
        overview.put("overdue", overdue);
        result.put("overview", overview);

        // ── 2. THEO GIAI ĐOẠN ─────────────────────────────────────────────────
        List<Map<String, Object>> byPhase = jdbc.queryForList(
            "SELECT phase, COUNT(*) AS total, " +
            "SUM(CASE WHEN actual_end_date IS NOT NULL THEN 1 ELSE 0 END) AS done, " +
            "SUM(CASE WHEN remind='Quá hạn' THEN 1 ELSE 0 END) AS overdue " +
            "FROM milestones WHERE phase IS NOT NULL GROUP BY phase ORDER BY phase");
        result.put("byPhase", byPhase);

        // ── 3. THEO SẢN PHẨM ──────────────────────────────────────────────────
        List<Map<String, Object>> byProduct = jdbc.queryForList(
            "SELECT p.code, p.name, p.status AS projectStatus, " +
            "COUNT(m.id) AS totalMilestone, " +
            "SUM(CASE WHEN m.actual_end_date IS NOT NULL THEN 1 ELSE 0 END) AS done, " +
            "SUM(CASE WHEN m.current_phase IS NOT NULL AND m.actual_end_date IS NULL THEN 1 ELSE 0 END) AS inProgress, " +
            "SUM(CASE WHEN m.remind='Quá hạn' THEN 1 ELSE 0 END) AS overdue, " +
            "p.current_phase AS currentPhase " +
            "FROM products p LEFT JOIN milestones m ON m.product_id = p.id " +
            "GROUP BY p.id, p.code, p.name, p.status, p.current_phase " +
            "ORDER BY p.code");
        result.put("byProduct", byProduct);

        // ── 4. MILESTONE THÀNH PHẦN (top components with counts) ──────────────
        List<Map<String, Object>> components = jdbc.queryForList(
            "SELECT p.code AS productCode, m.component_milestone, " +
            "COUNT(m.id) AS total, " +
            "SUM(CASE WHEN m.actual_end_date IS NOT NULL THEN 1 ELSE 0 END) AS done, " +
            "SUM(CASE WHEN m.current_phase IS NOT NULL AND m.actual_end_date IS NULL THEN 1 ELSE 0 END) AS inProgress " +
            "FROM milestones m JOIN products p ON m.product_id = p.id " +
            "WHERE m.component_milestone IS NOT NULL AND m.phase = 'Giai đoạn 1' " +
            "GROUP BY p.code, m.component_milestone " +
            "ORDER BY p.code, m.component_milestone");
        result.put("milestoneComponents", components);

        // ── 5. NHÂN SỰ ────────────────────────────────────────────────────────
        Long totalEmp = jdbc.queryForObject("SELECT COUNT(*) FROM employees", Long.class);
        Long gtelEmp  = jdbc.queryForObject(
            "SELECT COUNT(*) FROM employees WHERE company='GTEL ICT'", Long.class);

        List<Map<String, Object>> byCompany = jdbc.queryForList(
            "SELECT company, COUNT(*) AS headcount FROM employees " +
            "WHERE company IS NOT NULL GROUP BY company ORDER BY headcount DESC");

        List<Map<String, Object>> byRole = jdbc.queryForList(
            "SELECT role, COUNT(*) AS headcount FROM employees " +
            "WHERE role IS NOT NULL GROUP BY role ORDER BY headcount DESC LIMIT 15");

        Map<String, Object> employees = new LinkedHashMap<>();
        employees.put("total", totalEmp);
        employees.put("gtel", gtelEmp);
        employees.put("outsourcing", totalEmp - gtelEmp);
        employees.put("byCompany", byCompany);
        employees.put("byRole", byRole);
        result.put("employees", employees);

        // ── 6. PHÂN BỔ THEO SẢN PHẨM (resource_allocations) ──────────────────
        List<Map<String, Object>> allocByProduct = jdbc.queryForList(
            "SELECT p.code, p.name, COUNT(DISTINCT ra.employee_id) AS headcount, " +
            "SUM(ra.allocation_percent) AS totalMM " +
            "FROM resource_allocations ra JOIN products p ON ra.product_id = p.id " +
            "GROUP BY p.id, p.code, p.name ORDER BY totalMM DESC");
        result.put("allocationByProduct", allocByProduct);

        return result;
    }

    /**
     * GET /api/report/export-pdf?date=dd/MM/yyyy
     * Gọi Python script generate_report_pdf.py, stream PDF về client.
     */
    @GetMapping("/export-pdf")
    public ResponseEntity<InputStreamResource> exportPdf(
            @RequestParam(value = "date",    required = false) String dateParam,
            @RequestParam(value = "project", required = false) String projectParam) throws Exception {

        String reportDate = (dateParam != null && !dateParam.isBlank())
            ? dateParam
            : LocalDate.now().format(DateTimeFormatter.ofPattern("dd/MM/yyyy"));

        // projectParam:
        //   null / blank / "ALL" → tất cả dự án (không filter)
        //   "H05YTS"             → 1 dự án
        //   "H05YTS,H06ABC"      → nhiều dự án (comma-separated)
        String projectCode = (projectParam != null && !projectParam.isBlank()) ? projectParam : "ALL";

        // Filename prefix: dùng cho tên file tải về
        String projLabel = projectCode.equals("ALL") ? "TatCa" : projectCode.replace(",", "-");

        return runReportScript("generate_report_pdf.py", "BaoCaoTienDo_" + projLabel,
                reportDate, projectCode);
    }

    /**
     * GET /api/report/export-slides?date=dd/MM/yyyy&project=H05YTS
     * Gọi generate_report_slides.py (báo cáo dạng slide 16:9), stream PDF về client.
     */
    @GetMapping("/export-slides")
    public ResponseEntity<InputStreamResource> exportSlides(
            @RequestParam(value = "date",    required = false) String dateParam,
            @RequestParam(value = "project", required = false) String projectParam) throws Exception {

        String reportDate = (dateParam != null && !dateParam.isBlank())
            ? dateParam
            : LocalDate.now().format(DateTimeFormatter.ofPattern("dd/MM/yyyy"));
        String projectCode = (projectParam != null && !projectParam.isBlank()) ? projectParam : "ALL";
        String projLabel = projectCode.equals("ALL") ? "TatCa" : projectCode.replace(",", "-");

        return runReportScript("generate_report_slides.py", "BaoCaoSlide_" + projLabel,
                reportDate, projectCode);
    }

    /**
     * Giải nén các script báo cáo từ classpath ra thư mục tạm, chạy script được chỉ định
     * với tham số kết nối DB lấy từ cấu hình Spring, rồi stream PDF kết quả về client.
     */
    private ResponseEntity<InputStreamResource> runReportScript(
            String scriptName, String filePrefix, String reportDate, String projectCode) throws Exception {

        Path tempDir = Files.createTempDirectory("qt175_report_");
        Path pdfPath = tempDir.resolve("report.pdf");
        try {
            // 1. Giải nén report_data.py + generate_*.py vào cùng thư mục
            for (String s : REPORT_SCRIPTS) {
                Resource res = new ClassPathResource("scripts/" + s);
                if (!res.exists()) {
                    log.error("Thiếu script báo cáo trong ứng dụng: {}", s);
                    return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(null);
                }
                try (InputStream in = res.getInputStream()) {
                    Files.copy(in, tempDir.resolve(s), StandardCopyOption.REPLACE_EXISTING);
                }
            }

            // 2. Dựng lệnh: python <script> --out ... --date ... --project ... + tham số DB
            List<String> cmd = new ArrayList<>(Arrays.asList(
                pythonBin, tempDir.resolve(scriptName).toString(),
                "--out",     pdfPath.toString(),
                "--date",    reportDate,
                "--project", projectCode
            ));
            cmd.addAll(buildDbArgs());

            ProcessBuilder pb = new ProcessBuilder(cmd);
            pb.redirectErrorStream(true);
            pb.environment().put("PYTHONIOENCODING", "utf-8");

            Process process;
            try {
                process = pb.start();
            } catch (IOException e) {
                log.error("Không khởi chạy được Python ('{}'): {}", pythonBin, e.getMessage());
                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(null);
            }
            String pyOutput = new String(process.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
            boolean finished = process.waitFor(120, TimeUnit.SECONDS);

            if (!finished || process.exitValue() != 0) {
                log.error("Report generation failed ({}): {}", scriptName, pyOutput);
                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(null);
            }
            log.info("Report generated ({}): {}", scriptName, pyOutput.trim());

            byte[] pdfBytes = Files.readAllBytes(pdfPath);
            String filename = filePrefix + "_" + reportDate.replace("/", "-") + ".pdf";

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_PDF);
            headers.setContentDisposition(ContentDisposition.attachment().filename(filename).build());
            headers.setContentLength(pdfBytes.length);
            return ResponseEntity.ok().headers(headers)
                .body(new InputStreamResource(new ByteArrayInputStream(pdfBytes)));
        } finally {
            // Dọn dẹp toàn bộ thư mục tạm
            try (var paths = Files.walk(tempDir)) {
                paths.sorted(Comparator.reverseOrder())
                     .forEach(p -> { try { Files.deleteIfExists(p); } catch (Exception ignored) {} });
            } catch (Exception ignored) {}
        }
    }

    /** Lấy --host/--port/--db/--user/--pwd cho script Python từ cấu hình datasource. */
    private List<String> buildDbArgs() {
        String host = "mysql", port = "3306", db = "project_mgmt";
        Matcher m = JDBC_URL.matcher(datasourceUrl == null ? "" : datasourceUrl);
        if (m.find()) {
            host = m.group(1);
            if (m.group(2) != null) port = m.group(2);
            db = m.group(3);
        }
        return new ArrayList<>(Arrays.asList(
            "--host", host,
            "--port", port,
            "--db",   db,
            "--user", dbUser == null ? "root" : dbUser,
            "--pwd",  dbPwd  == null ? "" : dbPwd
        ));
    }
}
