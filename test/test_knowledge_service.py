
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

    assert "Pricing" in result
    assert "project-specific estimate" in result


def test_unknown_question_returns_fallback():
    result = answer_customer_with_knowledge(
        "Can you build a spaceship?"
    )

    assert result == (
        "I don't have enough company information to answer that question."
    )
