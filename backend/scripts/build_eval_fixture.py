"""Build retrieval evaluation fixture from curated CELEX metadata."""
import json
from pathlib import Path

from ingestion.src.data.curated_loader import load_curated_documents

OUTPUT = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "rag_eval_questions.json"
QUESTION_TEMPLATES = (
    "Wat regelt {label}?",
    "Welke verplichtingen gelden onder {label}?",
    "Wat is het doel van {label}?",
)


def build_questions(limit: int = 100) -> list[dict]:
    documents = load_curated_documents()
    rows: list[dict] = []
    for document in documents:
        label = document.short_title or document.title
        for template in QUESTION_TEMPLATES:
            rows.append({
                "question": template.format(label=label),
                "expected_celex": [document.celex],
                "min_hits": 1,
            })
            if len(rows) >= limit:
                return rows
    return rows


def main() -> None:
    payload = build_questions(limit=100)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(payload)} eval questions to {OUTPUT}")


if __name__ == "__main__":
    main()
