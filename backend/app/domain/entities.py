from dataclasses import dataclass, field
from domain.enums import Role, Permission
from domain.value_objects import ROLE_PERMISSIONS

@dataclass
class User:
    id: str
    name: str
    email: str
    hashed_password: str
    role: Role
    is_active: bool = True
    permissions: list[Permission] = field(default_factory=list)

    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions


class UserFactory:
    @staticmethod
    def create(
        id: str,
        name: str,
        email: str,
        hashed_password: str,
        role: Role,
        is_active: bool = True,
    ) -> User:
        permissions = ROLE_PERMISSIONS.get(role, [])
        return User(
            id=id,
            name=name,
            email=email,
            hashed_password=hashed_password,
            role=role,
            is_active=is_active,
            permissions=permissions,
        )