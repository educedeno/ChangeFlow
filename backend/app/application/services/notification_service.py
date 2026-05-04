import logging
import os
from typing import Protocol

from app.domain.entities import Notification
from app.domain.enums import Role
from app.domain.events import (
    ChangesRequested,
    OpsReviewRequired,
    RequestApproved,
    RequestCancelled,
    RequestCreated,
    RequestExecuted,
    RequestFailed,
    RequestRejected,
    RequestScheduled,
    RequestSubmitted,
    ReviewerAssigned,
    SecurityReviewRequired,
    TechReviewRequired,
)
from app.infrastructure.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class NotificationRepository(Protocol):
    def save(self, notification: Notification) -> None: ...


# ----- Strategy: canales de notificación -----

class NotificationChannel(Protocol):
    def send(self, notification: Notification) -> None: ...


class InAppChannel:
    def __init__(self, repo: NotificationRepository) -> None:
        self._repo = repo

    def send(self, notification: Notification) -> None:
        self._repo.save(notification)


class EmailChannel:
    """Mock de email — loguea el mensaje. Activar con EMAIL_NOTIFICATIONS=true."""

    def send(self, notification: Notification) -> None:
        if os.getenv("EMAIL_NOTIFICATIONS", "false").lower() == "true":
            logger.info(
                "EMAIL -> user=%s event=%s msg=%s",
                notification.user_id,
                notification.event_type,
                notification.message,
            )


class NotificationService:
    """Suscriptor del EventBus que genera Notifications ante eventos de dominio."""

    def __init__(
        self,
        channels: list[NotificationChannel],
        user_repo: UserRepository | None = None,
    ) -> None:
        self._channels = channels
        self._users = user_repo or UserRepository()

    def _notify(self, notification: Notification) -> None:
        for channel in self._channels:
            channel.send(notification)

    def _notify_role(self, role: Role, message: str, event_type: str) -> None:
        for user in self._users.get_by_role(role):
            self._notify(Notification(
                user_id=user.id,
                message=message,
                event_type=event_type,
            ))

    # ----- handlers -----

    def on_request_created(self, event: RequestCreated) -> None:
        self._notify(Notification(
            user_id=str(event.requester_id),
            message=f"Tu solicitud '{event.title}' fue creada.",
            event_type="REQUEST_CREATED",
        ))

    def on_request_submitted(self, event: RequestSubmitted) -> None:
        self._notify(Notification(
            user_id=str(event.requester_id),
            message=f"Tu solicitud '{event.title}' fue enviada para revisión.",
            event_type="REQUEST_SUBMITTED",
        ))

    def on_tech_review_required(self, event: TechReviewRequired) -> None:
        self._notify_role(
            Role.TECH_LEAD,
            f"Nueva revisión técnica pendiente: '{event.title}'.",
            "TECH_REVIEW_REQUIRED",
        )

    def on_ops_review_required(self, event: OpsReviewRequired) -> None:
        self._notify_role(
            Role.OPS_REVIEWER,
            f"Nueva revisión de Operations pendiente: '{event.title}'.",
            "OPS_REVIEW_REQUIRED",
        )

    def on_security_review_required(self, event: SecurityReviewRequired) -> None:
        self._notify_role(
            Role.SECURITY_REVIEWER,
            f"Nueva revisión de Security pendiente: '{event.title}'.",
            "SECURITY_REVIEW_REQUIRED",
        )

    def on_reviewer_assigned(self, event: ReviewerAssigned) -> None:
        self._notify(Notification(
            user_id=str(event.reviewer_id),
            message=f"Se te asignó como revisor ({event.area}) de la solicitud {event.request_id}.",
            event_type="REVIEWER_ASSIGNED",
        ))

    def on_request_approved(self, event: RequestApproved) -> None:
        if event.requester_id is not None:
            self._notify(Notification(
                user_id=str(event.requester_id),
                message=f"Tu solicitud {event.request_id} fue aprobada.",
                event_type="REQUEST_APPROVED",
            ))

    def on_request_rejected(self, event: RequestRejected) -> None:
        if event.requester_id is not None:
            self._notify(Notification(
                user_id=str(event.requester_id),
                message=f"Tu solicitud {event.request_id} fue rechazada. Motivo: {event.comment}",
                event_type="REQUEST_REJECTED",
            ))

    def on_changes_requested(self, event: ChangesRequested) -> None:
        if event.requester_id is not None:
            self._notify(Notification(
                user_id=str(event.requester_id),
                message=f"Se solicitaron cambios en la solicitud {event.request_id}: {event.comment}",
                event_type="CHANGES_REQUESTED",
            ))

    def on_request_scheduled(self, event: RequestScheduled) -> None:
        # Notifica al solicitante y a stakeholders (Tech Lead y Ops como mínimo)
        if event.requester_id is not None:
            self._notify(Notification(
                user_id=str(event.requester_id),
                message=f"Tu solicitud {event.request_id} fue agendada para {event.scheduled_at}.",
                event_type="CHANGE_SCHEDULED",
            ))
        for role in (Role.TECH_LEAD, Role.OPS_REVIEWER):
            self._notify_role(
                role,
                f"Cambio agendado: solicitud {event.request_id} para {event.scheduled_at}.",
                "CHANGE_SCHEDULED",
            )

    def on_request_executed(self, event: RequestExecuted) -> None:
        if event.requester_id is not None:
            self._notify(Notification(
                user_id=str(event.requester_id),
                message=f"Tu solicitud {event.request_id} fue ejecutada.",
                event_type="CHANGE_EXECUTED",
            ))

    def on_request_failed(self, event: RequestFailed) -> None:
        if event.requester_id is not None:
            self._notify(Notification(
                user_id=str(event.requester_id),
                message=f"La ejecución de {event.request_id} falló. Motivo: {event.reason}",
                event_type="CHANGE_FAILED",
            ))
        # Tech Lead también es notificado cuando algo falla
        self._notify_role(
            Role.TECH_LEAD,
            f"Falla al ejecutar solicitud {event.request_id}: {event.reason}",
            "CHANGE_FAILED",
        )

    def on_request_cancelled(self, event: RequestCancelled) -> None:
        if event.requester_id is not None:
            self._notify(Notification(
                user_id=str(event.requester_id),
                message=f"La solicitud {event.request_id} fue cancelada.",
                event_type="REQUEST_CANCELLED",
            ))
