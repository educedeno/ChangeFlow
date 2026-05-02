"""Implementación de ChangeRequestRepository usando SQLAlchemy."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.enums import RequestStatus, RiskLevel
from app.domain.repositories import ChangeRequestRepository
from app.infrastructure.db.models import ChangeRequestModel


class SQLAlchemyChangeRequestRepository(ChangeRequestRepository):
    def __init__(self, session: Session):
        self.session = session

    def _get(self, request_id: UUID) -> Optional[ChangeRequestModel]:
        return self.session.get(ChangeRequestModel, request_id)

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