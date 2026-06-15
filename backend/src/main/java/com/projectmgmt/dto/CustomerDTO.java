package com.projectmgmt.dto;

import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CustomerDTO {
    private Long id;
    private String investorCode;
    private String investorName;
    private String beneficiaryCode;
    private String beneficiaryName;
    private String projectGroupCode;
}
