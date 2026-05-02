def get_change_request_repository():
    class FakeRepository:
        def __init__(self):
            self.data = []

        def save(self, change_request):
            self.data.append(change_request)

        def get_all(self):
            return self.data

        def get_by_id(self, request_id):
            for cr in self.data:
                if cr.id == request_id:
                    return cr
            return None

    return FakeRepository()
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from infrastructure.auth.token_provider import TokenProvider
from domain.enums import Role


bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    token = credentials.credentials
    try:
        payload = TokenProvider().decode_token(token)
        return payload  # {"sub": user_id, "email": ..., "role": ...}
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )


def require_role(*allowed_roles: Role):
    def dependency(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role not in [r.value for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción",
            )
        return current_user
    return dependency
