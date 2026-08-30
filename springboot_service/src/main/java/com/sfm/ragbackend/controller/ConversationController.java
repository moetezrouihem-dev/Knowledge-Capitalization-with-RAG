package com.sfm.ragbackend.controller;

import com.sfm.ragbackend.dto.ConversationDetailDto;
import com.sfm.ragbackend.dto.ConversationSummaryDto;
import com.sfm.ragbackend.dto.MessageDto;
import com.sfm.ragbackend.entity.Conversation;
import com.sfm.ragbackend.entity.User;
import com.sfm.ragbackend.repository.ConversationRepository;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;

@RestController
@RequestMapping("/api/conversations")
public class ConversationController {

    private final ConversationRepository conversationRepository;

    public ConversationController(ConversationRepository conversationRepository) {
        this.conversationRepository = conversationRepository;
    }

    @GetMapping
    public List<ConversationSummaryDto> list(@AuthenticationPrincipal User user) {
        return conversationRepository.findByUserOrderByCreatedAtDesc(user).stream()
                .map(c -> new ConversationSummaryDto(c.getId(), c.getTitle(), c.getCreatedAt()))
                .toList();
    }

    @GetMapping("/{id}")
    public ConversationDetailDto get(@PathVariable Long id, @AuthenticationPrincipal User user) {
        Conversation conversation = conversationRepository.findByIdAndUser(id, user)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Conversation not found."));

        List<MessageDto> messages = conversation.getMessages().stream()
                .map(m -> new MessageDto(m.getRole().name(), m.getContent(), m.getSources(), m.getCreatedAt()))
                .toList();

        return new ConversationDetailDto(conversation.getId(), conversation.getTitle(), messages);
    }
}
