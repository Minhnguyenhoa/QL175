package com.projectmgmt.repository;

import com.projectmgmt.entity.ProjectGroup;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import java.util.List;
import java.util.Optional;

public interface ProjectGroupRepository extends JpaRepository<ProjectGroup, Long> {
    Optional<ProjectGroup> findByCode(String code);
    boolean existsByCode(String code);

    @Query("SELECT pg FROM ProjectGroup pg LEFT JOIN FETCH pg.products")
    List<ProjectGroup> findAllWithProducts();
}
