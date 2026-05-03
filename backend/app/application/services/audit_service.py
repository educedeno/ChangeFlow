from typing import Protocol

from app.domain.entities import AuditEntry
from app.domain.events import (
    ChangesRequested,
    RequestApproved,
    RequestCreated,
    RequestRejected,
    RequestSubmitted,
    ReviewerAssigned,
    UserCreated,
)


class AuditRepository(Protocol):
    def save(self, entry: AuditEntry) -> None: ...


class AuditService:
    """Suscriptor del EventBus que registra AuditEntries ante eventos de dominio."""

    def __init__(self, audit_repo: AuditRepository) -> None:
        self._repo = audit_repo

    def on_user_created(self, event: UserCreated) -> None:
        self._repo.save(AuditEntry(
            actor_id=event.user_id,
            action="USER_CREATED",
            entity_type="User",
            entity_id=event.user_id,
            detail=f"role={event.role}",
        ))

    def on_request_created(self, event: RequestCreated) -> None:
        self._repo.save(AuditEntry(
            actor_id=str(event.requester_id),
            action="REQUEST_CREATED",
            entity_type="ChangeRequest",
            entity_id=str(event.request_id),
            detail=f"risk={event.risk_level}",
        ))

    def on_request_submitted(self, event: RequestSubmitted) -> None:
        self._repo.save(AuditEntry(
            actor_id=str(event.requester_id),
            action="REQUEST_SUBMITTED",
            entity_type="ChangeRequest",
            entity_id=str(event.request_id),
        ))

    def on_request_approved(self, event: RequestApproved) -> None:
        self._repo.save(AuditEntry(
            actor_id=str(event.reviewer_id),
            action="REQUEST_APPROVED",
            entity_type="ChangeRequest",
            entity_id=str(event.request_id),
            detail=f"approval_id={event.approval_id}",
        ))

    def on_request_rejected(self, event: RequestRejected) -> None:
        self._repo.save(AuditEntry(
            actor_id=str(event.reviewer_id),
            action="REQUEST_REJECTED",
            entity_type="ChangeRequest",
            entity_id=str(event.request_id),
            detail=event.comment,
        ))

    def on_reviewer_assigned(self, event: ReviewerAssigned) -> None:
        self._repo.save(AuditEntry(
            actor_id=str(event.reviewer_id),
            action="REVIEWER_ASSIGNED",
            entity_type="ChangeRequest",
            entity_id=str(event.request_id),
            detail=f"approval_id={event.approval_id}",
        ))

    def on_changes_requested(self, event: ChangesRequested) -> None:
        self._repo.save(AuditEntry(
            actor_id=str(event.reviewer_id),
            action="CHANGES_REQUESTED",
            entity_type="ChangeRequest",
            entity_id=str(event.request_id),
            detail=event.comment,
        ))
