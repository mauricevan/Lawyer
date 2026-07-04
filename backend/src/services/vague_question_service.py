"""Detect vague layperson questions that need clarification first."""
import re

_VAGUE_PATTERNS = (
    re.compile(r"^mag ik dit\??$", re.IGNORECASE),
    re.compile(r"^mag dat\??$", re.IGNORECASE),
    re.compile(r"^ai\??$", re.IGNORECASE),
    re.compile(r"^help\??$", re.IGNORECASE),
    re.compile(r"^wat nu\??$", re.IGNORECASE),
)
_STOPWORDS = frozenset(
    "mag ik dit dat wat hoe de een en of is zijn voor bij".split(),
)


class VagueQuestionService:
    """Flags questions too vague for retrieval or coverage-gap answers."""

    def is_vague(self, question: str) -> bool:
        cleaned = question.strip()
        if len(cleaned) < 8:
            return True
        lowered = cleaned.lower()
        if any(pattern.match(lowered) for pattern in _VAGUE_PATTERNS):
            return True
        tokens = [t for t in re.findall(r"[a-zà-ÿ]+", lowered) if t not in _STOPWORDS]
        return len(tokens) < 2

    def build_questions(self, audience: str = "layperson") -> list[str]:
        if audience == "professional":
            return [
                "Welke verordening of richtlijn is leidend (CELEX indien bekend)?",
                "Wat is de concrete feitelijke situatie of use case?",
            ]
        return [
            "Waar gaat uw vraag precies over (bijv. privacy, AI, arbeid)?",
            "Geldt dit voor u persoonlijk, uw bedrijf, of een algemene situatie?",
            "Welke EU-wet of regeling heeft u in gedachten, als u die weet?",
        ]

    def build_answer(self, audience: str = "layperson") -> str:
        if audience == "professional":
            return (
                "Uw vraag is te kort om een onderbouwd juridisch antwoord te geven. "
                "Beantwoord de controlevragen hieronder zodat ik gericht kan zoeken."
            )
        return (
            "## Kort antwoord\n"
            "Kunt u uw vraag iets concreter maken? Dan kan ik gerichter zoeken in EUR-Lex.\n\n"
            "## Let op\n"
            "Zonder meer context geef ik geen antwoord op gok — dat zou misleidend zijn."
        )
