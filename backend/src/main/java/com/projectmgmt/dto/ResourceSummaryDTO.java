package com.projectmgmt.dto;

import lombok.*;
import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class ResourceSummaryDTO {
    private Long employeeId;
    private String employeeName;
    private String employeeCompany;
    private String contractType;
    // key = yearMonth (e.g. "T6-2025"), value = total allocation %
    private Map<String, BigDecimal> monthlyTotal;
    // projects this employee is assigned to
    private List<String> projects;
    // flag months where total > 100%
    private Map<String, Boolean> overloaded;
}
