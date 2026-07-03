"""Domain clustering for low-confidence router decisions (plan12 AC)."""
from dataclasses import replace

from backend.src.models.query_route import QueryRoute
from ingestion.src.data.domain_registry_loader import load_domain_registry, resolve_domain_for_celex


class DomainClusterService:
    """Resolves ambiguous domain signals via keyword scoring and clusters."""

    def enrich(self, question: str, route: QueryRoute, threshold: float) -> QueryRoute:
        if route.celex_hint:
            if route.domains and route.confidence >= threshold:
                cluster = self._cluster_for(route.domains[0])
                return replace(
                    route,
                    confidence=max(route.confidence, 0.95),
                    domain_cluster=cluster,
                )
            domain = resolve_domain_for_celex(route.celex_hint)
            domains = [domain] if domain else route.domains
            cluster = self._cluster_for(domains[0]) if domains else route.domain_cluster
            return replace(route, domains=domains, confidence=max(route.confidence, 0.95), domain_cluster=cluster)

        scores = self._score_domains(question.lower())
        if route.intent_id and route.confidence >= threshold:
            if not route.domains:
                scores = self._score_domains(question.lower())
                route = self._fallback_from_scores(route, scores, threshold)
            cluster = self._cluster_for(route.domains[0]) if route.domains else route.domain_cluster
            return replace(route, domain_cluster=cluster)

        if len(route.domains) > 1:
            best = max(route.domains, key=lambda domain: scores.get(domain, 0))
            return replace(
                route,
                domains=[best],
                confidence=min(route.confidence, 0.65),
                domain_cluster=self._cluster_for(best),
            )

        if not route.domains:
            return self._fallback_from_scores(route, scores, threshold)

        if route.confidence < threshold:
            return self._fallback_from_scores(route, scores, threshold)

        cluster = self._cluster_for(route.domains[0])
        return replace(route, domain_cluster=cluster)

    def _fallback_from_scores(
        self,
        route: QueryRoute,
        scores: dict[str, int],
        threshold: float,
    ) -> QueryRoute:
        if not scores:
            return replace(route, confidence=min(route.confidence, 0.35))
        best_domain = max(scores, key=scores.get)
        best_score = scores[best_domain]
        if best_score <= 0:
            return replace(route, confidence=min(route.confidence, 0.35))
        domains = [best_domain] if confidence >= threshold else []
        return replace(
            route,
            domains=domains,
            confidence=confidence,
            domain_cluster=self._cluster_for(best_domain),
        )

    def _score_domains(self, question_lower: str) -> dict[str, int]:
        registry = load_domain_registry()
        scores: dict[str, int] = {}
        for domain_id, config in registry.items():
            hits = sum(1 for term in config.keywords if term in question_lower)
            if hits:
                scores[domain_id] = hits
        return scores

    def _cluster_for(self, domain_id: str | None) -> str | None:
        if not domain_id:
            return None
        registry = load_domain_registry()
        config = registry.get(domain_id)
        return config.cluster if config else None
