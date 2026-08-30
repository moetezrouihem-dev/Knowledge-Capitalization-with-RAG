package com.sfm.ragbackend.dto;

import java.util.List;

public record ConversationDetailDto(
        Long id,
        String title,
        List<MessageDto> messages
) {
}
