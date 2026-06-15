package com.projectmgmt.repository;

import com.projectmgmt.entity.Department;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface DepartmentRepository extends JpaRepository<Department, Long> {
    List<Department> findByCenter(String center);
    List<Department> findAllByOrderBySortOrderAsc();
}
