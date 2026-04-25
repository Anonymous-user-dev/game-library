from pydantic import BaseModel, field_validator, EmailStr, Field
import re
from typing import List

class Token(BaseModel):
    access_token: str
    token_type: str

class GameCreate(BaseModel):
    name: str
    genre: str
    price: int


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
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

class GameResponse(BaseModel):
    id: int
    name: str
    genre: str
    price: int

    developer_id: int

    model_config = {"from_attributes": True}

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

    games: List[GameResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}



