package com.projectmgmt.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "users")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class User {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false, length = 100)
    private String username;

    @Column(nullable = false)
    private String password;

    @Column(name = "full_name", length = 200)
    private String fullName;

    @Builder.Default
    private boolean enabled = true;
}
