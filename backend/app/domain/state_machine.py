r"""
Máquina de estados para solicitudes de cambio en ChangeFlow.

Implementa el patrón State: cada estado es una clase que conoce sus
transiciones válidas. Las transiciones inválidas lanzan
InvalidStateTransitionError.

Ciclo de vida:
    DRAFT -> SUBMITTED -> IN_REVIEW -> APPROVED -> COMPLETED
                                    \-> REJECTED
                                    \-> CHANGES_REQUESTED -> SUBMITTED (vuelve)
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from app.domain.enums import RequestStatus, RiskLevel
from app.domain.exceptions import (
    InvalidStateTransitionError,
    BusinessRuleViolationError,
)

if TYPE_CHECKING:
    # Solo para type hints, evita circular imports
    pass


class RequestState(ABC):
    """Clase base abstracta para todos los estados de una solicitud."""

    status: RequestStatus  # cada subclase define su status

    def submit(self, context: "ChangeRequestContext") -> "RequestState":
        raise InvalidStateTransitionError(
            f"No se puede hacer submit desde el estado {self.status.value}"
        )

    def start_review(self, context: "ChangeRequestContext") -> "RequestState":
        raise InvalidStateTransitionError(
            f"No se puede iniciar review desde el estado {self.status.value}"
        )

    def approve(self, context: "ChangeRequestContext") -> "RequestState":
        raise InvalidStateTransitionError(
            f"No se puede aprobar desde el estado {self.status.value}"
        )

    def reject(self, context: "ChangeRequestContext") -> "RequestState":
        raise InvalidStateTransitionError(
            f"No se puede rechazar desde el estado {self.status.value}"
        )

    def request_changes(self, context: "ChangeRequestContext") -> "RequestState":
        raise InvalidStateTransitionError(
            f"No se pueden solicitar cambios desde el estado {self.status.value}"
        )

    def complete(self, context: "ChangeRequestContext") -> "RequestState":
        raise InvalidStateTransitionError(
            f"No se puede completar desde el estado {self.status.value}"
        )


class DraftState(RequestState):
    status = RequestStatus.DRAFT

    def submit(self, context: "ChangeRequestContext") -> "RequestState":
        # Regla de negocio: HIGH risk requiere plan de rollback al hacer submit
        if context.risk_level == RiskLevel.HIGH and not context.has_rollback_plan:
            raise BusinessRuleViolationError(
                "Cambios HIGH risk requieren plan de rollback antes de submit."
            )
        return SubmittedState()


class SubmittedState(RequestState):
    status = RequestStatus.SUBMITTED

    def start_review(self, context: "ChangeRequestContext") -> "RequestState":
        return InReviewState()

    def reject(self, context: "ChangeRequestContext") -> "RequestState":
        # Permitir rechazo directo si el aprobador lo hace antes de empezar review
        return RejectedState()


class InReviewState(RequestState):
    status = RequestStatus.IN_REVIEW

    def approve(self, context: "ChangeRequestContext") -> "RequestState":
        # Regla de negocio: HIGH risk requiere 2 aprobaciones
        required = 2 if context.risk_level == RiskLevel.HIGH else 1
        if context.approvals_count < required:
            raise BusinessRuleViolationError(
                f"Cambios {context.risk_level.value} requieren "
                f"{required} aprobación(es). Actuales: {context.approvals_count}"
            )
        return ApprovedState()

    def reject(self, context: "ChangeRequestContext") -> "RequestState":
        return RejectedState()

    def request_changes(self, context: "ChangeRequestContext") -> "RequestState":
        return ChangesRequestedState()


class ChangesRequestedState(RequestState):
    status = RequestStatus.CHANGES_REQUESTED

    def submit(self, context: "ChangeRequestContext") -> "RequestState":
        # El solicitante corrige y vuelve a enviar
        return SubmittedState()


class ApprovedState(RequestState):
    status = RequestStatus.APPROVED

    def complete(self, context: "ChangeRequestContext") -> "RequestState":
        return CompletedState()


class RejectedState(RequestState):
    """Estado terminal: una solicitud rechazada no se puede reabrir."""
    status = RequestStatus.REJECTED


class CompletedState(RequestState):
    """Estado terminal: una solicitud completada no cambia más."""
    status = RequestStatus.COMPLETED


# ---------------------------------------------------------------------------
# Context: lo que la máquina de estados necesita saber para decidir
# ---------------------------------------------------------------------------

class ChangeRequestContext:
    """
    Contexto que se pasa a los estados para evaluar reglas de negocio.
    Es un DTO interno del dominio, no expone la entidad completa.
    """

    def __init__(
        self,
        risk_level: RiskLevel,
        has_rollback_plan: bool = False,
        approvals_count: int = 0,
    ):
        self.risk_level = risk_level
        self.has_rollback_plan = has_rollback_plan
        self.approvals_count = approvals_count


# ---------------------------------------------------------------------------
# Factory para reconstruir estados desde un RequestStatus persistido
# ---------------------------------------------------------------------------

_STATE_REGISTRY: dict[RequestStatus, type[RequestState]] = {
    RequestStatus.DRAFT: DraftState,
    RequestStatus.SUBMITTED: SubmittedState,
    RequestStatus.IN_REVIEW: InReviewState,
    RequestStatus.CHANGES_REQUESTED: ChangesRequestedState,
    RequestStatus.APPROVED: ApprovedState,
    RequestStatus.REJECTED: RejectedState,
    RequestStatus.COMPLETED: CompletedState,
}


def state_from_status(status: RequestStatus) -> RequestState:
    """Reconstruye una instancia de estado desde un RequestStatus."""
    state_class = _STATE_REGISTRY.get(status)
    if state_class is None:
        raise ValueError(f"Estado desconocido: {status}")
    return state_class()