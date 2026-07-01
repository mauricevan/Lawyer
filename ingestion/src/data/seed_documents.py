"""Top-20 seed documents for prototype corpus."""
from shared.schemas.document import DocumentMetadata, VersionType

SEED_DOCUMENTS: list[DocumentMetadata] = [
    DocumentMetadata(
        celex="32024R1689", title="Verordening (EU) 2024/1689 betreffende artificiële intelligentie (AI Act)",
        short_title="AI Act", doc_type="regulation", language="nl", is_in_force=True,
        is_consolidated=True, version_type=VersionType.CONSOLIDATED,
        eli_uri="http://data.europa.eu/eli/reg/2024/1689/oj", oj_reference="L 2024/1689",
    ),
    DocumentMetadata(
        celex="32016R0679", title="Verordening (EU) 2016/679 betreffende de bescherming van natuurlijke personen (GDPR)",
        short_title="GDPR", doc_type="regulation", language="nl", is_in_force=True,
        is_consolidated=True, version_type=VersionType.CONSOLIDATED,
        eli_uri="http://data.europa.eu/eli/reg/2016/679/oj", oj_reference="L 119/1",
    ),
    DocumentMetadata(
        celex="32022L2555", title="Richtlijn (EU) 2022/2555 betreffende maatregelen voor een hoog gemeenschappelijk niveau van cyberbeveiliging (NIS2)",
        short_title="NIS2", doc_type="directive", language="nl", is_in_force=True,
        is_consolidated=False, version_type=VersionType.BASE, oj_reference="L 333/80",
    ),
    DocumentMetadata(
        celex="32022R2065", title="Verordening (EU) 2022/2065 betreffende een eengemaakte markt voor digitale diensten (DSA)",
        short_title="DSA", doc_type="regulation", language="nl", is_in_force=True,
        is_consolidated=False, version_type=VersionType.BASE, oj_reference="L 277/1",
    ),
    DocumentMetadata(
        celex="32022R1925", title="Verordening (EU) 2022/1925 betreffende betwistbare en eerlijke markten in de digitale sector (DMA)",
        short_title="DMA", doc_type="regulation", language="nl", is_in_force=True,
        is_consolidated=False, version_type=VersionType.BASE, oj_reference="L 265/1",
    ),
    DocumentMetadata(
        celex="32014R0596", title="Verordening (EU) Nr. 596/2014 betreffende marktmisbruik (MAR)",
        short_title="MAR", doc_type="regulation", language="nl", is_in_force=True,
        is_consolidated=True, version_type=VersionType.CONSOLIDATED, oj_reference="L 173/1",
    ),
    DocumentMetadata(
        celex="32013L0036", title="Richtlijn 2013/36/EU betreffende toegang tot het bedrijf van kredietinstellingen (CRD IV)",
        short_title="CRD IV", doc_type="directive", language="nl", is_in_force=True,
        is_consolidated=False, version_type=VersionType.BASE, oj_reference="L 176/338",
    ),
    DocumentMetadata(
        celex="32015L0849", title="Richtlijn (EU) 2015/849 betreffende de voorkoming van het gebruik van het financiële stelsel voor witwassen (AML)",
        short_title="AML", doc_type="directive", language="nl", is_in_force=True,
        is_consolidated=True, version_type=VersionType.CONSOLIDATED, oj_reference="L 141/73",
    ),
    DocumentMetadata(
        celex="32019R1150", title="Verordening (EU) 2019/1150 betreffende bevordering van billijkheid en transparantie (P2B)",
        short_title="P2B", doc_type="regulation", language="nl", is_in_force=True,
        is_consolidated=False, version_type=VersionType.BASE, oj_reference="L 186/57",
    ),
    DocumentMetadata(
        celex="32017R1128", title="Verordening (EU) 2017/1128 betreffende grensoverschrijdende portabiliteit van online inhoud (Portability)",
        short_title="Portability", doc_type="regulation", language="nl", is_in_force=True,
        is_consolidated=False, version_type=VersionType.BASE, oj_reference="L 168/1",
    ),
    DocumentMetadata(
        celex="32018R1807", title="Verordening (EU) 2018/1807 betreffende de vrijwaringsclausule voor niet-persoonlijke gegevens",
        short_title="Data FWD", doc_type="regulation", language="nl", is_in_force=True,
        is_consolidated=False, version_type=VersionType.BASE, oj_reference="L 303/59",
    ),
    DocumentMetadata(
        celex="32021R0104", title="Verordening (EU) 2021/104 betreffende de oprichting van het programma Digital Europe",
        short_title="Digital Europe", doc_type="regulation", language="nl", is_in_force=True,
        is_consolidated=False, version_type=VersionType.BASE, oj_reference="L 231/1",
    ),
    DocumentMetadata(
        celex="32019L1024", title="Richtlijn (EU) 2019/1024 betreffende open data en het hergebruik van overheidsinformatie",
        short_title="Open Data", doc_type="directive", language="nl", is_in_force=True,
        is_consolidated=False, version_type=VersionType.BASE, oj_reference="L 172/56",
    ),
    DocumentMetadata(
        celex="32018L1972", title="Richtlijn (EU) 2018/1972 tot vaststelling van het Europees wetboek voor elektronische communicatie",
        short_title="EECC", doc_type="directive", language="nl", is_in_force=True,
        is_consolidated=False, version_type=VersionType.BASE, oj_reference="L 321/36",
    ),
    DocumentMetadata(
        celex="32022R0868", title="Verordening (EU) 2022/868 betreffende Europese governance inzake data (Data Governance Act)",
        short_title="DGA", doc_type="regulation", language="nl", is_in_force=True,
        is_consolidated=False, version_type=VersionType.BASE, oj_reference="L 152/1",
    ),
    DocumentMetadata(
        celex="32023R2854", title="Verordening (EU) 2023/2854 betreffende geharmoniseerde regels voor eerlijke toegang tot en gebruik van data (Data Act)",
        short_title="Data Act", doc_type="regulation", language="nl", is_in_force=True,
        is_consolidated=False, version_type=VersionType.BASE, oj_reference="L 2023/2854",
    ),
    DocumentMetadata(
        celex="32024R1689R(01)", title="Rectificatie Verordening (EU) 2024/1689 (AI Act corrigendum)",
        short_title="AI Act Corrigendum", doc_type="regulation", language="nl", is_in_force=True,
        is_consolidated=False, version_type=VersionType.CORRIGENDUM,
        corrigendum_celex="32024R1689R(01)",
    ),
    DocumentMetadata(
        celex="32017R0745", title="Verordening (EU) 2017/745 betreffende medische hulpmiddelen (MDR)",
        short_title="MDR", doc_type="regulation", language="nl", is_in_force=True,
        is_consolidated=True, version_type=VersionType.CONSOLIDATED, oj_reference="L 117/1",
    ),
    DocumentMetadata(
        celex="32014L0065", title="Richtlijn 2014/65/EU betreffende markten voor financiële instrumenten (MiFID II)",
        short_title="MiFID II", doc_type="directive", language="nl", is_in_force=True,
        is_consolidated=True, version_type=VersionType.CONSOLIDATED, oj_reference="L 173/349",
    ),
    DocumentMetadata(
        celex="32010L0013", title="Richtlijn 2010/13/EU betreffende audiovisuele mediadiensten (AVMSD)",
        short_title="AVMSD", doc_type="directive", language="nl", is_in_force=True,
        is_consolidated=True, version_type=VersionType.CONSOLIDATED, oj_reference="L 95/1",
    ),
]
