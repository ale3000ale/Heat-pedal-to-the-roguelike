from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.models.championship import Championship, ChampionshipPilot
from app.db.models.pilot import Pilot


@dataclass
class ShopEntry:
    # Un campionato attivo a cui l'utente partecipa e i suoi piloti iscritti.
    championship_id: int
    championship_name: str
    pilots: list[Pilot]


def list_my_shops(db: Session, user: User) -> list[ShopEntry]:
    # Negozi che l'utente può aprire come giocatore: campionati attivi a cui partecipa
    # con almeno un proprio pilota non eliminato. Campionati e piloti in ordine
    # alfabetico senza distinguere le maiuscole. Vale anche per l'admin, che qui è un
    # giocatore come gli altri.
    stmt = (
        select(Championship, Pilot)
        .join(ChampionshipPilot, ChampionshipPilot.championship_id == Championship.id)
        .join(Pilot, Pilot.id == ChampionshipPilot.pilot_id)
        .where(Pilot.user_id == user.id, Pilot.deleted_at.is_(None))
    )
    entries: dict[int, ShopEntry] = {}
    for championship, pilot in db.execute(stmt):
        if championship.is_closed:
            continue
        entry = entries.setdefault(
            championship.id, ShopEntry(championship.id, championship.name, [])
        )
        entry.pilots.append(pilot)
    for entry in entries.values():
        entry.pilots.sort(key=lambda pilot: pilot.name.casefold())
    return sorted(entries.values(), key=lambda entry: entry.championship_name.casefold())
