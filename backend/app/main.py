"""Punto de entrada de la API FastAPI."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import audit as audit_router
from app.api.routes import auth as auth_router
from app.api.routes import notifications as notifications_router
from app.api.routes import requests as requests_router
from app.api.routes import users as users_router
from app.application.services.audit_service import AuditService
from app.application.services.event_bus import EventBus
from app.application.services.notification_service import (
    EmailChannel,
    InAppChannel,
    NotificationService,
)
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
    UserCreated,
)
from app.infrastructure.db import models  # noqa: F401
from app.infrastructure.db.base import Base
from app.infrastructure.db.session import SessionLocal, engine
from app.infrastructure.repositories.audit_repository import SQLAlchemyAuditRepository
from app.infrastructure.repositories.notification_repository import SQLAlchemyNotificationRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    notification_repo = SQLAlchemyNotificationRepository(session)
    audit_repo = SQLAlchemyAuditRepository(session)

    channels = [InAppChannel(notification_repo)]
    if os.getenv("EMAIL_NOTIFICATIONS", "false").lower() == "true":
        channels.append(EmailChannel())
    notification_svc = NotificationService(channels)
    audit_svc = AuditService(audit_repo)

    bus = EventBus()
    bus.reset()  # evita acumular handlers entre reinicios en dev

    # ----- Notificaciones -----
    bus.subscribe(RequestCreated, notification_svc.on_request_created)
    bus.subscribe(RequestSubmitted, notification_svc.on_request_submitted)
    bus.subscribe(TechReviewRequired, notification_svc.on_tech_review_required)
    bus.subscribe(OpsReviewRequired, notification_svc.on_ops_review_required)
    bus.subscribe(SecurityReviewRequired, notification_svc.on_security_review_required)
    bus.subscribe(ReviewerAssigned, notification_svc.on_reviewer_assigned)
    bus.subscribe(RequestApproved, notification_svc.on_request_approved)
    bus.subscribe(RequestRejected, notification_svc.on_request_rejected)
    bus.subscribe(ChangesRequested, notification_svc.on_changes_requested)
    bus.subscribe(RequestScheduled, notification_svc.on_request_scheduled)
    bus.subscribe(RequestExecuted, notification_svc.on_request_executed)
    bus.subscribe(RequestFailed, notification_svc.on_request_failed)
    bus.subscribe(RequestCancelled, notification_svc.on_request_cancelled)

    # ----- Auditoría -----
    bus.subscribe(UserCreated, audit_svc.on_user_created)
    bus.subscribe(RequestCreated, audit_svc.on_request_created)
    bus.subscribe(RequestSubmitted, audit_svc.on_request_submitted)
    bus.subscribe(TechReviewRequired, audit_svc.on_tech_review_required)
    bus.subscribe(OpsReviewRequired, audit_svc.on_ops_review_required)
    bus.subscribe(SecurityReviewRequired, audit_svc.on_security_review_required)
    bus.subscribe(RequestApproved, audit_svc.on_request_approved)
    bus.subscribe(RequestRejected, audit_svc.on_request_rejected)
    bus.subscribe(ReviewerAssigned, audit_svc.on_reviewer_assigned)
    bus.subscribe(ChangesRequested, audit_svc.on_changes_requested)
    bus.subscribe(RequestScheduled, audit_svc.on_request_scheduled)
    bus.subscribe(RequestExecuted, audit_svc.on_request_executed)
    bus.subscribe(RequestFailed, audit_svc.on_request_failed)
    bus.subscribe(RequestCancelled, audit_svc.on_request_cancelled)

    yield

    session.close()


app = FastAPI(title="ChangeFlow API", lifespan=lifespan)

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(requests_router.router)
app.include_router(notifications_router.router)
app.include_router(audit_router.router)


@app.get("/health")
def health():
    return {"status": "ok"}
