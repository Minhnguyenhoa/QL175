package com.projectmgmt.service;

import com.projectmgmt.dto.ProductDTO;
import com.projectmgmt.entity.Product;
import com.projectmgmt.repository.ProductRepository;
import com.projectmgmt.repository.ProjectGroupRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
public class ProductService {
    private final ProductRepository productRepository;
    private final ProjectGroupRepository projectGroupRepository;

    public List<ProductDTO> getAll() {
        return productRepository.findAll().stream().map(this::toDTO).collect(Collectors.toList());
    }

    public ProductDTO getById(Long id) {
        return productRepository.findById(id).map(this::toDTO)
                .orElseThrow(() -> new RuntimeException("Product not found: " + id));
    }

    public List<ProductDTO> getByProjectGroup(Long projectGroupId) {
        return productRepository.findByProjectGroupId(projectGroupId).stream()
                .map(this::toDTO).collect(Collectors.toList());
    }

    public ProductDTO create(ProductDTO dto) {
        Product entity = toEntity(dto);
        return toDTO(productRepository.save(entity));
    }

    public ProductDTO update(Long id, ProductDTO dto) {
        Product existing = productRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Product not found: " + id));
        existing.setCode(dto.getCode());
        existing.setName(dto.getName());
        existing.setPm(dto.getPm());
        existing.setStartDate(dto.getStartDate());
        existing.setEndDate(dto.getEndDate());
        existing.setStatus(dto.getStatus());
        existing.setCurrentPhase(dto.getCurrentPhase());
        existing.setHasWorkPlan(dto.getHasWorkPlan());
        if (dto.getProjectGroupId() != null) {
            projectGroupRepository.findById(dto.getProjectGroupId()).ifPresent(existing::setProjectGroup);
        }
        return toDTO(productRepository.save(existing));
    }

    public void delete(Long id) {
        productRepository.deleteById(id);
    }

    public ProductDTO toDTO(Product p) {
        ProductDTO dto = ProductDTO.builder()
                .id(p.getId())
                .code(p.getCode())
                .name(p.getName())
                .pm(p.getPm())
                .startDate(p.getStartDate())
                .endDate(p.getEndDate())
                .status(p.getStatus())
                .currentPhase(p.getCurrentPhase())
                .hasWorkPlan(p.getHasWorkPlan())
                .build();
        if (p.getProjectGroup() != null) {
            dto.setProjectGroupId(p.getProjectGroup().getId());
            dto.setProjectGroupCode(p.getProjectGroup().getCode());
            dto.setProjectGroupName(p.getProjectGroup().getName());
        }
        return dto;
    }

    private Product toEntity(ProductDTO dto) {
        Product p = Product.builder()
                .code(dto.getCode())
                .name(dto.getName())
                .pm(dto.getPm())
                .startDate(dto.getStartDate())
                .endDate(dto.getEndDate())
                .status(dto.getStatus())
                .currentPhase(dto.getCurrentPhase())
                .hasWorkPlan(dto.getHasWorkPlan())
                .build();
        if (dto.getProjectGroupId() != null) {
            projectGroupRepository.findById(dto.getProjectGroupId()).ifPresent(p::setProjectGroup);
        }
        return p;
    }
}
