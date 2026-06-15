package com.projectmgmt.service;

import com.projectmgmt.dto.ProductDTO;
import com.projectmgmt.dto.ProjectGroupDTO;
import com.projectmgmt.entity.Customer;
import com.projectmgmt.entity.ProjectGroup;
import com.projectmgmt.repository.CustomerRepository;
import com.projectmgmt.repository.ProjectGroupRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
public class ProjectGroupService {
    private final ProjectGroupRepository projectGroupRepository;
    private final CustomerRepository customerRepository;

    public List<ProjectGroupDTO> getAll() {
        return projectGroupRepository.findAll().stream().map(this::toDTO).collect(Collectors.toList());
    }

    public ProjectGroupDTO getById(Long id) {
        return projectGroupRepository.findById(id).map(this::toDTO)
                .orElseThrow(() -> new RuntimeException("ProjectGroup not found: " + id));
    }

    public ProjectGroupDTO create(ProjectGroupDTO dto) {
        ProjectGroup entity = toEntity(dto);
        return toDTO(projectGroupRepository.save(entity));
    }

    public ProjectGroupDTO update(Long id, ProjectGroupDTO dto) {
        ProjectGroup existing = projectGroupRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("ProjectGroup not found: " + id));
        existing.setCode(dto.getCode());
        existing.setName(dto.getName());
        existing.setDirector(dto.getDirector());
        if (dto.getCustomerId() != null) {
            customerRepository.findById(dto.getCustomerId()).ifPresent(existing::setCustomer);
        }
        return toDTO(projectGroupRepository.save(existing));
    }

    public void delete(Long id) {
        projectGroupRepository.deleteById(id);
    }

    public ProjectGroupDTO toDTO(ProjectGroup pg) {
        ProjectGroupDTO dto = ProjectGroupDTO.builder()
                .id(pg.getId())
                .code(pg.getCode())
                .name(pg.getName())
                .director(pg.getDirector())
                .build();
        if (pg.getCustomer() != null) {
            dto.setCustomerId(pg.getCustomer().getId());
            dto.setCustomerName(pg.getCustomer().getInvestorName());
        }
        if (pg.getProducts() != null) {
            dto.setProducts(pg.getProducts().stream().map(p -> ProductDTO.builder()
                    .id(p.getId())
                    .code(p.getCode())
                    .name(p.getName())
                    .pm(p.getPm())
                    .startDate(p.getStartDate())
                    .endDate(p.getEndDate())
                    .status(p.getStatus())
                    .currentPhase(p.getCurrentPhase())
                    .hasWorkPlan(p.getHasWorkPlan())
                    .build()).collect(Collectors.toList()));
        }
        return dto;
    }

    private ProjectGroup toEntity(ProjectGroupDTO dto) {
        ProjectGroup pg = ProjectGroup.builder()
                .code(dto.getCode())
                .name(dto.getName())
                .director(dto.getDirector())
                .build();
        if (dto.getCustomerId() != null) {
            customerRepository.findById(dto.getCustomerId()).ifPresent(pg::setCustomer);
        }
        return pg;
    }
}
