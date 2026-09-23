# backend/app/models/user.py
# Modello SQLAlchemy per la tabella User.

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)  # hash bcrypt
    role = Column(String, nullable=False, default="user")  # 'user' | 'admin'
    created_at = Column(DateTime, server_default=func.now())

    pilots = relationship("Pilot", back_populates="user")
