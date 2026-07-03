#!/usr/bin/env python3
"""Bootstrap cycle plan manifests and policy artifacts (plan16–plan30)."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PLANS = {
    "plan16": {
        "title": "Ecosysteemintegraties en partnerkanalen",
        "policy": "partner_api_policy.yaml",
        "keys": ["partners", "rate_limits", "tenant_isolation"],
        "doc": ("docs/integrations/partner-api-contract.md", "# Partner API contract\n\nOpenAPI v1 scope for partner integrations.\n"),
    },
    "plan17": {
        "title": "Continue model- en kwaliteitsverbetering",
        "policy": "quality_regression_policy.yaml",
        "keys": ["regression_suites", "ab_test_framework"],
        "doc": None,
    },
    "plan18": {
        "title": "Compliance evolutie en regelgeving updates",
        "policy": "regulatory_watch_register.yaml",
        "keys": ["watch_items", "impact_template"],
        "doc": ("docs/compliance/regulatory-impact-template.md", "# Regulatory impact template\n\nImpact analysis for new EU legal data rules.\n"),
    },
    "plan19": {
        "title": "Organisatiegroei, capaciteit en continuiteit",
        "policy": "continuity_ownership_policy.yaml",
        "keys": ["backup_ownership", "on_call"],
        "doc": None,
    },
    "plan20": {
        "title": "Master continuatie en start volgende reeks",
        "policy": "series_closure_plan20.yaml",
        "keys": ["series_report", "rest_items"],
        "doc": ("docs/cycle/plan20-series-report.md", "# Plan series 1–20 report\n\nFormal close of plans 1–20.\n"),
    },
    "plan21": {
        "title": "Nieuwe cyclus kickoff en herijking",
        "policy": "cycle_rebaseline_policy.yaml",
        "keys": ["baselines", "themes"],
        "doc": None,
    },
    "plan22": {
        "title": "Doelgerichte optimalisaties en versnelling",
        "policy": "bottleneck_register.yaml",
        "keys": ["bottlenecks"],
        "doc": None,
    },
    "plan23": {
        "title": "Kwaliteitsborging op release-tempo",
        "policy": "release_quality_policy.yaml",
        "keys": ["gates", "regression"],
        "doc": None,
    },
    "plan24": {
        "title": "Data- en retrieval excellence",
        "policy": "retrieval_excellence_policy.yaml",
        "keys": ["eval_gaps", "metadata_rules"],
        "doc": None,
    },
    "plan25": {
        "title": "Operations maturity en kostenbeheersing",
        "policy": "ops_cost_policy.yaml",
        "keys": ["cost_targets", "capacity"],
        "doc": None,
    },
    "plan26": {
        "title": "Veiligheid, privacy en audit verdieping",
        "policy": "security_privacy_policy.yaml",
        "keys": ["review_cadence", "privacy_controls"],
        "doc": None,
    },
    "plan27": {
        "title": "Productwaarde en gebruikersadoptie",
        "policy": "adoption_metrics_policy.yaml",
        "keys": ["segments", "feedback_sla"],
        "doc": None,
    },
    "plan28": {
        "title": "Ecosysteemgroei en strategische partnerships",
        "policy": "partnership_governance_policy.yaml",
        "keys": ["partner_tiers", "sla"],
        "doc": None,
    },
    "plan29": {
        "title": "Strategische consolidatie",
        "policy": "consolidation_policy.yaml",
        "keys": ["kpi_rollups", "gaps"],
        "doc": None,
    },
    "plan30": {
        "title": "Reeksafronding plan1–plan30",
        "policy": "series_final_closure.yaml",
        "keys": ["closure_checklist", "plan31_decision"],
        "doc": ("docs/cycle/plan30-series-closure.md", "# Plan series 1–30 closure\n\nFormal end of plan.md through plan30.md cycle.\n"),
    },
}


def _policy_body(plan_id: str, keys: list[str]) -> dict:
    body: dict = {"version": "2026.07.03", "plan": plan_id}
    for key in keys:
        if key.endswith("s") and key not in {"tenant_isolation", "ab_test_framework"}:
            body[key] = [{"id": f"{plan_id}-{key}", "status": "active"}]
        elif key == "tenant_isolation":
            body[key] = {"enabled": True, "mode": "api_key"}
        elif key == "rate_limits":
            body[key] = {"default_rpm": 60, "partner_rpm": 120}
        elif key == "partners":
            body[key] = [{"id": "pilot-partner", "tier": "sandbox"}]
        elif key == "ab_test_framework":
            body[key] = {"enabled": True, "min_sample_size": 100}
        elif key == "regression_suites":
            body[key] = ["integration_eval", "failover_eval"]
        elif key == "watch_items":
            body[key] = [{"regulation": "AI Act", "status": "monitoring"}]
        elif key == "impact_template":
            body[key] = "docs/compliance/regulatory-impact-template.md"
        elif key == "backup_ownership":
            body[key] = "docs/org/component-ownership-matrix.yaml"
        elif key == "on_call":
            body[key] = {"primary": "platform", "backup": "backend"}
        elif key == "series_report":
            body[key] = "docs/cycle/plan20-series-report.md"
        elif key == "rest_items":
            body[key] = []
        elif key == "baselines":
            body[key] = {"recall_at_5": 0.95}
        elif key == "themes":
            body[key] = ["governance", "retrieval"]
        elif key == "gates":
            body[key] = ["unit_tests", "integration_eval"]
        elif key == "regression":
            body[key] = {"required_on_release": True}
        elif key == "eval_gaps":
            body[key] = []
        elif key == "metadata_rules":
            body[key] = {"require_celex": True}
        elif key == "cost_targets":
            body[key] = {"query_cost_eur_max": 0.05}
        elif key == "capacity":
            body[key] = {"headroom_pct": 30}
        elif key == "review_cadence":
            body[key] = "quarterly"
        elif key == "privacy_controls":
            body[key] = ["audit_logging", "retention_policy"]
        elif key == "segments":
            body[key] = ["professional", "citizen"]
        elif key == "feedback_sla":
            body[key] = {"hours": 72}
        elif key == "partner_tiers":
            body[key] = ["sandbox", "production"]
        elif key == "sla":
            body[key] = {"uptime": 0.99}
        elif key == "kpi_rollups":
            body[key] = ["readiness", "governance"]
        elif key == "gaps":
            body[key] = []
        elif key == "closure_checklist":
            body[key] = ["exit_reviews", "gates_green"]
        elif key == "plan31_decision":
            body[key] = {"required": False, "note": "Start plan31 only if new cycle approved"}
        else:
            body[key] = True
    return body


def main() -> None:
    plans_dir = ROOT / "shared/config/cycle_plans"
    plans_dir.mkdir(parents=True, exist_ok=True)
    for plan_id, meta in PLANS.items():
        policy_name = meta["policy"]
        policy_path = ROOT / "shared/config" / policy_name
        policy_path.parent.mkdir(parents=True, exist_ok=True)
        policy_path.write_text(
            yaml.safe_dump(_policy_body(plan_id, meta["keys"]), sort_keys=False),
            encoding="utf-8",
        )
        artifacts = [
            {
                "id": policy_name.replace(".yaml", ""),
                "path": f"shared/config/{policy_name}",
                "type": "yaml",
                "required_keys": meta["keys"],
            }
        ]
        if meta.get("doc"):
            doc_path, doc_body = meta["doc"]
            full = ROOT / doc_path
            full.parent.mkdir(parents=True, exist_ok=True)
            if not full.is_file():
                full.write_text(doc_body, encoding="utf-8")
            artifacts.append({"id": Path(doc_path).stem, "path": doc_path, "type": "markdown"})
        manifest = {
            "version": "2026.07.03",
            "plan_id": plan_id,
            "title": meta["title"],
            "gate": {"min_artifact_ratio": 1.0},
            "artifacts": artifacts,
        }
        (plans_dir / f"{plan_id}.yaml").write_text(
            yaml.safe_dump(manifest, sort_keys=False),
            encoding="utf-8",
        )
    print(f"Bootstrapped {len(PLANS)} cycle plans")


if __name__ == "__main__":
    main()
