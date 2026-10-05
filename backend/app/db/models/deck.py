from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from app.db.base import Base


class DeckPrototype(Base):
    __tablename__ = "deck_prototype"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    base_cards = Column(String, nullable=True)
    # Tipo della pool: "modifiche" o "sponsor". Le derivate hanno il tipo della base da cui nascono.
    kind = Column(String, nullable=False, default="modifiche", server_default="modifiche")

class Deck(Base):
    __tablename__ = "deck"

    id = Column(Integer, primary_key=True, index=True)
    cards = Column(String, nullable=True)
    id_prototype = Column(Integer, ForeignKey("deck_prototype.id"), nullable=True)
    # Versione per il blocco ottimistico: ogni modifica la incrementa e salva solo se
    # nessun altro ha modificato il mazzo nel frattempo (altrimenti StaleDataError).
    version = Column(Integer, nullable=False, server_default="1")

    __mapper_args__ = {"version_id_col": version}
