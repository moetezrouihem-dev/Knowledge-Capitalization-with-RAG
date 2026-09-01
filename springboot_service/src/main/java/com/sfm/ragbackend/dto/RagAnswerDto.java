package com.sfm.ragbackend.dto;

import java.util.List;

public record RagAnswerDto(
        String answer,
        List<SourceDto> sources
) {
    public record SourceDto(
            String source,
            String page
    ) {
    }
}
