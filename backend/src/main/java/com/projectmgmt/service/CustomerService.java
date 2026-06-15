package com.projectmgmt.service;

import com.projectmgmt.dto.CustomerDTO;
import com.projectmgmt.entity.Customer;
import com.projectmgmt.repository.CustomerRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
public class CustomerService {
    private final CustomerRepository customerRepository;

    public List<CustomerDTO> getAll() {
        return customerRepository.findAll().stream().map(this::toDTO).collect(Collectors.toList());
    }

    public CustomerDTO getById(Long id) {
        return customerRepository.findById(id).map(this::toDTO)
                .orElseThrow(() -> new RuntimeException("Customer not found: " + id));
    }

    public CustomerDTO create(CustomerDTO dto) {
        Customer entity = toEntity(dto);
        return toDTO(customerRepository.save(entity));
    }

    public CustomerDTO update(Long id, CustomerDTO dto) {
        Customer existing = customerRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Customer not found: " + id));
        existing.setInvestorCode(dto.getInvestorCode());
        existing.setInvestorName(dto.getInvestorName());
        existing.setBeneficiaryCode(dto.getBeneficiaryCode());
        existing.setBeneficiaryName(dto.getBeneficiaryName());
        existing.setProjectGroupCode(dto.getProjectGroupCode());
        return toDTO(customerRepository.save(existing));
    }

    public void delete(Long id) {
        customerRepository.deleteById(id);
    }

    public CustomerDTO toDTO(Customer c) {
        return CustomerDTO.builder()
                .id(c.getId())
                .investorCode(c.getInvestorCode())
                .investorName(c.getInvestorName())
                .beneficiaryCode(c.getBeneficiaryCode())
                .beneficiaryName(c.getBeneficiaryName())
                .projectGroupCode(c.getProjectGroupCode())
                .build();
    }

    private Customer toEntity(CustomerDTO dto) {
        return Customer.builder()
                .investorCode(dto.getInvestorCode())
                .investorName(dto.getInvestorName())
                .beneficiaryCode(dto.getBeneficiaryCode())
                .beneficiaryName(dto.getBeneficiaryName())
                .projectGroupCode(dto.getProjectGroupCode())
                .build();
    }
}
