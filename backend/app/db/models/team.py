from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from app.db.base import Base


class Team(Base):
    __tablename__ = "team"

    id = Column(Integer, primary_key=True, index=True)
    # Nome come lo scrive l'utente (mostrato nell'interfaccia).
    name = Column(String, unique=True, nullable=False)
    # Nome normalizzato (senza spazi doppi, maiuscole azzerate): garantisce
    # l'unicità senza distinguere le maiuscole. Lo imposta il servizio.
    name_key = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    # Data di eliminazione logica; None = team visibile.
    deleted_at = Column(DateTime, nullable=True)

    __table_args__ = (UniqueConstraint("name_key", name="uq_team_name_key"),)