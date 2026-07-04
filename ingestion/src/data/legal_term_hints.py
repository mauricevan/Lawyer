"""CELEX hint map derived from curated corpus metadata."""
import re

from ingestion.src.data.cn_code_parser import is_classification_question
from ingestion.src.data.curated_loader import load_curated_documents
from ingestion.src.data.oj_citation_parser import parse_oj_celex

STATIC_HINTS: dict[str, str] = {
    "dora": "32022R2554",
    "digitale operationele weerbaarheid": "32022R2554",
    "csrd": "32022L2464",
    "duurzaamheidsrapportering": "32022L2464",
    "gdpr": "32016R0679",
    "avg": "32016R0679",
    "ai act": "32024R1689",
    "ai-wet": "32024R1689",
    "chatbot": "32024R1689",
    "chatbots": "32024R1689",
    "kunstmatige intelligentie": "32024R1689",
    "goederencode": "31987R2658",
    "goederen code": "31987R2658",
    "taric": "31987R2658",
    "gecombineerde nomenclatuur": "31987R2658",
    "douane nomenclatuur": "31987R2658",
    "douanetarief": "31987R2658",
    "combined nomenclature": "31987R2658",
    "transparante arbeidsvoorwaarden": "32019L1152",
    "consumer cooperation": "32017R2394",
    "consumentenautoriteiten": "32017R2394",
    "whistleblower": "32024L1385",
    "whistleblower-richtlijn": "32024L1385",
    "klokkenluider": "32024L1385",
    "meldingen doen": "32024L1385",
    "cookie": "32002L0058",
    "cookiebanner": "32002L0058",
    "cookies": "32002L0058",
    "vlucht": "32004R0261",
    "vertraging": "32004R0261",
    "compensatie": "32004R0261",
    "luchthaven": "32004R0261",
    "garantie": "32011L0083",
    "online kopen": "32011L0083",
    "webshop": "32011L0083",
    "bedenktijd": "32011L0083",
    "herroepingstermijn": "32011L0083",
    "herroepingsrecht": "32011L0083",
    "overeenkomst op afstand": "32011L0083",
    "crypto": "32023R1114",
    "bitcoin": "32023R1114",
    "mica": "32023R1114",
    "deepfake": "32024R1689",
    "drone": "32016R0679",
    "zorgverzekering": "32011L0024",
    "behandeling in belgi": "32011L0024",
    "ouderschapsverlof": "32019L1152",
    "vaderschap": "32019L1152",
    "rekening sluiten": "32014L0092",
    "betaalrekening": "32014L0092",
    "energielabel": "32010L0031",
    "invoerrechten": "32013R0952",
    "terugbetaling": "32013R0952",
    "douanewaarde": "32013R0952",
    "douane cadeau": "32013R0952",
    "toegankelijk": "32019L0882",
    "productveiligheid": "32023R0988",
    "gegevensoverdraagbaarheid": "32016R0679",
    "sollicitaties": "32024R1689",
    "ai te trainen": "32024R1689",
    "klantgegevens gebruiken": "32016R0679",
    "douanewetboek": "32013R0952",
    "conformiteitsverklaring": "32019R1020",
    "rechtsgronden": "32016R0679",
    "zonder toestemming": "32016R0679",
    "EU-conformiteitsverklaring": "32019R1020",
    "harmonisatiewetgeving": "32019R1020",
    "harmonisatie wetgeving": "32019R1020",
    "milieuaansprakelijkheid": "32004L0035",
    "milieuaansprakelijkheidsrichtlijn": "32004L0035",
    "milieuschade": "32004L0035",
    "environmental liability": "32004L0035",
    "gelijke behandeling": "32000L0078",
    "gelijke behandeling arbeid": "32000L0078",
    "discriminatie werknemer": "32000L0078",
    "2000/78": "32000L0078",
}


def build_legal_term_celex_hints() -> dict[str, str]:
    """Build hint -> CELEX map from curated short titles and static aliases."""
    hints = dict(STATIC_HINTS)
    for document in load_curated_documents():
        if document.short_title:
            hints[document.short_title.lower().strip()] = document.celex
        label = _normalize_label(document.title)
        if label and label not in hints:
            hints[label] = document.celex
    return hints


def match_celex_hints(question: str, hints: dict[str, str] | None = None) -> set[str]:
    """Return CELEX codes whose hints appear in the question (longest match first)."""
    matched: set[str] = set()
    oj_celex = parse_oj_celex(question)
    if oj_celex:
        matched.add(oj_celex)
    source = hints or build_legal_term_celex_hints()
    query_lower = question.lower()
    for hint in sorted(source.keys(), key=len, reverse=True):
        if hint in query_lower:
            matched.add(source[hint])
    return matched


def match_primary_celex_hint(question: str, hints: dict[str, str] | None = None) -> str | None:
    """Return the best CELEX hint: OJ citation, explicit CELEX, then longest alias."""
    oj_celex = parse_oj_celex(question)
    if oj_celex:
        return oj_celex
    if is_classification_question(question):
        return "31987R2658"
    source = hints or build_legal_term_celex_hints()
    query_lower = question.lower()
    for hint in sorted(source.keys(), key=len, reverse=True):
        if hint in query_lower:
            return source[hint]
    return None


def _normalize_label(title: str) -> str:
    cleaned = re.sub(r"\([^)]*\)", "", title).strip().lower()
    for prefix in ("verordening ", "richtlijn ", "besluit "):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):]
    return cleaned[:120].strip()
