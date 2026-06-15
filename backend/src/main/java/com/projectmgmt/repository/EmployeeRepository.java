package com.projectmgmt.repository;

import com.projectmgmt.entity.Employee;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface EmployeeRepository extends JpaRepository<Employee, Long> {
    List<Employee> findByCompany(String company);
    List<Employee> findByContractType(String contractType);
    List<Employee> findByNameContainingIgnoreCase(String name);
}
