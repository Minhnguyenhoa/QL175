package com.projectmgmt.service;

import com.projectmgmt.dto.DepartmentDTO;
import com.projectmgmt.entity.Department;
import com.projectmgmt.repository.DepartmentRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.stream.Collectors;

@Service @RequiredArgsConstructor @Transactional
public class DepartmentService {
    private final DepartmentRepository repo;

    public List<DepartmentDTO> getAll() {
        return repo.findAllByOrderBySortOrderAsc().stream().map(this::toDTO).collect(Collectors.toList());
    }

    public DepartmentDTO getById(Long id) {
        return repo.findById(id).map(this::toDTO)
                .orElseThrow(() -> new RuntimeException("Department not found: " + id));
    }

    public DepartmentDTO create(DepartmentDTO dto) {
        return toDTO(repo.save(toEntity(dto)));
    }

    public DepartmentDTO update(Long id, DepartmentDTO dto) {
        Department e = repo.findById(id).orElseThrow(() -> new RuntimeException("Department not found: " + id));
        e.setCenter(dto.getCenter());
        e.setDivision(dto.getDivision());
        e.setManager(dto.getManager());
        e.setSortOrder(dto.getSortOrder());
        return toDTO(repo.save(e));
    }

    public void delete(Long id) { repo.deleteById(id); }

    public DepartmentDTO toDTO(Department d) {
        return DepartmentDTO.builder().id(d.getId()).center(d.getCenter())
                .division(d.getDivision()).manager(d.getManager()).sortOrder(d.getSortOrder()).build();
    }

    private Department toEntity(DepartmentDTO dto) {
        return Department.builder().center(dto.getCenter()).division(dto.getDivision())
                .manager(dto.getManager()).sortOrder(dto.getSortOrder()).build();
    }
}
