from fastapi import FastAPI
from pydantic import BaseModel 
import os
from dotenv import load_dotenv
app = FastAPI(title="AI Lead Analyzer API")
load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")
print(APP_ENV)
class Lead(BaseModel):
    name: str
    company: str
    message: str
class LeadAnalysis(BaseModel):
    score: int
    priority: str
    recommendation: str
class LeadResponse(BaseModel):
    message: str
    lead: Lead
    analysis: LeadAnalysis
@app.get("/")
def home():
    return {
        "message": "AI Lead Analyzer API is running"
    }

@app.get("/about")
def about():
    return {
  "name": "Dixit",
  "role": "Aspiring AI Full Stack Engineer"
}

def calculate_score(message: str) -> int:
    message_lower = message.lower()
    score = 20
    if "ai" in message_lower:
        score += 20

    if "chatbot" in message_lower:
        score += 20

    if "urgent" in message_lower:
        score += 15

    if "budget" in message_lower:
        score += 15

    if "enterprise" in message_lower:
        score += 20

    return min(score, 100)

@app.post("/leads", response_model=LeadResponse)
def lead(lead: Lead):
    score = calculate_score(lead.message)
    if score >= 70:
        priority = "high"
        recommendation = "Contact sales immediately"
    elif score >= 40:
        priority = "medium"
        recommendation = "Follow up within 24 hours"
    else:
        priority = "low"
        recommendation = "Add to nurture campaign"
    return {
        "message": "Lead analyzed successfully",
        "lead": lead,
        "analysis": {
            "score": score,
            "priority": priority,
            "recommendation": recommendation,
        },
    }

