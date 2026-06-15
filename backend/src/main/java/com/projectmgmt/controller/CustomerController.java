package com.projectmgmt.controller;

import com.projectmgmt.dto.CustomerDTO;
import com.projectmgmt.service.CustomerService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/customers")
@RequiredArgsConstructor
public class CustomerController {
    private final CustomerService customerService;

    @GetMapping
    public List<CustomerDTO> getAll() { return customerService.getAll(); }

    @GetMapping("/{id}")
    public CustomerDTO getById(@PathVariable Long id) { return customerService.getById(id); }

    @PostMapping
    public CustomerDTO create(@RequestBody CustomerDTO dto) { return customerService.create(dto); }

    @PutMapping("/{id}")
    public CustomerDTO update(@PathVariable Long id, @RequestBody CustomerDTO dto) {
        return customerService.update(id, dto);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        customerService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
