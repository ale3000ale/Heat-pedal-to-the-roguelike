from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.db.models.championship import Championship
from app.db.models.shop import Pack, PackPurchase
from app.services.championships import ChampionshipClosedError, get_championship
from app.services.pack_values import apply_pack_values, resolve_image


class PackNotFoundError(Exception):
    """Il pacchetto non esiste in questo campionato."""


def _active_championship(db: Session, championship_id: int) -> Championship:
    # Errori: ChampionshipNotFoundError, ChampionshipClosedError (negozio in sola lettura).
    championship = get_championship(db, championship_id)
    if championship.is_closed:
        raise ChampionshipClosedError
    return championship


def list_packs(db: Session, championship_id: int) -> list[Pack]:
    # Pacchetti del negozio di un campionato (anche chiuso), in ordine alfabetico senza
    # distinguere le maiuscole. Errori: ChampionshipNotFoundError.
    get_championship(db, championship_id)
    stmt = (
        select(Pack)
        .where(Pack.championship_id == championship_id)
        .order_by(func.lower(Pack.name), Pack.id)
    )
    return list(db.scalars(stmt))


def get_pack(db: Session, championship_id: int, pack_id: int) -> Pack:
    pack = db.get(Pack, pack_id)
    if pack is None or pack.championship_id != championship_id:
        raise PackNotFoundError
    return pack


def create_pack(db: Session, championship_id: int, values: dict) -> Pack:
    # Aggiunge un pacchetto al negozio di un campionato attivo. Senza immagine usa quella
    # predefinita. Errori: ChampionshipNotFoundError, ChampionshipClosedError, PackImageError.
    _active_championship(db, championship_id)
    values = {**values, "image_path": resolve_image(values.get("image_path"))}
    pack = Pack(championship_id=championship_id)
    apply_pack_values(pack, values)
    db.add(pack)
    db.commit()
    db.refresh(pack)
    return pack


def update_pack(db: Session, championship_id: int, pack_id: int, values: dict) -> Pack:
    # Modifica per intero un pacchetto: vale subito per gli acquisti successivi, lo storico
    # conserva i valori del momento dell'acquisto.
    # Errori: ChampionshipNotFoundError, ChampionshipClosedError, PackNotFoundError, PackImageError.
    _active_championship(db, championship_id)
    pack = get_pack(db, championship_id, pack_id)
    values = {**values, "image_path": resolve_image(values.get("image_path"))}
    apply_pack_values(pack, values)
    db.commit()
    db.refresh(pack)
    return pack


def delete_pack(db: Session, championship_id: int, pack_id: int) -> None:
    # Elimina un pacchetto. Gli acquisti già fatti restano nello storico, senza più il
    # collegamento al pacchetto.
    # Errori: ChampionshipNotFoundError, ChampionshipClosedError, PackNotFoundError.
    _active_championship(db, championship_id)
    pack = get_pack(db, championship_id, pack_id)
    db.execute(update(PackPurchase).where(PackPurchase.pack_id == pack.id).values(pack_id=None))
    db.delete(pack)
    db.commit()
