"""Caso de uso: enviar (submit) una solicitud DRAFT al flujo de aprobación."""

from uuid import UUID

from app.application.commands import CommandResult
from app.application.services.event_bus import EventBus
from app.domain.entities import Approval
from app.domain.enums import ApprovalArea, RequestStatus, Role
from app.domain.events import RequestSubmitted, ReviewerAssigned, TechReviewRequired
from app.domain.exceptions import (
    BusinessRuleViolationError,
    InvalidStateTransitionError,
)
from app.domain.repositories import ApprovalRepository, ChangeRequestRepository
from app.domain.state_machine import (
    ChangeRequestContext,
    state_from_status,
)
from app.infrastructure.repositories.user_repository import UserRepository


class SubmitRequestUseCase:
    """
    DRAFT/CHANGES_REQUESTED -> TECH_REVIEW. Crea automáticamente la primera
    aprobación pendiente (TECH) asignada al primer Tech Lead disponible.
    """

    def __init__(
        self,
        request_repo: ChangeRequestRepository,
        approval_repo: ApprovalRepository,
        event_bus: EventBus | None = None,
        user_repo: UserRepository | None = None,
    ):
        self.request_repo = request_repo
        self.approval_repo = approval_repo
        self.event_bus = event_bus or EventBus()
        self.user_repo = user_repo or UserRepository()

    def run(self, request_id: UUID, requester_id: UUID) -> CommandResult:
        cr = self.request_repo.get_by_id(request_id)
        if cr is None:
            return CommandResult(success=False, message="Solicitud no encontrada.")

        if cr.requester_id != requester_id:
            return CommandResult(
                success=False,
                message="No autorizado: solo el solicitante puede enviar la solicitud.",
            )

        state = state_from_status(cr.status)
        ctx = ChangeRequestContext(
            risk_level=cr.risk_level,
            has_rollback_plan=cr.has_rollback_plan(),
        )
        try:
            new_state = state.submit(ctx)
        except (InvalidStateTransitionError, BusinessRuleViolationError) as e:
            return CommandResult(success=False, message=str(e))

        self.request_repo.update_status(request_id, new_state.status)

        approval = self._ensure_pending_approval(request_id, ApprovalArea.TECH)

        self.event_bus.publish(RequestSubmitted(
            request_id=request_id,
            requester_id=cr.requester_id,
            title=cr.title,
            risk_level=cr.risk_level.value,
        ))
        self.event_bus.publish(TechReviewRequired(
            request_id=request_id,
            requester_id=cr.requester_id,
            title=cr.title,
        ))
        if approval is not None:
            self.event_bus.publish(ReviewerAssigned(
                request_id=request_id,
                reviewer_id=approval.reviewer_id,
                approval_id=approval.id,
                area=ApprovalArea.TECH.value,
            ))

        return CommandResult(
            success=True,
            message="Solicitud enviada al revisor técnico.",
            data={"new_status": new_state.status.value},
        )

    def _ensure_pending_approval(self, request_id: UUID, area: ApprovalArea) -> Approval | None:
        existing = [
            a for a in self.approval_repo.list_by_request(request_id)
            if a.area == area and a.is_pending()
        ]
        if existing:
            return existing[0]

        role = _role_for_area(area)
        reviewer = self.user_repo.first_by_role(role)
        if reviewer is None:
            return None
        try:
            reviewer_uuid = UUID(reviewer.id)
        except (ValueError, TypeError):
            return None
        approval = Approval(
            request_id=request_id,
            reviewer_id=reviewer_uuid,
            area=area,
        )
        return self.approval_repo.save(approval)


def _role_for_area(area: ApprovalArea) -> Role:
    if area == ApprovalArea.TECH:
        return Role.TECH_LEAD
    if area == ApprovalArea.OPS:
        return Role.OPS_REVIEWER
    if area == ApprovalArea.SECURITY:
        return Role.SECURITY_REVIEWER
    raise ValueError(f"Área desconocida: {area}")
