"""
IPulse Pipeline — LangChain replication
4-step biomedical entity & relation extraction from PubMed abstracts.

Steps:
  1. Entity Extraction  — identify diseases and chemicals
  2. Entity Validation  — filter out non-medical noise
  3. Relation Validation — check if a disease-chemical pair has a direct relation
  4. Relation Classification — therapeutic vs. side_effect
"""

import json
import os
from itertools import product
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

load_dotenv()

# ── Paths ────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent
PROMPTS_DIR = ROOT / "prompts"
INPUT_FILE = ROOT / "data" / "ipulse" / "input" / "abstracts.jsonl"
OUTPUT_FILE = ROOT / "data" / "ipulse" / "output" / "results.jsonl"

# ── LLM ──────────────────────────────────────────────────────────────────────

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY", ""),
    base_url="https://api.deepseek.com",
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_prompt(filename: str) -> str:
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8").strip()


def make_chain(prompt_file: str, output_model):
    system_prompt = load_prompt(prompt_file)
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    return prompt | llm.with_structured_output(output_model, method="json_mode")

# ── Pydantic output models ────────────────────────────────────────────────────

class EntityExtractionResult(BaseModel):
    diseases: list[str]
    chemicals: list[str]


class EntityValidationResult(BaseModel):
    valid_diseases: list[str]
    valid_chemicals: list[str]


class RelationValidationResult(BaseModel):
    has_relation: bool
    rationale: str


class RelationClassificationResult(BaseModel):
    relation_type: Literal["therapeutic", "side_effect"]
    rationale: str

# ── Chains ────────────────────────────────────────────────────────────────────

extraction_chain = make_chain("01_entity_extraction.md", EntityExtractionResult)
validation_chain = make_chain("02_entity_validation.md", EntityValidationResult)
rel_validation_chain = make_chain("03_relation_validation.md", RelationValidationResult)
rel_classification_chain = make_chain("04_relation_classification.md", RelationClassificationResult)

# ── Pipeline ──────────────────────────────────────────────────────────────────

def run_pipeline(pmid: str, abstract: str) -> dict:
    print(f"\n{'='*60}")
    print(f"PMID: {pmid}")
    print(f"Abstract: {abstract[:120]}...")

    # Step 1: Entity Extraction
    extraction: EntityExtractionResult = extraction_chain.invoke({"input": abstract})
    print(f"\n[Step 1] Extracted — diseases: {extraction.diseases} | chemicals: {extraction.chemicals}")

    # Step 2: Entity Validation
    validation_input = (
        f"Abstract:\n{abstract}\n\n"
        f"Candidate diseases: {extraction.diseases}\n"
        f"Candidate chemicals: {extraction.chemicals}"
    )
    validation: EntityValidationResult = validation_chain.invoke({"input": validation_input})
    print(f"[Step 2] Validated — diseases: {validation.valid_diseases} | chemicals: {validation.valid_chemicals}")

    # Steps 3 & 4: Relation Validation + Classification for each pair
    relations = []
    pairs = list(product(validation.valid_diseases, validation.valid_chemicals))

    for disease, chemical in pairs:
        rel_input = (
            f"Abstract:\n{abstract}\n\n"
            f"Disease: {disease}\n"
            f"Chemical: {chemical}"
        )

        # Step 3: Validate relation
        rel_val: RelationValidationResult = rel_validation_chain.invoke({"input": rel_input})
        print(f"[Step 3] ({disease}, {chemical}) → has_relation={rel_val.has_relation}")

        if not rel_val.has_relation:
            continue

        # Step 4: Classify relation
        rel_cls: RelationClassificationResult = rel_classification_chain.invoke({"input": rel_input})
        print(f"[Step 4] ({disease}, {chemical}) → {rel_cls.relation_type}")

        relations.append({
            "disease": disease,
            "chemical": chemical,
            "relation_type": rel_cls.relation_type,
            "rationale": rel_cls.rationale,
        })

    return {
        "pmid": pmid,
        "abstract": abstract,
        "entities": {
            "diseases": validation.valid_diseases,
            "chemicals": validation.valid_chemicals,
        },
        "relations": relations,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(INPUT_FILE, encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]

    print(f"Processing {len(records)} abstract(s)...")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for record in records:
            result = run_pipeline(record["pmid"], record["abstract"])
            out.write(json.dumps(result, ensure_ascii=False) + "\n")

    print(f"\nDone. Results written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
