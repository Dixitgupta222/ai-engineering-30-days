from app.schemas.llm_schema import LeadMessageAnalysis

analysis = LeadMessageAnalysis(
    business_need="AI chatbot",
    urgency="high",
    budget_mentioned=True,
    sentiment="positive",
    summary="Customer urgently needs an AI chatbot.",
)

print(analysis.model_dump())
print("Schema validation successful!")