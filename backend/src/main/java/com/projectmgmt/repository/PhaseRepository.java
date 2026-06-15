package com.projectmgmt.repository;

import com.projectmgmt.entity.Phase;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface PhaseRepository extends JpaRepository<Phase, Long> {
    List<Phase> findByPhaseGroup(String phaseGroup);
    List<Phase> findAllByOrderBySortOrderAsc();
    List<String> findDistinctPhaseGroupBy();
}
