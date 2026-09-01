package com.sfm.ragbackend.controller;

import com.sfm.ragbackend.dto.AuthResponseDto;
import com.sfm.ragbackend.dto.LoginRequestDto;
import com.sfm.ragbackend.dto.MeResponseDto;
import com.sfm.ragbackend.dto.RegisterRequestDto;
import com.sfm.ragbackend.entity.User;
import com.sfm.ragbackend.repository.UserRepository;
import com.sfm.ragbackend.security.JwtService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public AuthController(UserRepository userRepository, PasswordEncoder passwordEncoder, JwtService jwtService) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
    }

    @PostMapping("/register")
    public AuthResponseDto register(@Valid @RequestBody RegisterRequestDto request) {
        String email = request.email().trim().toLowerCase();

        if (userRepository.existsByEmail(email)) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "An account with this email already exists.");
        }

        User user = new User();
        user.setEmail(email);
        user.setPasswordHash(passwordEncoder.encode(request.password()));
        userRepository.save(user);

        String token = jwtService.generateToken(email);
        return new AuthResponseDto(token, email);
    }

    @PostMapping("/login")
    public AuthResponseDto login(@Valid @RequestBody LoginRequestDto request) {
        String email = request.email().trim().toLowerCase();

        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid email or password."));

        if (user.getPasswordHash() == null) {
            throw new ResponseStatusException(
                    HttpStatus.UNAUTHORIZED, "This account uses Google sign-in — use the Google button instead.");
        }

        if (!passwordEncoder.matches(request.password(), user.getPasswordHash())) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid email or password.");
        }

        String token = jwtService.generateToken(email);
        return new AuthResponseDto(token, email);
    }

    @GetMapping("/me")
    public MeResponseDto me(@AuthenticationPrincipal User user) {
        return new MeResponseDto(user.getEmail());
    }
}
