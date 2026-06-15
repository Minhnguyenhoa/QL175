package com.projectmgmt.service;

import com.projectmgmt.dto.PhaseDTO;
import com.projectmgmt.entity.Phase;
import com.projectmgmt.repository.PhaseRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.stream.Collectors;

@Service @RequiredArgsConstructor @Transactional
public class PhaseService {
    private final PhaseRepository repo;

    public List<PhaseDTO> getAll() {
        return repo.findAllByOrderBySortOrderAsc().stream().map(this::toDTO).collect(Collectors.toList());
    }

    public PhaseDTO getById(Long id) {
        return repo.findById(id).map(this::toDTO)
                .orElseThrow(() -> new RuntimeException("Phase not found: " + id));
    }

    public PhaseDTO create(PhaseDTO dto) {
        return toDTO(repo.save(toEntity(dto)));
    }

    public PhaseDTO update(Long id, PhaseDTO dto) {
        Phase e = repo.findById(id).orElseThrow(() -> new RuntimeException("Phase not found: " + id));
        e.setPhaseGroup(dto.getPhaseGroup());
        e.setPhaseName(dto.getPhaseName());
        e.setNote(dto.getNote());
        e.setSortOrder(dto.getSortOrder());
        return toDTO(repo.save(e));
    }

    public void delete(Long id) { repo.deleteById(id); }

    public PhaseDTO toDTO(Phase p) {
        return PhaseDTO.builder().id(p.getId()).phaseGroup(p.getPhaseGroup())
                .phaseName(p.getPhaseName()).note(p.getNote()).sortOrder(p.getSortOrder()).build();
    }

    private Phase toEntity(PhaseDTO dto) {
        return Phase.builder().phaseGroup(dto.getPhaseGroup()).phaseName(dto.getPhaseName())
                .note(dto.getNote()).sortOrder(dto.getSortOrder()).build();
    }
}
