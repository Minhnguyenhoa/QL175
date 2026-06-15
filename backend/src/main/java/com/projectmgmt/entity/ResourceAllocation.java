package com.projectmgmt.entity;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

@Entity
@Table(name = "resource_allocations")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ResourceAllocation {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "product_id")
    @ToString.Exclude
    private Product product;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "employee_id")
    @ToString.Exclude
    private Employee employee;

    @Column(name = "role_in_project", length = 255)
    private String roleInProject;

    @Column(name = "from_date")
    private LocalDate fromDate;

    @Column(name = "to_date")
    private LocalDate toDate;

    @Column(name = "allocation_percent", precision = 5, scale = 4)
    private BigDecimal allocationPercent;

    @OneToMany(mappedBy = "allocation", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    @ToString.Exclude
    private List<MonthlyAllocation> monthlyAllocations;
}
