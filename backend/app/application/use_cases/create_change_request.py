from app.application.dtos import ChangeRequestOutput, CreateChangeRequestInput
from app.application.services.event_bus import EventBus
from app.domain.entities import ChangeRequest
from app.domain.events import RequestCreated


class CreateChangeRequestUseCase:
    def __init__(self, change_request_repository, event_bus: EventBus | None = None) -> None:
        self.change_request_repository = change_request_repository
        self.event_bus = event_bus or EventBus()

    def execute(self, input_data: CreateChangeRequestInput) -> ChangeRequestOutput:
        change_request = ChangeRequest(
            title=input_data.title,
            description=input_data.description,
            affected_system=input_data.affected_system,
            risk_level=input_data.risk_level,
            requester_id=input_data.requester_id,
            rollback_plan=input_data.rollback_plan,
        )

        self.change_request_repository.save(change_request)

        self.event_bus.publish(RequestCreated(
            request_id=change_request.id,
            requester_id=change_request.requester_id,
            title=change_request.title,
            risk_level=change_request.risk_level.value,
        ))

        return _to_output(change_request)


def _to_output(cr) -> ChangeRequestOutput:
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
