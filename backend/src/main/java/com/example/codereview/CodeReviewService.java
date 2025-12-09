package com.example.codereview;

import org.springframework.stereotype.Service;

import java.util.*;

@Service
public class CodeReviewService {

    private final LlmClient llm = new LlmClient();
    private final CustomValidator validator = new CustomValidator();

    public Map<String, Object> reviewCode(String code) {

        Map<String, Object> llmData = llm.askReview(code);
        // Normalize LLM lists
        llmData.put("bugs", normalizeList(llmData.get("bugs")));
        llmData.put("security_issues", normalizeList(llmData.get("security_issues")));
        llmData.put("code_smells", normalizeList(llmData.get("code_smells")));
        llmData.put("suggestions", normalizeList(llmData.get("suggestions")));

        // Add custom validations
        List<String> custom = validator.validate(code);
        llmData.put("custom_validations", custom);

        llmData.putIfAbsent("bugs", new ArrayList<>());
        llmData.putIfAbsent("security_issues", new ArrayList<>());
        llmData.putIfAbsent("code_smells", new ArrayList<>());
        llmData.putIfAbsent("suggestions", new ArrayList<>());
        llmData.putIfAbsent("improved_code", code);

        return llmData;
    }


    private List<String> normalizeList(Object value) {
        List<String> result = new ArrayList<>();

        if (value instanceof List<?> list) {
            for (Object item : list) {

                if (item instanceof Map<?, ?> map) {
                    // Convert {"issue": "..."} → text
                    map.values().forEach(v -> {
                        if (v != null) result.add(v.toString());
                    });
                }
                else if (item != null) {
                    result.add(item.toString());
                }
            }
        }

        return result;
    }

}
