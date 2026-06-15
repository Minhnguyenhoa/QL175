package com.projectmgmt.repository;

import com.projectmgmt.entity.Task;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.util.List;

public interface TaskRepository extends JpaRepository<Task, Long> {
    List<Task> findByProductId(Long productId);
    List<Task> findByPhaseGroup(String phaseGroup);

    @Query("SELECT t FROM Task t LEFT JOIN FETCH t.product ORDER BY t.phaseGroup, t.product.code, t.taskNo")
    List<Task> findAllOrdered();

    @Query("SELECT t FROM Task t LEFT JOIN FETCH t.product WHERE t.product.id = :productId ORDER BY t.taskNo")
    List<Task> findByProductIdOrdered(@Param("productId") Long productId);
}
