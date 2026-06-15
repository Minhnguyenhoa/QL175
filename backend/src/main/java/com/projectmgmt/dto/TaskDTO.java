package com.projectmgmt.dto;

import lombok.*;

@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class TaskDTO {
    private Long id;
    private String phaseGroup;
    private Long productId;
    private String productCode;
    private String productName;
    private Integer taskNo;
    private String taskName;
    private String content;
    private String featureGroup;
}
