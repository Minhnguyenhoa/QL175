package com.projectmgmt.entity;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

@Entity
@Table(name = "allocation_history")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class AllocationHistory {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // comma-separated product codes, e.g. "HIS, LIS, EMR"
    @Column(name = "projects_text", length = 500)
    private String projectsText;

    @Column(name = "employee_name", length = 255)
    private String employeeName;

    @Column(name = "role_in_project", length = 255)
    private String roleInProject;

    @Column(name = "from_date")
    private LocalDate fromDate;

    @Column(name = "to_date")
    private LocalDate toDate;

    @Column(name = "allocation_percent", precision = 5, scale = 4)
    private BigDecimal allocationPercent;

    @OneToMany(mappedBy = "history", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    @ToString.Exclude
    private List<AllocationHistoryMonthly> monthlyAllocations;
}
