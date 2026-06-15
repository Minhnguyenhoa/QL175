package com.projectmgmt.dto;

import lombok.*;
import java.util.List;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DashboardDTO {
    private long totalProjects;
    private long totalProducts;
    private long totalEmployees;
    private long totalMilestones;
    private long overdueMilestones;
    private long upcomingMilestones;
    private Map<String, Long> productsByStatus;
    private Map<String, Long> milestonesByStatus;
    private Map<String, Long> employeesByCompany;
    private List<MilestoneDTO> recentOverdue;
}
