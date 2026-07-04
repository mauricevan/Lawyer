"""V5.1 — conflict-aware CELEX resolver; juridische waarheid > planner."""
from backend.src.utils.celex_conflict_scoring import pick_final_celex, score_celex_candidates
from backend.src.utils.conflict_celex_registry import (
    conflict_celex_candidates,
    is_celex_allowed_for_conflict_type,
    primary_celex_for_conflict,
)
from backend.src.utils.conflict_domain_mapping import map_conflict_to_domain
from backend.src.utils.domain_framework_registry import celex_from_frameworks
from backend.src.utils.legal_domain_retrieval_filter import is_celex_allowed_for_domain
from shared.schemas.celex_resolution import CelexRejectionReason, CelexResolutionResult
from shared.schemas.legal_conflict import LegalCaseAnalysis
from shared.schemas.legal_interpretation import InstrumentTarget, LegalInterpretationPlan

_MAX_DISCOVERY = 5


class ConflictAwareCelexResolverService:
    """Select CELEX as juridical consequence of the primary legal conflict."""

    def resolve(
        self,
        analysis: LegalCaseAnalysis,
        plan: LegalInterpretationPlan,
        discovery_celex: list[str] | None = None,
    ) -> CelexResolutionResult:
        """Lock domain, reject invalid planner CELEX, score and select final set."""
        locked = map_conflict_to_domain(analysis.primary_legal_conflict)
        rejected, reason = self._reject_planner_celex(plan, analysis, locked.domain)
        candidates = self._build_candidate_pool(analysis, plan, discovery_celex, rejected)
        scored = score_celex_candidates(analysis, candidates)
        chosen, needs_retry = pick_final_celex(scored)
        instruments = [
            InstrumentTarget(
                name=item.name,
                celex=item.celex,
                articles=[],
                confidence=min(1.0, item.score / 100),
            )
            for item in chosen
        ]
        confidence = min(1.0, chosen[0].score / 100) if chosen else 0.0
        return CelexResolutionResult(
            final_domain=locked.domain,
            final_celex=[item.celex for item in chosen],
            rejected_celex=rejected,
            rejection_reason=reason,
            confidence=confidence,
            instruments=instruments,
            needs_domain_retrieval=needs_retry or not chosen,
        )

    def apply_to_plan(
        self,
        plan: LegalInterpretationPlan,
        resolution: CelexResolutionResult,
    ) -> LegalInterpretationPlan:
        """Replace plan instruments with conflict-resolved CELEX set."""
        if not resolution.instruments:
            return plan
        return plan.model_copy(update={
            "legal_domain": resolution.final_domain,
            "instruments": resolution.instruments,
        })

    def _reject_planner_celex(
        self,
        plan: LegalInterpretationPlan,
        analysis: LegalCaseAnalysis,
        locked_domain: str,
    ) -> tuple[list[str], CelexRejectionReason]:
        rejected: list[str] = []
        reason: CelexRejectionReason = "none"
        planner_domain_mismatch = plan.legal_domain != locked_domain
        for instrument in plan.instruments:
            celex = instrument.celex
            if not celex:
                continue
            if planner_domain_mismatch:
                rejected.append(celex)
                reason = "planner_domain_mismatch"
                continue
            if not is_celex_allowed_for_conflict_type(celex, analysis.primary_legal_conflict):
                rejected.append(celex)
                reason = "forbidden_for_conflict"
            elif not is_celex_allowed_for_domain(celex, locked_domain):  # type: ignore[arg-type]
                rejected.append(celex)
                reason = "conflict_domain_mismatch"
        return rejected, reason

    def _build_candidate_pool(
        self,
        analysis: LegalCaseAnalysis,
        plan: LegalInterpretationPlan,
        discovery_celex: list[str] | None,
        rejected: list[str],
    ) -> list[str]:
        pool: list[str] = []
        pool.extend(primary_celex_for_conflict(analysis.primary_legal_conflict))
        if analysis.default_celex:
            pool.append(analysis.default_celex)
        framework_celex = celex_from_frameworks(analysis.likely_eu_frameworks)
        if framework_celex:
            pool.append(framework_celex)
        pool.extend(conflict_celex_candidates(analysis.primary_legal_conflict))
        for instrument in plan.instruments:
            celex = instrument.celex
            if celex and celex not in rejected:
                pool.append(celex)
        for celex in (discovery_celex or [])[:_MAX_DISCOVERY]:
            pool.append(celex)
        return list(dict.fromkeys(pool))
