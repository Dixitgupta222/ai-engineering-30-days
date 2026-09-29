import logging

logger = logging.getLogger(__name__)

from openai import OpenAIError

from app.models.lead import LeadDB
from app.repositories.lead_repository import (
    delete_lead,
    get_lead_by_id,
    get_leads,
    patch_lead,
    save_lead,
    update_lead,
    update_lead_analysis,
)
from app.services.llm_service import analyze_lead_message

BASE_SCORE = 20
AI_SCORE = 20
CHATBOT_SCORE = 20
URGENT_SCORE = 15
BUDGET_SCORE = 15
ENTERPRISE_KEYWORD_SCORE = 20
DEMO_SCORE = 10
VERY_SMALL_COMPANY_SCORE = 0
SMALL_COMPANY_SCORE = 5
MEDIUM_COMPANY_SCORE = 10
LARGE_COMPANY_SCORE = 20
ENTERPRISE_COMPANY_SCORE = 30
def calculate_lead_score(message: str, company_size: int) -> int:
    message_lower = message.lower()
    score = BASE_SCORE

    if "ai" in message_lower:
        score += AI_SCORE

    if "chatbot" in message_lower or "chat bot" in message_lower:
        score += CHATBOT_SCORE

    if "urgent" in message_lower:
        score += URGENT_SCORE

    if "budget" in message_lower:
        score += BUDGET_SCORE

    if "enterprise" in message_lower:
        score += ENTERPRISE_KEYWORD_SCORE
   
    if "demo" in message_lower:
        score += DEMO_SCORE

    if company_size < 10:
     score += VERY_SMALL_COMPANY_SCORE

    elif company_size < 50:
        score += SMALL_COMPANY_SCORE

    elif company_size < 200:
        score += MEDIUM_COMPANY_SCORE

    elif company_size < 500:
        score += LARGE_COMPANY_SCORE

    else:
        score += ENTERPRISE_COMPANY_SCORE

    return min(score, 100)


def determine_priority(score: int) -> str:
    if score >= 70:
        return "high"
    elif score >= 40:
        return "medium"
    else:
        return "low"
        
def determine_recommendation(priority: str, company_size: int) -> str:
    if company_size >= 500:
        return "Assign to enterprise sales"
    elif priority == "high":
        return "Contact sales immediately"
    elif priority == "medium":
        return "Follow up within 24 hours"
    else:
        return "Add to nurture campaign"

def determine_contact(priority: str, company_size: int) -> str:
    if company_size >= 500 and priority in ("high", "medium"):
        return "Contact immediately"

    elif (
        priority == "medium"
        or company_size >= 150 and priority == "low"
        or priority == "high"
    ):
        return "followed up later"

    else:
        return "no contact"

def analyze_lead(message: str, company_size: int) -> dict:
    score = calculate_lead_score(message, company_size)
    priority = determine_priority(score)
    recommendation = determine_recommendation(priority, company_size)
    contact = determine_contact(priority, company_size)
    return {
        "score": score,
        "priority": priority,
        "recommendation": recommendation,
        "contact": contact,
    }


def create_lead_service(lead, db):
    try:
        # Existing rule-based analysis
        analysis = analyze_lead(
            lead.message,
            lead.company_size
        )

        # Additional AI analysis
        try:
            ai_analysis = analyze_lead_message(lead.message)
        except OpenAIError:
            logger.warning(
                "AI analysis unavailable; "
                "continuing with rule-based analysis."
            )
            ai_analysis = None

        analysis["ai_analysis"] = ai_analysis

        # Save the lead using existing database logic
        lead_db = LeadDB(
            name=lead.name,
            company=lead.company,
            company_size=lead.company_size,
            message=lead.message,
            score=analysis["score"],
            priority=analysis["priority"],
            recommendation=analysis["recommendation"],
        )

        saved_lead = save_lead(db, lead_db)

        logger.info(
            "Lead created successfully: id=%s, company=%s",
            saved_lead.id,
            saved_lead.company,
        )

        return {
            "lead": saved_lead,
            "analysis": analysis,
        }

    except Exception:
        logger.exception(
            "Failed to create lead: company=%s",
            lead.company,
        )
        raise

def get_leads_service(
    db,
    priority=None,
    skip=0,
    limit=10,
    sort_by="score",
    order="desc",
    search=None
):
    return get_leads(
        db=db,
        priority=priority,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        order=order,
        search=search,
    )

def get_lead_service_by_id(db, lead_id):
    return get_lead_by_id(db, lead_id)

def update_lead_service(db, lead_id, lead_data):
    lead = get_lead_by_id(db, lead_id)
    analysis = analyze_lead(
        lead_data.message,
        lead_data.company_size
    )
    lead = update_lead(
        db,
        lead,
        lead_data,
        analysis
    )
    return {
        "lead": lead,
        "analysis": analysis,
    }

def delete_lead_service(db, lead_id):
    lead = get_lead_by_id(db, lead_id)
    delete_lead(db, lead)
    return {
        "message": "Lead deleted successfully"
    }

def patch_lead_service(db, lead_id, lead_data):
    lead = get_lead_by_id(db, lead_id)
    should_recalculate = (
        lead_data.message is not None
        or lead_data.company_size is not None
    )
    if lead_data.name is not None:
        lead.name = lead_data.name
    if lead_data.company is not None:
        lead.company = lead_data.company
    if lead_data.message is not None:
        lead.message = lead_data.message
    if lead_data.company_size is not None:
        lead.company_size = lead_data.company_size
    if should_recalculate:
        analysis = analyze_lead(
            lead.message,
            lead.company_size
        )

        lead.score = analysis["score"]
        lead.priority = analysis["priority"]
        lead.recommendation = analysis["recommendation"]
    lead = patch_lead(db, lead)
    return lead

def update_lead_analysis_service(db, lead_id):
    lead = get_lead_by_id(db, lead_id)
    analysis = analyze_lead(
        lead.message,
        lead.company_size
    )
    lead = update_lead_analysis(
        db,
        lead,
        analysis
    )
    return {
        "lead": lead,
        "analysis": analysis,
    }
