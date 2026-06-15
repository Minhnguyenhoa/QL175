package com.projectmgmt.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDate;
import java.util.List;

@Entity
@Table(name = "products")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "code", length = 50, unique = true, nullable = false)
    private String code;

    @Column(name = "name", length = 500)
    private String name;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "project_group_id")
    @ToString.Exclude
    private ProjectGroup projectGroup;

    @Column(name = "pm", length = 255)
    private String pm;

    @Column(name = "start_date")
    private LocalDate startDate;

    @Column(name = "end_date")
    private LocalDate endDate;

    @Column(name = "status", length = 50)
    private String status;

    @Column(name = "current_phase", length = 255)
    private String currentPhase;

    @Column(name = "has_work_plan")
    private Boolean hasWorkPlan;

    @OneToMany(mappedBy = "product", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    @ToString.Exclude
    private List<ResourceAllocation> resourceAllocations;

    @OneToMany(mappedBy = "product", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    @ToString.Exclude
    private List<Milestone> milestones;
}
