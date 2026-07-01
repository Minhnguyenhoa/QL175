package com.projectmgmt.service;

import com.projectmgmt.dto.MonthlyAllocationDTO;
import com.projectmgmt.dto.ResourceAllocationDTO;
import com.projectmgmt.entity.*;
import com.projectmgmt.repository.*;
import com.projectmgmt.util.LazyRefs;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
public class ResourceAllocationService {
    private final ResourceAllocationRepository allocationRepository;
    private final MonthlyAllocationRepository monthlyRepository;
    private final ProductRepository productRepository;
    private final EmployeeRepository employeeRepository;

    public List<ResourceAllocationDTO> getAll() {
        return allocationRepository.findAllWithDetails().stream().map(this::toDTO).collect(Collectors.toList());
    }

    public List<ResourceAllocationDTO> getByProduct(Long productId) {
        return allocationRepository.findByProductIdWithMonthly(productId).stream()
                .map(this::toDTO).collect(Collectors.toList());
    }

    public List<ResourceAllocationDTO> getByEmployee(Long employeeId) {
        return allocationRepository.findByEmployeeIdWithMonthly(employeeId).stream()
                .map(this::toDTO).collect(Collectors.toList());
    }

    public ResourceAllocationDTO getById(Long id) {
        return allocationRepository.findById(id).map(this::toDTO)
                .orElseThrow(() -> new RuntimeException("Allocation not found: " + id));
    }

    public ResourceAllocationDTO create(ResourceAllocationDTO dto) {
        ResourceAllocation entity = toEntity(dto);
        ResourceAllocation saved = allocationRepository.save(entity);
        if (dto.getMonthlyAllocations() != null) {
            saveMonthlyAllocations(saved, dto.getMonthlyAllocations());
        }
        return toDTO(allocationRepository.findById(saved.getId()).orElse(saved));
    }

    public ResourceAllocationDTO update(Long id, ResourceAllocationDTO dto) {
        ResourceAllocation existing = allocationRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Allocation not found: " + id));
        existing.setRoleInProject(dto.getRoleInProject());
        existing.setFromDate(dto.getFromDate());
        existing.setToDate(dto.getToDate());
        existing.setAllocationPercent(dto.getAllocationPercent());
        if (dto.getProductId() != null) {
            productRepository.findById(dto.getProductId()).ifPresent(existing::setProduct);
        }
        if (dto.getEmployeeId() != null) {
            employeeRepository.findById(dto.getEmployeeId()).ifPresent(existing::setEmployee);
        }
        allocationRepository.save(existing);
        if (dto.getMonthlyAllocations() != null) {
            monthlyRepository.deleteByAllocationId(id);
            saveMonthlyAllocations(existing, dto.getMonthlyAllocations());
        }
        return toDTO(allocationRepository.findById(id).orElse(existing));
    }

    public void delete(Long id) {
        monthlyRepository.deleteByAllocationId(id);
        allocationRepository.deleteById(id);
    }

    private void saveMonthlyAllocations(ResourceAllocation allocation, List<MonthlyAllocationDTO> monthlyDTOs) {
        monthlyDTOs.forEach(m -> {
            MonthlyAllocation ma = MonthlyAllocation.builder()
                    .allocation(allocation)
                    .yearMonth(m.getYearMonth())
                    .percent(m.getPercent())
                    .build();
            monthlyRepository.save(ma);
        });
    }

    public ResourceAllocationDTO toDTO(ResourceAllocation ra) {
        ResourceAllocationDTO dto = ResourceAllocationDTO.builder()
                .id(ra.getId())
                .roleInProject(ra.getRoleInProject())
                .fromDate(ra.getFromDate())
                .toDate(ra.getToDate())
                .allocationPercent(ra.getAllocationPercent())
                .build();
        var prod = LazyRefs.load(ra.getProduct());
        if (prod != null) {
            dto.setProductId(prod.getId());
            dto.setProductCode(prod.getCode());
            dto.setProductName(prod.getName());
        }
        var emp = LazyRefs.load(ra.getEmployee());
        if (emp != null) {
            dto.setEmployeeId(emp.getId());
            dto.setEmployeeName(emp.getName());
            dto.setEmployeeCompany(emp.getCompany());
        }
        if (ra.getMonthlyAllocations() != null) {
            dto.setMonthlyAllocations(ra.getMonthlyAllocations().stream()
                    .map(m -> MonthlyAllocationDTO.builder()
                            .id(m.getId())
                            .yearMonth(m.getYearMonth())
                            .percent(m.getPercent())
                            .build())
                    .collect(Collectors.toList()));
        }
        return dto;
    }

    private ResourceAllocation toEntity(ResourceAllocationDTO dto) {
        ResourceAllocation ra = ResourceAllocation.builder()
                .roleInProject(dto.getRoleInProject())
                .fromDate(dto.getFromDate())
                .toDate(dto.getToDate())
                .allocationPercent(dto.getAllocationPercent())
                .build();
        if (dto.getProductId() != null) {
            productRepository.findById(dto.getProductId()).ifPresent(ra::setProduct);
        }
        if (dto.getEmployeeId() != null) {
            employeeRepository.findById(dto.getEmployeeId()).ifPresent(ra::setEmployee);
        }
        return ra;
    }
}
