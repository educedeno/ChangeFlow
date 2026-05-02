from enum import Enum


class RiskLevel(str, Enum):
    """Nivel de riesgo de un cambio técnico en ChangeFlow."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RequestStatus(str, Enum):
    """Estados del ciclo de vida de una solicitud de cambio."""
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    COMPLETED = "COMPLETED"


class ApprovalStatus(str, Enum):
    """Estado de una aprobación individual dentro de una solicitud."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class DecisionAction(str, Enum):
    """Acción tomada por un aprobador."""
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REQUEST_CHANGES = "REQUEST_CHANGES"
    
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
