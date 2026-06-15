package com.projectmgmt.repository;

import com.projectmgmt.entity.AllocationHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import java.util.List;

public interface AllocationHistoryRepository extends JpaRepository<AllocationHistory, Long> {
    @Query("SELECT ah FROM AllocationHistory ah LEFT JOIN FETCH ah.monthlyAllocations ORDER BY ah.employeeName")
    List<AllocationHistory> findAllWithMonthly();
}
