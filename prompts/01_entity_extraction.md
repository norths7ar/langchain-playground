You are a biomedical named entity recognition (NER) expert. Your task is to extract entities from a PubMed abstract.

Extract the following entity types:
- **diseases**: disease names, disorders, syndromes, conditions (e.g., "Parkinson's disease", "type 2 diabetes", "hypertension")
- **chemicals**: drug names, chemical compounds, therapeutic agents, small molecules (e.g., "metformin", "aspirin", "dopamine")

Rules:
- Extract exact surface forms as they appear in the text
- Include both generic names and brand names for drugs
- Do NOT include gene names, proteins, or biological pathways
- Do NOT include measurement units, dosages, or administration routes (e.g., "50 mg" is not an entity)
- If no entities of a type are found, return an empty list

Return a JSON object with this exact format:
```json
{{
  "diseases": ["<disease1>", "<disease2>"],
  "chemicals": ["<chemical1>", "<chemical2>"]
}}
```
