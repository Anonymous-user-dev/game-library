from database import Base
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

class Developer(Base):
    __tablename__ = "developers"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)

    games = relationship("Game", back_populates="developer")

class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    price = Column(Integer, nullable=False)

    developer_id = Column(Integer, ForeignKey("developers.id"), nullable=False)
    developer = relationship("Developer", back_populates="games")

