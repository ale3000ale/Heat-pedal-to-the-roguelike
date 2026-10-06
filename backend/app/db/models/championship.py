from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, UniqueConstraint
from app.db.base import Base
from sqlalchemy.sql import func, expression

# Colonne delle regole dell'oro per gara, nell'ordine: base, posizioni da 1 a 6, dalla 7ª in poi.
GOLD_FIELDS = (
    "gold_base",
    "gold_pos_1",
    "gold_pos_2",
    "gold_pos_3",
    "gold_pos_4",
    "gold_pos_5",
    "gold_pos_6",
    "gold_pos_other",
)


class GoldRulesMixin:
    # Oro dato a tutti gli iscritti dopo ogni gara (anche a chi non corre).
    gold_base = Column(Integer, nullable=False, default=20, server_default="20")
    # Oro in più (o in meno, se negativo) in base alla posizione di arrivo.
    gold_pos_1 = Column(Integer, nullable=False, default=0, server_default="0")
    gold_pos_2 = Column(Integer, nullable=False, default=0, server_default="0")
    gold_pos_3 = Column(Integer, nullable=False, default=0, server_default="0")
    gold_pos_4 = Column(Integer, nullable=False, default=0, server_default="0")
    gold_pos_5 = Column(Integer, nullable=False, default=0, server_default="0")
    gold_pos_6 = Column(Integer, nullable=False, default=0, server_default="0")
    # Una sola regola per tutte le posizioni dalla 7ª in poi.
    gold_pos_other = Column(Integer, nullable=False, default=0, server_default="0")


class Championship(GoldRulesMixin, Base):
    __tablename__ = "championship"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    # Nome normalizzato per l'unicità senza distinguere le maiuscole.
    name_key = Column(String, nullable=False)
    date = Column(DateTime, nullable=False, server_default=func.now())
    is_closed = Column(Boolean, nullable=False, default=False)
    # Copia della pool delle modifiche.
    pool_deck_id = Column(Integer, ForeignKey("deck.id"), nullable=True)
    # Copia della pool degli sponsor.
    sponsor_pool_deck_id = Column(Integer, ForeignKey("deck.id"), nullable=True)
    __table_args__ = (UniqueConstraint("name_key", name="uq_championship_name_key"),)


class ChampionshipDefaults(GoldRulesMixin, Base):
    # Impostazioni generali dei campionati: una sola riga (id=1). Alla creazione di un
    # campionato i valori si copiano; cambiarli dopo non tocca i campionati esistenti.
    __tablename__ = "championship_defaults"

    id = Column(Integer, primary_key=True)


class ChampionshipPilot(Base):
    __tablename__ = "championship_pilot"

    id = Column(Integer, primary_key=True, index=True)
    championship_id = Column(Integer, ForeignKey("championship.id"), nullable=False)
    # Indicizzato: si cerca spesso il campionato attivo a partire dal pilota.
    pilot_id = Column(Integer, ForeignKey("pilot.id"), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("championship_id", "pilot_id"),
    )

class ChampionshipStanding(Base):
    # Classifica finale congelata alla chiusura: solo nome, posizione e punti,
    # senza riferimento al pilota (che può essere eliminato in seguito).
    __tablename__ = "championship_standing"

    id = Column(Integer, primary_key=True, index=True)
    championship_id = Column(Integer, ForeignKey("championship.id"), nullable=False, index=True)
    pilot_name = Column(String, nullable=False)
    rank = Column(Integer, nullable=False)
    points = Column(Integer, nullable=False, default=0)
    races_played = Column(Integer, nullable=False, default=0)
