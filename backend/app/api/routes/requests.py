from fastapi import APIRouter, Depends
from uuid import UUID

from app.application.dtos import CreateChangeRequestInput
from app.application.use_cases.create_change_request import CreateChangeRequestUseCase
from app.application.use_cases.list_change_requests import ListChangeRequestsUseCase
from app.application.use_cases.get_change_request import GetChangeRequestUseCase
from app.api.dependencies import get_change_request_repository

router = APIRouter(prefix="/requests", tags=["requests"])


@router.post("/")
def create_request(
    input_data: CreateChangeRequestInput,
    repository=Depends(get_change_request_repository),
):
    use_case = CreateChangeRequestUseCase(repository)
    return use_case.execute(input_data)


@router.get("/")
def list_requests(repository=Depends(get_change_request_repository)):
    use_case = ListChangeRequestsUseCase(repository)
    return use_case.execute()


@router.get("/{request_id}")
def get_request(
    request_id: UUID,
    repository=Depends(get_change_request_repository),
):
    use_case = GetChangeRequestUseCase(repository)
    return use_case.execute(request_id)