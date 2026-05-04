from app.domain.entities import User
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.auth.password_hasher import verify_password
from app.infrastructure.auth.token_provider import TokenProvider


class LoginUseCase:
    def __init__(self):
        self.user_repo = UserRepository()
        self.token_provider = TokenProvider()  # Singleton

    def execute(self, email: str, password: str) -> dict:
        user: User | None = self.user_repo.get_by_email(email)

        if not user:
            raise ValueError("Credenciales inválidas")

        if not user.is_active:
            raise ValueError("Usuario inactivo")

        if not verify_password(password, user.hashed_password):
            raise ValueError("Credenciales inválidas")

        token = self.token_provider.create_token(
            user_id=user.id,
            email=user.email,
            role=user.role.value,
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "id": user.id,
            "role": user.role.value,
            "name": user.name,
        }