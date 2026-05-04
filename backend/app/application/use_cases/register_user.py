import uuid
from app.domain.entities import UserFactory
from app.domain.enums import Role
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.auth.password_hasher import hash_password


class RegisterUserUseCase:
    def __init__(self):
        self.user_repo = UserRepository()

    def execute(self, name: str, email: str, password: str, role: Role):
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise ValueError(f"Ya existe un usuario con el email {email}")

        user = UserFactory.create(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            hashed_password=hash_password(password),
            role=role,
        )

        return self.user_repo.save(user)