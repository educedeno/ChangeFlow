"""Caso de uso: aprobar una solicitud de cambio."""

from uuid import UUID

from app.application.commands import CommandResult
from app.domain.enums import DecisionAction, RequestStatus
from app.domain.entities import Decision
from app.domain.exceptions import (
    BusinessRuleViolationError,
    InvalidStateTransitionError,
)
from app.domain.policies import policy_for
from app.domain.repositories import ApprovalRepository, ChangeRequestRepository
from app.domain.state_machine import (
    ChangeRequestContext,
    state_from_status,
)


class ApproveRequestUseCase:
    """
    Marca una Approval como aprobada y, si la policy lo permite,
    transiciona la solicitud principal a APPROVED.
    """

    def __init__(
        self,
        approval_repo: ApprovalRepository,
        request_repo: ChangeRequestRepository,
    ):
        self.approval_repo = approval_repo
        self.request_repo = request_repo

    def run(self, approval_id: UUID, reviewer_id: UUID) -> CommandResult:
        approval = self.approval_repo.get_by_id(approval_id)
        if approval is None:
            return CommandResult(success=False, message="Approval no encontrada.")

        if approval.reviewer_id != reviewer_id:
            return CommandResult(
                success=False,
                message="No autorizado: la approval pertenece a otro reviewer.",
            )

        try:
            approval.mark_approved()
        except ValueError as e:
            return CommandResult(success=False, message=str(e))

        self.approval_repo.save(approval)
        self.approval_repo.save_decision(
            Decision(approval_id=approval.id, action=DecisionAction.APPROVE)
        )

        # ¿Se cumple la policy para transicionar la solicitud completa?
        risk_level = self.request_repo.get_risk_level(approval.request_id)
        policy = policy_for(risk_level)
        approved_count = self.approval_repo.count_approved_for_request(
            approval.request_id
        )

        if policy.is_satisfied(approved_count):
            current_status = self.request_repo.get_status(approval.request_id)
            state = state_from_status(current_status)
            ctx = ChangeRequestContext(
                risk_level=risk_level,
                approvals_count=approved_count,
            )
            try:
                new_state = state.approve(ctx)
                self.request_repo.update_status(
                    approval.request_id, new_state.status
                )
                return CommandResult(
                    success=True,
                    message="Solicitud aprobada completamente.",
                    data={"new_status": new_state.status.value},
                )
            except (InvalidStateTransitionError, BusinessRuleViolationError) as e:
                return CommandResult(success=False, message=str(e))

        return CommandResult(
            success=True,
            message=(
                f"Aprobación registrada. Faltan "
                f"{policy.required_approvals() - approved_count} "
                f"aprobación(es) más."
            ),
        )