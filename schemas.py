from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class GameCreate(BaseModel):
    name: str
    genre: str
    price: int

    developer_id: int

class GameResponse(BaseModel):
    id: int
    name: str
    genre: str
    price: int

    developer_id: int

    model_config = {"from_attributes": True}

class DeveloperCreate(BaseModel):
    username: str
    email: str
    password: str
    age: int

class DeveloperResponse(BaseModel):
    id: int
    username: str
    age: int

    games: list[GameResponse] | None = []

    model_config = {"from_attributes": True}



