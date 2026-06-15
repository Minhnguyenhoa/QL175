package com.projectmgmt.dto;

import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ResourceAllocationDTO {
    private Long id;
    private Long productId;
    private String productCode;
    private String productName;
    private Long employeeId;
    private String employeeName;
    private String employeeCompany;
    private String roleInProject;
    private LocalDate fromDate;
    private LocalDate toDate;
    private BigDecimal allocationPercent;
    private List<MonthlyAllocationDTO> monthlyAllocations;
}
