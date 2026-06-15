package com.projectmgmt.service;

import com.projectmgmt.dto.TaskDTO;
import com.projectmgmt.entity.Task;
import com.projectmgmt.repository.ProductRepository;
import com.projectmgmt.repository.TaskRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.stream.Collectors;

@Service @RequiredArgsConstructor @Transactional
public class TaskService {
    private final TaskRepository taskRepo;
    private final ProductRepository productRepo;

    public List<TaskDTO> getAll() {
        return taskRepo.findAllOrdered().stream().map(this::toDTO).collect(Collectors.toList());
    }

    public List<TaskDTO> getByProduct(Long productId) {
        return taskRepo.findByProductIdOrdered(productId).stream().map(this::toDTO).collect(Collectors.toList());
    }

    public TaskDTO getById(Long id) {
        return taskRepo.findById(id).map(this::toDTO)
                .orElseThrow(() -> new RuntimeException("Task not found: " + id));
    }

    public TaskDTO create(TaskDTO dto) {
        return toDTO(taskRepo.save(toEntity(dto)));
    }

    public TaskDTO update(Long id, TaskDTO dto) {
        Task e = taskRepo.findById(id).orElseThrow(() -> new RuntimeException("Task not found: " + id));
        e.setPhaseGroup(dto.getPhaseGroup());
        e.setTaskNo(dto.getTaskNo());
        e.setTaskName(dto.getTaskName());
        e.setContent(dto.getContent());
        e.setFeatureGroup(dto.getFeatureGroup());
        if (dto.getProductId() != null) productRepo.findById(dto.getProductId()).ifPresent(e::setProduct);
        return toDTO(taskRepo.save(e));
    }

    public void delete(Long id) { taskRepo.deleteById(id); }

    public TaskDTO toDTO(Task t) {
        TaskDTO dto = TaskDTO.builder()
                .id(t.getId()).phaseGroup(t.getPhaseGroup()).taskNo(t.getTaskNo())
                .taskName(t.getTaskName()).content(t.getContent()).featureGroup(t.getFeatureGroup()).build();
        if (t.getProduct() != null) {
            dto.setProductId(t.getProduct().getId());
            dto.setProductCode(t.getProduct().getCode());
            dto.setProductName(t.getProduct().getName());
        }
        return dto;
    }

    private Task toEntity(TaskDTO dto) {
        Task t = Task.builder().phaseGroup(dto.getPhaseGroup()).taskNo(dto.getTaskNo())
                .taskName(dto.getTaskName()).content(dto.getContent()).featureGroup(dto.getFeatureGroup()).build();
        if (dto.getProductId() != null) productRepo.findById(dto.getProductId()).ifPresent(t::setProduct);
        return t;
    }
}
