package com.sfm.ragbackend.dto;

import jakarta.validation.constraints.NotBlank;

public record LoginRequestDto(
        @NotBlank String email,
        @NotBlank String password
) {
}
