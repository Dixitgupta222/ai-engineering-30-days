
from app.services.knowledge_service import (
    answer_customer_with_knowledge,
    find_knowledge_section,
)


def test_find_healthcare_section():
    result = find_knowledge_section("healthcare")

    assert "Healthcare Projects" in result
    assert "privacy, security, and regulatory requirements" in result


def test_answer_pricing_question():
    result = answer_customer_with_knowledge(
        "How much does your chatbot cost?"
    )

    assert "scope of the project" in result.lower() or "project scope" in result.lower()
    assert "integrations" in result.lower()
    assert "complexity" in result.lower()
    assert "maintenance" in result.lower()
    assert "sales team" in result.lower()

def test_unknown_question_returns_fallback():
    result = answer_customer_with_knowledge(
        "Can you build a spaceship?"
    )

    assert result == (
        "I don't have enough company information to answer that question."
    )

def test_answer_multi_intent_question():
    result = answer_customer_with_knowledge(
        "How much does your chatbot cost for a hospital?"
    )

    assert "estimate" in result.lower()
    assert "scope of the project" in result.lower() or "project scope" in result.lower()
    assert "privacy" in result.lower()
    assert "security" in result.lower()
    assert "regulatory" in result.lower()