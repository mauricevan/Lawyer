"""Per-domain retrieval benchmarks and go/no-go evaluation."""
from ingestion.src.data.domain_registry_loader import DomainConfig, load_domain_registry
from backend.src.utils.retrieval_metrics import mean_reciprocal_rank, recall_at_k, summarize_eval_results


class DomainBenchmarkService:
    """Groups eval rows by domain and checks registry thresholds."""

    def group_questions(self, questions: list[dict]) -> dict[str, list[dict]]:
        from ingestion.src.data.domain_registry_loader import resolve_domain_for_celex

        grouped: dict[str, list[dict]] = {}
        for item in questions:
            domain = item.get("domain")
            if not domain:
                expected = item.get("expected_celex", [])
                domain = resolve_domain_for_celex(expected[0]) if expected else None
            if not domain:
                domain = "unknown"
            grouped.setdefault(domain, []).append(item)
        return grouped

    def evaluate_domain(
        self,
        domain_id: str,
        metric_rows: list[dict],
        registry: dict[str, DomainConfig] | None = None,
    ) -> dict[str, object]:
        registry = registry or load_domain_registry()
        summary = summarize_eval_results(metric_rows)
        config = registry.get(domain_id)
        threshold = config.min_recall_at_5 if config else 0.8
        recall = float(summary["recall_at_5"])
        decision = "pass" if recall >= threshold else "fail"
        if config and config.status == "no_go":
            decision = "blocked"
        return {
            "domain": domain_id,
            "label": config.label if config else domain_id,
            "status": config.status if config else "unknown",
            "recall_at_5": recall,
            "mrr": summary["mrr"],
            "threshold": threshold,
            "decision": decision,
            "count": int(summary["count"]),
        }

    def build_go_no_go_report(self, domain_results: list[dict]) -> dict[str, object]:
        go_domains = [row["domain"] for row in domain_results if row["decision"] == "pass"]
        blocked = [row["domain"] for row in domain_results if row["decision"] == "blocked"]
        failed = [row["domain"] for row in domain_results if row["decision"] == "fail"]
        return {
            "go": go_domains,
            "pilot_or_failed": failed,
            "blocked": blocked,
            "domains": domain_results,
        }
