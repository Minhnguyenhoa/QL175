package com.projectmgmt.controller;

import com.projectmgmt.dto.ProductDTO;
import com.projectmgmt.service.ProductService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/products")
@RequiredArgsConstructor
public class ProductController {
    private final ProductService productService;

    @GetMapping
    public List<ProductDTO> getAll() { return productService.getAll(); }

    @GetMapping("/{id}")
    public ProductDTO getById(@PathVariable Long id) { return productService.getById(id); }

    @GetMapping("/project-group/{projectGroupId}")
    public List<ProductDTO> getByProjectGroup(@PathVariable Long projectGroupId) {
        return productService.getByProjectGroup(projectGroupId);
    }

    @PostMapping
    public ProductDTO create(@RequestBody ProductDTO dto) { return productService.create(dto); }

    @PutMapping("/{id}")
    public ProductDTO update(@PathVariable Long id, @RequestBody ProductDTO dto) {
        return productService.update(id, dto);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        productService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
