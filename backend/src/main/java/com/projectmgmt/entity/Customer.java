package com.projectmgmt.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "customers")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Customer {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "investor_code", length = 50)
    private String investorCode;

    @Column(name = "investor_name", length = 255)
    private String investorName;

    @Column(name = "beneficiary_code", length = 50)
    private String beneficiaryCode;

    @Column(name = "beneficiary_name", length = 255)
    private String beneficiaryName;

    @Column(name = "project_group_code", length = 50)
    private String projectGroupCode;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
