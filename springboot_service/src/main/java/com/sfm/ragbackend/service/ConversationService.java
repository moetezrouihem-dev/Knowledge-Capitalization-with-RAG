package com.sfm.ragbackend.service;

import com.sfm.ragbackend.dto.RagAnswerDto;
import com.sfm.ragbackend.entity.Conversation;
import com.sfm.ragbackend.entity.Message;
import com.sfm.ragbackend.entity.User;
import com.sfm.ragbackend.repository.ConversationRepository;
import com.sfm.ragbackend.repository.MessageRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.util.stream.Collectors;

@Service
public class ConversationService {

    private final ConversationRepository conversationRepository;
    private final MessageRepository messageRepository;

    public ConversationService(ConversationRepository conversationRepository, MessageRepository messageRepository) {
        this.conversationRepository = conversationRepository;
        this.messageRepository = messageRepository;
    }

    public Conversation getOrCreate(Long conversationId, User user, String firstQuestion) {
        if (conversationId != null) {
            return conversationRepository.findByIdAndUser(conversationId, user)
                    .orElseThrow(() -> new ResponseStatusException(
                            HttpStatus.NOT_FOUND, "Conversation not found."));
        }

        Conversation conversation = new Conversation();
        conversation.setUser(user);
        conversation.setTitle(truncateTitle(firstQuestion));
        return conversationRepository.save(conversation);
    }

    public void appendExchange(Conversation conversation, String question, RagAnswerDto answer) {
        Message userMessage = new Message();
        userMessage.setConversation(conversation);
        userMessage.setRole(Message.Role.USER);
        userMessage.setContent(question);
        messageRepository.save(userMessage);

        Message assistantMessage = new Message();
        assistantMessage.setConversation(conversation);
        assistantMessage.setRole(Message.Role.ASSISTANT);
        assistantMessage.setContent(answer.answer());
        assistantMessage.setSources(
                answer.sources().stream()
                        .map(RagAnswerDto.SourceDto::source)
                        .distinct()
                        .collect(Collectors.joining(", "))
        );
        messageRepository.save(assistantMessage);
    }

    private String truncateTitle(String question) {
        String trimmed = question.trim();
        return trimmed.length() > 60 ? trimmed.substring(0, 60) + "…" : trimmed;
    }
}
