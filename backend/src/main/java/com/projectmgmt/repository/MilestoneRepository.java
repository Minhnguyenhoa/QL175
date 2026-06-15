package com.projectmgmt.repository;

import com.projectmgmt.entity.Milestone;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.util.List;

public interface MilestoneRepository extends JpaRepository<Milestone, Long> {
    List<Milestone> findByProductId(Long productId);
    List<Milestone> findByStatus(String status);
    List<Milestone> findByRemind(String remind);
    List<Milestone> findByPhase(String phase);
    List<Milestone> findByParentIsNull();

    @Query("SELECT m FROM Milestone m WHERE m.product.id = :productId AND m.parent IS NULL")
    List<Milestone> findRootMilestonesByProduct(@Param("productId") Long productId);

    @Query("SELECT m FROM Milestone m WHERE m.remind IN ('Quá hạn', 'Sắp đến hạn')")
    List<Milestone> findOverdueOrUpcoming();

    @Query("SELECT m.status, COUNT(m) FROM Milestone m GROUP BY m.status")
    List<Object[]> countByStatus();
}
