package com.projectmgmt.dto;

import lombok.*;

@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class DepartmentDTO {
    private Long id;
    private String center;
    private String division;
    private String manager;
    private Integer sortOrder;
}
