from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from app.db.base import Base


def _now() -> datetime:
    # Data e ora UTC senza fuso, coerenti con le altre colonne DateTime.
    return datetime.now(timezone.utc).replace(tzinfo=None)


class PackFields:
    # Caratteristiche comuni a template di pacchetto e pacchetti del campionato.
    name = Column(String, nullable=False)
    image_path = Column(String, nullable=False)
    # "gold" (sezione modifiche) oppure "sponsor" (sezione sponsor).
    currency = Column(String, nullable=False)
    cost = Column(Integer, nullable=False)
    modifiche_count = Column(Integer, nullable=False, default=3, server_default="3")
    sponsor_count = Column(Integer, nullable=False, default=0, server_default="0")
    filter_enabled = Column(Boolean, nullable=False, default=False, server_default="0")
    # Nomi separati da virgola; usato solo se filter_enabled è vero.
    filter_text = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)
    updated_at = Column(DateTime, nullable=False, default=_now, onupdate=_now)


class PackTemplate(PackFields, Base):
    __tablename__ = "pack_template"

    id = Column(Integer, primary_key=True, index=True)


class ShopTemplate(Base):
    __tablename__ = "shop_template"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    # Nome normalizzato per l'unicità senza distinguere le maiuscole.
    name_key = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=_now)

    __table_args__ = (UniqueConstraint("name_key", name="uq_shop_template_name_key"),)


class ShopTemplatePack(Base):
    # Collegamento vivo: un template di negozio usa dei template di pacchetto.
    __tablename__ = "shop_template_pack"

    shop_template_id = Column(
        Integer, ForeignKey("shop_template.id", ondelete="CASCADE"), primary_key=True
    )
    pack_template_id = Column(
        Integer, ForeignKey("pack_template.id", ondelete="CASCADE"), primary_key=True
    )


class Pack(PackFields, Base):
    # Pacchetto in vendita nel negozio di un campionato (copia indipendente).
    __tablename__ = "pack"

    id = Column(Integer, primary_key=True, index=True)
    championship_id = Column(Integer, ForeignKey("championship.id"), nullable=False, index=True)


class PackPurchase(Base):
    # Storico acquisti: nomi e valori copiati al momento dell'acquisto.
    __tablename__ = "pack_purchase"

    id = Column(Integer, primary_key=True, index=True)
    championship_id = Column(Integer, ForeignKey("championship.id"), nullable=False, index=True)
    pilot_id = Column(Integer, ForeignKey("pilot.id", ondelete="SET NULL"), nullable=True)
    pilot_name = Column(String, nullable=False)
    pack_id = Column(Integer, ForeignKey("pack.id", ondelete="SET NULL"), nullable=True)
    pack_name = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    cost = Column(Integer, nullable=False)
    # Carte ottenute, nello stesso formato testo dei mazzi.
    cards_modifiche = Column(String, nullable=True)
    cards_sponsor = Column(String, nullable=True)
    purchased_at = Column(DateTime, nullable=False, default=_now)
