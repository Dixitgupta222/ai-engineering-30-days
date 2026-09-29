import logging

from openai import OpenAI, OpenAIError

from app.schemas.llm_schema import LeadMessageAnalysis

logger = logging.getLogger(__name__)

client = OpenAI()


def analyze_lead_message(message: str) -> str:
    """
    Generate a plain-text analysis of a lead message.
    """
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            instructions=(
                "Analyze the customer's message and provide a concise "
                "business-focused summary."
            ),
            input=message,
        )

        return response.output_text

    except OpenAIError:
        logger.exception("OpenAI text analysis failed")
        raise


def analyze_lead_message_structured(
    message: str,
) -> LeadMessageAnalysis:
    """
    Analyze a lead message and return validated structured data.
    """
    try:
        response = client.responses.parse(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "Analyze the customer's message. Extract the main "
                        "business need, urgency, whether a budget is "
                        "explicitly mentioned, sentiment, and a concise "
                        "summary. Do not invent information that is not "
                        "present in the message."
                    ),
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
            text_format=LeadMessageAnalysis,
        )

        if response.output_parsed is None:
            raise ValueError("The AI returned no structured analysis.")

        return response.output_parsed

    except OpenAIError:
        logger.exception("OpenAI structured analysis failed")
        raise