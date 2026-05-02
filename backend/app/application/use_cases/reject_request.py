"""Caso de uso: rechazar una solicitud de cambio."""

from uuid import UUID

from app.application.commands import CommandResult
from app.domain.enums import DecisionAction
from app.domain.entities import Decision
from app.domain.exceptions import (
    BusinessRuleViolationError,
    InvalidStateTransitionError,
)
from app.domain.repositories import ApprovalRepository, ChangeRequestRepository
from app.domain.state_machine import (
    ChangeRequestContext,
    state_from_status,
)


class RejectRequestUseCase:
    """
    Marca una Approval como rechazada y transiciona la solicitud completa
    a REJECTED. Un único rechazo es suficiente para tumbar la solicitud.
    """

    def __init__(
        self,
        approval_repo: ApprovalRepository,
        request_repo: ChangeRequestRepository,
    ):
        self.approval_repo = approval_repo
        self.request_repo = request_repo

    def run(
        self, approval_id: UUID, reviewer_id: UUID, comment: str
    ) -> CommandResult:
        if not comment or not comment.strip():
            return CommandResult(
                success=False, message="El rechazo requiere un comentario."
            )

        approval = self.approval_repo.get_by_id(approval_id)
        if approval is None:
            return CommandResult(success=False, message="Approval no encontrada.")

        if approval.reviewer_id != reviewer_id:
            return CommandResult(
                success=False,
                message="No autorizado: la approval pertenece a otro reviewer.",
            )

        try:
            approval.mark_rejected()
        except ValueError as e:
            return CommandResult(success=False, message=str(e))

        self.approval_repo.save(approval)
        self.approval_repo.save_decision(
            Decision(
                approval_id=approval.id,
                action=DecisionAction.REJECT,
                comment=comment,
            )
        )

        # Tumbar la solicitud completa
        current_status = self.request_repo.get_status(approval.request_id)
        risk_level = self.request_repo.get_risk_level(approval.request_id)
        state = state_from_status(current_status)
        ctx = ChangeRequestContext(risk_level=risk_level)

        try:
            new_state = state.reject(ctx)
            self.request_repo.update_status(approval.request_id, new_state.status)
            return CommandResult(
                success=True,
                message="Solicitud rechazada.",
                data={"new_status": new_state.status.value},
            )
        except (InvalidStateTransitionError, BusinessRuleViolationError) as e:
            return CommandResult(success=False, message=str(e))