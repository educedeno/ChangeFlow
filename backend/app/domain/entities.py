from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from app.domain.enums import ChangeStatus, RiskLevel


@dataclass
class ChangeRequest:
    title: str
    description: str
    affected_system: str
    risk_level: RiskLevel
    requester_id: UUID
    id: UUID = field(default_factory=uuid4)
    status: ChangeStatus = ChangeStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)
    scheduled_at: datetime | None = None
    executed_at: datetime | None = None
    failure_reason: str | None = None

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("title is required")
        if not self.description.strip():
            raise ValueError("description is required")
        if not self.affected_system.strip():
            raise ValueError("affected_system is required")
        if not isinstance(self.risk_level, RiskLevel):
            raise ValueError("risk_level must be a valid RiskLevel")
        if not isinstance(self.status, ChangeStatus):
            raise ValueError("status must be a valid ChangeStatus")
    
    def submit(self) -> None:
    if self.status != ChangeStatus.DRAFT:
        raise ValueError("Only draft requests can be submitted")
    self.status = ChangeStatus.SUBMITTED
from domain.enums import Role, Permission
from domain.value_objects import ROLE_PERMISSIONS

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
    ) -> User:
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
