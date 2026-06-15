package com.projectmgmt.service;

import com.projectmgmt.dto.EmployeeDTO;
import com.projectmgmt.entity.Employee;
import com.projectmgmt.repository.EmployeeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
public class EmployeeService {
    private final EmployeeRepository employeeRepository;

    public List<EmployeeDTO> getAll() {
        return employeeRepository.findAll().stream().map(this::toDTO).collect(Collectors.toList());
    }

    public EmployeeDTO getById(Long id) {
        return employeeRepository.findById(id).map(this::toDTO)
                .orElseThrow(() -> new RuntimeException("Employee not found: " + id));
    }

    public EmployeeDTO create(EmployeeDTO dto) {
        return toDTO(employeeRepository.save(toEntity(dto)));
    }

    public EmployeeDTO update(Long id, EmployeeDTO dto) {
        Employee existing = employeeRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Employee not found: " + id));
        existing.setName(dto.getName());
        existing.setAccount(dto.getAccount());
        existing.setCompany(dto.getCompany());
        existing.setDepartment(dto.getDepartment());
        existing.setRole(dto.getRole());
        existing.setLevel(dto.getLevel());
        existing.setContractType(dto.getContractType());
        existing.setWorkMode(dto.getWorkMode());
        existing.setWorkTime(dto.getWorkTime());
        existing.setPaymentType(dto.getPaymentType());
        existing.setWorkStatus(dto.getWorkStatus());
        return toDTO(employeeRepository.save(existing));
    }

    public void delete(Long id) {
        employeeRepository.deleteById(id);
    }

    public EmployeeDTO toDTO(Employee e) {
        return EmployeeDTO.builder()
                .id(e.getId())
                .name(e.getName())
                .account(e.getAccount())
                .company(e.getCompany())
                .department(e.getDepartment())
                .role(e.getRole())
                .level(e.getLevel())
                .contractType(e.getContractType())
                .workMode(e.getWorkMode())
                .workTime(e.getWorkTime())
                .paymentType(e.getPaymentType())
                .workStatus(e.getWorkStatus())
                .build();
    }

    private Employee toEntity(EmployeeDTO dto) {
        return Employee.builder()
                .name(dto.getName())
                .account(dto.getAccount())
                .company(dto.getCompany())
                .department(dto.getDepartment())
                .role(dto.getRole())
                .level(dto.getLevel())
                .contractType(dto.getContractType())
                .workMode(dto.getWorkMode())
                .workTime(dto.getWorkTime())
                .paymentType(dto.getPaymentType())
                .workStatus(dto.getWorkStatus())
                .build();
    }
}
