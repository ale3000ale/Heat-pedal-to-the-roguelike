# backend/app/models/team.py
# Modello SQLAlchemy per la tabella Team.

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class Team(Base):
    __tablename__ = "Team"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    pilots = relationship("Pilot", back_populates="team_rel")
