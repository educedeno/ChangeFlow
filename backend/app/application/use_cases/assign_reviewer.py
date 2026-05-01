"""Caso de uso: asignar un reviewer a una solicitud de cambio."""

from uuid import UUID

from app.application.commands import CommandResult
from app.domain.entities import Approval
from app.domain.policies import policy_for
from app.domain.repositories import ApprovalRepository, ChangeRequestRepository


class AssignReviewerUseCase:
    """
    Asigna uno o más reviewers a una solicitud creando Approvals pendientes.
    La cantidad necesaria depende de la policy según el risk level.
    """

    def __init__(
        self,
        approval_repo: ApprovalRepository,
        request_repo: ChangeRequestRepository,
    ):
        self.approval_repo = approval_repo
        self.request_repo = request_repo

    def run(self, request_id: UUID, reviewer_id: UUID) -> CommandResult:
        # Validar que la solicitud exista
        risk_level = self.request_repo.get_risk_level(request_id)
        if risk_level is None:
            return CommandResult(
                success=False, message="Solicitud no encontrada."
            )

        # Validar que no se exceda la policy
        policy = policy_for(risk_level)
        existing = self.approval_repo.list_by_request(request_id)
        if len(existing) >= policy.required_approvals():
            return CommandResult(
                success=False,
                message=(
                    f"Ya hay {len(existing)} reviewer(s) asignado(s). "
                    f"La policy permite máximo {policy.required_approvals()}."
                ),
            )

        # Validar que no se asigne dos veces al mismo reviewer
        for ap in existing:
            if ap.reviewer_id == reviewer_id:
                return CommandResult(
                    success=False,
                    message="Este reviewer ya está asignado a la solicitud.",
                )

        approval = Approval(request_id=request_id, reviewer_id=reviewer_id)
        saved = self.approval_repo.save(approval)

        return CommandResult(
            success=True,
            message="Reviewer asignado exitosamente.",
            data={"approval_id": str(saved.id)},
        )