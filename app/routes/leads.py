from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.lead import (
    Lead,
    LeadDBResponse,
    LeadListResponse,
    LeadPatch,
    LeadResponse,
    LeadUpdate,
)
from app.services.lead_service import (
    create_lead_service,
    delete_lead_service,
    get_lead_service_by_id,
    get_leads_service,
    patch_lead_service,
    update_lead_analysis_service,
    update_lead_service,
)

router = APIRouter()


@router.post("/leads", response_model=LeadResponse)
def create_lead(
    lead: Lead,
    db: Session = Depends(get_db)
    ):
    result = create_lead_service(lead, db)

    return {
        "message": "Lead analyzed successfully",
        **result,
    }

@router.get("/leads", response_model=LeadListResponse)
def get_leads(
   priority: str | None = None,   
   skip: int = Query(0, ge=0),
   limit: int = Query(10, ge=1, le=100),
   sort_by: str = Query("score"),
   order: str = Query("desc"),
   search: str | None = None,
   db: Session = Depends(get_db)):

    result = get_leads_service(
        db=db,
        priority=priority,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        order=order,
        search=search,
    )
    return result

@router.get("/leads/{lead_id}",response_model=LeadDBResponse)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):

    try:
        lead = get_lead_service_by_id(db, lead_id)
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )
    return lead


@router.delete("/leads/{lead_id}")
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    try:
        result = delete_lead_service(db, lead_id)
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    return result

@router.put("/leads/{lead_id}")
def update_lead(lead_id: int, lead_data: LeadUpdate, db: Session = Depends(get_db)):
    try:
        result = update_lead_service(db, lead_id, lead_data)
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )
    return {
        "message": "Lead updated successfully",
        **result
    }

@router.patch("/leads/{lead_id}", response_model=LeadDBResponse)
def patch_lead(
    lead_id: int,
    lead_data: LeadPatch,
    db: Session = Depends(get_db)
):
    try:
        result = patch_lead_service(db, lead_id, lead_data)
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )
    return result

# @router.post(
#     "/leads/{lead_id}/follow-ups",
#     response_model=FollowUpResponse
# )
# def create_follow_up(
#     lead_id: int,
#     follow_up_data: FollowUpCreate,
#     db: Session = Depends(get_db)
# ):
#     lead = db.query(LeadDB).filter(LeadDB.id == lead_id).first()

#     if not lead:
#         raise HTTPException(
#             status_code=404,
#             detail="Lead not found"
#         )

#     follow_up = FollowUpDB(
#         lead_id=lead_id,
#         message=follow_up_data.message
#     )

#     try:
#         db.add(follow_up)
#         db.commit()
#         db.refresh(follow_up)

#     except SQLAlchemyError:
#         db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail="Database error"
#         )

#     return follow_up

# @router.get(
#     "/leads/{lead_id}/follow-ups",
#     response_model=FollowUpListResponse
# )
# def get_follow_ups(
#     lead_id: int,
#     skip: int = Query(0, ge=0),
#     limit: int = Query(10, ge=1, le=100),
#     db: Session = Depends(get_db)
# ):
#     lead = db.query(LeadDB).filter(LeadDB.id == lead_id).first()

#     if not lead:
#         raise HTTPException(
#             status_code=404,
#             detail="Lead not found"
#         )
#     follow_ups_query = (
#         db.query(FollowUpDB)
#         .filter(FollowUpDB.lead_id == lead_id)
#         .order_by(FollowUpDB.created_at.desc())
#     )
#     total = follow_ups_query.count()
#     items = (
#         follow_ups_query
#         .offset(skip)
#         .limit(limit)
#         .all()
#     )
#     return {
#         "total": total,
#         "skip": skip,
#         "limit": limit,
#         "items": items
#     }

# @router.delete(
#     "/leads/{lead_id}/follow-ups/{follow_up_id}"
# )
# def delete_follow_ups(
#     lead_id: int,
#     follow_up_id: int,
#     db: Session = Depends(get_db)
# ):
#     lead = db.query(LeadDB).filter(LeadDB.id == lead_id).first()
#     if not lead:
#         raise HTTPException(
#             status_code=404,
#             detail="Lead not found"
#     )
#     follow_up = (
#         db.query(FollowUpDB)
#         .filter(
#             FollowUpDB.id == follow_up_id,
#             FollowUpDB.lead_id == lead_id
#         )
#         .first()
#     )
#     if not follow_up:
#         raise HTTPException(
#             status_code=404,
#             detail="Follow-up not found"
#         )
#     try:
#         db.delete(follow_up)
#         db.commit()

#     except SQLAlchemyError:
#         db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail="Database error"
#         )
#     return {
#         "message": "Follow-up deleted successfully"
#     }

# @router.get("/follow-ups/{follow_up_id}")
# def get_follow_up(
#     follow_up_id: int,
#     db: Session = Depends(get_db)
# ):
#     follow_up = (
#         db.query(FollowUpDB)
#         .filter(FollowUpDB.id == follow_up_id)
#         .first()
#     )

#     if not follow_up:
#         raise HTTPException(
#             status_code=404,
#             detail="Follow-up not found"
#         )

#     return {
#         "follow_up_id": follow_up.id,
#         "message": follow_up.message,
#         "lead_name": follow_up.lead.name,
#         "lead_company": follow_up.lead.company,
#         "lead_score": follow_up.lead.score
#     }

# @router.get(
#     "/leads/{lead_id}/with-follow-ups",
#     response_model=LeadWithFollowUpsResponse
# )
# def get_lead_with_follow_ups(
#     lead_id: int,
#     db: Session = Depends(get_db)
# ):
#     lead = (
#         db.query(LeadDB)
#         .options(joinedload(LeadDB.follow_ups))
#         .filter(LeadDB.id == lead_id)
#         .first()
#     )
#     if not lead:
#         raise HTTPException(
#             status_code=404,
#             detail="Lead not found"
#     )

#     return lead

@router.post("/leads/{lead_id}/reanalyze")
def reanalyze_lead(
        lead_id: int,
        db: Session = Depends(get_db)
):
    try:
        result = update_lead_analysis_service(db, lead_id)
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )
    return result