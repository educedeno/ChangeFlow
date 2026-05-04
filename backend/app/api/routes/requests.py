"""Rutas de solicitudes: CRUD + submit + approve/reject/changes + assign + cancel + schedule + execute + fail."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_approval_repo,
    get_approve_use_case,
    get_assign_use_case,
    get_cancel_use_case,
    get_change_request_repo,
    get_create_use_case,
    get_current_user_id,
    get_execute_use_case,
    get_fail_use_case,
    get_get_use_case,
    get_list_use_case,
    get_reject_use_case,
    get_request_changes_use_case,
    get_schedule_use_case,
    get_submit_use_case,
)
from app.api.schemas import (
    ActionResponse,
    AssignReviewerRequest,
    ChangeRequestView,
    CreateChangeRequestPayload,
    FailRequest,
    RejectRequest,
    RequestChangesRequest,
    ScheduleRequest,
)
from app.application.dtos import CreateChangeRequestInput
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

router = APIRouter(prefix="/requests", tags=["requests"])


def _result_to_response(result, default_status: int = 400):
    if not result.success:
        msg = result.message.lower()
        if "no encontrada" in msg or "no encontrado" in msg:
            raise HTTPException(status_code=404, detail=result.message)
        if "autorizado" in msg or "permisos" in msg:
            raise HTTPException(status_code=403, detail=result.message)
        raise HTTPException(status_code=default_status, detail=result.message)
    return ActionResponse(
        success=True,
        message=result.message,
        new_status=(result.data or {}).get("new_status"),
    )


@router.post("/", response_model=ChangeRequestView, status_code=201)
def create_request(
    payload: CreateChangeRequestPayload,
    use_case: CreateChangeRequestUseCase = Depends(get_create_use_case),
):
    output = use_case.execute(CreateChangeRequestInput(
        title=payload.title,
        description=payload.description,
        affected_system=payload.affected_system,
        risk_level=payload.risk_level,
        requester_id=payload.requester_id,
        rollback_plan=payload.rollback_plan,
    ))
    return ChangeRequestView(**output.__dict__)


@router.get("/", response_model=list[ChangeRequestView])
def list_requests(use_case: ListChangeRequestsUseCase = Depends(get_list_use_case)):
    return [ChangeRequestView(**o.__dict__) for o in use_case.execute()]


# Endpoint que el frontend usa para mostrar la bandeja del aprobador.
@router.get("/approvals/mine")
def my_pending_approvals(
    current_user: UUID = Depends(get_current_user_id),
    approval_repo=Depends(get_approval_repo),
    request_repo=Depends(get_change_request_repo),
):
    pending = approval_repo.list_pending_for_reviewer(current_user)
    out = []
    for ap in pending:
        cr = request_repo.get_by_id(ap.request_id)
        out.append({
            "approval_id": str(ap.id),
            "request_id": str(ap.request_id),
            "area": ap.area.value,
            "status": ap.status.value,
            "request_title": cr.title if cr else None,
            "request_status": cr.status.value if cr else None,
            "risk_level": cr.risk_level.value if cr else None,
            "created_at": ap.created_at.isoformat() if ap.created_at else None,
        })
    return out


@router.get("/{request_id}", response_model=ChangeRequestView)
def get_request(
    request_id: UUID,
    use_case: GetChangeRequestUseCase = Depends(get_get_use_case),
):
    try:
        return ChangeRequestView(**use_case.execute(request_id).__dict__)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{request_id}/submit", response_model=ActionResponse)
def submit_request(
    request_id: UUID,
    current_user: UUID = Depends(get_current_user_id),
    use_case: SubmitRequestUseCase = Depends(get_submit_use_case),
):
    return _result_to_response(use_case.run(request_id, current_user))


@router.post("/{approval_id}/approve", response_model=ActionResponse)
def approve_request(
    approval_id: UUID,
    current_user: UUID = Depends(get_current_user_id),
    use_case: ApproveRequestUseCase = Depends(get_approve_use_case),
):
    return _result_to_response(use_case.run(approval_id=approval_id, reviewer_id=current_user))


@router.post("/{approval_id}/reject", response_model=ActionResponse)
def reject_request(
    approval_id: UUID,
    payload: RejectRequest,
    current_user: UUID = Depends(get_current_user_id),
    use_case: RejectRequestUseCase = Depends(get_reject_use_case),
):
    return _result_to_response(use_case.run(
        approval_id=approval_id,
        reviewer_id=current_user,
        comment=payload.comment,
    ))


@router.post("/{approval_id}/request-changes", response_model=ActionResponse)
def request_changes(
    approval_id: UUID,
    payload: RequestChangesRequest,
    current_user: UUID = Depends(get_current_user_id),
    use_case: RequestChangesUseCase = Depends(get_request_changes_use_case),
):
    return _result_to_response(use_case.run(
        approval_id=approval_id,
        reviewer_id=current_user,
        comment=payload.comment,
    ))


@router.post("/{request_id}/assign", response_model=ActionResponse, status_code=201)
def assign_reviewer(
    request_id: UUID,
    payload: AssignReviewerRequest,
    _current_user: UUID = Depends(get_current_user_id),
    use_case: AssignReviewerUseCase = Depends(get_assign_use_case),
):
    return _result_to_response(use_case.run(request_id=request_id, reviewer_id=payload.reviewer_id), default_status=400)


@router.post("/{request_id}/cancel", response_model=ActionResponse)
def cancel_request(
    request_id: UUID,
    current_user: UUID = Depends(get_current_user_id),
    use_case: CancelRequestUseCase = Depends(get_cancel_use_case),
):
    return _result_to_response(use_case.run(request_id=request_id, actor_id=current_user))


@router.post("/{request_id}/schedule", response_model=ActionResponse)
def schedule_request(
    request_id: UUID,
    payload: ScheduleRequest,
    _current_user: UUID = Depends(get_current_user_id),
    use_case: ScheduleRequestUseCase = Depends(get_schedule_use_case),
):
    return _result_to_response(use_case.run(request_id=request_id, scheduled_at=payload.scheduled_at))


@router.post("/{request_id}/execute", response_model=ActionResponse)
def execute_request(
    request_id: UUID,
    _current_user: UUID = Depends(get_current_user_id),
    use_case: ExecuteRequestUseCase = Depends(get_execute_use_case),
):
    return _result_to_response(use_case.run(request_id=request_id))


@router.post("/{request_id}/fail", response_model=ActionResponse)
def fail_request(
    request_id: UUID,
    payload: FailRequest,
    _current_user: UUID = Depends(get_current_user_id),
    use_case: MarkFailedUseCase = Depends(get_fail_use_case),
):
    return _result_to_response(use_case.run(request_id=request_id, reason=payload.reason))
