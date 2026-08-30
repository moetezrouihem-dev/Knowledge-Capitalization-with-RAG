package com.sfm.ragbackend.security;

import com.sfm.ragbackend.entity.User;
import com.sfm.ragbackend.repository.UserRepository;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.lang.NonNull;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;
import java.util.Optional;

/**
 * Runs once per incoming request. Looks for "Authorization: Bearer
 * <token>", and if it's a valid token, tells Spring Security "this
 * request is authenticated as this user" for the rest of the request.
 *
 * If there's no token, or it's invalid/expired, this filter just does
 * nothing and lets the request continue unauthenticated — it's
 * SecurityConfig's job (not this filter's) to decide which endpoints
 * actually require authentication.
 */
@Component
public class JwtAuthFilter extends OncePerRequestFilter {

    private final JwtService jwtService;
    private final UserRepository userRepository;

    public JwtAuthFilter(JwtService jwtService, UserRepository userRepository) {
        this.jwtService = jwtService;
        this.userRepository = userRepository;
    }

    @Override
    protected void doFilterInternal(
            @NonNull HttpServletRequest request,
            @NonNull HttpServletResponse response,
            @NonNull FilterChain filterChain
    ) throws ServletException, IOException {
        String header = request.getHeader("Authorization");

        if (header != null && header.startsWith("Bearer ")) {
            String token = header.substring(7);
            try {
                String email = jwtService.extractEmail(token);
                Optional<User> userOpt = userRepository.findByEmail(email);

                if (userOpt.isPresent() && SecurityContextHolder.getContext().getAuthentication() == null) {
                    User user = userOpt.get();
                    // principal = the User entity itself, so controllers can
                    // pull it straight out of Authentication without another
                    // DB lookup (see ConversationController/AskController).
                    var authToken = new UsernamePasswordAuthenticationToken(
                            user, null, List.of()
                    );
                    SecurityContextHolder.getContext().setAuthentication(authToken);
                }
            } catch (Exception e) {
                // Invalid/expired token: treat as unauthenticated rather
                // than crashing the request — SecurityConfig will reject
                // it below if the endpoint actually requires auth.
                SecurityContextHolder.clearContext();
            }
        }

        filterChain.doFilter(request, response);
    }
}
