package com.projectmgmt.entity;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;

@Entity
@Table(name = "allocation_history_monthly")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class AllocationHistoryMonthly {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "history_id", nullable = false)
    @ToString.Exclude
    private AllocationHistory history;

    @Column(name = "year_month", length = 10)
    private String yearMonth;

    @Column(precision = 5, scale = 4)
    private BigDecimal percent;
}
