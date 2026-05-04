from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.domain.enums import RequestStatus, RiskLevel


@dataclass
class CreateChangeRequestInput:
    title: str
    description: str
    affected_system: str
    risk_level: RiskLevel
    requester_id: UUID
    rollback_plan: Optional[str] = None


@dataclass
class ChangeRequestOutput:
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
