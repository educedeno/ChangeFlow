from dataclasses import dataclass

@dataclass
class UserCreated:
    user_id: str
    email: str
    role: str