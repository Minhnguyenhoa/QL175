package com.projectmgmt.controller;

import com.projectmgmt.dto.DepartmentDTO;
import com.projectmgmt.service.DepartmentService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController @RequestMapping("/api/departments") @RequiredArgsConstructor
public class DepartmentController {
    private final DepartmentService service;

    @GetMapping public List<DepartmentDTO> getAll() { return service.getAll(); }
    @GetMapping("/{id}") public DepartmentDTO getById(@PathVariable Long id) { return service.getById(id); }
    @PostMapping public DepartmentDTO create(@RequestBody DepartmentDTO dto) { return service.create(dto); }
    @PutMapping("/{id}") public DepartmentDTO update(@PathVariable Long id, @RequestBody DepartmentDTO dto) { return service.update(id, dto); }
    @DeleteMapping("/{id}") public ResponseEntity<Void> delete(@PathVariable Long id) { service.delete(id); return ResponseEntity.noContent().build(); }
}
