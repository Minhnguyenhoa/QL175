package com.projectmgmt.controller;

import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.InputStreamResource;
import org.springframework.http.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.*;

import java.io.*;
import java.nio.file.*;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.TimeUnit;

@RestController
@RequestMapping("/api/report")
@RequiredArgsConstructor
public class ReportController {

    private static final Logger log = LoggerFactory.getLogger(ReportController.class);
    private final JdbcTemplate jdbc;

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

        // Tạo temp file cho PDF output
        Path pdfPath = Files.createTempFile("qt175_report_", ".pdf");

        try {
            List<String> cmd = new java.util.ArrayList<>(java.util.Arrays.asList(
                "python",
                "D:/QT_175/generate_report_pdf.py",
                "--out",  pdfPath.toString(),
                "--date", reportDate,
                "--project", projectCode
            ));
            ProcessBuilder pb = new ProcessBuilder(cmd);
            pb.redirectErrorStream(true);
            pb.environment().put("PYTHONIOENCODING", "utf-8");

            Process process = pb.start();
            String pyOutput = new String(process.getInputStream().readAllBytes(), java.nio.charset.StandardCharsets.UTF_8);
            boolean finished = process.waitFor(120, TimeUnit.SECONDS);

            if (!finished || process.exitValue() != 0) {
                log.error("PDF generation failed: {}", pyOutput);
                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(null);
            }

            log.info("PDF generated: {}", pyOutput.trim());

            byte[] pdfBytes = Files.readAllBytes(pdfPath);
            String filename = "BaoCaoTienDo_" + projLabel + "_" + reportDate.replace("/", "-") + ".pdf";

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_PDF);
            headers.setContentDisposition(ContentDisposition.attachment().filename(filename).build());
            headers.setContentLength(pdfBytes.length);

            return ResponseEntity.ok()
                .headers(headers)
                .body(new InputStreamResource(new ByteArrayInputStream(pdfBytes)));

        } finally {
            try { Files.deleteIfExists(pdfPath); } catch (Exception ignored) {}
        }
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

        Path pdfPath = Files.createTempFile("qt175_slides_", ".pdf");
        try {
            List<String> cmd = new java.util.ArrayList<>(java.util.Arrays.asList(
                "python",
                "D:/QT_175/generate_report_slides.py",
                "--out",  pdfPath.toString(),
                "--date", reportDate,
                "--project", projectCode
            ));
            ProcessBuilder pb = new ProcessBuilder(cmd);
            pb.redirectErrorStream(true);
            pb.environment().put("PYTHONIOENCODING", "utf-8");

            Process process = pb.start();
            String pyOutput = new String(process.getInputStream().readAllBytes(), java.nio.charset.StandardCharsets.UTF_8);
            boolean finished = process.waitFor(120, TimeUnit.SECONDS);

            if (!finished || process.exitValue() != 0) {
                log.error("Slide PDF generation failed: {}", pyOutput);
                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(null);
            }
            log.info("Slide PDF generated: {}", pyOutput.trim());

            byte[] pdfBytes = Files.readAllBytes(pdfPath);
            String filename = "BaoCaoSlide_" + projLabel + "_" + reportDate.replace("/", "-") + ".pdf";

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_PDF);
            headers.setContentDisposition(ContentDisposition.attachment().filename(filename).build());
            headers.setContentLength(pdfBytes.length);
            return ResponseEntity.ok().headers(headers)
                .body(new InputStreamResource(new ByteArrayInputStream(pdfBytes)));
        } finally {
            try { Files.deleteIfExists(pdfPath); } catch (Exception ignored) {}
        }
    }
}
