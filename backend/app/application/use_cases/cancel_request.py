"""Caso de uso: cancelar una solicitud antes de su aprobación final."""

from uuid import UUID

from app.application.commands import CommandResult
from app.application.services.event_bus import EventBus
from app.domain.enums import Role
from app.domain.events import RequestCancelled
from app.domain.exceptions import (
    BusinessRuleViolationError,
    InvalidStateTransitionError,
)
from app.domain.repositories import ChangeRequestRepository
from app.domain.state_machine import (
    ChangeRequestContext,
    state_from_status,
)
from app.infrastructure.repositories.user_repository import UserRepository


class CancelRequestUseCase:
    """Solo el solicitante o un Admin pueden cancelar antes de aprobación."""

    def __init__(
        self,
        request_repo: ChangeRequestRepository,
        event_bus: EventBus | None = None,
        user_repo: UserRepository | None = None,
    ):
        self.request_repo = request_repo
        self.event_bus = event_bus or EventBus()
        self.user_repo = user_repo or UserRepository()

    def run(self, request_id: UUID, actor_id: UUID) -> CommandResult:
        cr = self.request_repo.get_by_id(request_id)
        if cr is None:
            return CommandResult(success=False, message="Solicitud no encontrada.")

        actor = self.user_repo.get_by_id(str(actor_id))
        is_admin = actor is not None and actor.role == Role.ADMIN
        is_requester = cr.requester_id == actor_id
        if not (is_admin or is_requester):
            return CommandResult(
                success=False,
                message="No autorizado: solo el solicitante o un Admin pueden cancelar.",
            )

        state = state_from_status(cr.status)
        ctx = ChangeRequestContext(risk_level=cr.risk_level)
        try:
            new_state = state.cancel(ctx)
        except (InvalidStateTransitionError, BusinessRuleViolationError) as e:
            return CommandResult(success=False, message=str(e))

        self.request_repo.update_status(request_id, new_state.status)

        self.event_bus.publish(RequestCancelled(
            request_id=request_id,
            requester_id=cr.requester_id,
            actor_id=actor_id,
        ))

        return CommandResult(
            success=True,
            message="Solicitud cancelada.",
            data={"new_status": new_state.status.value},
        )
