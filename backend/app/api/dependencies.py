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