package com.projectmgmt.entity;

import jakarta.persistence.*;
import lombok.*;
import java.util.List;

@Entity
@Table(name = "project_groups")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ProjectGroup {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "code", length = 50, unique = true, nullable = false)
    private String code;

    @Column(name = "name", length = 500)
    private String name;

    @Column(name = "director", length = 255)
    private String director;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "customer_id")
    @ToString.Exclude
    private Customer customer;

    @OneToMany(mappedBy = "projectGroup", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    @ToString.Exclude
    private List<Product> products;
}
