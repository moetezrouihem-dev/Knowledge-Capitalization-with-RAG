package com.sfm.ragbackend.dto;

import java.util.List;

public record AskResponseDto(
        Long conversationId,
        String answer,
        List<RagAnswerDto.SourceDto> sources
) {
}
