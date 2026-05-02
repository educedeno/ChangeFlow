"""Tests de NotificationService, AuditService y EventBus usando fakes en memoria."""

from typing import List
from uuid import uuid4

import pytest

from app.application.services.audit_service import AuditService
from app.application.services.event_bus import EventBus
from app.application.services.notification_service import NotificationService
from app.domain.entities import AuditEntry, Notification
from app.domain.events import (
    ChangesRequested,
    RequestApproved,
    RequestCreated,
    RequestRejected,
    RequestSubmitted,
    ReviewerAssigned,
    UserCreated,
)


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------

class FakeNotificationRepository:
    def __init__(self):
        self.saved: List[Notification] = []

    def save(self, notification: Notification) -> None:
        self.saved.append(notification)


class FakeAuditRepository:
    def __init__(self):
        self.saved: List[AuditEntry] = []

    def save(self, entry: AuditEntry) -> None:
        self.saved.append(entry)


# ---------------------------------------------------------------------------
# NotificationService
# ---------------------------------------------------------------------------

class TestNotificationService:
    def setup_method(self):
        self.repo = FakeNotificationRepository()
        self.service = NotificationService(self.repo)

    def test_on_request_created_saves_notification(self):
        event = RequestCreated(
            request_id=uuid4(),
            requester_id=uuid4(),
            title="Deploy v2",
            risk_level="LOW",
        )
        self.service.on_request_created(event)

        assert len(self.repo.saved) == 1
        n = self.repo.saved[0]
        assert n.user_id == str(event.requester_id)
        assert n.event_type == "REQUEST_CREATED"
        assert "Deploy v2" in n.message
        assert n.read is False

    def test_on_request_submitted_saves_notification(self):
        event = RequestSubmitted(
            request_id=uuid4(),
            requester_id=uuid4(),
            title="Fix config",
        )
        self.service.on_request_submitted(event)

        assert len(self.repo.saved) == 1
        n = self.repo.saved[0]
        assert n.user_id == str(event.requester_id)
        assert n.event_type == "REQUEST_SUBMITTED"

    def test_on_request_approved_notifies_reviewer(self):
        event = RequestApproved(
            request_id=uuid4(),
            reviewer_id=uuid4(),
            approval_id=uuid4(),
        )
        self.service.on_request_approved(event)

        assert len(self.repo.saved) == 1
        n = self.repo.saved[0]
        assert n.user_id == str(event.reviewer_id)
        assert n.event_type == "REQUEST_APPROVED"

    def test_on_request_rejected_includes_comment(self):
        event = RequestRejected(
            request_id=uuid4(),
            reviewer_id=uuid4(),
            approval_id=uuid4(),
            comment="Falta plan de rollback",
        )
        self.service.on_request_rejected(event)

        n = self.repo.saved[0]
        assert n.event_type == "REQUEST_REJECTED"
        assert "Falta plan de rollback" in n.message

    def test_on_reviewer_assigned_notifies_reviewer(self):
        event = ReviewerAssigned(
            request_id=uuid4(),
            reviewer_id=uuid4(),
            approval_id=uuid4(),
        )
        self.service.on_reviewer_assigned(event)

        n = self.repo.saved[0]
        assert n.user_id == str(event.reviewer_id)
        assert n.event_type == "REVIEWER_ASSIGNED"

    def test_on_changes_requested_saves_notification(self):
        event = ChangesRequested(
            request_id=uuid4(),
            reviewer_id=uuid4(),
            approval_id=uuid4(),
            comment="Ajusta el impacto en prod",
        )
        self.service.on_changes_requested(event)

        n = self.repo.saved[0]
        assert n.event_type == "CHANGES_REQUESTED"
        assert "Ajusta el impacto en prod" in n.message


# ---------------------------------------------------------------------------
# AuditService
# ---------------------------------------------------------------------------

