from app.core.database import Base, engine
from app.models.lead import LeadDB
from app.models.follow_up import FollowUpDB

# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

print("Database tables created successfully")