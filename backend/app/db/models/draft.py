"""Contenitore della preparazione; non rappresenta una gara gia creata."""
from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, Text, String, UniqueConstraint, func

from app.db.base import Base


class DraftPreparation(Base):
    """Una preparazione per campionato, con stato e ripristino validati dai servizi.

    I campi JSON non hanno valori vuoti impliciti: il chiamante deve prepararli.
    La versione ORM impedisce salvataggi su letture superate. Questo modello
    non implementa autorizzazioni, rollback di gioco o validazione JSON.
    """

    __tablename__ = "draft_preparation"

    id = Column(Integer, primary_key=True)
    championship_id = Column(Integer, ForeignKey("championship.id"), nullable=False)
    creator_user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    phase = Column(String(16), nullable=False)
    state_json = Column(Text, nullable=False)
    snapshot_json = Column(Text, nullable=False)
    version = Column(Integer, nullable=False, server_default="1")
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __mapper_args__ = {"version_id_col": version}
    __table_args__ = (
        UniqueConstraint("championship_id", name="uq_draft_preparation_championship"),
        CheckConstraint("phase IN ('attendance', 'order', 'picking', 'decks')", name="ck_draft_preparation_phase"),
        CheckConstraint("version >= 1", name="ck_draft_preparation_version"),
        {"sqlite_autoincrement": True},
    )
