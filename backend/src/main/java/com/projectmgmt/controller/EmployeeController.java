package com.projectmgmt.controller;

import com.projectmgmt.dto.EmployeeDTO;
import com.projectmgmt.service.EmployeeService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/employees")
@RequiredArgsConstructor
public class EmployeeController {
    private final EmployeeService employeeService;

    @GetMapping
    public List<EmployeeDTO> getAll() { return employeeService.getAll(); }

    @GetMapping("/{id}")
    public EmployeeDTO getById(@PathVariable Long id) { return employeeService.getById(id); }

    @PostMapping
    public EmployeeDTO create(@RequestBody EmployeeDTO dto) { return employeeService.create(dto); }

    @PutMapping("/{id}")
    public EmployeeDTO update(@PathVariable Long id, @RequestBody EmployeeDTO dto) {
        return employeeService.update(id, dto);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        employeeService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
