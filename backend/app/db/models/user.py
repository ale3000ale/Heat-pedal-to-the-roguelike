from sqlalchemy import Column, Integer, String, CheckConstraint
from app.db.base import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="player", server_default="player")

    __table_args__ = (
        CheckConstraint("role IN ('admin', 'player')", name="ck_user_role"),
    )
