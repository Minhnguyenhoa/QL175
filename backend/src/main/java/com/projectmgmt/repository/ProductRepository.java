package com.projectmgmt.repository;

import com.projectmgmt.entity.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import java.util.List;
import java.util.Optional;

public interface ProductRepository extends JpaRepository<Product, Long> {
    Optional<Product> findByCode(String code);
    boolean existsByCode(String code);
    List<Product> findByProjectGroupId(Long projectGroupId);

    @Query("SELECT p FROM Product p WHERE p.status = :status")
    List<Product> findByStatus(String status);

    @Query("SELECT p.status, COUNT(p) FROM Product p GROUP BY p.status")
    List<Object[]> countByStatus();
}
