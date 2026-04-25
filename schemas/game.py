from pydantic import BaseModel


class GameCreate(BaseModel):
    name: str
    genre: str
    price: int

class GameResponse(BaseModel):
    id: int
    name: str
    genre: str
    price: int

    developer_id: int

    model_config = {"from_attributes": True}