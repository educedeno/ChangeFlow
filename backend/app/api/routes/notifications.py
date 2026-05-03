"""Rutas de notificaciones: GET /notifications/me, POST /notifications/{id}/read."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user, get_notification_repo
from app.api.schemas import NotificationResponse
from app.infrastructure.repositories.notification_repository import (
    SQLAlchemyNotificationRepository,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/me", response_model=List[NotificationResponse])
def list_my_notifications(
    current_user: dict = Depends(get_current_user),
    repo: SQLAlchemyNotificationRepository = Depends(get_notification_repo),
):
    """Devuelve todas las notificaciones del usuario autenticado, ordenadas por fecha desc."""
    user_id = current_user["sub"]
    notifications = repo.list_for_user(user_id)
    return [
        NotificationResponse(
            id=n.id,
            user_id=n.user_id,
            message=n.message,
            event_type=n.event_type,
            read=n.read,
            created_at=n.created_at,
        )
        for n in notifications
    ]


@router.post("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
def mark_notification_read(
    notification_id: UUID,
    current_user: dict = Depends(get_current_user),
    repo: SQLAlchemyNotificationRepository = Depends(get_notification_repo),
):
    """Marca una notificación como leída. Solo el dueño puede marcarla."""
    user_id = current_user["sub"]
    success = repo.mark_read(notification_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada o no pertenece al usuario.",
        )
