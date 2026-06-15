package com.projectmgmt.dto;

import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class EmployeeDTO {
    private Long id;
    private String name;
    private String account;
    private String company;
    private String department;
    private String role;
    private String level;
    private String contractType;
    private String workMode;
    private String workTime;
    private String paymentType;
    private String workStatus;
}
