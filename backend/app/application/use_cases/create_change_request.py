from app.application.dtos import CreateChangeRequestInput, ChangeRequestOutput
from app.domain.entities import ChangeRequest


class CreateChangeRequestUseCase:
    def __init__(self, change_request_repository) -> None:
        self.change_request_repository = change_request_repository

    def execute(self, input_data: CreateChangeRequestInput) -> ChangeRequestOutput:
        change_request = ChangeRequest(
            title=input_data.title,
            description=input_data.description,
            affected_system=input_data.affected_system,
            risk_level=input_data.risk_level,
            requester_id=input_data.requester_id,
        )

        self.change_request_repository.save(change_request)

        return ChangeRequestOutput(
            id=change_request.id,
            title=change_request.title,
            description=change_request.description,
            affected_system=change_request.affected_system,
            risk_level=change_request.risk_level,
            status=change_request.status,
            requester_id=change_request.requester_id,
        )