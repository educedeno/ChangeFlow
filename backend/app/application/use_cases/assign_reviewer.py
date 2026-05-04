"""Caso de uso: reasignar manualmente un reviewer (override del Admin)."""

from uuid import UUID

from app.application.commands import CommandResult
from app.application.services.event_bus import EventBus
from app.domain.entities import Approval
from app.domain.enums import ApprovalArea, ApprovalStatus, Role
from app.domain.events import ReviewerAssigned
from app.domain.repositories import ApprovalRepository, ChangeRequestRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.domain.value_objects import ROLE_TO_AREA


class AssignReviewerUseCase:
    """
    Asigna un reviewer concreto a una solicitud, infiriendo el área desde
    el rol del reviewer. Si ya existe una approval pendiente para esa área,
    cambia el reviewer asignado.
    """

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

    def run(self, request_id: UUID, reviewer_id: UUID) -> CommandResult:
        risk_level = self.request_repo.get_risk_level(request_id)
        if risk_level is None:
            return CommandResult(success=False, message="Solicitud no encontrada.")

        reviewer = self.user_repo.get_by_id(str(reviewer_id))
        if reviewer is None:
            return CommandResult(success=False, message="Reviewer no encontrado.")
        area = ROLE_TO_AREA.get(reviewer.role)
        if area is None:
            return CommandResult(
                success=False,
                message=f"El rol {reviewer.role.value} no puede ser asignado como reviewer.",
            )

        existing = self.approval_repo.list_by_request(request_id)
        for ap in existing:
            if ap.area == area and ap.status == ApprovalStatus.PENDING:
                ap.reviewer_id = reviewer_id
                self.approval_repo.save(ap)
                self.event_bus.publish(ReviewerAssigned(
                    request_id=request_id,
                    reviewer_id=reviewer_id,
                    approval_id=ap.id,
                    area=area.value,
                ))
                return CommandResult(
                    success=True,
                    message=f"Reviewer reasignado al área {area.value}.",
                    data={"approval_id": str(ap.id)},
                )

        approval = Approval(
            request_id=request_id,
            reviewer_id=reviewer_id,
            area=area,
        )
        saved = self.approval_repo.save(approval)
        self.event_bus.publish(ReviewerAssigned(
            request_id=request_id,
            reviewer_id=reviewer_id,
            approval_id=saved.id,
            area=area.value,
        ))
        return CommandResult(
            success=True,
            message="Reviewer asignado exitosamente.",
            data={"approval_id": str(saved.id)},
        )
