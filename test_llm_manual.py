
from unittest.mock import patch

from app.services.llm_service import analyze_lead_message


message = """
We run an e-commerce business and want to add an AI chatbot
to our website. We have a budget of $5,000 and want to
launch it as soon as possible.
"""

mocked_analysis = """
Business need: AI chatbot for an e-commerce website.
Intent: The customer wants to implement a chatbot.
Urgency: High, as they want to launch as soon as possible.
Budget: $5,000.
"""


if __name__ == "__main__":
    with patch(
        "app.services.llm_service.client.responses.create"
    ) as mock_create:

        mock_create.return_value.output_text = mocked_analysis

        result = analyze_lead_message(message)

        print("\nLLM Analysis:")
        print(result)

        mock_create.assert_called_once()

        print("\nTest passed: LLM service returned the mocked response.")