package com.projectmgmt.dto;

import lombok.*;

@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class PhaseDTO {
    private Long id;
    private String phaseGroup;
    private String phaseName;
    private String note;
    private Integer sortOrder;
}
