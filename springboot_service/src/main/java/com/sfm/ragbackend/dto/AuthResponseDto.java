package com.sfm.ragbackend.dto;

public record AuthResponseDto(
        String token,
        String email
) {
}
