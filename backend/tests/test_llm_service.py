"""Unit tests for LlmService prompt and context building."""
from backend.src.services.llm_service import LlmService
from shared.config.prompt_loader import get_mode_hint, get_system_prompt


def test_system_prompt_layperson():
    service = LlmService()
    prompt = get_system_prompt("layperson")
    assert service._system_prompt("layperson") == prompt
    assert "CELEX" not in prompt or "GEEN CELEX" in prompt


def test_system_prompt_professional():
    service = LlmService()
    assert service._system_prompt("professional") == get_system_prompt("professional")


def test_system_prompt_specific_variant():
    service = LlmService()
    specific = get_system_prompt("professional", specific=True)
    assert service._system_prompt("professional", specific=True) == specific
    assert "Wettelijke grondslag" in specific


def test_build_context_layperson_uses_title():
    service = LlmService()
    chunks = [
        {
            "celex": "32024R1689",
            "article_number": "5",
            "title": "AI Act",
            "text": "Sample legal text.",
        }
    ]
    context = service._build_context(chunks, "layperson")
    assert "AI Act — artikel 5" in context
    assert "CELEX:" not in context


def test_build_context_professional_uses_celex():
    service = LlmService()
    chunks = [
        {
            "celex": "32024R1689",
            "article_number": "5",
            "title": "AI Act",
            "text": "Sample legal text.",
        }
    ]
    context = service._build_context(chunks, "professional")
    assert "CELEX:32024R1689" in context


def test_mode_instruction_per_audience():
    service = LlmService()
    lay = service._mode_instruction("compliance", "layperson")
    pro = service._mode_instruction("compliance", "professional")
    assert lay == get_mode_hint("compliance", "layperson")
    assert pro == get_mode_hint("compliance", "professional")
    assert "niet kunt bevestigen" in lay.lower()


def test_fallback_answer_layperson_structure():
    service = LlmService()
    chunks = [
        {
            "celex": "32024R1689",
            "article_number": "5",
            "title": "AI Act",
            "text": "Relevant passage.",
        }
    ]
    answer = service._fallback_answer("test?", chunks, "layperson")
    assert "## Kort antwoord" in answer
    assert "## Let op" in answer


def test_fallback_answer_no_chunks_layperson():
    service = LlmService()
    answer = service._fallback_answer("test?", [], "layperson")
    assert "geen relevante" in answer.lower()


def test_build_messages_adds_follow_up_hint_with_history():
    service = LlmService()
    history = [
        {"role": "user", "content": "Eerste vraag"},
        {"role": "assistant", "content": "Eerste antwoord"},
    ]
    messages = service._build_messages("Tweede vraag?", "context", "hint", history)
    assert len(messages) == 3
    assert "vervolgvraag" in messages[-1]["content"].lower()
    assert messages[0]["content"] == "Eerste vraag"


def test_build_messages_no_follow_up_without_history():
    service = LlmService()
    messages = service._build_messages("Vraag?", "context", "hint", None)
    assert len(messages) == 1
    assert "vervolgvraag" not in messages[0]["content"].lower()
