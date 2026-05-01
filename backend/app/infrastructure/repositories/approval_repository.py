"""Implementación concreta de ApprovalRepository usando SQLAlchemy."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities import Approval, Decision
from app.domain.enums import ApprovalStatus
from app.domain.repositories import ApprovalRepository
from app.infrastructure.db.models import ApprovalModel, DecisionModel


class SQLAlchemyApprovalRepository(ApprovalRepository):
    """Adapter concreto: convierte entre entidades de dominio y modelos ORM."""

    def __init__(self, session: Session):
        self.session = session

    # ----- mappers -----

    @staticmethod
    def _to_entity(model: ApprovalModel) -> Approval:
        return Approval(
            id=model.id,
            request_id=model.request_id,
            reviewer_id=model.reviewer_id,
            status=model.status,
            created_at=model.created_at,
            decided_at=model.decided_at,
        )

    @staticmethod
    def _to_model(entity: Approval) -> ApprovalModel:
        return ApprovalModel(
            id=entity.id,
            request_id=entity.request_id,
            reviewer_id=entity.reviewer_id,
            status=entity.status,
            created_at=entity.created_at,
            decided_at=entity.decided_at,
        )

    # ----- métodos del puerto -----

    def get_by_id(self, approval_id: UUID) -> Optional[Approval]:
        model = self.session.get(ApprovalModel, approval_id)
        return self._to_entity(model) if model else None

    def list_by_request(self, request_id: UUID) -> List[Approval]:
        models = (
            self.session.query(ApprovalModel)
            .filter(ApprovalModel.request_id == request_id)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def list_pending_for_reviewer(self, reviewer_id: UUID) -> List[Approval]:
        models = (
            self.session.query(ApprovalModel)
            .filter(
                ApprovalModel.reviewer_id == reviewer_id,
                ApprovalModel.status == ApprovalStatus.PENDING,
            )
            .all()
        )
        return [self._to_entity(m) for m in models]

    def save(self, approval: Approval) -> Approval:
        existing = self.session.get(ApprovalModel, approval.id)
        if existing:
            existing.status = approval.status
            existing.decided_at = approval.decided_at
        else:
            self.session.add(self._to_model(approval))
        self.session.commit()
        return approval

    def save_decision(self, decision: Decision) -> Decision:
        model = DecisionModel(
            id=decision.id,
            approval_id=decision.approval_id,
            action=decision.action,
            comment=decision.comment,
            decided_at=decision.decided_at,
        )
        self.session.add(model)
        self.session.commit()
        return decision

    def count_approved_for_request(self, request_id: UUID) -> int:
        return (
            self.session.query(ApprovalModel)
            .filter(
                ApprovalModel.request_id == request_id,
                ApprovalModel.status == ApprovalStatus.APPROVED,
            )
            .count()
        )