from dataclasses import dataclass
from uuid import UUID

from app.domain.enums import ChangeStatus, RiskLevel


@dataclass
class CreateChangeRequestInput:
    title: str
    description: str
    affected_system: str
    risk_level: RiskLevel
    requester_id: UUID


@dataclass
class ChangeRequestOutput:
    id: UUID
    title: str
    description: str
    affected_system: str
    risk_level: RiskLevel
    status: ChangeStatus
    requester_id: UUID