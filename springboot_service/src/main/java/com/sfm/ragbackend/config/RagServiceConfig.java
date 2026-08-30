package com.sfm.ragbackend.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestClient;

@Configuration
public class RagServiceConfig {

    // SimpleClientHttpRequestFactory (HttpURLConnection-based), not
    // RestClient's default — the default resolved to Java's newer
    // java.net.http.HttpClient in testing here, which had a confirmed
    // interop problem sending POST bodies to uvicorn/FastAPI.
    @Bean
    public RestClient ragServiceRestClient(
            @Value("${rag.service.base-url}") String baseUrl
    ) {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        return RestClient.builder()
                .baseUrl(baseUrl)
                .requestFactory(factory)
                .build();
    }
}
