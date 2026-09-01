package com.sfm.ragbackend.dto;

import jakarta.validation.constraints.NotBlank;

public record AskRequestDto(
        Long conversationId,
        @NotBlank String question
) {
}
