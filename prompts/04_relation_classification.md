You are a biomedical relation classification expert. A confirmed relationship exists between a disease and a chemical/drug. Your task is to classify the type of relationship.

Classify the relationship as one of:
- **therapeutic**: The chemical treats, prevents, or ameliorates the disease. This includes drugs used to manage symptoms, reduce progression, or cure the condition.
- **side_effect**: The chemical causes, induces, or is associated with the disease as an adverse effect. This includes drug-induced conditions, toxicity, or contraindications.

Rules:
- Base your classification strictly on what the abstract states
- If the abstract describes both therapeutic use AND side effects, classify by the primary relationship described
- Provide a brief rationale citing evidence from the abstract

Return a JSON object with this exact format:
```json
{{
  "relation_type": "therapeutic",
  "rationale": "<one sentence citing evidence from the abstract>"
}}
```

`relation_type` must be exactly `"therapeutic"` or `"side_effect"`.
