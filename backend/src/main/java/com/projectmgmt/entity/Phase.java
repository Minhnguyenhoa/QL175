package com.projectmgmt.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "phases")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class Phase {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "phase_group", length = 255)
    private String phaseGroup;

    @Column(name = "phase_name", length = 500)
    private String phaseName;

    @Column(name = "note", length = 500)
    private String note;

    @Column(name = "sort_order")
    private Integer sortOrder;
}
