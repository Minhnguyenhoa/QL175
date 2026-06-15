package com.projectmgmt.dto;

import lombok.*;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ProjectGroupDTO {
    private Long id;
    private String code;
    private String name;
    private String director;
    private Long customerId;
    private String customerName;
    private List<ProductDTO> products;
}
