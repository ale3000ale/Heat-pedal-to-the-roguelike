"""Letture draft autorizzate; nessun commit, evento o modifica del DB."""
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.models import ChampionshipPilot, Deck, DraftPreparation, Pilot, User
from app.schemas.draft import DraftPilotDeckRead, DraftPilotRead, DraftRead
from app.schemas.draft_state import DraftState
from app.services.cards import parse_cards
from app.services.draft_preparation import DraftPermissionError, DraftPreparationError


class DraftNotFoundError(LookupError):
    """Preparazione non trovata."""


def _role(db: Session, user_id: int) -> str:
    """Rilegge il ruolo dell'utente autenticato; rifiuta ID booleani."""
    if type(user_id) is not int or user_id < 1:
        raise DraftPermissionError("Utente non valido")
    role = db.scalar(select(User.role).where(User.id == user_id))
    if role is None:
        raise DraftPermissionError("Utente non disponibile")
    return role


def _own_ids(db: Session, row: DraftPreparation, state: DraftState, user_id: int) -> list[int]:
    """Incrocia i presenti con proprieta, iscrizione e visibilita reali."""
    present = {p.pilot_id for p in state.participants if p.present and p.user_id == user_id}
    actual = set(db.scalars(select(Pilot.id).join(ChampionshipPilot, ChampionshipPilot.pilot_id == Pilot.id)
        .where(ChampionshipPilot.championship_id == row.championship_id,
               Pilot.user_id == user_id, Pilot.deleted_at.is_(None))))
    return sorted(present & actual)


def _serialize(db: Session, row: DraftPreparation, user_id: int, role: str) -> DraftRead | None:
    """Ritorna un DTO pubblico o None se il modal non appartiene all'utente."""
    state = DraftState.model_validate_json(row.state_json)
    if row.phase != state.phase:
        raise DraftPreparationError("Fase persistita incoerente")
    own = _own_ids(db, row, state, user_id)
    creator = row.creator_user_id == user_id
    if not creator and not (own and state.phase in ("picking", "decks")):
        return None
    return DraftRead(id=row.id, championship_id=row.championship_id, version=row.version,
        phase=state.phase, first_race=state.first_race,
        can_manage=creator and role in ("admin", "judge"), my_pilot_ids=own,
        participants=[DraftPilotRead(pilot_id=p.pilot_id, name=p.name, present=p.present)
                      for p in state.participants],
        order=state.order, cards=state.cards, picks=state.picks,
        preview_slot_id=state.preview_slot_id, ready=state.ready,
        current_pilot_id=state.order[len(state.picks)] if state.phase == "picking" else None)


def list_my_drafts(db: Session, user_id: int) -> list[DraftRead]:
    """Elenca i modal pertinenti da qualsiasi pagina e dopo riconnessione.

    Parametro: ID autenticato. Filtra prima i campionati candidati, poi i
    presenti. Ritorna lista ordinata. Errori di JSON non diventano stati vuoti.
    Mai serializzare state_json o snapshot_json nella risposta pubblica.
    """
    role = _role(db, user_id)
    championships = select(ChampionshipPilot.championship_id).join(Pilot,
        Pilot.id == ChampionshipPilot.pilot_id).where(Pilot.user_id == user_id, Pilot.deleted_at.is_(None))
    rows = db.scalars(select(DraftPreparation).where(or_(
        DraftPreparation.creator_user_id == user_id,
        DraftPreparation.championship_id.in_(championships),
    )).order_by(DraftPreparation.id))
    result = []
    for row in rows:
        item = _serialize(db, row, user_id, role)
        if item is not None:
            result.append(item)
    return result


def read_draft(db: Session, preparation_id: int, user_id: int) -> DraftRead:
    """Legge un modal autorizzato; rifiuta assenti ed estranei anche se gestori."""
    role = _role(db, user_id)
    if type(preparation_id) is not int or preparation_id < 1:
        raise DraftNotFoundError("Preparazione non trovata")
    row = db.get(DraftPreparation, preparation_id)
    if row is None:
        raise DraftNotFoundError("Preparazione non trovata")
    result = _serialize(db, row, user_id, role)
    if result is None:
        raise DraftPermissionError("Preparazione non accessibile")
    return result


def read_draft_deck(db: Session, preparation_id: int, user_id: int, pilot_id: int) -> DraftPilotDeckRead:
    """Legge il proprio presente in decks, senza sponsor o snapshot.

    Contenitori assenti/coincidenti o carte corrotte sono errori, non inventari
    vuoti. Le scritture devono ricontrollare fase e versioni sotto lock.
    """
    draft = read_draft(db, preparation_id, user_id)
    if draft.phase != "decks" or type(pilot_id) is not int or pilot_id not in draft.my_pilot_ids:
        raise DraftPermissionError("Mazzo non accessibile nella fase corrente")
    pilot = db.get(Pilot, pilot_id)
    if pilot is None or pilot.user_id != user_id or pilot.deleted_at is not None:
        raise DraftPermissionError("Pilota non disponibile")
    keys = [pilot.inventory_deck_id, pilot.game_deck_id]
    if len(set(keys)) != 2:
        raise DraftPreparationError("Contenitori non indipendenti")
    decks = {d.id: d for d in db.scalars(select(Deck).where(Deck.id.in_(keys)))}
    if set(decks) != set(keys):
        raise DraftPreparationError("Contenitori mancanti")
    inventory, game = decks[keys[0]], decks[keys[1]]
    return DraftPilotDeckRead(pilot_id=pilot_id, preparation_version=draft.version,
        ready=pilot_id in draft.ready, inventory_version=inventory.version, game_version=game.version,
        inventory=parse_cards(inventory.cards), game_deck=parse_cards(game.cards))
