"""Endpoints de aprobación, rechazo y asignación de reviewers."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_approve_use_case,
    get_assign_use_case,
    get_current_user_id,
    get_reject_use_case,
)
from app.api.schemas import (
    ActionResponse,
    AssignReviewerRequest,
    RejectRequest,
)
from app.application.use_cases.approve_request import ApproveRequestUseCase
from app.application.use_cases.assign_reviewer import AssignReviewerUseCase
from app.application.use_cases.reject_request import RejectRequestUseCase

router = APIRouter(prefix="/requests", tags=["approvals"])


@router.post(
    "/{approval_id}/approve",
    response_model=ActionResponse,
    status_code=status.HTTP_200_OK,
)
def approve_request(
    approval_id: UUID,
    current_user: UUID = Depends(get_current_user_id),
    use_case: ApproveRequestUseCase = Depends(get_approve_use_case),
):
    result = use_case.run(approval_id=approval_id, reviewer_id=current_user)
    if not result.success:
        # Diferenciar autorización vs. otros errores
        if "autorizado" in result.message.lower():
            raise HTTPException(status_code=403, detail=result.message)
        if "no encontrada" in result.message.lower():
            raise HTTPException(status_code=404, detail=result.message)
        raise HTTPException(status_code=400, detail=result.message)
    return ActionResponse(
        success=True,
        message=result.message,
        new_status=(result.data or {}).get("new_status"),
    )


@router.post(
    "/{approval_id}/reject",
    response_model=ActionResponse,
    status_code=status.HTTP_200_OK,
)
def reject_request(
    approval_id: UUID,
    payload: RejectRequest,
    current_user: UUID = Depends(get_current_user_id),
    use_case: RejectRequestUseCase = Depends(get_reject_use_case),
):
    result = use_case.run(
        approval_id=approval_id,
        reviewer_id=current_user,
        comment=payload.comment,
    )
    if not result.success:
        if "autorizado" in result.message.lower():
            raise HTTPException(status_code=403, detail=result.message)
        if "no encontrada" in result.message.lower():
            raise HTTPException(status_code=404, detail=result.message)
        raise HTTPException(status_code=400, detail=result.message)
    return ActionResponse(
        success=True,
        message=result.message,
        new_status=(result.data or {}).get("new_status"),
    )


@router.post(
    "/{request_id}/assign",
    response_model=ActionResponse,
    status_code=status.HTTP_201_CREATED,
)
def assign_reviewer(
    request_id: UUID,
    payload: AssignReviewerRequest,
    _current_user: UUID = Depends(get_current_user_id),
    use_case: AssignReviewerUseCase = Depends(get_assign_use_case),
):
    result = use_case.run(
        request_id=request_id, reviewer_id=payload.reviewer_id
    )
    if not result.success:
        if "no encontrada" in result.message.lower():
            raise HTTPException(status_code=404, detail=result.message)
        raise HTTPException(status_code=400, detail=result.message)
    return ActionResponse(success=True, message=result.message)