from uuid import UUID

from app.application.dtos import ChangeRequestOutput


class GetChangeRequestUseCase:
    def __init__(self, change_request_repository) -> None:
        self.change_request_repository = change_request_repository

    def execute(self, change_request_id: UUID) -> ChangeRequestOutput:
        cr = self.change_request_repository.get_by_id(change_request_id)
        if cr is None:
            raise ValueError("Change request not found")

        return ChangeRequestOutput(
            id=cr.id,
            title=cr.title,
            description=cr.description,
            affected_system=cr.affected_system,
            risk_level=cr.risk_level,
            status=cr.status,
            requester_id=cr.requester_id,
            rollback_plan=cr.rollback_plan,
            failure_reason=cr.failure_reason,
            scheduled_at=cr.scheduled_at,
            executed_at=cr.executed_at,
        )
