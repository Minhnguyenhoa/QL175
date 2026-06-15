package com.projectmgmt.config;

import com.projectmgmt.entity.User;
import com.projectmgmt.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class DataInitializer implements CommandLineRunner {

    private final UserRepository userRepo;
    private final PasswordEncoder passwordEncoder;

    @Override
    public void run(String... args) {
        if (userRepo.count() == 0) {
            userRepo.save(User.builder()
                    .username("admin")
                    .password(passwordEncoder.encode("admin123"))
                    .fullName("Quản trị viên")
                    .enabled(true)
                    .build());
        }
    }
}
