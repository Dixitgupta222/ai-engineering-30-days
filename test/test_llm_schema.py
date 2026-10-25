import pytest
from pydantic import ValidationError

from app.schemas.llm_schema import LeadMessageAnalysis


def test_business_need_cannot_be_empty():
    with pytest.raises(ValidationError):
        LeadMessageAnalysis(
            business_need="     ",
            urgency="medium",
            budget_mentioned=True,
            sentiment="positive",
            summary="Customer wants an AI chatbot.",
        )

def test_business_need_trims_whitespace():
    result = LeadMessageAnalysis(
        business_need="   AI chatbot   ",
        urgency="medium",
        budget_mentioned=True,
        sentiment="positive",
        summary="Customer wants an AI chatbot.",
    )

    assert result.business_need == "AI chatbot"

def test_summary_trims_whitespace():
    result = LeadMessageAnalysis(
        business_need="AI chatbot",
        urgency="medium",
        budget_mentioned=True,
        sentiment="positive",
        summary="   Customer wants an AI chatbot.   ",
    )

    assert result.summary == "Customer wants an AI chatbot."