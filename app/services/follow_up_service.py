from sqlalchemy.orm import Session

from app.models.follow_up import FollowUpDB
from app.repositories.follow_up_repository import (
    create_follow_up,
    delete_follow_up,
    get_follow_up_by_id,
    get_follow_up_by_id_only,
    get_follow_ups,
    get_lead_with_follow_ups,
)
from app.repositories.lead_repository import get_lead_by_id


def create_follow_up_service(
    db: Session,
    lead_id: int,
    message: str
):
    get_lead_by_id(db, lead_id)
    
    follow_up = FollowUpDB(
        lead_id=lead_id,
        message=message
    )

    return create_follow_up(db, follow_up)

def get_follow_ups_service(
    db: Session,
    lead_id: int,
    skip: int,
    limit: int
):
    get_lead_by_id(db, lead_id)

    result = get_follow_ups(
        db,
        lead_id,
        skip,
        limit
    )

    return {
        "total": result["total"],
        "skip": skip,
        "limit": limit,
        "items": result["items"]
    }

def delete_follow_up_service(
    db: Session,
    lead_id: int,
    follow_up_id: int
):
    follow_up = get_follow_up_by_id(
        db,
        lead_id,
        follow_up_id
    )

    delete_follow_up(db, follow_up)

    return {
        "message": "Follow-up deleted successfully"
    }

def get_follow_up_by_id_service(
    db: Session,
    follow_up_id: int
):
    follow_up = get_follow_up_by_id_only(
        db,
        follow_up_id
    )
    return {
        "follow_up_id": follow_up.id,
        "message": follow_up.message,
        "lead_name": follow_up.lead.name,
        "lead_company": follow_up.lead.company,
        "lead_score": follow_up.lead.score
    }

def get_lead_with_follow_ups_service(
    db: Session,
    lead_id: int
):
    lead = get_lead_with_follow_ups(
        db,
        lead_id
    )
    return lead