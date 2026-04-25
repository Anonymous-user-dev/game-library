from pydantic import BaseModel, field_validator
from auth_utils import validate_password_strength

class Token(BaseModel):
    access_token: str
    token_type: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    def validate(cls, v):
        return validate_password_strength(v)