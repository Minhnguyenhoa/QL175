package com.projectmgmt.service;

import com.projectmgmt.dto.ResourceSummaryDTO;
import com.projectmgmt.entity.Employee;
import com.projectmgmt.entity.MonthlyAllocation;
import com.projectmgmt.entity.Product;
import com.projectmgmt.entity.ResourceAllocation;
import com.projectmgmt.repository.EmployeeRepository;
import com.projectmgmt.repository.ResourceAllocationRepository;
import com.projectmgmt.util.LazyRefs;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.*;
import java.util.stream.Collectors;

@Service @RequiredArgsConstructor @Transactional(readOnly = true)
public class ResourceSummaryService {

    private static final List<String> MONTH_ORDER = List.of(
        "T6-2025","T7-2025","T8-2025","T9-2025","T10-2025","T11-2025","T12-2025",
        "T1-2026","T2-2026","T3-2026","T4-2026","T5-2026","T6-2026","T7-2026",
        "T8-2026","T9-2026","T10-2026","T11-2026","T12-2026"
    );

    private final EmployeeRepository employeeRepo;
    private final ResourceAllocationRepository allocationRepo;

    public List<ResourceSummaryDTO> getSummary() {
        List<Employee> employees = employeeRepo.findAll();
        List<ResourceAllocation> allAllocations = allocationRepo.findAllWithDetails();

        // group allocations by employee
        Map<Long, List<ResourceAllocation>> byEmployee = allAllocations.stream()
                .filter(ra -> ra.getEmployee() != null)
                .collect(Collectors.groupingBy(ra -> ra.getEmployee().getId()));

        return employees.stream().map(emp -> {
            List<ResourceAllocation> empAllocations = byEmployee.getOrDefault(emp.getId(), List.of());

            // sum monthly % per month
            Map<String, BigDecimal> monthlyTotal = new LinkedHashMap<>();
            for (String month : MONTH_ORDER) {
                BigDecimal total = BigDecimal.ZERO;
                for (ResourceAllocation ra : empAllocations) {
                    if (ra.getMonthlyAllocations() != null) {
                        for (MonthlyAllocation ma : ra.getMonthlyAllocations()) {
                            if (month.equals(ma.getYearMonth()) && ma.getPercent() != null) {
                                total = total.add(ma.getPercent());
                            }
                        }
                    }
                }
                if (total.compareTo(BigDecimal.ZERO) > 0) {
                    monthlyTotal.put(month, total);
                }
            }

            // detect overloaded months (>100%)
            Map<String, Boolean> overloaded = new LinkedHashMap<>();
            monthlyTotal.forEach((m, v) -> overloaded.put(m, v.compareTo(BigDecimal.ONE) > 0));

            // list of projects
            List<String> projects = empAllocations.stream()
                    .map(ra -> LazyRefs.load(ra.getProduct()))
                    .filter(p -> p != null)
                    .map(Product::getCode)
                    .distinct().sorted().collect(Collectors.toList());

            return ResourceSummaryDTO.builder()
                    .employeeId(emp.getId())
                    .employeeName(emp.getName())
                    .employeeCompany(emp.getCompany())
                    .contractType(emp.getContractType())
                    .monthlyTotal(monthlyTotal)
                    .projects(projects)
                    .overloaded(overloaded)
                    .build();
        }).collect(Collectors.toList());
    }

    public ResourceSummaryDTO getByEmployee(Long employeeId) {
        return getSummary().stream()
                .filter(s -> s.getEmployeeId().equals(employeeId))
                .findFirst()
                .orElseThrow(() -> new RuntimeException("Employee not found: " + employeeId));
    }

    public List<String> getMonthOrder() { return MONTH_ORDER; }
}
