"""Match CN classification questions to configured position guidance."""
from dataclasses import dataclass

from shared.config.cn_classification_loader import get_cn_positions, load_cn_classification_config
from ingestion.src.data.cn_code_parser import extract_cn_code, is_classification_question


@dataclass(frozen=True)
class CnSubheadingMatch:
    code: str
    label_nl: str


@dataclass(frozen=True)
class CnPositionMatch:
    position_code: str
    title_nl: str
    summary_nl: str
    subheading: CnSubheadingMatch | None
    regulation_celex: str
    regulation_title: str


class CnClassificationService:
    """Resolves goods-code questions to structured CN guidance."""

    def matches(self, question: str) -> bool:
        return is_classification_question(question) and self.resolve(question) is not None

    def resolve(self, question: str) -> CnPositionMatch | None:
        if not is_classification_question(question):
            return None
        position_code = extract_cn_code(question)
        if not position_code:
            return None
        config = load_cn_classification_config()
        for entry in get_cn_positions():
            if str(entry.get("code")) != position_code:
                continue
            if not self._matches_product(question, entry.get("product_signals", [])):
                continue
            return CnPositionMatch(
                position_code=position_code,
                title_nl=str(entry.get("title_nl", "")),
                summary_nl=str(entry.get("summary_nl", "")),
                subheading=self._match_subheading(question, entry.get("subheadings", [])),
                regulation_celex=str(config.get("regulation_celex", "31987R2658")),
                regulation_title=str(config.get("regulation_title", "")),
            )
        return None

    def _matches_product(self, question: str, signals: list[str]) -> bool:
        if not signals:
            return True
        lowered = question.lower()
        return any(str(signal).lower() in lowered for signal in signals)

    def _match_subheading(
        self,
        question: str,
        subheadings: list[dict],
    ) -> CnSubheadingMatch | None:
        lowered = question.lower()
        for item in subheadings:
            signals = item.get("signals", [])
            if any(str(signal).lower() in lowered for signal in signals):
                return CnSubheadingMatch(
                    code=str(item.get("code", "")),
                    label_nl=str(item.get("label_nl", "")),
                )
        return None
