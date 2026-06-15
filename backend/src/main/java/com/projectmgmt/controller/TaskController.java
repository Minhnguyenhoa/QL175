package com.projectmgmt.controller;

import com.projectmgmt.dto.TaskDTO;
import com.projectmgmt.service.TaskService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController @RequestMapping("/api/tasks") @RequiredArgsConstructor
public class TaskController {
    private final TaskService service;

    @GetMapping public List<TaskDTO> getAll() { return service.getAll(); }
    @GetMapping("/{id}") public TaskDTO getById(@PathVariable Long id) { return service.getById(id); }
    @GetMapping("/product/{productId}") public List<TaskDTO> getByProduct(@PathVariable Long productId) { return service.getByProduct(productId); }
    @PostMapping public TaskDTO create(@RequestBody TaskDTO dto) { return service.create(dto); }
    @PutMapping("/{id}") public TaskDTO update(@PathVariable Long id, @RequestBody TaskDTO dto) { return service.update(id, dto); }
    @DeleteMapping("/{id}") public ResponseEntity<Void> delete(@PathVariable Long id) { service.delete(id); return ResponseEntity.noContent().build(); }
}
