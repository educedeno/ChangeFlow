"""Implementación concreta de AuditRepository usando SQLAlchemy."""

from typing import List

from sqlalchemy.orm import Session

from app.domain.entities import AuditEntry
from app.infrastructure.db.models import AuditEntryModel


class SQLAlchemyAuditRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    @staticmethod
    def _to_entity(model: AuditEntryModel) -> AuditEntry:
        return AuditEntry(
            id=model.id,
            actor_id=model.actor_id,
            action=model.action,
            entity_type=model.entity_type,
            entity_id=model.entity_id,
            detail=model.detail,
            occurred_at=model.occurred_at,
        )

    @staticmethod
    def _to_model(entity: AuditEntry) -> AuditEntryModel:
        return AuditEntryModel(
            id=entity.id,
            actor_id=entity.actor_id,
            action=entity.action,
            entity_type=entity.entity_type,
            entity_id=entity.entity_id,
            detail=entity.detail,
            occurred_at=entity.occurred_at,
        )

    def save(self, entry: AuditEntry) -> None:
        self.session.add(self._to_model(entry))
        self.session.commit()

    def list_all(self) -> List[AuditEntry]:
        models = (
            self.session.query(AuditEntryModel)
            .order_by(AuditEntryModel.occurred_at.desc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    def list_for_entity(self, entity_type: str, entity_id: str) -> List[AuditEntry]:
        models = (
            self.session.query(AuditEntryModel)
            .filter(
                AuditEntryModel.entity_type == entity_type,
                AuditEntryModel.entity_id == entity_id,
            )
            .order_by(AuditEntryModel.occurred_at.desc())
            .all()
        )
        return [self._to_entity(m) for m in models]
