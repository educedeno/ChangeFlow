"""Implementación concreta de NotificationRepository usando SQLAlchemy."""

from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities import Notification
from app.infrastructure.db.models import NotificationModel


class SQLAlchemyNotificationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    @staticmethod
    def _to_entity(model: NotificationModel) -> Notification:
        return Notification(
            id=model.id,
            user_id=model.user_id,
            message=model.message,
            event_type=model.event_type,
            read=model.read,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_model(entity: Notification) -> NotificationModel:
        return NotificationModel(
            id=entity.id,
            user_id=entity.user_id,
            message=entity.message,
            event_type=entity.event_type,
            read=entity.read,
            created_at=entity.created_at,
        )

    def save(self, notification: Notification) -> None:
        self.session.add(self._to_model(notification))
        self.session.commit()

    def list_for_user(self, user_id: str) -> List[Notification]:
        models = (
            self.session.query(NotificationModel)
            .filter(NotificationModel.user_id == user_id)
            .order_by(NotificationModel.created_at.desc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    def mark_read(self, notification_id: UUID, user_id: str) -> bool:
        model = self.session.get(NotificationModel, notification_id)
        if not model or model.user_id != user_id:
            return False
        model.read = True
        self.session.commit()
        return True
