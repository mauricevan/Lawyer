"""V10.3 ILCL detection patterns — pre-retrieval ambiguity signals."""
import re

PLATFORM_START_HINTS = (
    "platform starten", "platform beginnen", "online platform", "marktplaats starten",
    "app starten", "website starten", "marktplaats bouwen", "platform opzetten",
)
ACTOR_HINTS = (
    "ondernemer", "bedrijf", "zzp", "consument", "overheid", "lidstaat",
    "platformoperator", "verkoper", "koper", "werkgever", "organisatie",
)
ACTIVITY_HINTS = (
    "verkopen", "adverteren", "marktplaats", "webshop", "saas", "app",
    "social media", "content", "gebruikers", "advertentie", "marktplaats",
    "c2c", "b2c", "marktplace", "dienst", "abonnement",
)
SCOPE_HINTS = (
    "eu-breed", "eu breed", "europ", "in de eu", "eu-wet", "eu regel",
    "eu wetgeving", "eu-wetgeving", "europese wet", "europese wetgeving",
    "nederland", "belgi", "duitsland",
    "één land", "een land", "wereldwijd", "internationaal", "lidstaat",
)
NON_EU_HINTS = (
    "amerikaanse wet", "us law", "california", "verenigde staten",
    "nederlandse wet alleen", "alleen nederlandse wet", "zonder eu",
)
REFUSAL_HINTS = (
    "weet niet", "geen idee", "maakt niet uit", "maakt me niet uit",
    "kies maar", "jij mag kiezen", "maakt niet", "onzeker",
)
PLATFORM_VAGUE_PATTERN = re.compile(
    r"mag ik (?:een )?(?:platform|platfrom|app|website|marktplaats)\b",
    re.IGNORECASE,
)
IDENTIFICATION_HINTS = (
    "legitim", "identif", "identiteit", "paspoort", "id-kaart", "id kaart",
    "eidas", "digitaal identiteit", "inloggen", "account aanmaken", "kyc",
    "ken uw klant", "verificatie van identiteit",
)
PRIVACY_HINTS = (
    "privacy", "avg", "gdpr", "persoonsgegeven", "gegevens", "cookie",
    "data", "opslaan", "bewaren", "opslag", "verwerking", "verwerken", "derden",
)
DATA_STORAGE_HINTS = (
    "opslaan", "bewaren", "opslag", "data van derden", "gegevens van derden",
    "gegevens opslaan", "data opslaan", "doorgeven", "doorgifte",
)
EU_FACTUAL_ASKS = (
    "welke lidstaten", "welke landen", "welke lidstaat", "wie doet mee",
    "waar staat", "wat zegt", "wat zeggen", "in welk artikel",
    "in welke verordening", "welke verordening", "welke richtlijn",
)
LEGAL_INFO_ASKS = (
    "wat zegt", "wat zeggen", "welke regel", "welke regels", "welke wet",
    "eu wetgeving", "eu-wetgeving", "europese wetgeving",
    *EU_FACTUAL_ASKS,
)
EMPLOYMENT_HINTS = (
    "werk", "arbeid", "loon", "ontslag", "werkgever", "werknemer",
    "non-actief", "concurrentiebeding", "staande voet",
)
AI_REGISTRATION_HINTS = (
    "chatbot", "ai-assistent", "website-bot", " bot", "plugin", "widget",
)
COMMERCE_HINTS = (
    "webshop", "verkopen", "kopen", "retour", "garantie", "consument",
)
CUSTOMS_HINTS = (
    "douane", "customs", "invoer", "import", "uitvoer", "export",
    "douane-unie", "douane unie", "douanegebied", "douanewetboek",
    "aangifte", "goederencode", "tarief", "invoerrechten",
)
