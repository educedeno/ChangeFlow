"""
Interfaces de repositorio (puertos del dominio).

Estas interfaces son lo que los casos de uso conocen. Las implementaciones
concretas viven en `infrastructure/repositories/` y se inyectan en runtime.
Esto cumple con la inversión de dependencias de la arquitectura hexagonal:
el dominio no depende de SQLAlchemy ni de ningún detalle de persistencia.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from app.domain.entities import Approval, Decision


class ApprovalRepository(ABC):
    """Puerto para persistencia de Approvals y Decisions."""

    @abstractmethod
    def get_by_id(self, approval_id: UUID) -> Optional[Approval]:
        ...

    @abstractmethod
    def list_by_request(self, request_id: UUID) -> List[Approval]:
        ...

    @abstractmethod
    def list_pending_for_reviewer(self, reviewer_id: UUID) -> List[Approval]:
        ...

    @abstractmethod
    def save(self, approval: Approval) -> Approval:
        ...

    @abstractmethod
    def save_decision(self, decision: Decision) -> Decision:
        ...

    @abstractmethod
    def count_approved_for_request(self, request_id: UUID) -> int:
        ...


class ChangeRequestRepository(ABC):
    """Puerto mínimo para leer/actualizar el estado de la solicitud principal."""

    @abstractmethod
    def get_status(self, request_id: UUID):
        """Devuelve el RequestStatus actual."""
        ...

    @abstractmethod
    def update_status(self, request_id: UUID, new_status) -> None:
        """Persiste el nuevo estado tras una transición válida."""
        ...

    @abstractmethod
    def get_risk_level(self, request_id: UUID):
        ...

    @abstractmethod
    def has_rollback_plan(self, request_id: UUID) -> bool:
        ...