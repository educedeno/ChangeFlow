r"""
Máquina de estados para solicitudes de cambio.

Flujo principal:
    DRAFT -> SUBMITTED -> TECH_REVIEW -> OPS_REVIEW -> SECURITY_REVIEW
          -> APPROVED -> SCHEDULED -> EXECUTED
                                  \-> FAILED
    Desde TECH_REVIEW/OPS_REVIEW/SECURITY_REVIEW también:
       \-> REJECTED
       \-> CHANGES_REQUESTED -> SUBMITTED
    Cancelación válida desde DRAFT/SUBMITTED/*REVIEW/CHANGES_REQUESTED:
       \-> CANCELLED
"""

from __future__ import annotations
from abc import ABC

from app.domain.enums import ApprovalArea, RequestStatus, RiskLevel
from app.domain.exceptions import (
    BusinessRuleViolationError,
    InvalidStateTransitionError,
)
from app.domain.policies import policy_for


class ChangeRequestContext:
    """Contexto que la máquina necesita para evaluar reglas."""

    def __init__(
        self,
        risk_level: RiskLevel,
        has_rollback_plan: bool = False,
        approved_areas: set[ApprovalArea] | None = None,
        approving_area: ApprovalArea | None = None,
    ):
        self.risk_level = risk_level
        self.has_rollback_plan = has_rollback_plan
        self.approved_areas = approved_areas or set()
        self.approving_area = approving_area


class RequestState(ABC):
    status: RequestStatus

    def submit(self, context: ChangeRequestContext) -> "RequestState":
        raise InvalidStateTransitionError(
            f"No se puede hacer submit desde el estado {self.status.value}"
        )

    def approve(self, context: ChangeRequestContext) -> "RequestState":
        raise InvalidStateTransitionError(
            f"No se puede aprobar desde el estado {self.status.value}"
        )

    def reject(self, context: ChangeRequestContext) -> "RequestState":
        raise InvalidStateTransitionError(
            f"No se puede rechazar desde el estado {self.status.value}"
        )

    def request_changes(self, context: ChangeRequestContext) -> "RequestState":
        raise InvalidStateTransitionError(
            f"No se pueden solicitar cambios desde el estado {self.status.value}"
        )

    def schedule(self, context: ChangeRequestContext) -> "RequestState":
        raise InvalidStateTransitionError(
            f"No se puede agendar desde el estado {self.status.value}"
        )

    def execute(self, context: ChangeRequestContext) -> "RequestState":
        raise InvalidStateTransitionError(
            f"No se puede ejecutar desde el estado {self.status.value}"
        )

    def fail(self, context: ChangeRequestContext) -> "RequestState":
        raise InvalidStateTransitionError(
            f"No se puede marcar como fallido desde el estado {self.status.value}"
        )

    def cancel(self, context: ChangeRequestContext) -> "RequestState":
        raise InvalidStateTransitionError(
            f"No se puede cancelar desde el estado {self.status.value}"
        )


def _validate_rollback(context: ChangeRequestContext) -> None:
    if context.risk_level in (RiskLevel.MEDIUM, RiskLevel.HIGH):
        if not context.has_rollback_plan:
            raise BusinessRuleViolationError(
                f"Cambios {context.risk_level.value} requieren plan de rollback."
            )


def _next_review_state(context: ChangeRequestContext) -> "RequestState":
    """Decide a qué estado de review pasar tras hacer submit."""
    return TechReviewState()


def _advance_after_approval(context: ChangeRequestContext) -> "RequestState":
    """Avanza al siguiente estado tras una aprobación de área."""
    policy = policy_for(context.risk_level)
    if policy.is_satisfied(context.approved_areas):
        return ApprovedState()

    pending = [a for a in policy.required_areas() if a not in context.approved_areas]
    next_area = pending[0]
    return _state_for_area(next_area)


def _state_for_area(area: ApprovalArea) -> "RequestState":
    if area == ApprovalArea.TECH:
        return TechReviewState()
    if area == ApprovalArea.OPS:
        return OpsReviewState()
    if area == ApprovalArea.SECURITY:
        return SecurityReviewState()
    raise ValueError(f"Área desconocida: {area}")


