from enum import Enum


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RequestStatus(str, Enum):
    """Ciclo de vida completo de una solicitud de cambio."""
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    TECH_REVIEW = "TECH_REVIEW"
    OPS_REVIEW = "OPS_REVIEW"
    SECURITY_REVIEW = "SECURITY_REVIEW"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    APPROVED = "APPROVED"
    SCHEDULED = "SCHEDULED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class DecisionAction(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REQUEST_CHANGES = "REQUEST_CHANGES"


class ApprovalArea(str, Enum):
    """Área que debe revisar una Approval. Determina qué rol puede atenderla."""
    TECH = "TECH"
    OPS = "OPS"
    SECURITY = "SECURITY"


class Role(str, Enum):
    ENGINEER = "ENGINEER"
    TECH_LEAD = "TECH_LEAD"
    OPS_REVIEWER = "OPS_REVIEWER"
    SECURITY_REVIEWER = "SECURITY_REVIEWER"
    ADMIN = "ADMIN"


class Permission(str, Enum):
    CREATE_CHANGE = "CREATE_CHANGE"
    REVIEW_TECH = "REVIEW_TECH"
    REVIEW_OPS = "REVIEW_OPS"
    REVIEW_SECURITY = "REVIEW_SECURITY"
    MANAGE_USERS = "MANAGE_USERS"
    VIEW_ALL = "VIEW_ALL"
    CANCEL_ANY = "CANCEL_ANY"
