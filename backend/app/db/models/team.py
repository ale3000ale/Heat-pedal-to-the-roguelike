from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base

class Team(Base):
    __tablename__ = "team"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
