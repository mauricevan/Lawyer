"""Match layperson questions to deterministic topic guidance."""
from dataclasses import dataclass

from shared.config.layperson_topic_loader import get_layperson_topics


@dataclass(frozen=True)
class LaypersonTopicMatch:
    topic_id: str
    regulation_celex: str
    regulation_title: str
    short_answer_nl: str
    summary_nl: str
    practical_nl: str


class LaypersonTopicService:
    """Resolves layperson topic templates from question patterns."""

    def match(self, question: str) -> LaypersonTopicMatch | None:
        lowered = question.lower()
        best: tuple[int, dict] | None = None
        for topic in get_layperson_topics():
            score = self._score_topic(topic, lowered)
            if score is None:
                continue
            if best is None or score > best[0]:
                best = (score, topic)
        if best is None:
            return None
        return self._to_match(best[1])

    def _score_topic(self, topic: dict, lowered: str) -> int | None:
        patterns = [str(p).lower() for p in topic.get("patterns", [])]
        matching = [p for p in patterns if p in lowered]
        if not matching:
            return None
        excludes = [str(p).lower() for p in topic.get("exclude_patterns", [])]
        if any(ex in lowered for ex in excludes):
            return None
        min_hits = int(topic.get("min_pattern_hits", 1))
        if len(matching) < min_hits:
            return None
        return len(matching) * 1000 + max(len(p) for p in matching)

    def _to_match(self, topic: dict) -> LaypersonTopicMatch:
        return LaypersonTopicMatch(
            topic_id=str(topic["id"]),
            regulation_celex=str(topic["regulation_celex"]),
            regulation_title=str(topic["regulation_title"]),
            short_answer_nl=str(topic["short_answer_nl"]).strip(),
            summary_nl=str(topic["summary_nl"]).strip(),
            practical_nl=str(topic["practical_nl"]).strip(),
        )
