package com.projectmgmt.service;

import com.projectmgmt.dto.DashboardDTO;
import com.projectmgmt.dto.MilestoneDTO;
import com.projectmgmt.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class DashboardService {
    private final ProjectGroupRepository projectGroupRepository;
    private final ProductRepository productRepository;
    private final EmployeeRepository employeeRepository;
    private final MilestoneRepository milestoneRepository;
    private final MilestoneService milestoneService;

    public DashboardDTO getDashboard() {
        Map<String, Long> productsByStatus = new HashMap<>();
        productRepository.countByStatus().forEach(row -> {
            productsByStatus.put((String) row[0], (Long) row[1]);
        });

        Map<String, Long> milestonesByStatus = new HashMap<>();
        milestoneRepository.countByStatus().forEach(row -> {
            milestonesByStatus.put((String) row[0], (Long) row[1]);
        });

        Map<String, Long> employeesByCompany = employeeRepository.findAll().stream()
                .filter(e -> e.getCompany() != null)
                .collect(Collectors.groupingBy(e -> e.getCompany(), Collectors.counting()));

        List<MilestoneDTO> recentOverdue = milestoneRepository.findOverdueOrUpcoming().stream()
                .limit(10).map(milestoneService::toDTO).collect(Collectors.toList());

        long overdue = milestoneRepository.findByRemind("Quá hạn").size();
        long upcoming = milestoneRepository.findByRemind("Sắp đến hạn").size();

        return DashboardDTO.builder()
                .totalProjects(projectGroupRepository.count())
                .totalProducts(productRepository.count())
                .totalEmployees(employeeRepository.count())
                .totalMilestones(milestoneRepository.count())
                .overdueMilestones(overdue)
                .upcomingMilestones(upcoming)
                .productsByStatus(productsByStatus)
                .milestonesByStatus(milestonesByStatus)
                .employeesByCompany(employeesByCompany)
                .recentOverdue(recentOverdue)
                .build();
    }
}
