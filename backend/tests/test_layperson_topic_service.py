"""Tests for layperson topic matching and answers."""
from backend.src.services.layperson_topic_answer_service import LaypersonTopicAnswerService
from backend.src.services.layperson_topic_service import LaypersonTopicService


def test_flight_compensation_topic_matches():
    match = LaypersonTopicService().match(
        "Mijn vlucht binnen Europa had 5 uur vertraging. Heb ik recht op compensatie?"
    )
    assert match is not None
    assert match.regulation_celex == "32004R0261"


def test_cookie_topic_matches():
    match = LaypersonTopicService().match("Moet elke website een cookiebanner tonen?")
    assert match is not None
    assert match.regulation_celex == "32002L0058"


def test_topic_answer_has_layperson_sections():
    match = LaypersonTopicService().match("Moet elke website een cookiebanner tonen?")
    assert match is not None
    answer = LaypersonTopicAnswerService().build(match, "layperson")
    assert "## Kort antwoord" in answer
    assert "## Uitleg" in answer
    assert "## Wat dit voor u kan betekenen" in answer
    assert "CELEX" not in answer


def test_crypto_mica_topic_matches():
    match = LaypersonTopicService().match("Welke EU-regels gelden voor crypto via een app?")
    assert match is not None
    assert match.regulation_celex == "32023R1114"


def test_warranty_topic_matches_webshop():
    match = LaypersonTopicService().match(
        "Ik kocht online een kapotte wasmachine met garantie uit Duitsland."
    )
    assert match is not None
    assert match.regulation_celex == "32011L0083"


def test_minors_social_media_topic_matches():
    match = LaypersonTopicService().match("Mijn kind is 15. Mag TikTok zijn gegevens bewaren?")
    assert match is not None
    assert match.topic_id == "minors_social_media"


def test_avg_contacts_topic_matches():
    match = LaypersonTopicService().match("Een app vraagt toegang tot mijn contacten.")
    assert match is not None
    assert match.topic_id == "avg_contacts"


def test_cash_payments_topic_matches():
    match = LaypersonTopicService().match("De supermarkt weigert contant geld te accepteren.")
    assert match is not None
    assert match.topic_id == "cash_payments"


def test_working_time_topic_matches():
    match = LaypersonTopicService().match("Wat is het maximum aantal uur dat ik per week mag werken?")
    assert match is not None
    assert match.topic_id == "working_time"


def test_driving_license_topic_matches():
    match = LaypersonTopicService().match("Mag ik met mijn Nederlandse rijbewijs in Italië rijden?")
    assert match is not None
    assert match.topic_id == "driving_license_eu"


def test_wine_import_topic_matches():
    match = LaypersonTopicService().match("Ik importeer wijn uit Frankrijk voor eigen gebruik.")
    assert match is not None
    assert match.topic_id == "wine_import_personal"


def test_iot_smart_home_topic_matches():
    match = LaypersonTopicService().match("Mijn slimme thermostaat verzamelt data.")
    assert match is not None
    assert match.topic_id == "iot_smart_home"


def test_telecom_contract_topic_matches():
    match = LaypersonTopicService().match("Mijn telefoonabonnement loopt 3 jaar. Mag de provider me vastzetten?")
    assert match is not None
    assert match.topic_id == "telecom_contract"


def test_eu_tenant_rental_topic_matches():
    match = LaypersonTopicService().match("Ik huur een huis in Spanje. Welke EU-regels beschermen mij als huurder?")
    assert match is not None
    assert match.topic_id == "eu_tenant_rental"


def test_cross_border_social_security_topic_matches():
    match = LaypersonTopicService().match("Ik werk in Nederland maar woon in Duitsland. Welke EU-regels gelden voor mijn sociale zekerheid?")
    assert match is not None
    assert match.topic_id == "cross_border_social_security"


def test_food_liability_topic_matches():
    match = LaypersonTopicService().match("Ik bestelde eten via Deliveroo en werd ziek.")
    assert match is not None
    assert match.topic_id == "food_liability_consumer"


def test_e_evidence_police_topic_matches():
    match = LaypersonTopicService().match("Mag de politie mijn telefoon uitlezen zonder warrant onder EU-regels?")
    assert match is not None
    assert match.topic_id == "e_evidence_police"


def test_pregnancy_employment_topic_matches():
    match = LaypersonTopicService().match("Ik ben zwanger en mijn baas wil me ontslaan.")
    assert match is not None
    assert match.topic_id == "pregnancy_employment"


def test_gdpr_recruitment_retention_topic_matches():
    match = LaypersonTopicService().match("Hoe lang mag een EU-bedrijf mijn sollicitatiegegevens bewaren?")
    assert match is not None
    assert match.topic_id == "gdpr_recruitment_retention"


def test_used_car_warranty_topic_matches():
    match = LaypersonTopicService().match("Ik koop een tweedehands auto met verborgen gebreken uit België.")
    assert match is not None
    assert match.topic_id == "online_warranty"


def test_chargeback_does_not_match_warranty():
    q = "Mijn creditcardgegevens zijn gelekt door een webshop. Kan ik chargeback doen?"
    match = LaypersonTopicService().match(q)
    assert match is None or match.topic_id == "psd2_chargeback"


def test_spotify_block_does_not_match_portability():
    q = "Mag Spotify mijn account permanent blokkeren zonder uitleg?"
    match = LaypersonTopicService().match(q)
    assert match is None or match.topic_id == "platform_account_termination"


