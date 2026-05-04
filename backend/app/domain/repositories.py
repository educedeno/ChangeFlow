"""Interfaces de repositorio (puertos del dominio)."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.domain.entities import Approval, ChangeRequest, Decision
from app.domain.enums import ApprovalArea, RequestStatus, RiskLevel


class ApprovalRepository(ABC):
    @abstractmethod
    def get_by_id(self, approval_id: UUID) -> Optional[Approval]: ...

    @abstractmethod
    def list_by_request(self, request_id: UUID) -> List[Approval]: ...

    @abstractmethod
    def list_pending_for_reviewer(self, reviewer_id: UUID) -> List[Approval]: ...

    @abstractmethod
    def save(self, approval: Approval) -> Approval: ...

    @abstractmethod
    def save_decision(self, decision: Decision) -> Decision: ...

    @abstractmethod
    def approved_areas_for_request(self, request_id: UUID) -> set[ApprovalArea]: ...


class ChangeRequestRepository(ABC):
    @abstractmethod
    def save(self, change_request: ChangeRequest) -> ChangeRequest: ...

    @abstractmethod
    def get_by_id(self, request_id: UUID) -> Optional[ChangeRequest]: ...

    @abstractmethod
    def get_all(self) -> List[ChangeRequest]: ...

    @abstractmethod
    def get_status(self, request_id: UUID) -> Optional[RequestStatus]: ...

    @abstractmethod
    def update_status(self, request_id: UUID, new_status: RequestStatus) -> None: ...

    @abstractmethod
    def get_risk_level(self, request_id: UUID) -> Optional[RiskLevel]: ...

    @abstractmethod
    def has_rollback_plan(self, request_id: UUID) -> bool: ...

    @abstractmethod
    def set_scheduled_at(self, request_id: UUID, scheduled_at: datetime) -> None: ...

    @abstractmethod
    def set_executed_at(self, request_id: UUID, executed_at: datetime) -> None: ...

    @abstractmethod
    def set_failure_reason(self, request_id: UUID, reason: str) -> None: ...
