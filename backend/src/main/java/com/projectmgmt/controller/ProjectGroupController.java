package com.projectmgmt.controller;

import com.projectmgmt.dto.ProjectGroupDTO;
import com.projectmgmt.service.ProjectGroupService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/project-groups")
@RequiredArgsConstructor
public class ProjectGroupController {
    private final ProjectGroupService projectGroupService;

    @GetMapping
    public List<ProjectGroupDTO> getAll() { return projectGroupService.getAll(); }

    @GetMapping("/{id}")
    public ProjectGroupDTO getById(@PathVariable Long id) { return projectGroupService.getById(id); }

    @PostMapping
    public ProjectGroupDTO create(@RequestBody ProjectGroupDTO dto) { return projectGroupService.create(dto); }

    @PutMapping("/{id}")
    public ProjectGroupDTO update(@PathVariable Long id, @RequestBody ProjectGroupDTO dto) {
        return projectGroupService.update(id, dto);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        projectGroupService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