def test_v03_chargeback_not_warranty():
    q = "Mijn creditcardgegevens zijn gelekt door een webshop. Kan ik chargeback doen onder EU-recht?"
    match = LaypersonTopicService().match(q)
    assert match is not None
    assert match.topic_id == "psd2_chargeback"


def test_v10_spotify_not_portability():
    q = "Mag Spotify mijn account permanent blokkeren zonder uitleg volgens EU-regels?"
    match = LaypersonTopicService().match(q)
    assert match is not None
    assert match.topic_id == "platform_account_termination"


def test_v01_byod_email_not_warranty():
    q = "Mag mijn werkgever mijn privé-e-mail lezen op een zakelijke laptop volgens EU-regels?"
    match = LaypersonTopicService().match(q)
    assert match is not None
    assert match.topic_id == "employer_byod_email"


def test_psd2_chargeback_matches():
    match = LaypersonTopicService().match("Kan ik chargeback doen bij creditcard fraude?")
    assert match is not None
    assert match.topic_id == "psd2_chargeback"


def test_platform_account_termination_matches():
    match = LaypersonTopicService().match("Spotify heeft mijn account permanent geblokkeerd.")
    assert match is not None
    assert match.topic_id == "platform_account_termination"


def test_employer_byod_email_matches():
    match = LaypersonTopicService().match("Mag mijn werkgever privé-e-mail lezen op zakelijke laptop?")
    assert match is not None
    assert match.topic_id == "employer_byod_email"


def test_retail_cctv_matches():
    match = LaypersonTopicService().match("Moet een winkel camerabeelden van klanten bewaren?")
    assert match is not None
    assert match.topic_id == "retail_cctv_gdpr"


def test_food_allergen_matches():
    match = LaypersonTopicService().match("Moet een restaurant allergenen vermelden op het menu?")
    assert match is not None
    assert match.topic_id == "food_allergen_labelling"


def test_agency_equal_treatment_matches():
    match = LaypersonTopicService().match("Kan een uitzendbureau mij minder betalen dan vaste collega's?")
    assert match is not None
    assert match.topic_id == "agency_equal_treatment"


def test_workplace_biometrics_matches():
    match = LaypersonTopicService().match("Mag mijn werkgever vingerafdruk-scannen voor inklokken?")
    assert match is not None
    assert match.topic_id == "workplace_biometrics"


def test_car_rental_matches():
    match = LaypersonTopicService().match("Ik huur een auto in Spanje en weiger hem vanwege krassen.")
    assert match is not None
    assert match.topic_id == "car_rental_consumer"


def test_school_photos_matches():
    match = LaypersonTopicService().match("Moet een school toestemming vragen voor foto's van leerlingen op de website?")
    assert match is not None
    assert match.topic_id == "school_photos_gdpr"


def test_ce_marking_matches():
    match = LaypersonTopicService().match("Ik verkoop handgemaakte sieraden via Etsy. Moet ik CE-markering hebben?")
    assert match is not None
    assert match.topic_id == "ce_marking_consumer"


def test_digital_content_subscription_matches():
    match = LaypersonTopicService().match("Mag de verkoper updates stoppen bij software abonnement?")
    assert match is not None
    assert match.topic_id == "digital_content_subscription"


def test_eu_whistleblower_matches():
    match = LaypersonTopicService().match(
        "Wat verplicht de EU-whistleblower-richtlijn werkgevers te doen bij meldingen?"
    )
    assert match is not None
    assert match.topic_id == "eu_whistleblower"


def test_employer_email_avg_matches():
    match = LaypersonTopicService().match(
        "Mag mijn werkgever mijn e-mails lezen onder de AVG?"
    )
    assert match is not None
    assert match.topic_id == "employer_byod_email"


def test_bezorgdrone_not_drone_privacy():
    match = LaypersonTopicService().match(
        "Mag ik een bezorgdrone inzetten voor pakketten?"
    )
    assert match is not None
    assert match.topic_id == "bezorgdrone_registratie"


def test_schoolreis_not_drone_privacy():
    match = LaypersonTopicService().match("filmen op schoolreis buitenland met drone")
    assert match is None or match.topic_id != "drone_privacy"


def test_restvoorraad_not_warranty():
    match = LaypersonTopicService().match(
        "Webshop moet mij waarschuwen bij restvoorraad product"
    )
    assert match is None or match.topic_id != "online_warranty"


def test_spam_sms_matches():
    match = LaypersonTopicService().match("ik krijg spam sms wat zijn mijn rechten")
    assert match is not None
    assert match.topic_id == "spam_sms"


def test_vereniging_ledenlijst_matches():
    match = LaypersonTopicService().match(
        "Onze vereniging verwerkt ledenlijsten. Moeten we ons registreren bij de AP?"
    )
    assert match is not None
    assert match.topic_id == "vereniging_ledenlijst_avg"


def test_app_contacten_matches():
    match = LaypersonTopicService().match(
        "Een app vraagt toegang tot mijn contacten. Moet ik daarmee instemmen?"
    )
    assert match is not None
    assert match.topic_id in {"app_contacten_toestemming", "avg_contacts"}


def test_n08_webshop_frankrijk_matches():
    match = LaypersonTopicService().match(
        "Ik start een webshop en verkoop aan consumenten in Frankrijk. Welke EU-regels moet ik kennen?"
    )
    assert match is not None
    assert match.topic_id == "webshop_eu_consument"
