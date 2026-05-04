"""Modelos ORM (SQLAlchemy)."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from app.domain.enums import (
    ApprovalArea,
    ApprovalStatus,
    DecisionAction,
    RequestStatus,
    RiskLevel,
)
from app.infrastructure.db.base import Base


class ChangeRequestModel(Base):
    __tablename__ = "change_requests"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(200), nullable=False, default="")
    description = Column(Text, nullable=False, default="")
    affected_system = Column(String(200), nullable=False, default="")
    requester_id = Column(PGUUID(as_uuid=True), nullable=True)
    status = Column(
        SAEnum(RequestStatus, name="request_status"),
        nullable=False,
        default=RequestStatus.DRAFT,
    )
    risk_level = Column(
        SAEnum(RiskLevel, name="risk_level"),
        nullable=False,
        default=RiskLevel.LOW,
    )
    rollback_plan = Column(Text, nullable=True)
    failure_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    scheduled_at = Column(DateTime, nullable=True)
    executed_at = Column(DateTime, nullable=True)


class ApprovalModel(Base):
    __tablename__ = "approvals"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    request_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("change_requests.id"),
        nullable=False,
    )
    reviewer_id = Column(PGUUID(as_uuid=True), nullable=False)
    area = Column(
        SAEnum(ApprovalArea, name="approval_area"),
        nullable=False,
    )
    status = Column(
        SAEnum(ApprovalStatus, name="approval_status"),
        nullable=False,
        default=ApprovalStatus.PENDING,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    decided_at = Column(DateTime, nullable=True)

    decisions = relationship("DecisionModel", back_populates="approval")


class DecisionModel(Base):
    __tablename__ = "decisions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    approval_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("approvals.id"),
        nullable=False,
    )
    action = Column(
        SAEnum(DecisionAction, name="decision_action"),
        nullable=False,
    )
    comment = Column(Text, nullable=True)
    decided_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    approval = relationship("ApprovalModel", back_populates="decisions")


class NotificationModel(Base):
    __tablename__ = "notifications"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    event_type = Column(String(100), nullable=False)
    read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AuditEntryModel(Base):
    __tablename__ = "audit_entries"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    actor_id = Column(String, nullable=False)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String, nullable=False)
    detail = Column(Text, nullable=True)
    occurred_at = Column(DateTime, default=datetime.utcnow, nullable=False)
