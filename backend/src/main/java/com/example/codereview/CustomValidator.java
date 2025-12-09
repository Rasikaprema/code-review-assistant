package com.example.codereview;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;

@Component
public class CustomValidator {

    private final List<String> jsonRules = new ArrayList<>();

    public CustomValidator() {
        loadJsonRules();
    }

    // ---------------------------------------------------
    // Load rules from validation-rules.json
    // ---------------------------------------------------
    private void loadJsonRules() {
        try {
            ObjectMapper mapper = new ObjectMapper();
            JsonNode root = mapper.readTree(
                    new ClassPathResource("validation-rules.json").getInputStream()
            );

            root.get("rules").forEach(rule -> jsonRules.add(rule.asText()));

        } catch (IOException e) {
            throw new RuntimeException("Failed to load validation rules JSON", e);
        }
    }

    // ---------------------------------------------------
    // Java-coded validations (pattern-based)
    // ---------------------------------------------------
    public List<String> javaValidations(String code) {
        List<String> issues = new ArrayList<>();

        // Rule: No println
        if (code.contains("System.out.println")) {
            issues.add("Avoid System.out.println — use a logger instead.");
        }

        // Rule: Empty catch
        Pattern emptyCatchPattern = Pattern.compile("catch\\s*\\([^)]*\\)\\s*\\{\\s*}");
        if (emptyCatchPattern.matcher(code).find()) {
            issues.add("Empty catch block detected — always handle exceptions.");
        }

        // Rule: Hardcoded password
        if (code.toLowerCase().contains("password")) {
            issues.add("Hardcoded password detected — move to config or secret manager.");
        }

        // Rule: Large file
        if (code.split("\n").length > 300) {
            issues.add("File too long (>300 lines) — consider splitting.");
        }

        // Rule: Raw List/Map detection
        Pattern rawListPattern = Pattern.compile("List\\s+[^<]");
        Pattern rawMapPattern = Pattern.compile("Map\\s+[^<]");
        if (rawListPattern.matcher(code).find() || rawMapPattern.matcher(code).find()) {
            issues.add("Raw types detected — use generics (e.g., List<String>).");
        }

        return issues;
    }

    // ---------------------------------------------------
    // NEW LOGIC:
    // Combine JSON rules + Java validations
    // BUT return ONLY violations (not full rule list)
    // ---------------------------------------------------
    public List<String> validate(String code) {
        List<String> violations = new ArrayList<>();

        // Add Java-coded rule violations
        violations.addAll(javaValidations(code));

        // JSON rules — check if the code violates them
        for (String rule : jsonRules) {
            String lower = rule.toLowerCase();

            if (lower.contains("system.out.println") && code.contains("System.out.println")) {
                violations.add(rule);
            }
            if (lower.contains("empty catch") &&
                    Pattern.compile("catch\\s*\\([^)]*\\)\\s*\\{\\s*}")
                            .matcher(code).find()) {
                violations.add(rule);
            }
            if (lower.contains("hardcoded") &&
                    code.toLowerCase().contains("password")) {
                violations.add(rule);
            }
            if (lower.contains("raw type") &&
                    Pattern.compile("List\\s+[^<]").matcher(code).find()) {
                violations.add(rule);
            }
            if (lower.contains("nested if") &&
                    code.contains("if") && code.split("if").length > 4) { // naive check
                violations.add(rule);
            }
        }

        return violations;
    }
}
