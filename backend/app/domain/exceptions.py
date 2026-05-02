class DomainError(Exception):
    """Error base del dominio."""
    pass


class InvalidStateTransitionError(DomainError):
    """Se lanza cuando se intenta una transición de estado no permitida."""
    pass


class BusinessRuleViolationError(DomainError):
    """Se lanza cuando una regla de negocio es violada."""
    pass