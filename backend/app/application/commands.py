"""
Patrón Command: cada acción del aprobador es un objeto ejecutable.

Beneficios:
- Permite encolar, loguear, auditar y eventualmente deshacer (undo) acciones
- Desacopla el "qué se quiere hacer" del "cómo se hace"
- Facilita aplicar Template Method o decoradores en el futuro
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional
from uuid import UUID

if TYPE_CHECKING:
    from app.application.use_cases.approve_request import ApproveRequestUseCase
    from app.application.use_cases.assign_reviewer import AssignReviewerUseCase
    from app.application.use_cases.reject_request import RejectRequestUseCase


@dataclass
class CommandResult:
    """Resultado estandarizado para todos los comandos."""
    success: bool
    message: str
    data: Optional[dict] = None


class Command(ABC):
    """Interfaz base del patrón Command."""

    @abstractmethod
    def execute(self) -> CommandResult:
        ...

    def undo(self) -> CommandResult:
        """Hook opcional para deshacer la acción."""
        return CommandResult(
            success=False, message="Esta acción no soporta undo."
        )


@dataclass
class ApproveCommand(Command):
    approval_id: UUID
    reviewer_id: UUID
    use_case: "ApproveRequestUseCase"  # forward ref, se resuelve en runtime

    def execute(self) -> CommandResult:
        return self.use_case.run(
            approval_id=self.approval_id, reviewer_id=self.reviewer_id
        )


@dataclass
class RejectCommand(Command):
    approval_id: UUID
    reviewer_id: UUID
    comment: str
    use_case: "RejectRequestUseCase"

    def execute(self) -> CommandResult:
        return self.use_case.run(
            approval_id=self.approval_id,
            reviewer_id=self.reviewer_id,
            comment=self.comment,
        )


@dataclass
class AssignCommand(Command):
    request_id: UUID
    reviewer_id: UUID
    use_case: "AssignReviewerUseCase"

    def execute(self) -> CommandResult:
        return self.use_case.run(
            request_id=self.request_id, reviewer_id=self.reviewer_id
        )