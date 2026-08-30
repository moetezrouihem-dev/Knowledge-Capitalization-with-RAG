package com.sfm.ragbackend.dto;

import java.time.LocalDateTime;

public record MessageDto(
        String role,
        String content,
        String sources,
        LocalDateTime createdAt
) {
}
