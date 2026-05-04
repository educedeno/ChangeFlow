from typing import Protocol

from app.domain.entities import AuditEntry
from app.domain.events import (
    ChangesRequested,
    OpsReviewRequired,
    RequestApproved,
    RequestCancelled,
    RequestCreated,
    RequestExecuted,
    RequestFailed,
    RequestRejected,
    RequestScheduled,
    RequestSubmitted,
    ReviewerAssigned,
    SecurityReviewRequired,
    TechReviewRequired,
    UserCreated,
)


class AuditRepository(Protocol):
    def save(self, entry: AuditEntry) -> None: ...


class AuditService:
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

    def on_tech_review_required(self, event: TechReviewRequired) -> None:
        self._repo.save(AuditEntry(
            actor_id=str(event.requester_id),
            action="TECH_REVIEW_REQUIRED",
            entity_type="ChangeRequest",
            entity_id=str(event.request_id),
        ))

    def on_ops_review_required(self, event: OpsReviewRequired) -> None:
        self._repo.save(AuditEntry(
            actor_id=str(event.requester_id),
            action="OPS_REVIEW_REQUIRED",
            entity_type="ChangeRequest",
            entity_id=str(event.request_id),
        ))

    def on_security_review_required(self, event: SecurityReviewRequired) -> None:
        self._repo.save(AuditEntry(
            actor_id=str(event.requester_id),
            action="SECURITY_REVIEW_REQUIRED",
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
            detail=f"area={event.area} approval_id={event.approval_id}",
        ))

    def on_changes_requested(self, event: ChangesRequested) -> None:
        self._repo.save(AuditEntry(
            actor_id=str(event.reviewer_id),
            action="CHANGES_REQUESTED",
            entity_type="ChangeRequest",
            entity_id=str(event.request_id),
            detail=event.comment,
        ))

    def on_request_scheduled(self, event: RequestScheduled) -> None:
        self._repo.save(AuditEntry(
            actor_id=str(event.requester_id),
            action="CHANGE_SCHEDULED",
            entity_type="ChangeRequest",
            entity_id=str(event.request_id),
            detail=f"scheduled_at={event.scheduled_at}",
        ))

    def on_request_executed(self, event: RequestExecuted) -> None:
        self._repo.save(AuditEntry(
            actor_id=str(event.requester_id),
            action="CHANGE_EXECUTED",
            entity_type="ChangeRequest",
            entity_id=str(event.request_id),
        ))

    def on_request_failed(self, event: RequestFailed) -> None:
        self._repo.save(AuditEntry(
            actor_id=str(event.requester_id),
            action="CHANGE_FAILED",
            entity_type="ChangeRequest",
            entity_id=str(event.request_id),
            detail=event.reason,
        ))

    def on_request_cancelled(self, event: RequestCancelled) -> None:
        self._repo.save(AuditEntry(
            actor_id=str(event.actor_id),
            action="REQUEST_CANCELLED",
            entity_type="ChangeRequest",
            entity_id=str(event.request_id),
        ))
