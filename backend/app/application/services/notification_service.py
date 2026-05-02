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


class NotificationRepository(Protocol):
    def save(self, notification: Notification) -> None: ...


class NotificationService:
    """Suscriptor del EventBus que genera Notifications ante eventos de dominio."""

    def __init__(self, notification_repo: NotificationRepository) -> None:
        self._repo = notification_repo

    def on_request_created(self, event: RequestCreated) -> None:
        n = Notification(
            user_id=str(event.requester_id),
            message=f"Tu solicitud '{event.title}' fue creada exitosamente.",
            event_type="REQUEST_CREATED",
        )
        self._repo.save(n)

    def on_request_submitted(self, event: RequestSubmitted) -> None:
        n = Notification(
            user_id=str(event.requester_id),
            message=f"Tu solicitud '{event.title}' fue enviada para revisión.",
            event_type="REQUEST_SUBMITTED",
        )
        self._repo.save(n)

    def on_request_approved(self, event: RequestApproved) -> None:
        n = Notification(
            user_id=str(event.reviewer_id),
            message=f"La solicitud {event.request_id} fue aprobada.",
            event_type="REQUEST_APPROVED",
        )
        self._repo.save(n)

    def on_request_rejected(self, event: RequestRejected) -> None:
        n = Notification(
            user_id=str(event.reviewer_id),
            message=f"La solicitud {event.request_id} fue rechazada. Motivo: {event.comment}",
            event_type="REQUEST_REJECTED",
        )
        self._repo.save(n)

    def on_reviewer_assigned(self, event: ReviewerAssigned) -> None:
        n = Notification(
            user_id=str(event.reviewer_id),
            message=f"Se te asignó como revisor de la solicitud {event.request_id}.",
            event_type="REVIEWER_ASSIGNED",
        )
        self._repo.save(n)

    def on_changes_requested(self, event: ChangesRequested) -> None:
        n = Notification(
            user_id=str(event.reviewer_id),
            message=f"Se solicitaron cambios en la solicitud {event.request_id}: {event.comment}",
            event_type="CHANGES_REQUESTED",
        )
        self._repo.save(n)
