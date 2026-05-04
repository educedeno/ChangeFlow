"""Caso de uso: agendar una solicitud aprobada."""

from datetime import datetime
from uuid import UUID

from app.application.commands import CommandResult
from app.application.services.event_bus import EventBus
from app.domain.events import RequestScheduled
from app.domain.exceptions import (
    BusinessRuleViolationError,
    InvalidStateTransitionError,
)
from app.domain.repositories import ChangeRequestRepository
from app.domain.state_machine import (
    ChangeRequestContext,
    state_from_status,
)


class ScheduleRequestUseCase:
    def __init__(
        self,
        request_repo: ChangeRequestRepository,
        event_bus: EventBus | None = None,
    ):
        self.request_repo = request_repo
        self.event_bus = event_bus or EventBus()

    def run(self, request_id: UUID, scheduled_at: datetime) -> CommandResult:
        cr = self.request_repo.get_by_id(request_id)
        if cr is None:
            return CommandResult(success=False, message="Solicitud no encontrada.")

        state = state_from_status(cr.status)
        ctx = ChangeRequestContext(risk_level=cr.risk_level)
        try:
            new_state = state.schedule(ctx)
        except (InvalidStateTransitionError, BusinessRuleViolationError) as e:
            return CommandResult(success=False, message=str(e))

        self.request_repo.set_scheduled_at(request_id, scheduled_at)
        self.request_repo.update_status(request_id, new_state.status)

        self.event_bus.publish(RequestScheduled(
            request_id=request_id,
            requester_id=cr.requester_id,
            scheduled_at=scheduled_at,
        ))

        return CommandResult(
            success=True,
            message="Solicitud agendada.",
            data={"new_status": new_state.status.value},
        )
