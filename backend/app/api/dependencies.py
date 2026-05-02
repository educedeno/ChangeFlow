"""
Dependencies de FastAPI: inyección de repositorios, casos de uso y usuario actual.
"""

from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.application.use_cases.approve_request import ApproveRequestUseCase
from app.application.use_cases.assign_reviewer import AssignReviewerUseCase
from app.application.use_cases.reject_request import RejectRequestUseCase
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.approval_repository import (
    SQLAlchemyApprovalRepository,
)
from app.infrastructure.repositories.change_request_repository import (
    SQLAlchemyChangeRequestRepository,
)


# ---- Repositorios ----

def get_approval_repo(db: Session = Depends(get_db)):
    return SQLAlchemyApprovalRepository(db)


def get_change_request_repo(db: Session = Depends(get_db)):
    return SQLAlchemyChangeRequestRepository(db)


# ---- Casos de uso ----

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


def get_assign_use_case(
    approval_repo=Depends(get_approval_repo),
    request_repo=Depends(get_change_request_repo),
):
    return AssignReviewerUseCase(approval_repo, request_repo)


# ---- Usuario actual (placeholder) ----

def get_current_user_id(x_user_id: str = Header(None)) -> UUID:
    """
    Placeholder de autenticación. Cuando se implemente JWT, esto se
    reemplaza por una dependencia que decodifique el token.
    Por ahora, espera el header X-User-Id.
    """
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
def get_change_request_repository():
    class FakeRepository:
        def __init__(self):
            self.data = []

        def save(self, change_request):
            self.data.append(change_request)

        def get_all(self):
            return self.data

        def get_by_id(self, request_id):
            for cr in self.data:
                if cr.id == request_id:
                    return cr
            return None

    return FakeRepository()
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from infrastructure.auth.token_provider import TokenProvider
from domain.enums import Role


bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    token = credentials.credentials
    try:
        payload = TokenProvider().decode_token(token)
        return payload  # {"sub": user_id, "email": ..., "role": ...}
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
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
