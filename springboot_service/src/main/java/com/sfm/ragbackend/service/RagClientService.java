package com.sfm.ragbackend.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.sfm.ragbackend.dto.RagAnswerDto;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

@Service
public class RagClientService {

    private final RestClient restClient;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public RagClientService(RestClient ragServiceRestClient) {
        this.restClient = ragServiceRestClient;
    }

    private record FastApiAskRequest(String question) {
    }

    public RagAnswerDto ask(String question) {
        String requestBody;
        try {
            requestBody = objectMapper.writeValueAsString(new FastApiAskRequest(question));
        } catch (Exception e) {
            throw new RuntimeException("Failed to build request JSON", e);
        }

        return restClient.post()
                .uri("/ask")
                .contentType(MediaType.APPLICATION_JSON)
                .body(requestBody)
                .retrieve()
                .body(RagAnswerDto.class);
    }
}
