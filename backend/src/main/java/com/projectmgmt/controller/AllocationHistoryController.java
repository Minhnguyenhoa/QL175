package com.projectmgmt.controller;

import com.projectmgmt.dto.AllocationHistoryDTO;
import com.projectmgmt.service.AllocationHistoryService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/allocation-history")
@RequiredArgsConstructor
public class AllocationHistoryController {

    private final AllocationHistoryService service;

    @GetMapping
    public List<AllocationHistoryDTO> getAll() {
        return service.getAll();
    }

    @GetMapping("/{id}")
    public AllocationHistoryDTO getById(@PathVariable Long id) {
        return service.getById(id);
    }

    @PostMapping
    public AllocationHistoryDTO create(@RequestBody AllocationHistoryDTO dto) {
        return service.create(dto);
    }

    @PutMapping("/{id}")
    public AllocationHistoryDTO update(@PathVariable Long id, @RequestBody AllocationHistoryDTO dto) {
        return service.update(id, dto);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}
