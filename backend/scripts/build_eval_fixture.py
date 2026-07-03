"""Build retrieval evaluation fixture from curated CELEX metadata."""
import json
from pathlib import Path

from ingestion.src.data.curated_loader import load_curated_documents
from ingestion.src.data.domain_registry_loader import load_domain_registry, resolve_domain_for_celex

OUTPUT = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "rag_eval_questions.json"
QUESTION_TEMPLATES = (
    "Wat regelt {label}?",
    "Welke verplichtingen gelden onder {label}?",
    "Wat is het doel van {label}?",
)


def _seed_celex_set() -> set[str]:
    seeds: set[str] = set()
    for config in load_domain_registry().values():
        if config.status in ("go", "pilot"):
            seeds.update(config.seed_celex)
    return seeds


def _append_questions(rows: list[dict], document) -> None:
    label = document.short_title or document.title
    for template in QUESTION_TEMPLATES:
        rows.append({
            "question": template.format(label=label),
            "expected_celex": [document.celex],
            "min_hits": 1,
            "domain": resolve_domain_for_celex(document.celex),
        })


def build_questions(limit: int = 100) -> list[dict]:
    documents = load_curated_documents()
    by_celex = {document.celex: document for document in documents}
    seed_celex = _seed_celex_set()
    priority = [by_celex[celex] for celex in sorted(seed_celex) if celex in by_celex]
    remainder = [document for document in documents if document.celex not in seed_celex]

    rows: list[dict] = []
    for document in priority:
        _append_questions(rows, document)
    for document in remainder:
        _append_questions(rows, document)
        if len(rows) >= limit:
            break
    return rows


def main() -> None:
    payload = build_questions(limit=100)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(payload)} eval questions to {OUTPUT}")


if __name__ == "__main__":
    main()
