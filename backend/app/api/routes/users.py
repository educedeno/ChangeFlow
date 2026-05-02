from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from domain.enums import Role
from application.use_cases.register_user import RegisterUserUseCase
from infrastructure.repositories.user_repository import UserRepository
from api.dependencies import get_current_user, require_role

router = APIRouter(prefix="/users", tags=["Users"])


# --- Schemas ---

class CreateUserRequest(BaseModel):
    name: str
    email: str
    password: str
    role: Role


class UpdateUserRequest(BaseModel):
    name: str | None = None
    is_active: bool | None = None


# --- Endpoints ---

@router.get("/")
def get_all_users(current_user: dict = Depends(require_role(Role.ADMIN))):
    repo = UserRepository()
    users = repo.get_all()
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role.value,
            "is_active": u.is_active,
        }
        for u in users
    ]


@router.post("/", status_code=201)
def create_user(
    body: CreateUserRequest,
    current_user: dict = Depends(require_role(Role.ADMIN)),
):
    use_case = RegisterUserUseCase()
    try:
        user = use_case.execute(
            name=body.name,
            email=body.email,
            password=body.password,
            role=body.role,
        )
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.value,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{user_id}")
def update_user(
    user_id: str,
    body: UpdateUserRequest,
    current_user: dict = Depends(require_role(Role.ADMIN)),
):
    repo = UserRepository()
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if body.name is not None:
        user.name = body.name
    if body.is_active is not None:
        user.is_active = body.is_active

    repo.save(user)
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active,
    }


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: str,
    current_user: dict = Depends(require_role(Role.ADMIN)),
):
    repo = UserRepository()
    deleted = repo.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")