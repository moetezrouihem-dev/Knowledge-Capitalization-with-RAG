package com.sfm.ragbackend.controller;

import com.sfm.ragbackend.dto.AskRequestDto;
import com.sfm.ragbackend.dto.AskResponseDto;
import com.sfm.ragbackend.dto.RagAnswerDto;
import com.sfm.ragbackend.entity.Conversation;
import com.sfm.ragbackend.entity.User;
import com.sfm.ragbackend.service.ConversationService;
import com.sfm.ragbackend.service.RagClientService;
import jakarta.validation.Valid;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")
public class AskController {

    private final RagClientService ragClientService;
    private final ConversationService conversationService;

    public AskController(RagClientService ragClientService, ConversationService conversationService) {
        this.ragClientService = ragClientService;
        this.conversationService = conversationService;
    }

    @PostMapping("/ask")
    public AskResponseDto ask(@Valid @RequestBody AskRequestDto request, @AuthenticationPrincipal User user) {
        Conversation conversation = conversationService.getOrCreate(
                request.conversationId(), user, request.question()
        );

        RagAnswerDto ragAnswer = ragClientService.ask(request.question());
        conversationService.appendExchange(conversation, request.question(), ragAnswer);

        return new AskResponseDto(conversation.getId(), ragAnswer.answer(), ragAnswer.sources());
    }
}
