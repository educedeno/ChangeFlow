"""Caso de uso: solicitar cambios sobre una solicitud en revisión."""

from uuid import UUID

from app.application.commands import CommandResult
from app.application.services.event_bus import EventBus
from app.application.use_cases.approve_request import _role_covers_area
from app.domain.entities import Decision
from app.domain.enums import DecisionAction
from app.domain.events import ChangesRequested
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


class RequestChangesUseCase:
    def __init__(
        self,
        approval_repo: ApprovalRepository,
        request_repo: ChangeRequestRepository,
        event_bus: EventBus | None = None,
        user_repo: UserRepository | None = None,
    ):
        self.approval_repo = approval_repo
        self.request_repo = request_repo
        self.event_bus = event_bus or EventBus()
        self.user_repo = user_repo or UserRepository()

    def run(self, approval_id: UUID, reviewer_id: UUID, comment: str) -> CommandResult:
        if not comment or not comment.strip():
            return CommandResult(
                success=False, message="Solicitar cambios requiere un comentario."
            )

        approval = self.approval_repo.get_by_id(approval_id)
        if approval is None:
            return CommandResult(success=False, message="Approval no encontrada.")
        if approval.reviewer_id != reviewer_id:
            return CommandResult(
                success=False,
                message="No autorizado: la approval pertenece a otro reviewer.",
            )

        reviewer = self.user_repo.get_by_id(str(reviewer_id))
        if reviewer is None or not _role_covers_area(reviewer.role, approval.area):
            return CommandResult(success=False, message="No autorizado para esta área.")

        cr = self.request_repo.get_by_id(approval.request_id)
        if cr is None:
            return CommandResult(success=False, message="Solicitud no encontrada.")

        state = state_from_status(cr.status)
        ctx = ChangeRequestContext(risk_level=cr.risk_level)
        try:
            new_state = state.request_changes(ctx)
        except (InvalidStateTransitionError, BusinessRuleViolationError) as e:
            return CommandResult(success=False, message=str(e))

        self.approval_repo.save_decision(
            Decision(
                approval_id=approval.id,
                action=DecisionAction.REQUEST_CHANGES,
                comment=comment,
            )
        )
        self.request_repo.update_status(cr.id, new_state.status)

        self.event_bus.publish(ChangesRequested(
            request_id=cr.id,
            requester_id=cr.requester_id,
            reviewer_id=approval.reviewer_id,
            approval_id=approval.id,
            comment=comment,
        ))

        return CommandResult(
            success=True,
            message="Cambios solicitados al solicitante.",
            data={"new_status": new_state.status.value},
        )
