"""Caso de uso: marcar una solicitud agendada como ejecutada o fallida."""

from datetime import datetime
from uuid import UUID

from app.application.commands import CommandResult
from app.application.services.event_bus import EventBus
from app.domain.events import RequestExecuted, RequestFailed
from app.domain.exceptions import (
    BusinessRuleViolationError,
    InvalidStateTransitionError,
)
from app.domain.repositories import ChangeRequestRepository
from app.domain.state_machine import (
    ChangeRequestContext,
    state_from_status,
)


class ExecuteRequestUseCase:
    def __init__(
        self,
        request_repo: ChangeRequestRepository,
        event_bus: EventBus | None = None,
    ):
        self.request_repo = request_repo
        self.event_bus = event_bus or EventBus()

    def run(self, request_id: UUID) -> CommandResult:
        cr = self.request_repo.get_by_id(request_id)
        if cr is None:
            return CommandResult(success=False, message="Solicitud no encontrada.")

        state = state_from_status(cr.status)
        ctx = ChangeRequestContext(risk_level=cr.risk_level)
        try:
            new_state = state.execute(ctx)
        except (InvalidStateTransitionError, BusinessRuleViolationError) as e:
            return CommandResult(success=False, message=str(e))

        self.request_repo.set_executed_at(request_id, datetime.utcnow())
        self.request_repo.update_status(request_id, new_state.status)

        self.event_bus.publish(RequestExecuted(
            request_id=request_id,
            requester_id=cr.requester_id,
        ))
        return CommandResult(
            success=True,
            message="Cambio marcado como ejecutado.",
            data={"new_status": new_state.status.value},
        )


class MarkFailedUseCase:
    def __init__(
        self,
        request_repo: ChangeRequestRepository,
        event_bus: EventBus | None = None,
    ):
        self.request_repo = request_repo
        self.event_bus = event_bus or EventBus()

    def run(self, request_id: UUID, reason: str) -> CommandResult:
        if not reason or not reason.strip():
            return CommandResult(
                success=False, message="Debe registrarse el motivo del fallo."
            )

        cr = self.request_repo.get_by_id(request_id)
        if cr is None:
            return CommandResult(success=False, message="Solicitud no encontrada.")

        state = state_from_status(cr.status)
        ctx = ChangeRequestContext(risk_level=cr.risk_level)
        try:
            new_state = state.fail(ctx)
        except (InvalidStateTransitionError, BusinessRuleViolationError) as e:
            return CommandResult(success=False, message=str(e))

        self.request_repo.set_failure_reason(request_id, reason)
        self.request_repo.update_status(request_id, new_state.status)

        self.event_bus.publish(RequestFailed(
            request_id=request_id,
            requester_id=cr.requester_id,
            reason=reason,
        ))
        return CommandResult(
            success=True,
            message="Cambio marcado como fallido.",
            data={"new_status": new_state.status.value},
        )
