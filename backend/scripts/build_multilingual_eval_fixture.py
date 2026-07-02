"""Build multilingual retrieval evaluation fixture (plan5 I2)."""
import json
from pathlib import Path

from ingestion.src.data.curated_loader import load_curated_documents

OUTPUT = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "rag_eval_multilingual.json"

TEMPLATES: dict[str, tuple[str, ...]] = {
    "fr": (
        "Que prévoit {label}?",
        "Quelles obligations impose {label}?",
    ),
    "de": (
        "Was regelt {label}?",
        "Welche Pflichten gelten nach {label}?",
    ),
    "es": (
        "¿Qué regula {label}?",
        "¿Qué obligaciones impone {label}?",
    ),
}

PRIORITY_CELEX = (
    "32016R0679",
    "32024R1689",
    "32022R2554",
    "32022R2065",
    "32014R0910",
)


def build_questions(per_language: int = 5) -> list[dict]:
    documents = load_curated_documents()
    by_celex = {doc.celex: doc for doc in documents}
    selected = [by_celex[celex] for celex in PRIORITY_CELEX if celex in by_celex]
    rows: list[dict] = []
    for language, templates in TEMPLATES.items():
        count = 0
        for document in selected:
            label = document.short_title or document.title
            for template in templates:
                rows.append({
                    "question": template.format(label=label),
                    "expected_celex": [document.celex],
                    "min_hits": 1,
                    "language": language,
                })
                count += 1
                if count >= per_language:
                    break
            if count >= per_language:
                break
    return rows


def main() -> None:
    payload = build_questions()
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(payload)} multilingual eval questions to {OUTPUT}")


if __name__ == "__main__":
    main()
