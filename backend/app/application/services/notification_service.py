import logging
import os
from typing import Protocol

from app.domain.entities import Notification
from app.domain.events import (
    ChangesRequested,
    RequestApproved,
    RequestCreated,
    RequestRejected,
    RequestSubmitted,
    ReviewerAssigned,
)

logger = logging.getLogger(__name__)


class NotificationRepository(Protocol):
    def save(self, notification: Notification) -> None: ...


# ----- Strategy: canales de notificación -----

class NotificationChannel(Protocol):
    def send(self, notification: Notification) -> None: ...


class InAppChannel:
    """Persiste la notificación en base de datos (canal principal)."""

    def __init__(self, repo: NotificationRepository) -> None:
        self._repo = repo

    def send(self, notification: Notification) -> None:
        self._repo.save(notification)


class EmailChannel:
    """Mock de email — loguea el mensaje en lugar de enviarlo.
    Activar con variable de entorno EMAIL_NOTIFICATIONS=true."""

    def send(self, notification: Notification) -> None:
        if os.getenv("EMAIL_NOTIFICATIONS", "false").lower() == "true":
            logger.info(
                "EMAIL → user=%s event=%s msg=%s",
                notification.user_id,
                notification.event_type,
                notification.message,
            )


class NotificationService:
    """Suscriptor del EventBus que genera Notifications ante eventos de dominio."""

    def __init__(self, channels: list[NotificationChannel]) -> None:
        self._channels = channels

    def _notify(self, notification: Notification) -> None:
        for channel in self._channels:
            channel.send(notification)

    def on_request_created(self, event: RequestCreated) -> None:
        self._notify(Notification(
            user_id=str(event.requester_id),
            message=f"Tu solicitud '{event.title}' fue creada exitosamente.",
            event_type="REQUEST_CREATED",
        ))

    def on_request_submitted(self, event: RequestSubmitted) -> None:
        self._notify(Notification(
            user_id=str(event.requester_id),
            message=f"Tu solicitud '{event.title}' fue enviada para revisión.",
            event_type="REQUEST_SUBMITTED",
        ))

    def on_request_approved(self, event: RequestApproved) -> None:
        self._notify(Notification(
            user_id=str(event.reviewer_id),
            message=f"La solicitud {event.request_id} fue aprobada.",
            event_type="REQUEST_APPROVED",
        ))

    def on_request_rejected(self, event: RequestRejected) -> None:
        self._notify(Notification(
            user_id=str(event.reviewer_id),
            message=f"La solicitud {event.request_id} fue rechazada. Motivo: {event.comment}",
            event_type="REQUEST_REJECTED",
        ))

    def on_reviewer_assigned(self, event: ReviewerAssigned) -> None:
        self._notify(Notification(
            user_id=str(event.reviewer_id),
            message=f"Se te asignó como revisor de la solicitud {event.request_id}.",
            event_type="REVIEWER_ASSIGNED",
        ))

    def on_changes_requested(self, event: ChangesRequested) -> None:
        self._notify(Notification(
            user_id=str(event.reviewer_id),
            message=f"Se solicitaron cambios en la solicitud {event.request_id}: {event.comment}",
            event_type="CHANGES_REQUESTED",
        ))
