"""
Strategy: política de aprobación según risk level. Define qué áreas
deben aprobar para que la solicitud pueda avanzar a APPROVED.
"""

from abc import ABC, abstractmethod

from app.domain.enums import ApprovalArea, RiskLevel
from app.domain.value_objects import RISK_REQUIRED_AREAS


class ApprovalPolicy(ABC):
    @abstractmethod
    def required_areas(self) -> list[ApprovalArea]:
        ...

    def required_approvals(self) -> int:
        return len(self.required_areas())

    def is_satisfied(self, approved_areas: set[ApprovalArea]) -> bool:
        return set(self.required_areas()).issubset(approved_areas)


class _AreasPolicy(ApprovalPolicy):
    def __init__(self, areas: list[ApprovalArea]):
        self._areas = areas

    def required_areas(self) -> list[ApprovalArea]:
        return list(self._areas)


def policy_for(risk_level: RiskLevel) -> ApprovalPolicy:
    return _AreasPolicy(RISK_REQUIRED_AREAS[risk_level])
