from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import CheckConstraint, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.schemas.llm_schema import LeadMessageAnalysis

if TYPE_CHECKING:
    from app.models.follow_up import FollowUpDB

class Lead(BaseModel):
    name: str = Field(min_length=1)
    company: str = Field(min_length=1)
    message: str = Field(min_length=5)
    company_size: int = Field(ge=0)

class LeadAnalysis(BaseModel):
    score: int
    priority: str
    recommendation: str
    contact: str
    ai_analysis: str | None = None
    ai_details: LeadMessageAnalysis | None = None

class LeadDBResponse(BaseModel):
    id: int
    name: str
    company: str
    company_size: int
    message: str
    score: int
    priority: str
    recommendation: str
    model_config = ConfigDict(from_attributes=True)

class LeadResponse(BaseModel):
    message: str
    lead: LeadDBResponse
    analysis: LeadAnalysis


class LeadListResponse(BaseModel):
    items: list[LeadDBResponse]
    total: int
    skip: int
    limit: int

class LeadUpdate(BaseModel):
    name: str
    company: str
    message: str
    company_size: int

class LeadPatch(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1
    )

    company: str | None = Field(
        default=None,
        min_length=1
    )

    message: str | None = Field(
        default=None,
        min_length=5
    )

    company_size: int | None = Field(
        default=None,
        ge=0
    )

class FollowUpCreate(BaseModel):
    message: str = Field(min_length=1)

class FollowUpResponse(BaseModel):
    id: int
    lead_id: int
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FollowUpListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[FollowUpResponse]

class LeadWithFollowUpsResponse(BaseModel):
    id: int
    name: str
    company: str
    company_size: int
    message: str
    score: int
    priority: str
    recommendation: str
    follow_ups: list[FollowUpResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)



class LeadDB(Base):
    __tablename__ = "leads"
    __table_args__ = (
        CheckConstraint(
            "company_size >= 0",
            name="check_company_size_non_negative"
        ),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    company: Mapped[str] = mapped_column(String(150), nullable=False)
    company_size: Mapped[int] = mapped_column(Integer, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    follow_ups: Mapped[list["FollowUpDB"]] = relationship(
    "FollowUpDB",
    back_populates="lead",
    cascade="all, delete-orphan"
    )