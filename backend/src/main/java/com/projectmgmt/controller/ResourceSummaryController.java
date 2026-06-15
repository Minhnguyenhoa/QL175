package com.projectmgmt.controller;

import com.projectmgmt.dto.ResourceSummaryDTO;
import com.projectmgmt.service.ResourceSummaryService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController @RequestMapping("/api/resource-summary") @RequiredArgsConstructor
public class ResourceSummaryController {
    private final ResourceSummaryService service;

    @GetMapping public List<ResourceSummaryDTO> getSummary() { return service.getSummary(); }
    @GetMapping("/employee/{id}") public ResourceSummaryDTO getByEmployee(@PathVariable Long id) { return service.getByEmployee(id); }
    @GetMapping("/months") public List<String> getMonths() { return service.getMonthOrder(); }
}
