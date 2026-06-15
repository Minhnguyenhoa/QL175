package com.projectmgmt.controller;

import com.projectmgmt.dto.PhaseDTO;
import com.projectmgmt.service.PhaseService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController @RequestMapping("/api/phases") @RequiredArgsConstructor
public class PhaseController {
    private final PhaseService service;

    @GetMapping public List<PhaseDTO> getAll() { return service.getAll(); }
    @GetMapping("/{id}") public PhaseDTO getById(@PathVariable Long id) { return service.getById(id); }
    @PostMapping public PhaseDTO create(@RequestBody PhaseDTO dto) { return service.create(dto); }
    @PutMapping("/{id}") public PhaseDTO update(@PathVariable Long id, @RequestBody PhaseDTO dto) { return service.update(id, dto); }
    @DeleteMapping("/{id}") public ResponseEntity<Void> delete(@PathVariable Long id) { service.delete(id); return ResponseEntity.noContent().build(); }
}
