from unittest.mock import Mock, patch

from app.schemas.llm_schema import LeadMessageAnalysis
from app.services.llm_service import analyze_lead_message_structured


mock_analysis = LeadMessageAnalysis(
    business_need="AI chatbot",
    urgency="high",
    budget_mentioned=True,
    sentiment="positive",
    summary="Customer urgently needs an AI chatbot.",
)

mock_response = Mock()
mock_response.output_parsed = mock_analysis

with patch(
    "app.services.llm_service.client.responses.parse",
    return_value=mock_response,
) as mock_parse:
    result = analyze_lead_message_structured(
        "We urgently need an AI chatbot with a budget."
    )

    assert result.business_need == "AI chatbot"
    assert result.urgency == "high"
    assert result.budget_mentioned is True
    assert result.sentiment == "positive"
    assert mock_parse.call_count == 1

    print(result.model_dump())
    print("Structured LLM mock test passed!")