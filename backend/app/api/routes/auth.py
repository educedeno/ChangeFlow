from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.application.use_cases.login import LoginUseCase

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(body: LoginRequest):
    use_case = LoginUseCase()
    try:
        result = use_case.execute(body.email, body.password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))