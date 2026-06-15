package com.projectmgmt.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDate;
import java.util.List;

@Entity
@Table(name = "milestones")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Milestone {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "phase", length = 255)
    private String phase;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "product_id")
    @ToString.Exclude
    private Product product;

    @Column(name = "component_milestone", length = 500)
    private String componentMilestone;

    @Column(name = "detail_milestone", columnDefinition = "TEXT")
    private String detailMilestone;

    @Column(name = "has_gtel")
    private Boolean hasGtel;

    @Column(name = "has_outsource_gtel")
    private Boolean hasOutsourceGtel;

    @Column(name = "has_outsource_online")
    private Boolean hasOutsourceOnline;

    @Column(name = "plan_start_date")
    private LocalDate planStartDate;

    @Column(name = "plan_end_date")
    private LocalDate planEndDate;

    @Column(name = "actual_start_date")
    private LocalDate actualStartDate;

    @Column(name = "actual_end_date")
    private LocalDate actualEndDate;

    @Column(name = "current_phase", length = 255)
    private String currentPhase;

    @Column(name = "status", length = 100)
    private String status;

    @Column(name = "remind", length = 100)
    private String remind;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "parent_id")
    @ToString.Exclude
    private Milestone parent;

    @OneToMany(mappedBy = "parent", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    @ToString.Exclude
    private List<Milestone> children;
}
