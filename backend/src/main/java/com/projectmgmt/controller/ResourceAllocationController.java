package com.projectmgmt.controller;

import com.projectmgmt.dto.ResourceAllocationDTO;
import com.projectmgmt.service.ResourceAllocationService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/allocations")
@RequiredArgsConstructor
public class ResourceAllocationController {
    private final ResourceAllocationService allocationService;

    @GetMapping
    public List<ResourceAllocationDTO> getAll() { return allocationService.getAll(); }

    @GetMapping("/{id}")
    public ResourceAllocationDTO getById(@PathVariable Long id) { return allocationService.getById(id); }

    @GetMapping("/product/{productId}")
    public List<ResourceAllocationDTO> getByProduct(@PathVariable Long productId) {
        return allocationService.getByProduct(productId);
    }

    @GetMapping("/employee/{employeeId}")
    public List<ResourceAllocationDTO> getByEmployee(@PathVariable Long employeeId) {
        return allocationService.getByEmployee(employeeId);
    }

    @PostMapping
    public ResourceAllocationDTO create(@RequestBody ResourceAllocationDTO dto) {
        return allocationService.create(dto);
    }

    @PutMapping("/{id}")
    public ResourceAllocationDTO update(@PathVariable Long id, @RequestBody ResourceAllocationDTO dto) {
        return allocationService.update(id, dto);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        allocationService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
