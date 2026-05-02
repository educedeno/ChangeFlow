"""Punto de entrada de la API FastAPI."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import audit as audit_router
from app.api.routes import notifications as notifications_router
from app.api.routes import requests as requests_router
from app.application.services.audit_service import AuditService
from app.application.services.event_bus import EventBus
from app.application.services.notification_service import (
    EmailChannel,
    InAppChannel,
    NotificationService,
)
from app.domain.events import (
    ChangesRequested,
    RequestApproved,
    RequestCreated,
    RequestRejected,
    RequestSubmitted,
    ReviewerAssigned,
    UserCreated,
)
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.repositories.audit_repository import SQLAlchemyAuditRepository
from app.infrastructure.repositories.notification_repository import SQLAlchemyNotificationRepository

# Se ejecuta al arrancar y al apagar la app (antes y después del yield, respectivamente).
# Instancia repos y servicios, y registra todos los handlers en el EventBus.
@asynccontextmanager
async def lifespan(app: FastAPI):
    session = SessionLocal()

    notification_repo = SQLAlchemyNotificationRepository(session)
    audit_repo = SQLAlchemyAuditRepository(session)

    channels = [InAppChannel(notification_repo)]
    if os.getenv("EMAIL_NOTIFICATIONS", "false").lower() == "true":
        channels.append(EmailChannel())
    notification_svc = NotificationService(channels)
    audit_svc = AuditService(audit_repo)

    bus = EventBus()

    bus.subscribe(RequestCreated, notification_svc.on_request_created)
    bus.subscribe(RequestSubmitted, notification_svc.on_request_submitted)
    bus.subscribe(RequestApproved, notification_svc.on_request_approved)
    bus.subscribe(RequestRejected, notification_svc.on_request_rejected)
    bus.subscribe(ReviewerAssigned, notification_svc.on_reviewer_assigned)
    bus.subscribe(ChangesRequested, notification_svc.on_changes_requested)

    bus.subscribe(UserCreated, audit_svc.on_user_created)
    bus.subscribe(RequestCreated, audit_svc.on_request_created)
    bus.subscribe(RequestSubmitted, audit_svc.on_request_submitted)
    bus.subscribe(RequestApproved, audit_svc.on_request_approved)
    bus.subscribe(RequestRejected, audit_svc.on_request_rejected)
    bus.subscribe(ReviewerAssigned, audit_svc.on_reviewer_assigned)
    bus.subscribe(ChangesRequested, audit_svc.on_changes_requested)

    yield  # la app corre aquí

    session.close()


app = FastAPI(title="ChangeFlow API", lifespan=lifespan)

app.include_router(requests_router.router)
app.include_router(notifications_router.router)
app.include_router(audit_router.router)


@app.get("/health")
def health():
    return {"status": "ok"}