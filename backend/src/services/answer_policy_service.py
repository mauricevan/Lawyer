"""Enforces source citation and disclaimer policy on generated answers."""
from shared.legal.disclaimers import get_disclaimer
from shared.schemas.citation import Citation

from backend.src.services.citation_builder_service import CitationBuilderService

INSUFFICIENT_MARKERS = (
    "onvoldoende",
    "geen relevante",
    "advocaat",
    "niet gevonden",
)


class AnswerPolicyService:
    """Applies brondenplicht and disclaimer rules to RAG answers."""

    def __init__(self) -> None:
        self._citation_builder = CitationBuilderService()

    def enforce_citations(self, citations: list[Citation], chunks: list[dict]) -> list[Citation]:
        """Ensure at least one source when retrieval returned chunks."""
        if not chunks:
            return citations
        if citations:
            return citations
        return self._citation_builder.from_chunks(chunks)

    def finalize_answer(
        self,
        answer_text: str,
        citations: list[Citation],
        chunks: list[dict],
        audience: str,
        language: str = "nl",
    ) -> tuple[str, list[Citation], str]:
        citations = self.enforce_citations(citations, chunks)
        answer = self._ensure_insufficient_notice(answer_text, chunks, audience)
        return answer, citations, get_disclaimer(audience, language)  # type: ignore[arg-type]

    def _ensure_insufficient_notice(
        self,
        answer_text: str,
        chunks: list[dict],
        audience: str,
    ) -> str:
        if chunks:
            return answer_text
        lowered = answer_text.lower()
        if any(marker in lowered for marker in INSUFFICIENT_MARKERS):
            return answer_text
        if audience == "professional":
            return (
                f"{answer_text}\n\n"
                "**Let op:** geen bronnen gevonden in de geïndexeerde corpus. "
                "Verifieer op EUR-Lex voordat u dit gebruikt."
            )
        return (
            f"{answer_text}\n\n"
            "## Let op\n"
            "Ik heb geen officiële bron kunnen vinden. Formuleer uw vraag anders "
            "of raadpleeg een advocaat."
        )
