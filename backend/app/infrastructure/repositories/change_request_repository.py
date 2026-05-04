"""Implementación de ChangeRequestRepository usando SQLAlchemy."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities import ChangeRequest
from app.domain.enums import RequestStatus, RiskLevel
from app.domain.repositories import ChangeRequestRepository
from app.infrastructure.db.models import ChangeRequestModel


class SQLAlchemyChangeRequestRepository(ChangeRequestRepository):
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _to_entity(model: ChangeRequestModel) -> ChangeRequest:
        return ChangeRequest(
            id=model.id,
            title=model.title,
            description=model.description or "",
            affected_system=model.affected_system or "",
            risk_level=model.risk_level,
            requester_id=model.requester_id,
            status=model.status,
            rollback_plan=model.rollback_plan,
            failure_reason=model.failure_reason,
            created_at=model.created_at,
            scheduled_at=model.scheduled_at,
            executed_at=model.executed_at,
        )

    @staticmethod
    def _to_model(entity: ChangeRequest) -> ChangeRequestModel:
        return ChangeRequestModel(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            affected_system=entity.affected_system,
            requester_id=entity.requester_id,
            status=entity.status,
            risk_level=entity.risk_level,
            rollback_plan=entity.rollback_plan,
            failure_reason=entity.failure_reason,
            created_at=entity.created_at,
            scheduled_at=entity.scheduled_at,
            executed_at=entity.executed_at,
        )

    def _get(self, request_id: UUID) -> Optional[ChangeRequestModel]:
        return self.session.get(ChangeRequestModel, request_id)

    def save(self, change_request: ChangeRequest) -> ChangeRequest:
        existing = self._get(change_request.id)
        if existing:
            existing.title = change_request.title
            existing.description = change_request.description
            existing.affected_system = change_request.affected_system
            existing.requester_id = change_request.requester_id
            existing.status = change_request.status
            existing.risk_level = change_request.risk_level
            existing.rollback_plan = change_request.rollback_plan
            existing.failure_reason = change_request.failure_reason
            existing.scheduled_at = change_request.scheduled_at
            existing.executed_at = change_request.executed_at
        else:
            self.session.add(self._to_model(change_request))
        self.session.commit()
        return change_request

    def get_by_id(self, request_id: UUID) -> Optional[ChangeRequest]:
        model = self._get(request_id)
        return self._to_entity(model) if model else None

    def get_all(self) -> List[ChangeRequest]:
        models = (
            self.session.query(ChangeRequestModel)
            .order_by(ChangeRequestModel.created_at.desc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    def get_status(self, request_id: UUID) -> Optional[RequestStatus]:
        model = self._get(request_id)
        return model.status if model else None

    def update_status(self, request_id: UUID, new_status: RequestStatus) -> None:
        model = self._get(request_id)
        if model:
            model.status = new_status
            self.session.commit()

    def get_risk_level(self, request_id: UUID) -> Optional[RiskLevel]:
        model = self._get(request_id)
        return model.risk_level if model else None

    def has_rollback_plan(self, request_id: UUID) -> bool:
        model = self._get(request_id)
        return bool(model and model.rollback_plan and model.rollback_plan.strip())

    def set_scheduled_at(self, request_id: UUID, scheduled_at: datetime) -> None:
        model = self._get(request_id)
        if model:
            model.scheduled_at = scheduled_at
            self.session.commit()

    def set_executed_at(self, request_id: UUID, executed_at: datetime) -> None:
        model = self._get(request_id)
        if model:
            model.executed_at = executed_at
            self.session.commit()

    def set_failure_reason(self, request_id: UUID, reason: str) -> None:
        model = self._get(request_id)
        if model:
            model.failure_reason = reason
            self.session.commit()
