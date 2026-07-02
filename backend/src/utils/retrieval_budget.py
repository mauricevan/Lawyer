"""Hard time budgets for retrieval phases."""
import time


class RetrievalBudgetExceeded(Exception):
    """Raised when retrieval exceeds configured time budget."""


class RetrievalBudget:
    """Tracks remaining time for retrieval pipeline stages."""

    def __init__(self, budget_seconds: float) -> None:
        self._deadline = time.perf_counter() + budget_seconds

    def remaining_seconds(self) -> float:
        return self._deadline - time.perf_counter()

    def ensure(self, phase: str) -> None:
        if self.remaining_seconds() <= 0:
            raise RetrievalBudgetExceeded(f"Retrieval budget exceeded before {phase}")
