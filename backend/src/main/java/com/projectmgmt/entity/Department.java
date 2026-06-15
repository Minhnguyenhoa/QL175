package com.projectmgmt.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "departments")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class Department {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "center", length = 255)
    private String center;

    @Column(name = "division", length = 255)
    private String division;

    @Column(name = "manager", length = 255)
    private String manager;

    @Column(name = "sort_order")
    private Integer sortOrder;
}
