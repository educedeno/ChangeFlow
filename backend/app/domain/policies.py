"""
Patrón Strategy: política de aprobación según risk level.

Diferentes niveles de riesgo requieren diferentes reglas de aprobación.
En lugar de hardcodear if/else en los casos de uso, encapsulamos cada
estrategia en su propia clase.
"""

from abc import ABC, abstractmethod

from app.domain.enums import RiskLevel


class ApprovalPolicy(ABC):
    """Strategy base. Define cuántas aprobaciones se necesitan."""

    @abstractmethod
    def required_approvals(self) -> int:
        ...

    @abstractmethod
    def is_satisfied(self, current_approvals: int) -> bool:
        ...


class SingleApprovalPolicy(ApprovalPolicy):
    """Política para LOW y MEDIUM risk: una sola aprobación basta."""

    def required_approvals(self) -> int:
        return 1

    def is_satisfied(self, current_approvals: int) -> bool:
        return current_approvals >= 1


class DualApprovalPolicy(ApprovalPolicy):
    """Política para HIGH risk: requiere dos aprobaciones independientes."""

    def required_approvals(self) -> int:
        return 2

    def is_satisfied(self, current_approvals: int) -> bool:
        return current_approvals >= 2


def policy_for(risk_level: RiskLevel) -> ApprovalPolicy:
    """Factory que devuelve la policy adecuada según el risk level."""
    if risk_level == RiskLevel.HIGH:
        return DualApprovalPolicy()
    return SingleApprovalPolicy()