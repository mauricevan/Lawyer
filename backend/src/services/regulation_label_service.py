"""Load human-readable regulation names from curated corpus metadata."""
from functools import lru_cache

from ingestion.src.data.curated_loader import load_curated_documents

_STATIC_LABELS: dict[str, str] = {
    "32013R0952": "het Douanewetboek van de Unie (Verordening 952/2013)",
    "32016R0679": "de Algemene Verordening Gegevensbescherming (AVG)",
    "32011L0083": "de Richtlijn consumentenrechten (2011/83/EU)",
    "32024R1689": "de AI-verordening (AI Act)",
    "32004R0261": "de verordening over vliegrechten (261/2004)",
    "32022R2065": "de Digital Services Act (DSA)",
    "32022R1925": "de Digital Markets Act (DMA)",
    "32023R1114": "MiCA (Markets in Crypto-Assets)",
    "32022R2554": "DORA (digitale operationele weerbaarheid)",
    "32022L2555": "NIS2-richtlijn",
    "32019R1020": "Verordening (EU) 2019/1020 markttoezicht",
    "32024L1385": "de EU-klokkenluidersrichtlijn",
    "32023R0988": "de algemene productveiligheidsverordening (GPSR, 2023/988)",
    "32004L0035": "de Milieuaansprakelijkheidsrichtlijn (2004/35/EG)",
}


@lru_cache(maxsize=1)
def load_regulation_labels() -> dict[str, str]:
    """Merge static labels with curated short titles."""
    labels = dict(_STATIC_LABELS)
    for document in load_curated_documents():
        if document.short_title:
            labels[document.celex] = document.short_title
        elif document.title and document.celex not in labels:
            labels[document.celex] = _shorten_title(document.title)
    return labels


def regulation_label(celex: str, fallback: str = "de relevante EU-verordening") -> str:
    return load_regulation_labels().get(celex, fallback)


def _shorten_title(title: str) -> str:
    cleaned = title.strip()
    if len(cleaned) <= 80:
        return cleaned
    return cleaned[:77] + "…"