class TestAuditService:
    def setup_method(self):
        self.repo = FakeAuditRepository()
        self.service = AuditService(self.repo)

    def test_on_user_created_saves_audit_entry(self):
        user_id = str(uuid4())
        event = UserCreated(user_id=user_id, email="a@b.com", role="ENGINEER")
        self.service.on_user_created(event)

        assert len(self.repo.saved) == 1
        e = self.repo.saved[0]
        assert e.actor_id == user_id
        assert e.action == "USER_CREATED"
        assert e.entity_type == "User"
        assert e.entity_id == user_id

    def test_on_request_created_saves_audit_entry(self):
        request_id = uuid4()
        requester_id = uuid4()
        event = RequestCreated(
            request_id=request_id,
            requester_id=requester_id,
            title="Deploy v2",
            risk_level="HIGH",
        )
        self.service.on_request_created(event)

        e = self.repo.saved[0]
        assert e.action == "REQUEST_CREATED"
        assert e.entity_type == "ChangeRequest"
        assert e.entity_id == str(request_id)
        assert "HIGH" in e.detail

    def test_on_request_approved_records_reviewer(self):
        request_id = uuid4()
        reviewer_id = uuid4()
        event = RequestApproved(
            request_id=request_id,
            reviewer_id=reviewer_id,
            approval_id=uuid4(),
        )
        self.service.on_request_approved(event)

        e = self.repo.saved[0]
        assert e.actor_id == str(reviewer_id)
        assert e.action == "REQUEST_APPROVED"

    def test_on_request_rejected_stores_comment_as_detail(self):
        event = RequestRejected(
            request_id=uuid4(),
            reviewer_id=uuid4(),
            approval_id=uuid4(),
            comment="Riesgo no justificado",
        )
        self.service.on_request_rejected(event)

        e = self.repo.saved[0]
        assert e.action == "REQUEST_REJECTED"
        assert e.detail == "Riesgo no justificado"

    def test_on_reviewer_assigned_records_approval_id(self):
        approval_id = uuid4()
        event = ReviewerAssigned(
            request_id=uuid4(),
            reviewer_id=uuid4(),
            approval_id=approval_id,
        )
        self.service.on_reviewer_assigned(event)

        e = self.repo.saved[0]
        assert e.action == "REVIEWER_ASSIGNED"
        assert str(approval_id) in e.detail

    def test_on_changes_requested_stores_comment(self):
        event = ChangesRequested(
            request_id=uuid4(),
            reviewer_id=uuid4(),
            approval_id=uuid4(),
            comment="Revisar impacto en base de datos",
        )
        self.service.on_changes_requested(event)

        e = self.repo.saved[0]
        assert e.action == "CHANGES_REQUESTED"
        assert e.detail == "Revisar impacto en base de datos"


# ---------------------------------------------------------------------------
# EventBus (Observer pattern)
# ---------------------------------------------------------------------------

class TestEventBus:
    def setup_method(self):
        # Resetear el Singleton entre tests
        EventBus().reset()

    def test_subscriber_receives_published_event(self):
        received = []
        bus = EventBus()
        bus.subscribe(RequestCreated, lambda e: received.append(e))

        event = RequestCreated(request_id=uuid4(), requester_id=uuid4(), title="X", risk_level="LOW")
        bus.publish(event)

        assert len(received) == 1
        assert received[0] is event

    def test_multiple_subscribers_all_called(self):
        calls = []
        bus = EventBus()
        bus.subscribe(RequestApproved, lambda e: calls.append("sub1"))
        bus.subscribe(RequestApproved, lambda e: calls.append("sub2"))

        bus.publish(RequestApproved(request_id=uuid4(), reviewer_id=uuid4(), approval_id=uuid4()))

        assert calls == ["sub1", "sub2"]

    def test_unrelated_event_does_not_trigger_subscriber(self):
        received = []
        bus = EventBus()
        bus.subscribe(RequestApproved, lambda e: received.append(e))

        bus.publish(RequestRejected(
            request_id=uuid4(), reviewer_id=uuid4(), approval_id=uuid4(), comment="x"
        ))

        assert len(received) == 0

    def test_singleton_is_same_instance(self):
        bus_a = EventBus()
        bus_b = EventBus()
        assert bus_a is bus_b

    def test_notification_service_wired_to_bus(self):
        """Prueba de integración: NotificationService conectado al EventBus."""
        repo = FakeNotificationRepository()
        service = NotificationService(repo)

        bus = EventBus()
        bus.subscribe(RequestCreated, service.on_request_created)

        event = RequestCreated(
            request_id=uuid4(),
            requester_id=uuid4(),
            title="Integración",
            risk_level="MEDIUM",
        )
        bus.publish(event)

        assert len(repo.saved) == 1
        assert repo.saved[0].event_type == "REQUEST_CREATED"

    def test_audit_service_wired_to_bus(self):
        """Prueba de integración: AuditService conectado al EventBus."""
        repo = FakeAuditRepository()
        service = AuditService(repo)

        bus = EventBus()
        bus.subscribe(RequestSubmitted, service.on_request_submitted)

        event = RequestSubmitted(request_id=uuid4(), requester_id=uuid4(), title="Fix")
        bus.publish(event)

        assert len(repo.saved) == 1
        assert repo.saved[0].action == "REQUEST_SUBMITTED"
