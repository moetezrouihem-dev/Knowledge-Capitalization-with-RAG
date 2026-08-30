package com.sfm.ragbackend.security;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Date;

/**
 * Issues a JWT on login/register, and validates one on every
 * subsequent request (see JwtAuthFilter). The token itself just
 * carries the user's email as its "subject" — Spring looks the real
 * User row up from that on each request, the token isn't a database
 * replacement.
 */
@Service
public class JwtService {

    private final SecretKey key;
    private final long expirationMillis;

    public JwtService(
            @Value("${app.jwt.secret}") String secret,
            @Value("${app.jwt.expiration-hours:24}") long expirationHours
    ) {
        // The secret in application.properties must be at least 32
        // characters (256 bits) for HS256 — jjwt throws at startup
        // otherwise, which is a deliberate safety check, not a bug.
        this.key = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
        this.expirationMillis = expirationHours * 60 * 60 * 1000;
    }

    public String generateToken(String email) {
        Instant now = Instant.now();
        return Jwts.builder()
                .subject(email)
                .issuedAt(Date.from(now))
                .expiration(Date.from(now.plusMillis(expirationMillis)))
                .signWith(key)
                .compact();
    }

    /** Returns the email (subject) if the token is valid, throws otherwise. */
    public String extractEmail(String token) {
        return Jwts.parser()
                .verifyWith(key)
                .build()
                .parseSignedClaims(token)
                .getPayload()
                .getSubject();
    }
}
