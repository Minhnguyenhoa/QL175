package com.projectmgmt.controller;

import com.projectmgmt.config.JwtUtil;
import com.projectmgmt.entity.User;
import com.projectmgmt.repository.UserRepository;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthenticationManager authManager;
    private final JwtUtil jwtUtil;
    private final UserRepository userRepo;

    @PostMapping("/login")
    public LoginResponse login(@RequestBody LoginRequest req) {
        authManager.authenticate(new UsernamePasswordAuthenticationToken(req.username, req.password));
        User user = userRepo.findByUsername(req.username).orElseThrow();
        String token = jwtUtil.generateToken(user.getUsername());
        return new LoginResponse(token, user.getUsername(), user.getFullName());
    }

    @GetMapping("/me")
    public LoginResponse me(Authentication auth) {
        User user = userRepo.findByUsername(auth.getName()).orElseThrow();
        return new LoginResponse(null, user.getUsername(), user.getFullName());
    }

    @Data static class LoginRequest { String username; String password; }

    @Data static class LoginResponse {
        final String token;
        final String username;
        final String fullName;
    }
}
