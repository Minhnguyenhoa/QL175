package com.projectmgmt.dto;

import lombok.*;
import java.time.LocalDate;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ProductDTO {
    private Long id;
    private String code;
    private String name;
    private Long projectGroupId;
    private String projectGroupCode;
    private String projectGroupName;
    private String pm;
    private LocalDate startDate;
    private LocalDate endDate;
    private String status;
    private String currentPhase;
    private Boolean hasWorkPlan;
}
