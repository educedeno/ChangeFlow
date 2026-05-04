from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from app.domain.enums import (
    ApprovalArea,
    ApprovalStatus,
    DecisionAction,
    Permission,
    RequestStatus,
    RiskLevel,
    Role,
)
from app.domain.value_objects import ROLE_PERMISSIONS


@dataclass
class ChangeRequest:
    title: str
    description: str
    affected_system: str
    risk_level: RiskLevel
    requester_id: UUID
    id: UUID = field(default_factory=uuid4)
    status: RequestStatus = RequestStatus.DRAFT
    rollback_plan: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("title is required")
        if not self.description.strip():
            raise ValueError("description is required")
        if not self.affected_system.strip():
            raise ValueError("affected_system is required")
        if not isinstance(self.risk_level, RiskLevel):
            raise ValueError("risk_level must be a valid RiskLevel")
        if not isinstance(self.status, RequestStatus):
            raise ValueError("status must be a valid RequestStatus")

    def has_rollback_plan(self) -> bool:
        return bool(self.rollback_plan and self.rollback_plan.strip())


@dataclass
class User:
    id: str
    name: str
    email: str
    hashed_password: str
    role: Role
    is_active: bool = True
    permissions: list[Permission] = field(default_factory=list)

    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions


class UserFactory:
    @staticmethod
    def create(
        id: str,
        name: str,
        email: str,
        hashed_password: str,
        role: Role,
        is_active: bool = True,
    ) -> "User":
        permissions = ROLE_PERMISSIONS.get(role, [])
        return User(
            id=id,
            name=name,
            email=email,
            hashed_password=hashed_password,
            role=role,
            is_active=is_active,
            permissions=permissions,
        )


@dataclass
class Approval:
    """Aprobación asignada a un reviewer para un área concreta de revisión."""
    request_id: UUID
    reviewer_id: UUID
    area: ApprovalArea
    id: UUID = field(default_factory=uuid4)
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    decided_at: Optional[datetime] = None

    def is_pending(self) -> bool:
        return self.status == ApprovalStatus.PENDING

    def mark_approved(self) -> None:
        if not self.is_pending():
            raise ValueError(
                f"No se puede aprobar una Approval con estado {self.status.value}"
            )
        self.status = ApprovalStatus.APPROVED
        self.decided_at = datetime.utcnow()

    def mark_rejected(self) -> None:
        if not self.is_pending():
            raise ValueError(
                f"No se puede rechazar una Approval con estado {self.status.value}"
            )
        self.status = ApprovalStatus.REJECTED
        self.decided_at = datetime.utcnow()


@dataclass
class Decision:
    approval_id: UUID
    action: DecisionAction
    id: UUID = field(default_factory=uuid4)
    comment: Optional[str] = None
    decided_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.action in (DecisionAction.REJECT, DecisionAction.REQUEST_CHANGES):
            if not self.comment or not self.comment.strip():
                raise ValueError(
                    f"La acción {self.action.value} requiere un comentario."
                )


@dataclass
class Notification:
    user_id: str
    message: str
    event_type: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    read: bool = False

    def mark_read(self) -> None:
        self.read = True


@dataclass
class AuditEntry:
    actor_id: str
    action: str
    entity_type: str
    entity_id: str
    id: UUID = field(default_factory=uuid4)
    detail: Optional[str] = None
    occurred_at: datetime = field(default_factory=datetime.utcnow)
