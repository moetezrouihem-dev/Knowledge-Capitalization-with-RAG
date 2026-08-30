package com.sfm.ragbackend.dto;

import jakarta.validation.constraints.NotBlank;

public record AskRequestDto(
        Long conversationId,  // null = start a new conversation
        @NotBlank String question
) {
}
