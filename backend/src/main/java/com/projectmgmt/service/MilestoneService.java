package com.projectmgmt.service;

import com.projectmgmt.dto.MilestoneDTO;
import com.projectmgmt.entity.Milestone;
import com.projectmgmt.repository.MilestoneRepository;
import com.projectmgmt.repository.ProductRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
public class MilestoneService {
    private final MilestoneRepository milestoneRepository;
    private final ProductRepository productRepository;

    public List<MilestoneDTO> getAll() {
        return milestoneRepository.findAll().stream().map(this::toDTO).collect(Collectors.toList());
    }

    public MilestoneDTO getById(Long id) {
        return milestoneRepository.findById(id).map(this::toDTO)
                .orElseThrow(() -> new RuntimeException("Milestone not found: " + id));
    }

    public List<MilestoneDTO> getByProduct(Long productId) {
        return milestoneRepository.findByProductId(productId).stream()
                .map(this::toDTO).collect(Collectors.toList());
    }

    public List<MilestoneDTO> getOverdueOrUpcoming() {
        return milestoneRepository.findOverdueOrUpcoming().stream()
                .map(this::toDTO).collect(Collectors.toList());
    }

    public MilestoneDTO create(MilestoneDTO dto) {
        return toDTO(milestoneRepository.save(toEntity(dto)));
    }

    public MilestoneDTO update(Long id, MilestoneDTO dto) {
        Milestone existing = milestoneRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Milestone not found: " + id));
        existing.setPhase(dto.getPhase());
        existing.setComponentMilestone(dto.getComponentMilestone());
        existing.setDetailMilestone(dto.getDetailMilestone());
        existing.setHasGtel(dto.getHasGtel());
        existing.setHasOutsourceGtel(dto.getHasOutsourceGtel());
        existing.setHasOutsourceOnline(dto.getHasOutsourceOnline());
        existing.setPlanStartDate(dto.getPlanStartDate());
        existing.setPlanEndDate(dto.getPlanEndDate());
        existing.setActualStartDate(dto.getActualStartDate());
        existing.setActualEndDate(dto.getActualEndDate());
        existing.setCurrentPhase(dto.getCurrentPhase());
        existing.setStatus(dto.getStatus());
        existing.setRemind(dto.getRemind());
        if (dto.getProductId() != null) {
            productRepository.findById(dto.getProductId()).ifPresent(existing::setProduct);
        }
        if (dto.getParentId() != null) {
            milestoneRepository.findById(dto.getParentId()).ifPresent(existing::setParent);
        }
        return toDTO(milestoneRepository.save(existing));
    }

    public void delete(Long id) {
        milestoneRepository.deleteById(id);
    }

    public MilestoneDTO toDTO(Milestone m) {
        MilestoneDTO dto = MilestoneDTO.builder()
                .id(m.getId())
                .phase(m.getPhase())
                .componentMilestone(m.getComponentMilestone())
                .detailMilestone(m.getDetailMilestone())
                .hasGtel(m.getHasGtel())
                .hasOutsourceGtel(m.getHasOutsourceGtel())
                .hasOutsourceOnline(m.getHasOutsourceOnline())
                .planStartDate(m.getPlanStartDate())
                .planEndDate(m.getPlanEndDate())
                .actualStartDate(m.getActualStartDate())
                .actualEndDate(m.getActualEndDate())
                .currentPhase(m.getCurrentPhase())
                .status(m.getStatus())
                .remind(m.getRemind())
                .build();
        if (m.getProduct() != null) {
            dto.setProductId(m.getProduct().getId());
            dto.setProductCode(m.getProduct().getCode());
            dto.setProductName(m.getProduct().getName());
        }
        if (m.getParent() != null) {
            dto.setParentId(m.getParent().getId());
        }
        if (m.getChildren() != null && !m.getChildren().isEmpty()) {
            dto.setChildren(m.getChildren().stream().map(this::toDTO).collect(Collectors.toList()));
        }
        return dto;
    }

    private Milestone toEntity(MilestoneDTO dto) {
        Milestone m = Milestone.builder()
                .phase(dto.getPhase())
                .componentMilestone(dto.getComponentMilestone())
                .detailMilestone(dto.getDetailMilestone())
                .hasGtel(dto.getHasGtel())
                .hasOutsourceGtel(dto.getHasOutsourceGtel())
                .hasOutsourceOnline(dto.getHasOutsourceOnline())
                .planStartDate(dto.getPlanStartDate())
                .planEndDate(dto.getPlanEndDate())
                .actualStartDate(dto.getActualStartDate())
                .actualEndDate(dto.getActualEndDate())
                .currentPhase(dto.getCurrentPhase())
                .status(dto.getStatus())
                .remind(dto.getRemind())
                .build();
        if (dto.getProductId() != null) {
            productRepository.findById(dto.getProductId()).ifPresent(m::setProduct);
        }
        if (dto.getParentId() != null) {
            milestoneRepository.findById(dto.getParentId()).ifPresent(m::setParent);
        }
        return m;
    }
}
