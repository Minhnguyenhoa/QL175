package com.projectmgmt.repository;

import com.projectmgmt.entity.ResourceAllocation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.util.List;

public interface ResourceAllocationRepository extends JpaRepository<ResourceAllocation, Long> {
    List<ResourceAllocation> findByProductId(Long productId);
    List<ResourceAllocation> findByEmployeeId(Long employeeId);

    @Query("SELECT ra FROM ResourceAllocation ra LEFT JOIN FETCH ra.monthlyAllocations WHERE ra.product.id = :productId")
    List<ResourceAllocation> findByProductIdWithMonthly(@Param("productId") Long productId);

    @Query("SELECT ra FROM ResourceAllocation ra LEFT JOIN FETCH ra.monthlyAllocations WHERE ra.employee.id = :employeeId")
    List<ResourceAllocation> findByEmployeeIdWithMonthly(@Param("employeeId") Long employeeId);

    @Query("SELECT ra FROM ResourceAllocation ra LEFT JOIN FETCH ra.employee LEFT JOIN FETCH ra.product LEFT JOIN FETCH ra.monthlyAllocations")
    List<ResourceAllocation> findAllWithDetails();

    void deleteByProductIdAndEmployeeId(Long productId, Long employeeId);
}
