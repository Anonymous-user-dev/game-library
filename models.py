from datetime import datetime, timezone

from database import Base
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship

class Developer(Base):
    __tablename__ = "developers"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    token_version = Column(Integer, default=0)
    password_history = relationship("PasswordHistory",back_populates="developer")

    games = relationship("Game", back_populates="developer")

class PasswordHistory(Base):
    __tablename__ = "password_history"
    id = Column(Integer, primary_key=True)
    developer_id = Column(Integer, ForeignKey("developers.id"), nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    developer = relationship("Developer", back_populates="password_history")


class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    price = Column(Integer, nullable=False)

    developer_id = Column(Integer, ForeignKey("developers.id"), nullable=False)
    developer = relationship("Developer", back_populates="games")

