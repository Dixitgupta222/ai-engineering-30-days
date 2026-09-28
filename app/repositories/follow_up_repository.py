from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.models.follow_up import FollowUpDB, LeadDB


def create_follow_up(db: Session, follow_up: FollowUpDB):
    try:    
        db.add(follow_up)
        db.commit()
        db.refresh(follow_up)
    except SQLAlchemyError:
        db.rollback()
        raise

    return follow_up

def get_follow_ups(
    db: Session,
    lead_id: int,
    skip: int,
    limit: int
):
    query = (
        db.query(FollowUpDB)
        .filter(FollowUpDB.lead_id == lead_id)
        .order_by(FollowUpDB.created_at.desc())
    )

    total = query.count()

    items = (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "items": items
    }

def get_follow_up_by_id(
    db: Session,
    lead_id: int,
    follow_up_id: int
):
    follow_up = (
        db.query(FollowUpDB)
        .filter(
            FollowUpDB.id == follow_up_id,
            FollowUpDB.lead_id == lead_id
        )
        .first()
    )

    if not follow_up:
        raise ValueError("Follow-up not found")

    return follow_up

def delete_follow_up(db: Session, follow_up: FollowUpDB):
    try:
        db.delete(follow_up)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return True


def get_follow_up_by_id_only(
    db: Session,
    follow_up_id: int
):
    follow_up = (
        db.query(FollowUpDB)
        .filter(FollowUpDB.id == follow_up_id)
        .first()
    )

    if not follow_up:
        raise ValueError("Follow-up not found")

    return follow_up

def get_lead_with_follow_ups(
    db: Session,
    lead_id: int
):
    lead = (
        db.query(LeadDB)
        .options(joinedload(LeadDB.follow_ups))
        .filter(LeadDB.id == lead_id)
        .first()
    )
    if not lead:
        raise ValueError("Lead not found")

    return lead


    