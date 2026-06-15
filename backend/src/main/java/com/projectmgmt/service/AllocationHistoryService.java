package com.projectmgmt.service;

import com.projectmgmt.dto.AllocationHistoryDTO;
import com.projectmgmt.entity.AllocationHistory;
import com.projectmgmt.entity.AllocationHistoryMonthly;
import com.projectmgmt.repository.AllocationHistoryMonthlyRepository;
import com.projectmgmt.repository.AllocationHistoryRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.NoSuchElementException;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class AllocationHistoryService {

    private final AllocationHistoryRepository historyRepo;
    private final AllocationHistoryMonthlyRepository monthlyRepo;

    @Transactional(readOnly = true)
    public List<AllocationHistoryDTO> getAll() {
        return historyRepo.findAllWithMonthly().stream().map(this::toDTO).collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public AllocationHistoryDTO getById(Long id) {
        return historyRepo.findById(id).map(this::toDTO)
                .orElseThrow(() -> new NoSuchElementException("AllocationHistory not found: " + id));
    }

    @Transactional
    public AllocationHistoryDTO create(AllocationHistoryDTO dto) {
        AllocationHistory entity = AllocationHistory.builder()
                .projectsText(dto.getProjectsText())
                .employeeName(dto.getEmployeeName())
                .roleInProject(dto.getRoleInProject())
                .fromDate(dto.getFromDate())
                .toDate(dto.getToDate())
                .allocationPercent(dto.getAllocationPercent())
                .build();
        AllocationHistory saved = historyRepo.save(entity);
        if (dto.getMonthlyAllocations() != null) {
            List<AllocationHistoryMonthly> monthlies = dto.getMonthlyAllocations().stream()
                    .map(m -> AllocationHistoryMonthly.builder()
                            .history(saved)
                            .yearMonth(m.getYearMonth())
                            .percent(m.getPercent())
                            .build())
                    .collect(Collectors.toList());
            monthlyRepo.saveAll(monthlies);
            saved.setMonthlyAllocations(monthlies);
        }
        return toDTO(saved);
    }

    @Transactional
    public AllocationHistoryDTO update(Long id, AllocationHistoryDTO dto) {
        AllocationHistory entity = historyRepo.findById(id)
                .orElseThrow(() -> new NoSuchElementException("AllocationHistory not found: " + id));
        entity.setProjectsText(dto.getProjectsText());
        entity.setEmployeeName(dto.getEmployeeName());
        entity.setRoleInProject(dto.getRoleInProject());
        entity.setFromDate(dto.getFromDate());
        entity.setToDate(dto.getToDate());
        entity.setAllocationPercent(dto.getAllocationPercent());
        historyRepo.save(entity);
        if (dto.getMonthlyAllocations() != null) {
            monthlyRepo.deleteByHistoryId(id);
            List<AllocationHistoryMonthly> monthlies = dto.getMonthlyAllocations().stream()
                    .map(m -> AllocationHistoryMonthly.builder()
                            .history(entity)
                            .yearMonth(m.getYearMonth())
                            .percent(m.getPercent())
                            .build())
                    .collect(Collectors.toList());
            monthlyRepo.saveAll(monthlies);
        }
        return getById(id);
    }

    @Transactional
    public void delete(Long id) {
        monthlyRepo.deleteByHistoryId(id);
        historyRepo.deleteById(id);
    }

    private AllocationHistoryDTO toDTO(AllocationHistory e) {
        List<AllocationHistoryDTO.MonthlyAllocationDTO> monthlies = e.getMonthlyAllocations() == null ? List.of()
                : e.getMonthlyAllocations().stream()
                .map(m -> AllocationHistoryDTO.MonthlyAllocationDTO.builder()
                        .id(m.getId()).yearMonth(m.getYearMonth()).percent(m.getPercent()).build())
                .collect(Collectors.toList());
        return AllocationHistoryDTO.builder()
                .id(e.getId())
                .projectsText(e.getProjectsText())
                .employeeName(e.getEmployeeName())
                .roleInProject(e.getRoleInProject())
                .fromDate(e.getFromDate())
                .toDate(e.getToDate())
                .allocationPercent(e.getAllocationPercent())
                .monthlyAllocations(monthlies)
                .build();
    }
}
