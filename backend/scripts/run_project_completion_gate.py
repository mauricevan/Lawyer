#!/usr/bin/env python3
"""Write project completion report (plan31 AC)."""
import json
import sys

from backend.src.services.project_completion_service import ProjectCompletionService

_REPO = ProjectCompletionService()._root  # noqa: SLF001


def main() -> None:
    service = ProjectCompletionService()
    payload = service.audit()
    path = _REPO / "docs/data/governance-reports/project-completion-latest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not payload.get("passed"):
        raise SystemExit("Project completion audit failed")


if __name__ == "__main__":
    main()
