from pydantic import BaseModel, EmailStr, field_validator, Field
import re

from schemas.game import GameResponse

class DeveloperCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    age: int

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 12:
            raise ValueError("Password must be at least 12 characters!")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")
        return value

class DeveloperResponse(BaseModel):
    id: int
    username: str
    age: int

    games: list["GameResponse"] = Field(default_factory=list)

    model_config = {"from_attributes": True}