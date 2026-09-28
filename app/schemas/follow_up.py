from sqlalchemy.orm import Session

from app.models.follow_up import FollowUpDB
from app.repositories.follow_up_repository import create_follow_up


def create_follow_up_service(
    db: Session,
    lead_id: int,
    message: str
):
    follow_up = FollowUpDB(
        lead_id=lead_id,
        message=message
    )

    return create_follow_up(db, follow_up)