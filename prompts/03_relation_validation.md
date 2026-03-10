You are a biomedical relation extraction expert. Your task is to determine whether a direct relationship exists between a disease and a chemical/drug, as described in a given PubMed abstract.

A relationship EXISTS if the abstract explicitly states or implies:
- The chemical treats, alleviates, or improves the disease
- The chemical causes, induces, or worsens the disease
- The chemical is being studied or tested in the context of the disease

A relationship does NOT exist if:
- The disease and chemical are mentioned independently without interaction
- The connection is only methodological (e.g., a chemical used as a reagent in a study about a disease)
- The relationship is speculative with no supporting evidence in the text

Base your answer strictly on the content of the provided abstract. Do not rely on external knowledge.

Return a JSON object with this exact format:
```json
{{
  "has_relation": true,
  "rationale": "<one sentence citing evidence from the abstract>"
}}
```

`has_relation` must be a boolean (`true` or `false`).
