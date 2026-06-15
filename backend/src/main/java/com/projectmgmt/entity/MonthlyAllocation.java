package com.projectmgmt.entity;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;

@Entity
@Table(name = "monthly_allocations")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MonthlyAllocation {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "allocation_id")
    @ToString.Exclude
    private ResourceAllocation allocation;

    @Column(name = "year_month", length = 10)
    private String yearMonth;

    @Column(name = "percent", precision = 5, scale = 4)
    private BigDecimal percent;
}
