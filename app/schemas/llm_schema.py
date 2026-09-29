from typing import Literal

from pydantic import BaseModel, Field


class LeadMessageAnalysis(BaseModel):
    business_need: str = Field(
        description="The main product, service, or business need."
    )
    urgency: Literal["low", "medium", "high"] = Field(
        description="How urgently the customer needs a solution."
    )
    budget_mentioned: bool = Field(
        description="Whether the customer explicitly mentions a budget."
    )
    sentiment: Literal["positive", "neutral", "negative"] = Field(
        description="The customer's expressed sentiment."
    )
    summary: str = Field(
        description="A concise summary of the customer's message."
    )