class DraftState(RequestState):
    status = RequestStatus.DRAFT

    def submit(self, context: ChangeRequestContext) -> RequestState:
        _validate_rollback(context)
        return TechReviewState()

    def cancel(self, context: ChangeRequestContext) -> RequestState:
        return CancelledState()


class SubmittedState(RequestState):
    """Estado breve entre DRAFT y TECH_REVIEW. Se mantiene por compatibilidad."""
    status = RequestStatus.SUBMITTED

    def approve(self, context: ChangeRequestContext) -> RequestState:
        return _advance_after_approval(context)

    def reject(self, context: ChangeRequestContext) -> RequestState:
        return RejectedState()

    def cancel(self, context: ChangeRequestContext) -> RequestState:
        return CancelledState()


class _ReviewState(RequestState):
    expected_area: ApprovalArea

    def approve(self, context: ChangeRequestContext) -> RequestState:
        if context.approving_area != self.expected_area:
            raise BusinessRuleViolationError(
                f"En {self.status.value} solo puede aprobar el área "
                f"{self.expected_area.value}."
            )
        return _advance_after_approval(context)

    def reject(self, context: ChangeRequestContext) -> RequestState:
        return RejectedState()

    def request_changes(self, context: ChangeRequestContext) -> RequestState:
        return ChangesRequestedState()

    def cancel(self, context: ChangeRequestContext) -> RequestState:
        return CancelledState()


class TechReviewState(_ReviewState):
    status = RequestStatus.TECH_REVIEW
    expected_area = ApprovalArea.TECH


class OpsReviewState(_ReviewState):
    status = RequestStatus.OPS_REVIEW
    expected_area = ApprovalArea.OPS


class SecurityReviewState(_ReviewState):
    status = RequestStatus.SECURITY_REVIEW
    expected_area = ApprovalArea.SECURITY


class ChangesRequestedState(RequestState):
    status = RequestStatus.CHANGES_REQUESTED

    def submit(self, context: ChangeRequestContext) -> RequestState:
        _validate_rollback(context)
        return TechReviewState()

    def cancel(self, context: ChangeRequestContext) -> RequestState:
        return CancelledState()


class ApprovedState(RequestState):
    status = RequestStatus.APPROVED

    def schedule(self, context: ChangeRequestContext) -> RequestState:
        return ScheduledState()


class ScheduledState(RequestState):
    status = RequestStatus.SCHEDULED

    def execute(self, context: ChangeRequestContext) -> RequestState:
        return ExecutedState()

    def fail(self, context: ChangeRequestContext) -> RequestState:
        return FailedState()


class ExecutedState(RequestState):
    """Terminal: una solicitud ejecutada no vuelve a revisión."""
    status = RequestStatus.EXECUTED


class FailedState(RequestState):
    """Terminal: el cambio falló al ejecutarse."""
    status = RequestStatus.FAILED


class RejectedState(RequestState):
    """Terminal."""
    status = RequestStatus.REJECTED


class CancelledState(RequestState):
    """Terminal."""
    status = RequestStatus.CANCELLED


_STATE_REGISTRY: dict[RequestStatus, type[RequestState]] = {
    RequestStatus.DRAFT: DraftState,
    RequestStatus.SUBMITTED: SubmittedState,
    RequestStatus.TECH_REVIEW: TechReviewState,
    RequestStatus.OPS_REVIEW: OpsReviewState,
    RequestStatus.SECURITY_REVIEW: SecurityReviewState,
    RequestStatus.CHANGES_REQUESTED: ChangesRequestedState,
    RequestStatus.APPROVED: ApprovedState,
    RequestStatus.SCHEDULED: ScheduledState,
    RequestStatus.EXECUTED: ExecutedState,
    RequestStatus.FAILED: FailedState,
    RequestStatus.REJECTED: RejectedState,
    RequestStatus.CANCELLED: CancelledState,
}


def state_from_status(status: RequestStatus) -> RequestState:
    state_class = _STATE_REGISTRY.get(status)
    if state_class is None:
        raise ValueError(f"Estado desconocido: {status}")
    return state_class()


# Alias retro-compatibles para que tests viejos no se rompan al importar.
InReviewState = TechReviewState
CompletedState = ExecutedState
