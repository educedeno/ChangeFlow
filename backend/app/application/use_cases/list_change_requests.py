from app.application.dtos import ChangeRequestOutput


class ListChangeRequestsUseCase:
    def __init__(self, change_request_repository) -> None:
        self.change_request_repository = change_request_repository

    def execute(self) -> list[ChangeRequestOutput]:
        change_requests = self.change_request_repository.get_all()

        return [
            ChangeRequestOutput(
                id=cr.id,
                title=cr.title,
                description=cr.description,
                affected_system=cr.affected_system,
                risk_level=cr.risk_level,
                status=cr.status,
                requester_id=cr.requester_id,
            )
            for cr in change_requests
        ]