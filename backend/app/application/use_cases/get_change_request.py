from uuid import UUID

from app.application.dtos import ChangeRequestOutput


class GetChangeRequestUseCase:
    def __init__(self, change_request_repository) -> None:
        self.change_request_repository = change_request_repository

    def execute(self, change_request_id: UUID) -> ChangeRequestOutput:
        change_request = self.change_request_repository.get_by_id(change_request_id)

        if change_request is None:
            raise ValueError("Change request not found")

        return ChangeRequestOutput(
            id=change_request.id,
            title=change_request.title,
            description=change_request.description,
            affected_system=change_request.affected_system,
            risk_level=change_request.risk_level,
            status=change_request.status,
            requester_id=change_request.requester_id,
        )