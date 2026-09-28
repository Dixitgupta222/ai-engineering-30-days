from sqlalchemy.exc import SQLAlchemyError

from app.models.lead import LeadDB


def save_lead(db,lead_db):
  try:
    db.add(lead_db)
    db.commit()
    db.refresh(lead_db)

  except SQLAlchemyError:
    db.rollback()
    raise

  return lead_db

def get_leads(
    db,
    priority=None,
    skip=0,
    limit=10,
    sort_by="score",
    order="desc",
    search=None
):
  query = db.query(LeadDB)
  if priority:
    query = query.filter(LeadDB.priority == priority)
  if search:
    search = search.strip()

    if search:
        search_pattern = f"%{search}%"

        query = query.filter(
            LeadDB.name.ilike(search_pattern)
            | LeadDB.company.ilike(search_pattern)
            | LeadDB.message.ilike(search_pattern)
        )
  allowed_sort_fields = {
    "score": LeadDB.score,
    "company_size": LeadDB.company_size,
  }

  
  if sort_by not in allowed_sort_fields:
    raise ValueError("Invalid sort field")

  if order not in ["asc", "desc"]:
     raise ValueError("Order must be 'asc' or 'desc'")

  sort_column = allowed_sort_fields[sort_by]

  if order == "desc":
    query = query.order_by(sort_column.desc())
  else:
    query = query.order_by(sort_column.asc())

  total = query.count()
  items = query.offset(skip).limit(limit).all()
  return {
    "items": items,
    "total": total,
    "skip": skip,
    "limit": limit
  }

def get_lead_by_id(db, lead_id):
    lead_id = db.query(LeadDB).filter(LeadDB.id == lead_id).first()
    if not lead_id:
       raise ValueError("Lead not found")

    return lead_id

def update_lead(db, lead, lead_data,analysis):
    lead.name = lead_data.name
    lead.company = lead_data.company
    lead.company_size = lead_data.company_size
    lead.message = lead_data.message
    lead.score = analysis["score"]
    lead.priority = analysis["priority"]
    lead.recommendation = analysis["recommendation"]
    try:
        db.commit()
        db.refresh(lead)
    except SQLAlchemyError:
        db.rollback()
        raise
    return lead

def delete_lead(db, lead):
    try:
       db.delete(lead)
       db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

def patch_lead(db, lead):
    try:
        db.commit()
        db.refresh(lead)
    except SQLAlchemyError:
        db.rollback()
        raise
    return lead

def update_lead_analysis(db, lead, analysis):
    lead.score = analysis["score"]
    lead.priority = analysis["priority"]
    lead.recommendation = analysis["recommendation"]
    try:
        db.commit()
        db.refresh(lead)
    except SQLAlchemyError:
        db.rollback()
        raise
    return lead


  