package com.projectmgmt.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "tasks")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class Task {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "phase_group", length = 255)
    private String phaseGroup;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "product_id")
    @ToString.Exclude
    private Product product;

    @Column(name = "task_no")
    private Integer taskNo;

    @Column(name = "task_name", length = 500)
    private String taskName;

    @Column(name = "content", columnDefinition = "TEXT")
    private String content;

    @Column(name = "feature_group", length = 500)
    private String featureGroup;
}
