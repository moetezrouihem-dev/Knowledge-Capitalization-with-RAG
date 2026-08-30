package com.sfm.ragbackend.dto;

import java.time.LocalDateTime;

public record ConversationSummaryDto(
        Long id,
        String title,
        LocalDateTime createdAt
) {
}
