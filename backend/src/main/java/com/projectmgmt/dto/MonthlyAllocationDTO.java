package com.projectmgmt.dto;

import lombok.*;
import java.math.BigDecimal;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MonthlyAllocationDTO {
    private Long id;
    private String yearMonth;
    private BigDecimal percent;
}
