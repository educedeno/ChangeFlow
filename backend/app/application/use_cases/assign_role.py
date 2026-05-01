from domain.enums import Role, Permission
from domain.value_objects import ROLE_PERMISSIONS
from infrastructure.repositories.user_repository import UserRepository


class AssignRoleUseCase:
    def __init__(self):
        self.user_repo = UserRepository()

    def execute(self, user_id: str, new_role: Role):
        user = self.user_repo.get_by_id(user_id)

        if not user:
            raise ValueError("Usuario no encontrado")

        user.role = new_role
        user.permissions = ROLE_PERMISSIONS.get(new_role, [])

        self.user_repo.save(user)
        return user