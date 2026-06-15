package com.projectmgmt.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "employees")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Employee {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "name", length = 255, nullable = false)
    private String name;

    @Column(name = "account", length = 255)
    private String account;

    @Column(name = "company", length = 255)
    private String company;

    @Column(name = "department", length = 255)
    private String department;

    @Column(name = "role", length = 255)
    private String role;

    @Column(name = "level", length = 100)
    private String level;

    @Column(name = "contract_type", length = 100)
    private String contractType;

    @Column(name = "work_mode", length = 100)
    private String workMode;

    @Column(name = "work_time", length = 100)
    private String workTime;

    @Column(name = "payment_type", length = 100)
    private String paymentType;

    @Column(name = "work_status", length = 100)
    private String workStatus;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @OneToMany(mappedBy = "employee", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    @ToString.Exclude
    private List<ResourceAllocation> resourceAllocations;

    @PrePersist
    void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
