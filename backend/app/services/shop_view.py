from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.models.championship import Championship, ChampionshipPilot
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.db.models.shop import Pack
from app.services.cards import CardEntry, parse_cards
from app.services.championships import get_championship
from app.services.pilots import get_own_pilot
from app.services.packs import list_packs
from app.services.races import has_race_in_progress
from app.services.shop_draw import is_sold_out


class ShopAccessDeniedError(Exception):
    """L'utente non può entrare in questo negozio."""


class PilotNotEnrolledError(Exception):
    """Il pilota non è iscritto a questo campionato."""


@dataclass
class ShopView:
    championship: Championship
    # Pilota con cui si entra; None per l'admin senza pilota (sola lettura).
    pilot: Pilot | None
    # Nessun acquisto possibile: campionato chiuso oppure admin senza pilota.
    read_only: bool
    # Gara in corso: acquisti bloccati.
    locked: bool
    packs: list[tuple[Pack, bool]]


def load_pool(db: Session, deck_id: int | None) -> list[CardEntry]:
    # Carte di una pool del campionato; senza mazzo (pool sponsor non creata) è vuota.
    if deck_id is None:
        return []
    return parse_cards(db.get(Deck, deck_id).cards)


def is_enrolled(db: Session, championship_id: int, pilot_id: int) -> bool:
    stmt = select(ChampionshipPilot.pilot_id).where(
        ChampionshipPilot.championship_id == championship_id,
        ChampionshipPilot.pilot_id == pilot_id,
    )
    return db.scalar(stmt) is not None


def open_shop(
    db: Session, user: User, championship_id: int, pilot_id: int | None = None
) -> ShopView:
    # Regole di accesso: un giocatore entra solo con un proprio pilota iscritto e solo se
    # il campionato è attivo; l'admin entra sempre, anche senza pilota o a campionato
    # chiuso, ma in quei casi in sola lettura. L'admin con un pilota iscritto si comporta
    # come un giocatore.
    # Errori: ChampionshipNotFoundError, PilotNotFoundError (pilota non suo),
    # ShopAccessDeniedError, PilotNotEnrolledError.
    championship = get_championship(db, championship_id)
    is_admin = user.role == "admin"
    pilot = None
    if pilot_id is not None:
        pilot = get_own_pilot(db, user, pilot_id)
        if not is_enrolled(db, championship_id, pilot.id):
            raise PilotNotEnrolledError
    if pilot is None and not is_admin:
        raise ShopAccessDeniedError
    if championship.is_closed and not is_admin:
        raise ShopAccessDeniedError
    modifiche_pool = load_pool(db, championship.pool_deck_id)
    sponsor_pool = load_pool(db, championship.sponsor_pool_deck_id)
    packs = [
        (
            pack,
            is_sold_out(
                pack.modifiche_count,
                pack.sponsor_count,
                pack.filter_enabled,
                pack.filter_text,
                modifiche_pool,
                sponsor_pool,
            ),
        )
        for pack in list_packs(db, championship_id)
    ]
    return ShopView(
        championship=championship,
        pilot=pilot,
        read_only=championship.is_closed or pilot is None,
        locked=(not championship.is_closed) and has_race_in_progress(db, championship_id),
        packs=packs,
    )
