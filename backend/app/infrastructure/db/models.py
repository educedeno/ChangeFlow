"""
Modelos ORM (SQLAlchemy).

Estos modelos viven en infraestructura, NO en el dominio. Son traducciones
1-a-1 de las entidades de dominio para persistir en PostgreSQL.

Nota: ChangeRequestModel es un placeholder mínimo. El compañero a cargo de
la entidad principal puede extenderlo con los campos que necesite.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from app.domain.enums import (
    ApprovalStatus,
    DecisionAction,
    RequestStatus,
    RiskLevel,
)
from app.infrastructure.db.base import Base


class ChangeRequestModel(Base):
    """
    Modelo placeholder de ChangeRequest. Solo incluye lo que necesita
    la feature de aprobación. Persona X que maneje la entidad principal
    puede extender este modelo o reemplazarlo y mantener los campos.
    """
    __tablename__ = "change_requests"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(200), nullable=False, default="")
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
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ApprovalModel(Base):
    __tablename__ = "approvals"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    request_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("change_requests.id"),
        nullable=False,
    )
    reviewer_id = Column(PGUUID(as_uuid=True), nullable=False)
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