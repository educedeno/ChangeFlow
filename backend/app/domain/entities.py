from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from app.domain.enums import ApprovalStatus, DecisionAction


@dataclass
class Approval:
    """
    Representa una aprobación asignada a un reviewer para una solicitud de cambio.
    Una solicitud puede tener múltiples Approvals (ej: cambios HIGH risk requieren 2).
    """
    request_id: UUID
    reviewer_id: UUID
    id: UUID = field(default_factory=uuid4)
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    decided_at: Optional[datetime] = None

    def is_pending(self) -> bool:
        return self.status == ApprovalStatus.PENDING

    def mark_approved(self) -> None:
        if not self.is_pending():
            raise ValueError(
                f"No se puede aprobar una Approval con estado {self.status.value}"
            )
        self.status = ApprovalStatus.APPROVED
        self.decided_at = datetime.utcnow()

    def mark_rejected(self) -> None:
        if not self.is_pending():
            raise ValueError(
                f"No se puede rechazar una Approval con estado {self.status.value}"
            )
        self.status = ApprovalStatus.REJECTED
        self.decided_at = datetime.utcnow()


@dataclass
class Decision:
    """
    Representa la decisión concreta tomada por un reviewer sobre una Approval.
    Guarda el detalle de la acción y el comentario asociado.
    """
    approval_id: UUID
    action: DecisionAction
    id: UUID = field(default_factory=uuid4)
    comment: Optional[str] = None
    decided_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        # Regla de negocio: rechazar o pedir cambios requiere comentario
        if self.action in (DecisionAction.REJECT, DecisionAction.REQUEST_CHANGES):
            if not self.comment or not self.comment.strip():
                raise ValueError(
                    f"La acción {self.action.value} requiere un comentario."
                )