package com.sfm.ragbackend.dto;

import java.util.List;

// The raw shape FastAPI returns. Kept separate from AskResponseDto
// (below), which is what THIS backend returns to Angular — the two
// happen to look similar right now but are allowed to diverge later
// (e.g. once conversationId gets added to what Angular receives).
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
