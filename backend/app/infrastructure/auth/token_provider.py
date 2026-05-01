from jose import jwt, JWTError
from datetime import datetime, timedelta
import os


class TokenProvider:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.secret = os.getenv("JWT_SECRET", "changeflow-secret-key")
            cls._instance.algorithm = "HS256"
            cls._instance.expire_minutes = 60
        return cls._instance

    def create_token(self, user_id: str, email: str, role: str) -> str:
        payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "exp": datetime.utcnow() + timedelta(minutes=self.expire_minutes),
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.secret, algorithms=[self.algorithm])
        except JWTError:
            raise ValueError("Token inválido o expirado")