package com.projectmgmt.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/dashboard")
@RequiredArgsConstructor
public class DashboardController {

    private final JdbcTemplate jdbc;

    @GetMapping
    public Map<String, Object> getDashboard(
            @RequestParam(value = "productId", required = false) Long productId) {
        Map<String, Object> r = new LinkedHashMap<>();

        // productId được validate là Long (an toàn để nội suy vào SQL).
        boolean filt = productId != null;
        // Điều kiện lọc theo dự án (sản phẩm) cho từng dạng truy vấn:
        String mWhere   = filt ? " WHERE product_id=" + productId : "";          // bảng milestones (không alias)
        String mAndM    = filt ? " AND m.product_id=" + productId : "";
        String mAndPhase= filt ? " AND product_id=" + productId : "";
        // Nhân viên thuộc dự án = có phân bổ vào sản phẩm này
        String empIn    = filt ? " WHERE id IN (SELECT DISTINCT employee_id FROM resource_allocations WHERE product_id="
                                  + productId + ")" : "";
        String prodWhere= filt ? " WHERE p.id=" + productId : "";

        // ── KPI tổng quan ────────────────────────────────────────────────────
        r.put("totalProjects",   jdbc.queryForObject("SELECT COUNT(*) FROM project_groups", Long.class));
        r.put("totalProducts",   filt ? 1L : jdbc.queryForObject("SELECT COUNT(*) FROM products", Long.class));
        r.put("totalEmployees",  jdbc.queryForObject("SELECT COUNT(*) FROM employees" + empIn, Long.class));
        r.put("totalMilestones", jdbc.queryForObject("SELECT COUNT(*) FROM milestones" + mWhere, Long.class));
        r.put("doneMilestones",  jdbc.queryForObject(
            "SELECT COUNT(*) FROM milestones WHERE actual_end_date IS NOT NULL" + mAndPhase, Long.class));
        r.put("inProgressMilestones", jdbc.queryForObject(
            "SELECT COUNT(*) FROM milestones WHERE actual_end_date IS NULL AND current_phase IS NOT NULL" + mAndPhase, Long.class));
        r.put("overdueMilestones",  jdbc.queryForObject(
            "SELECT COUNT(*) FROM milestones WHERE remind='Quá hạn'" + mAndPhase, Long.class));
        r.put("upcomingMilestones", jdbc.queryForObject(
            "SELECT COUNT(*) FROM milestones WHERE remind='Sắp đến hạn'" + mAndPhase, Long.class));
        r.put("totalMM", jdbc.queryForObject(
            "SELECT COALESCE(SUM(allocation_percent),0) FROM resource_allocations"
            + (filt ? " WHERE product_id=" + productId : ""), Double.class));
        r.put("gtelEmployees",  jdbc.queryForObject(
            "SELECT COUNT(*) FROM employees WHERE company='GTEL ICT'"
            + (filt ? " AND id IN (SELECT DISTINCT employee_id FROM resource_allocations WHERE product_id="
                      + productId + ")" : ""), Long.class));

        // ── Theo giai đoạn ────────────────────────────────────────────────────
        r.put("byPhase", jdbc.queryForList(
            "SELECT phase, COUNT(*) total," +
            " SUM(actual_end_date IS NOT NULL) done," +
            " SUM(actual_end_date IS NULL AND current_phase IS NOT NULL) in_progress," +
            " SUM(remind='Quá hạn') overdue" +
            " FROM milestones WHERE phase IS NOT NULL" + mAndPhase + " GROUP BY phase ORDER BY phase"));

        // ── Theo sản phẩm ─────────────────────────────────────────────────────
        r.put("byProduct", jdbc.queryForList(
            "SELECT p.code, p.name, p.current_phase cur_phase," +
            " COUNT(m.id) total," +
            " SUM(m.actual_end_date IS NOT NULL) done," +
            " SUM(m.actual_end_date IS NULL AND m.current_phase IS NOT NULL) in_progress," +
            " SUM(m.remind='Quá hạn') overdue" +
            " FROM products p LEFT JOIN milestones m ON m.product_id=p.id" + prodWhere +
            " GROUP BY p.id,p.code,p.name,p.current_phase ORDER BY p.code"));

        // ── Nhân sự theo công ty ─────────────────────────────────────────────
        r.put("byCompany", jdbc.queryForList(
            "SELECT e.company, COUNT(DISTINCT e.id) hc FROM employees e" +
            (filt ? " JOIN resource_allocations ra ON ra.employee_id=e.id AND ra.product_id=" + productId : "") +
            " WHERE e.company IS NOT NULL GROUP BY e.company ORDER BY hc DESC"));

        // ── Phân bổ MM theo sản phẩm ─────────────────────────────────────────
        r.put("allocationByProduct", jdbc.queryForList(
            "SELECT p.code, p.name," +
            " COUNT(DISTINCT ra.employee_id) hc," +
            " ROUND(SUM(ra.allocation_percent),2) mm" +
            " FROM resource_allocations ra JOIN products p ON ra.product_id=p.id" +
            (filt ? " WHERE p.id=" + productId : "") +
            " GROUP BY p.id,p.code,p.name ORDER BY mm DESC"));

        // ── Milestone sắp / quá hạn gần nhất ────────────────────────────────
        r.put("recentOverdue", jdbc.queryForList(
            "SELECT p.code product_code, m.component_milestone, m.detail_milestone," +
            " m.plan_end_date, m.remind" +
            " FROM milestones m JOIN products p ON m.product_id=p.id" +
            " WHERE m.remind IN ('Quá hạn','Sắp đến hạn')" + mAndM +
            " ORDER BY m.plan_end_date ASC LIMIT 15"));

        return r;
    }
}
