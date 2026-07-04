"""Verify LLM answers against fetched legal source chunks."""
import logging
import re

from backend.src.utils.llm_json_client import call_llm_json
from shared.config.prompt_loader import get_citation_verifier_system_prompt
from shared.schemas.legal_interpretation import LegalInterpretationPlan

logger = logging.getLogger(__name__)
_ARTICLE_REF = re.compile(r"\bart(?:ikel|\.?)\s*(\d+[a-z]?)\b", re.IGNORECASE)
_CELEX_REF = re.compile(r"\b(\d{5}[A-Z]\d{4})\b")


class CitationVerifierService:
    """Deterministic and LLM citation checks for agent answers."""

    async def verify(
        self,
        answer_text: str,
        chunks: list[dict],
        plan: LegalInterpretationPlan | None = None,
    ) -> tuple[bool, str, list[str]]:
        unsupported = self._deterministic_issues(answer_text, chunks, plan)
        if unsupported:
            return False, answer_text, unsupported
        try:
            llm_result = await self._llm_verify(answer_text, chunks)
            if llm_result.get("supported", True):
                return True, answer_text, []
            claims = llm_result.get("unsupported_claims", [])
            rewritten = self._rewrite_without_claims(answer_text, claims)
            return bool(rewritten.strip()), rewritten, claims
        except Exception as exc:
            logger.warning("LLM citation verify failed: %s", exc)
            return True, answer_text, []

    def _deterministic_issues(
        self,
        answer_text: str,
        chunks: list[dict],
        plan: LegalInterpretationPlan | None,
    ) -> list[str]:
        issues: list[str] = []
        chunk_articles = {
            str(c.get("article_number", "")).lstrip("0") or "0"
            for c in chunks if c.get("article_number")
        }
        for match in _ARTICLE_REF.finditer(answer_text):
            article = match.group(1).lstrip("0") or "0"
            if chunk_articles and article not in chunk_articles:
                issues.append(f"Artikel {match.group(1)} niet in opgehaalde bronnen")
        allowed_celex = {c.get("celex") for c in chunks if c.get("celex")}
        if plan:
            allowed_celex.update(i.celex for i in plan.instruments if i.celex)
        for match in _CELEX_REF.finditer(answer_text.upper()):
            celex = match.group(1)
            if allowed_celex and celex not in allowed_celex:
                issues.append(f"CELEX {celex} niet in fetch-plan")
        return issues

    async def _llm_verify(self, answer_text: str, chunks: list[dict]) -> dict:
        sources = "\n\n---\n\n".join(
            f"[{c.get('celex')} art. {c.get('article_number', '?')}]\n{c.get('text', '')[:800]}"
            for c in chunks[:8]
        )
        user = f"Antwoord:\n{answer_text}\n\nBronnen:\n{sources}"
        return await call_llm_json(get_citation_verifier_system_prompt(), user, max_tokens=400)

    def _rewrite_without_claims(self, answer_text: str, claims: list[str]) -> str:
        if not claims:
            return answer_text
        notice = (
            "\n\n*Let op: een deel van het antwoord kon niet volledig worden "
            "geverifieerd tegen de opgehaalde bronteksten.*"
        )
        return answer_text.strip() + notice
