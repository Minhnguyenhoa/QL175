package com.projectmgmt.repository;

import com.projectmgmt.entity.MonthlyAllocation;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface MonthlyAllocationRepository extends JpaRepository<MonthlyAllocation, Long> {
    List<MonthlyAllocation> findByAllocationId(Long allocationId);
    void deleteByAllocationId(Long allocationId);
}
