package com.projectmgmt.dto;

import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;

@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class AllocationHistoryDTO {
    private Long id;
    private String projectsText;
    private String employeeName;
    private String roleInProject;
    private LocalDate fromDate;
    private LocalDate toDate;
    private BigDecimal allocationPercent;
    private List<MonthlyAllocationDTO> monthlyAllocations;

    @Data @NoArgsConstructor @AllArgsConstructor @Builder
    public static class MonthlyAllocationDTO {
        private Long id;
        private String yearMonth;
        private BigDecimal percent;
    }
}
