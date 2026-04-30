from pydantic import BaseModel, EmailStr, field_validator, Field
from auth_utils import validate_password_strength

from schemas.game import GameResponse

class DeveloperCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    age: int

    @field_validator("password")
    def validate(cls, v):
        return validate_password_strength(v)

class DeveloperResponse(BaseModel):
    id: int
    username: str
    age: int

    games: list["GameResponse"] = Field(default_factory=list)

    model_config = {"from_attributes": True}