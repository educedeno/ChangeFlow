
import uuid
from app.domain.entities import User, UserFactory
from app.domain.enums import Role
from app.infrastructure.auth.password_hasher import hash_password

# Simulated in-memory DB for MVP
# Replace with real DB later

_users_db: dict[str, User] = {}


def _seed():
    """Seed one admin user for testing."""
    admin = UserFactory.create(
        id=str(uuid.uuid4()),
        name="Admin",
        email="admin@changeflow.com",
        hashed_password=hash_password("admin1234"),
        role=Role.ADMIN,
    )
    _users_db[admin.email] = admin

_seed()


class UserRepository:
    def get_by_email(self, email: str) -> User | None:
        return _users_db.get(email)

    def get_by_id(self, user_id: str) -> User | None:
        for user in _users_db.values():
            if user.id == user_id:
                return user
        return None

    def save(self, user: User) -> User:
        _users_db[user.email] = user
        return user

    def get_all(self) -> list[User]:
        return list(_users_db.values())

    def delete(self, user_id: str) -> bool:
        for email, user in _users_db.items():
            if user.id == user_id:
                del _users_db[email]
                return True
        return False