from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class DomainEvent:
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UserCreated(DomainEvent):
    user_id: str = ""
    email: str = ""
    role: str = ""


@dataclass
class RequestCreated(DomainEvent):
    request_id: UUID = None
    requester_id: UUID = None
    title: str = ""
    risk_level: str = ""


@dataclass
class RequestSubmitted(DomainEvent):
    request_id: UUID = None
    requester_id: UUID = None
    title: str = ""


@dataclass
class RequestApproved(DomainEvent):
    request_id: UUID = None
    reviewer_id: UUID = None
    approval_id: UUID = None


@dataclass
class RequestRejected(DomainEvent):
    request_id: UUID = None
    reviewer_id: UUID = None
    approval_id: UUID = None
    comment: str = ""


@dataclass
class ReviewerAssigned(DomainEvent):
    request_id: UUID = None
    reviewer_id: UUID = None
    approval_id: UUID = None


@dataclass
class ChangesRequested(DomainEvent):
    request_id: UUID = None
    reviewer_id: UUID = None
    approval_id: UUID = None
    comment: str = ""
