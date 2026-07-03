"""Build long-tail retrieval eval fixture (plan12 AD)."""
import json
from pathlib import Path

OUTPUT = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "rag_eval_longtail.json"

LONGTAIL_CASES: list[dict] = [
    {
        "question": "Welke EU-regels gelden voor digitale operationele weerbaarheid bij banken?",
        "expected_celex": ["32022R2554"],
        "category": "paraphrase",
    },
    {
        "question": "Mag ik klantdata delen onder de privacyverordening van de EU?",
        "expected_celex": ["32016R0679"],
        "category": "informal",
    },
    {
        "question": "Welke eisen gelden voor AI-systemen met een hoog risico?",
        "expected_celex": ["32024R1689"],
        "category": "paraphrase",
    },
    {
        "question": "Welke rapportageplichten gelden voor duurzaamheid in jaarverslagen?",
        "expected_celex": ["32022L2464"],
        "category": "vague",
    },
    {
        "question": "Hoe lang mag een werknemer achter elkaar werken volgens EU-recht?",
        "expected_celex": ["32003L0088"],
        "category": "vague",
    },
    {
        "question": "Wat zijn de rechten van uitzendkrachten in de Europese Unie?",
        "expected_celex": ["32008L0104"],
        "category": "paraphrase",
    },
    {
        "question": "Moet een werkgever transparante en voorspelbare arbeidsvoorwaarden verstrekken?",
        "expected_celex": ["32019L1152"],
        "category": "paraphrase",
    },
    {
        "question": "Leg 32016R0679 uit in het kort voor een compliance-team.",
        "expected_celex": ["32016R0679"],
        "category": "celex_explicit",
    },
    {
        "question": "Welke verplichtingen stelt de EU aan ICT-weerbaarheid bij banken?",
        "expected_celex": ["32022R2554"],
        "category": "cross_language",
        "language": "nl",
    },
    {
        "question": "Welke cybersecurity-verplichtingen gelden voor essentiële entiteiten onder NIS2?",
        "expected_celex": ["32022L2555"],
        "category": "acronym",
    },
    {
        "question": "Hoe werkt samenwerking tussen nationale consumentenautoriteiten in de EU?",
        "expected_celex": ["32017R2394"],
        "category": "vague",
    },
    {
        "question": "Welke ICT-risico-eisen gelden voor financiële instellingen onder DORA?",
        "expected_celex": ["32022R2554"],
        "category": "compound",
    },
    {
        "question": "Welke verordening behandelt foundation models en GPAI?",
        "expected_celex": ["32024R1689"],
        "category": "technical",
    },
    {
        "question": "Wat is gecorrigeerd in AI Act Corrigendum?",
        "expected_celex": ["32024R1689R(01)"],
        "category": "corrigendum",
    },
    {
        "question": "Regels over generatieve AI en chatbots in de Europese Unie",
        "expected_celex": ["32024R1689"],
        "category": "vague",
    },
    {
        "question": "Wanneer is verwerking van persoonsgegevens rechtmatig zonder toestemming?",
        "expected_celex": ["32016R0679"],
        "category": "legal_concept",
    },
    {
        "question": "Was sind die wichtigsten Pflichten unter DORA für Banken?",
        "expected_celex": ["32022R2554"],
        "category": "cross_language",
        "language": "de",
    },
    {
        "question": "Wat gold historisch voor werktijden voordat de huidige EU-richtlijn gold?",
        "expected_celex": ["32003L0088"],
        "category": "historical",
        "time_context": "historical",
    },
    {
        "question": "Hoe moet een onderneming omgaan met persoonsgegevens van sollicitanten?",
        "expected_celex": ["32016R0679"],
        "category": "scenario",
    },
    {
        "question": "Welke EU-wetgeving regelt netwerk- en informatiebeveiliging voor vitale sectoren?",
        "expected_celex": ["32022L2555"],
        "category": "paraphrase",
    },
]


def build_cases() -> list[dict]:
    rows: list[dict] = []
    for case in LONGTAIL_CASES:
        row = {
            "question": case["question"],
            "expected_celex": case["expected_celex"],
            "min_hits": 1,
            "category": case["category"],
        }
        if case.get("language"):
            row["language"] = case["language"]
        if case.get("time_context"):
            row["time_context"] = case["time_context"]
        rows.append(row)
    return rows


def main() -> None:
    payload = build_cases()
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(payload)} long-tail eval questions to {OUTPUT}")


if __name__ == "__main__":
    main()
