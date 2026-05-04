"""Caso de uso: aprobar una Approval. Avanza el estado según política."""

from uuid import UUID

from app.application.commands import CommandResult
from app.application.services.event_bus import EventBus
from app.application.use_cases.submit_request import SubmitRequestUseCase, _role_for_area
from app.domain.entities import Approval, Decision
from app.domain.enums import ApprovalArea, DecisionAction, RequestStatus, Role
from app.domain.events import (
    OpsReviewRequired,
    RequestApproved,
    ReviewerAssigned,
    SecurityReviewRequired,
)
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


class ApproveRequestUseCase:
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

    def run(self, approval_id: UUID, reviewer_id: UUID) -> CommandResult:
        approval = self.approval_repo.get_by_id(approval_id)
        if approval is None:
            return CommandResult(success=False, message="Approval no encontrada.")

        if approval.reviewer_id != reviewer_id:
            return CommandResult(
                success=False,
                message="No autorizado: la approval pertenece a otro reviewer.",
            )

        # Validar que el rol del reviewer cubre el área de la approval
        reviewer = self.user_repo.get_by_id(str(reviewer_id))
        if reviewer is None or not _role_covers_area(reviewer.role, approval.area):
            return CommandResult(
                success=False,
                message=(
                    f"No autorizado: el área {approval.area.value} requiere un "
                    f"rol distinto al actual."
                ),
            )

        try:
            approval.mark_approved()
        except ValueError as e:
            return CommandResult(success=False, message=str(e))

        self.approval_repo.save(approval)
        self.approval_repo.save_decision(
            Decision(approval_id=approval.id, action=DecisionAction.APPROVE)
        )

        cr = self.request_repo.get_by_id(approval.request_id)
        if cr is None:
            return CommandResult(success=False, message="Solicitud no encontrada.")

        approved_areas = self.approval_repo.approved_areas_for_request(approval.request_id)
        state = state_from_status(cr.status)
        ctx = ChangeRequestContext(
            risk_level=cr.risk_level,
            has_rollback_plan=cr.has_rollback_plan(),
            approved_areas=approved_areas,
            approving_area=approval.area,
        )
        try:
            new_state = state.approve(ctx)
        except (InvalidStateTransitionError, BusinessRuleViolationError) as e:
            return CommandResult(success=False, message=str(e))

        self.request_repo.update_status(approval.request_id, new_state.status)

        self._emit_post_approval_events(cr, approval, new_state.status, approved_areas)

        return CommandResult(
            success=True,
            message=f"Aprobación registrada. Estado actual: {new_state.status.value}.",
            data={"new_status": new_state.status.value},
        )

    def _emit_post_approval_events(
        self,
        cr,
        approval: Approval,
        new_status: RequestStatus,
        approved_areas: set[ApprovalArea],
    ) -> None:
        if new_status == RequestStatus.OPS_REVIEW:
            new_approval = self._auto_assign(cr.id, ApprovalArea.OPS)
            self.event_bus.publish(OpsReviewRequired(
                request_id=cr.id,
                requester_id=cr.requester_id,
                title=cr.title,
            ))
            if new_approval is not None:
                self.event_bus.publish(ReviewerAssigned(
                    request_id=cr.id,
                    reviewer_id=new_approval.reviewer_id,
                    approval_id=new_approval.id,
                    area=ApprovalArea.OPS.value,
                ))
        elif new_status == RequestStatus.SECURITY_REVIEW:
            new_approval = self._auto_assign(cr.id, ApprovalArea.SECURITY)
            self.event_bus.publish(SecurityReviewRequired(
                request_id=cr.id,
                requester_id=cr.requester_id,
                title=cr.title,
            ))
            if new_approval is not None:
                self.event_bus.publish(ReviewerAssigned(
                    request_id=cr.id,
                    reviewer_id=new_approval.reviewer_id,
                    approval_id=new_approval.id,
                    area=ApprovalArea.SECURITY.value,
                ))
        elif new_status == RequestStatus.APPROVED:
            self.event_bus.publish(RequestApproved(
                request_id=cr.id,
                requester_id=cr.requester_id,
                reviewer_id=approval.reviewer_id,
                approval_id=approval.id,
            ))

    def _auto_assign(self, request_id: UUID, area: ApprovalArea) -> Approval | None:
        existing = [
            a for a in self.approval_repo.list_by_request(request_id)
            if a.area == area and a.is_pending()
        ]
        if existing:
            return existing[0]
        reviewer = self.user_repo.first_by_role(_role_for_area(area))
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


def _role_covers_area(role: Role, area: ApprovalArea) -> bool:
    if role == Role.ADMIN:
        return True
    return {
        ApprovalArea.TECH: role == Role.TECH_LEAD,
        ApprovalArea.OPS: role == Role.OPS_REVIEWER,
        ApprovalArea.SECURITY: role == Role.SECURITY_REVIEWER,
    }[area]
