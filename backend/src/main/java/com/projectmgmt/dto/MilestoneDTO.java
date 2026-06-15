package com.projectmgmt.dto;

import lombok.*;
import java.time.LocalDate;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MilestoneDTO {
    private Long id;
    private String phase;
    private Long productId;
    private String productCode;
    private String productName;
    private String componentMilestone;
    private String detailMilestone;
    private Boolean hasGtel;
    private Boolean hasOutsourceGtel;
    private Boolean hasOutsourceOnline;
    private LocalDate planStartDate;
    private LocalDate planEndDate;
    private LocalDate actualStartDate;
    private LocalDate actualEndDate;
    private String currentPhase;
    private String status;
    private String remind;
    private Long parentId;
    private List<MilestoneDTO> children;
}
