"""DTOs (Pydantic schemas) de entrada y salida de la API."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums import ApprovalStatus, RequestStatus, RiskLevel


class CreateChangeRequestPayload(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    affected_system: str = Field(..., min_length=1)
    risk_level: RiskLevel
    requester_id: UUID
    rollback_plan: Optional[str] = None


class ChangeRequestView(BaseModel):
    id: UUID
    title: str
    description: str
    affected_system: str
    risk_level: RiskLevel
    status: RequestStatus
    requester_id: UUID
    rollback_plan: Optional[str] = None
    failure_reason: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None


class AssignReviewerRequest(BaseModel):
    reviewer_id: UUID


class RejectRequest(BaseModel):
    comment: str = Field(..., min_length=1)


class RequestChangesRequest(BaseModel):
    comment: str = Field(..., min_length=1)


class ScheduleRequest(BaseModel):
    scheduled_at: datetime


class FailRequest(BaseModel):
    reason: str = Field(..., min_length=1)


class ApprovalResponse(BaseModel):
    id: UUID
    request_id: UUID
    reviewer_id: UUID
    area: str
    status: ApprovalStatus
    created_at: datetime
    decided_at: Optional[datetime]


class ActionResponse(BaseModel):
    success: bool
    message: str
    new_status: Optional[str] = None


class NotificationResponse(BaseModel):
    id: UUID
    user_id: str
    message: str
    event_type: str
    read: bool
    created_at: datetime


class AuditEntryResponse(BaseModel):
    id: UUID
    actor_id: str
    action: str
    entity_type: str
    entity_id: str
    detail: Optional[str]
    occurred_at: datetime
