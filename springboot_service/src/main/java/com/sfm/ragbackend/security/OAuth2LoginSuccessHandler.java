package com.sfm.ragbackend.security;

import com.sfm.ragbackend.entity.User;
import com.sfm.ragbackend.repository.UserRepository;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;
import org.springframework.stereotype.Component;

import java.io.IOException;

/**
 * Runs once Google confirms the person's identity. Finds or creates a
 * matching User row (same table email/password login uses), issues
 * OUR OWN JWT (not Google's token — our backend never sees or stores
 * Google's token beyond this one moment), then redirects the browser
 * back to Angular with that JWT attached, so Angular can pick it up
 * exactly the same way it would after a normal email/password login.
 */
@Component
public class OAuth2LoginSuccessHandler implements AuthenticationSuccessHandler {

    private final UserRepository userRepository;
    private final JwtService jwtService;
    private final String frontendUrl;

    public OAuth2LoginSuccessHandler(
            UserRepository userRepository,
            JwtService jwtService,
            @Value("${app.frontend-url}") String frontendUrl
    ) {
        this.userRepository = userRepository;
        this.jwtService = jwtService;
        this.frontendUrl = frontendUrl;
    }

    @Override
    public void onAuthenticationSuccess(
            HttpServletRequest request, HttpServletResponse response, Authentication authentication
    ) throws IOException, ServletException {
        OAuth2User oauthUser = (OAuth2User) authentication.getPrincipal();
        String email = oauthUser.getAttribute("email");

        User user = userRepository.findByEmail(email).orElseGet(() -> {
            User newUser = new User();
            newUser.setEmail(email);
            newUser.setPasswordHash(null); // Google-only account, no local password
            return userRepository.save(newUser);
        });

        String token = jwtService.generateToken(user.getEmail());
        response.sendRedirect(frontendUrl + "/oauth-callback?token=" + token);
    }
}
