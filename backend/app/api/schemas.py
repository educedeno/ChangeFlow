"""DTOs (Pydantic schemas) de entrada y salida de la API."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums import ApprovalStatus


class AssignReviewerRequest(BaseModel):
    reviewer_id: UUID


class RejectRequest(BaseModel):
    comment: str = Field(..., min_length=1)


class ApprovalResponse(BaseModel):
    id: UUID
    request_id: UUID
    reviewer_id: UUID
    status: ApprovalStatus
    created_at: datetime
    decided_at: Optional[datetime]


class ActionResponse(BaseModel):
    success: bool
    message: str
    new_status: Optional[str] = None