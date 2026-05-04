import uuid

from app.domain.entities import User, UserFactory
from app.domain.enums import Role


# Base de datos en memoria (MVP). El seed cubre un usuario por cada rol
# para que las pruebas del flujo completo (LOW/MEDIUM/HIGH) sean posibles.

_users_db: dict[str, User] = {}


def _seed():
    from app.infrastructure.auth.password_hasher import hash_password

    seeds = [
        ("Admin", "admin@changeflow.com", "admin1234", Role.ADMIN),
        ("Engineer", "engineer@changeflow.com", "engineer1234", Role.ENGINEER),
        ("Tech Lead", "techlead@changeflow.com", "techlead1234", Role.TECH_LEAD),
        ("Ops Reviewer", "ops@changeflow.com", "ops1234", Role.OPS_REVIEWER),
        ("Security Reviewer", "security@changeflow.com", "security1234", Role.SECURITY_REVIEWER),
    ]
    for name, email, pwd, role in seeds:
        if email in _users_db:
            continue
        user = UserFactory.create(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            hashed_password=hash_password(pwd),
            role=role,
        )
        _users_db[user.email] = user


_seed()


class UserRepository:
    def get_by_email(self, email: str) -> User | None:
        return _users_db.get(email)

    def get_by_id(self, user_id: str) -> User | None:
        for user in _users_db.values():
            if user.id == user_id:
                return user
        return None

    def get_by_role(self, role: Role) -> list[User]:
        return [u for u in _users_db.values() if u.role == role and u.is_active]

    def first_by_role(self, role: Role) -> User | None:
        users = self.get_by_role(role)
        return users[0] if users else None

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
