"""Dependencies de FastAPI: inyección de repos, casos de uso y usuario actual."""

from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.application.use_cases.approve_request import ApproveRequestUseCase
from app.application.use_cases.assign_reviewer import AssignReviewerUseCase
from app.application.use_cases.cancel_request import CancelRequestUseCase
from app.application.use_cases.create_change_request import CreateChangeRequestUseCase
from app.application.use_cases.execute_request import ExecuteRequestUseCase, MarkFailedUseCase
from app.application.use_cases.get_change_request import GetChangeRequestUseCase
from app.application.use_cases.list_change_requests import ListChangeRequestsUseCase
from app.application.use_cases.reject_request import RejectRequestUseCase
from app.application.use_cases.request_changes import RequestChangesUseCase
from app.application.use_cases.schedule_request import ScheduleRequestUseCase
from app.application.use_cases.submit_request import SubmitRequestUseCase
from app.domain.enums import Role
from app.infrastructure.auth.token_provider import TokenProvider
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.approval_repository import (
    SQLAlchemyApprovalRepository,
)
from app.infrastructure.repositories.audit_repository import SQLAlchemyAuditRepository
from app.infrastructure.repositories.change_request_repository import (
    SQLAlchemyChangeRequestRepository,
)
from app.infrastructure.repositories.notification_repository import (
    SQLAlchemyNotificationRepository,
)


# ---- Repositorios ----

def get_approval_repo(db: Session = Depends(get_db)):
    return SQLAlchemyApprovalRepository(db)


def get_change_request_repo(db: Session = Depends(get_db)):
    return SQLAlchemyChangeRequestRepository(db)


def get_notification_repo(db: Session = Depends(get_db)):
    return SQLAlchemyNotificationRepository(db)


def get_audit_repo(db: Session = Depends(get_db)):
    return SQLAlchemyAuditRepository(db)


# Alias usado por las rutas de creación/listado de requests.
def get_change_request_repository(db: Session = Depends(get_db)):
    return SQLAlchemyChangeRequestRepository(db)


# ---- Casos de uso ----

def get_create_use_case(
    request_repo=Depends(get_change_request_repo),
):
    return CreateChangeRequestUseCase(request_repo)


def get_list_use_case(request_repo=Depends(get_change_request_repo)):
    return ListChangeRequestsUseCase(request_repo)


def get_get_use_case(request_repo=Depends(get_change_request_repo)):
    return GetChangeRequestUseCase(request_repo)


def get_submit_use_case(
    request_repo=Depends(get_change_request_repo),
    approval_repo=Depends(get_approval_repo),
):
    return SubmitRequestUseCase(request_repo, approval_repo)


def get_approve_use_case(
    approval_repo=Depends(get_approval_repo),
    request_repo=Depends(get_change_request_repo),
):
    return ApproveRequestUseCase(approval_repo, request_repo)


def get_reject_use_case(
    approval_repo=Depends(get_approval_repo),
    request_repo=Depends(get_change_request_repo),
):
    return RejectRequestUseCase(approval_repo, request_repo)


def get_request_changes_use_case(
    approval_repo=Depends(get_approval_repo),
    request_repo=Depends(get_change_request_repo),
):
    return RequestChangesUseCase(approval_repo, request_repo)


def get_assign_use_case(
    approval_repo=Depends(get_approval_repo),
    request_repo=Depends(get_change_request_repo),
):
    return AssignReviewerUseCase(approval_repo, request_repo)


def get_cancel_use_case(request_repo=Depends(get_change_request_repo)):
    return CancelRequestUseCase(request_repo)


def get_schedule_use_case(request_repo=Depends(get_change_request_repo)):
    return ScheduleRequestUseCase(request_repo)


def get_execute_use_case(request_repo=Depends(get_change_request_repo)):
    return ExecuteRequestUseCase(request_repo)


def get_fail_use_case(request_repo=Depends(get_change_request_repo)):
    return MarkFailedUseCase(request_repo)


# ---- Usuario actual ----

def get_current_user_id(x_user_id: str = Header(None)) -> UUID:
    """Placeholder de auth: lee X-User-Id. Para JWT, usar get_current_user."""
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta header X-User-Id (placeholder de auth).",
        )
    try:
        return UUID(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-User-Id no es un UUID válido.",
        )


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    x_user_id: str | None = Header(None, alias="X-User-Id"),
) -> dict:
    """Acepta JWT (Bearer) o X-User-Id como fallback para el MVP."""
    if credentials is not None:
        try:
            payload = TokenProvider().decode_token(credentials.credentials)
            return payload
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
            )
    if x_user_id:
        return {"sub": x_user_id, "email": None, "role": None}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado.",
    )


def require_role(*allowed_roles: Role):
    def dependency(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role not in [r.value for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción",
            )
        return current_user
    return dependency
