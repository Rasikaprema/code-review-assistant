package com.example.codereview;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;

import java.util.*;

@Component
public class LlmClient {

    private final RestTemplate rt = new RestTemplate();
    private final ObjectMapper mapper = new ObjectMapper();

    // ================================================================
    // PUBLIC API: Returns parsed JSON directly
    // ================================================================
    public Map<String, Object> askReview(String code) {

        String prompt =
                "You are a senior Java code reviewer.\n" +
                        "Analyze the code STRICTLY and return ONLY valid JSON with EXACT fields:\n\n" +
                        "{\n" +
                        "  \"bugs\": [],\n" +
                        "  \"security_issues\": [],\n" +
                        "  \"code_smells\": [],\n" +
                        "  \"suggestions\": [],\n" +
                        "  \"improved_code\": \"\"\n" +
                        "}\n\n" +
                        "RULES:\n" +
                        "- Identify real bugs.\n" +
                        "- Identify real security vulnerabilities.\n" +
                        "- Identify code smells.\n" +
                        "- Provide useful suggestions.\n" +
                        "- improved_code MUST contain a full improved version of the input.\n" +
                        "- STRICTLY return only JSON, no explanations.\n\n" +
                        "NOW REVIEW THIS CODE:\n\n" + code;


        try {
            String json = ask(prompt);

            System.out.println("RAW JSON FROM MODEL:\n" + json);

            return mapper.readValue(json, Map.class);

        } catch (Exception ex) {

            ex.printStackTrace();

            Map<String, Object> fallback = new HashMap<>();
            fallback.put("bugs", List.of());
            fallback.put("security_issues", List.of());
            fallback.put("code_smells", List.of());
            fallback.put("suggestions", List.of("LLM ERROR: " + ex.getMessage()));
            fallback.put("improved_code", code);
            return fallback;
        }
    }

    // ================================================================
    // OPENAI → fallback LM Studio
    // ================================================================
    public String ask(String prompt) {

        String openaiKey = System.getenv("OPENAI_API_KEY");
        System.out.println("openaiKey ::"+openaiKey);
        if (openaiKey != null && !openaiKey.isEmpty()) {

            try {
                String url = "https://api.openai.com/v1/chat/completions";

                Map<String, Object> body = new HashMap<>();
                body.put("model", "gpt-4o-mini");
                body.put("messages", List.of(Map.of("role", "user", "content", prompt)));
                body.put("response_format", Map.of("type", "json_object"));
                body.put("max_tokens", 2000);

                HttpHeaders headers = new HttpHeaders();
                headers.setBearerAuth(openaiKey);
                headers.setContentType(MediaType.APPLICATION_JSON);

                HttpEntity<Map<String, Object>> req = new HttpEntity<>(body, headers);

                Map res = rt.postForObject(url, req, Map.class);

                System.out.println("===== RAW LLM RESPONSE =====");
                System.out.println(res);
                System.out.println("============================");

                Map first = (Map) ((List) res.get("choices")).get(0);
                Map msg = (Map) first.get("message");

                return msg.get("content").toString();

            } catch (Exception e) {
                return errorJson("OpenAI Request Failed: " + e.getMessage());
            }
        }

        return errorJson("No LLM available.");
    }

    private String errorJson(String msg) {
        return "{"
                + "\"bugs\": [],"
                + "\"security_issues\": [],"
                + "\"code_smells\": [],"
                + "\"suggestions\": [\"" + msg + "\"],"
                + "\"improved_code\": \"\""
                + "}";
    }
}
