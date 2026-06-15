package com.projectmgmt.controller;

import com.projectmgmt.dto.MilestoneDTO;
import com.projectmgmt.service.MilestoneService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/milestones")
@RequiredArgsConstructor
public class MilestoneController {
    private final MilestoneService milestoneService;

    @GetMapping
    public List<MilestoneDTO> getAll() { return milestoneService.getAll(); }

    @GetMapping("/{id}")
    public MilestoneDTO getById(@PathVariable Long id) { return milestoneService.getById(id); }

    @GetMapping("/product/{productId}")
    public List<MilestoneDTO> getByProduct(@PathVariable Long productId) {
        return milestoneService.getByProduct(productId);
    }

    @GetMapping("/overdue-upcoming")
    public List<MilestoneDTO> getOverdueOrUpcoming() {
        return milestoneService.getOverdueOrUpcoming();
    }

    @PostMapping
    public MilestoneDTO create(@RequestBody MilestoneDTO dto) { return milestoneService.create(dto); }

    @PutMapping("/{id}")
    public MilestoneDTO update(@PathVariable Long id, @RequestBody MilestoneDTO dto) {
        return milestoneService.update(id, dto);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        milestoneService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
