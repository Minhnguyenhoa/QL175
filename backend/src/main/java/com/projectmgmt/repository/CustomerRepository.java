package com.projectmgmt.repository;

import com.projectmgmt.entity.Customer;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface CustomerRepository extends JpaRepository<Customer, Long> {
    Optional<Customer> findByProjectGroupCode(String projectGroupCode);
    boolean existsByInvestorCode(String investorCode);
}
