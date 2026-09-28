from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.lead import (
    FollowUpCreate,
    FollowUpListResponse,
    FollowUpResponse,
    LeadWithFollowUpsResponse,
)
from app.services.follow_up_service import (
    create_follow_up_service,
    delete_follow_up_service,
    get_follow_up_by_id_service,
    get_follow_ups_service,
    get_lead_with_follow_ups_service,
)

router = APIRouter()


@router.post(
    "/leads/{lead_id}/follow-ups",
    response_model=FollowUpResponse
)
def create_follow_up(
    lead_id: int,
    follow_up_data: FollowUpCreate,
    db: Session = Depends(get_db)
):
    try:
        return create_follow_up_service(
            db,
            lead_id,
            follow_up_data.message
        )
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )


@router.get(
    "/leads/{lead_id}/follow-ups",
    response_model=FollowUpListResponse
)
def get_follow_ups(
    lead_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    try:
        return get_follow_ups_service(
            db,
            lead_id,
            skip,
            limit
        )
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

@router.delete(
    "/leads/{lead_id}/follow-ups/{follow_up_id}"
)
def delete_follow_ups(
    lead_id: int,
    follow_up_id: int,
    db: Session = Depends(get_db)
):

    try:
        return delete_follow_up_service(
            db,
            lead_id,
            follow_up_id
        )
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Follow-up not found"
        )

@router.get("/follow-ups/{follow_up_id}")
def get_follow_up(
    follow_up_id: int,
    db: Session = Depends(get_db)
):
    try:
        return get_follow_up_by_id_service(
            db,
            follow_up_id
        )
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="FollowUp not found"
        )


@router.get(
    "/leads/{lead_id}/with-follow-ups",
    response_model=LeadWithFollowUpsResponse
)
def get_lead_with_follow_ups(
    lead_id: int,
    db: Session = Depends(get_db)
):
    try:
        return get_lead_with_follow_ups_service(
            db,
            lead_id
        )
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )