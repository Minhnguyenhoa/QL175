package com.projectmgmt.repository;

import com.projectmgmt.entity.AllocationHistoryMonthly;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;

public interface AllocationHistoryMonthlyRepository extends JpaRepository<AllocationHistoryMonthly, Long> {
    @Modifying
    @Query("DELETE FROM AllocationHistoryMonthly m WHERE m.history.id = :historyId")
    void deleteByHistoryId(Long historyId);
}
