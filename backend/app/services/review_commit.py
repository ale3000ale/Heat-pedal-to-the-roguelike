from collections import Counter
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.models.card_play import CardPlay, STATUS_CONSUMED, STATUS_PLAYED, STATUS_UNDONE
from app.db.models.deck import Deck
from app.schemas.events import EventCreate
from app.schemas.review_counts import ReviewCountsRequest
from app.services.event_log import append_event
from app.services.cards import CardEntry, CardError, card_key, dump_cards, parse_cards
from app.services.championships import get_championship, list_entrants
from app.services.race_review import (
    ReviewHeldByOtherError, ReviewNotActiveError, _closed_race, is_review_active,
)
from app.services.review_inventory import _pool_caps
from app.services.review_plan import PoolStock, ReviewHolding, ReviewPlan, build_review_plan
from app.services.shop_purchase import _lock_database


class ReviewPermissionError(Exception):
    """Solo giudice o amministratore possono modificare la revisione."""


class ReviewPlanConflict(Exception):
    """Conferma rifiutata; contiene il piano con le incongruenze per carta."""

    def __init__(self, plan: ReviewPlan):
        super().__init__("La revisione contiene incongruenze")
        self.plan = plan


def _authorize(db: Session, championship_id: int, race_id: int, user: User):
    """Restituisce la gara modificabile dall'utente o solleva un errore di permesso/stato."""
    if user.role not in ("admin", "judge"):
        raise ReviewPermissionError
    race = _closed_race(db, championship_id, race_id)
    if not is_review_active(race):
        raise ReviewNotActiveError
    if race.review_started_by_user_id != user.id:
        raise ReviewHeldByOtherError
    return race


def _snapshot(db: Session, championship_id: int, race_id: int):
    """Legge tutte le carte e giocate senza clamp; restituisce dati e modelli per il piano.

    Va chiamata nella transazione bloccata del salvataggio. CardError indica
    riferimenti mancanti o giocate di piloti non più iscritti.
    """
    championship = get_championship(db, championship_id)
    pilots = list_entrants(db, championship_id)
    inventories = {}
    labels = {}
    for pilot in pilots:
        deck = db.get(Deck, pilot.sponsor_inventory_deck_id)
        if deck is None:
            raise CardError(f"Inventario sponsor mancante: {pilot.name}")
        cards = {card_key(c.name): c for c in parse_cards(deck.cards)}
        inventories[pilot.id] = (deck, cards)
        labels.update(cards)
    plays = list(db.scalars(select(CardPlay).where(
        CardPlay.race_id == race_id,
        CardPlay.status.in_((STATUS_PLAYED, STATUS_CONSUMED)),
    ).order_by(CardPlay.id)))
    active = Counter()
    consumed = Counter()
    for play in plays:
        if play.pilot_id not in inventories:
            raise CardError("Giocata riferita a un pilota non iscritto")
        key = card_key(play.card_name)
        identity = (play.pilot_id, key)
        (active if play.status == STATUS_PLAYED else consumed)[identity] += 1
        labels.setdefault(key, CardEntry(name=play.card_name, path=play.card_path, copies=1))
    holdings = []
    for pilot_id, (_, cards) in inventories.items():
        keys = set(cards) | {key for pid, key in active if pid == pilot_id}
        keys |= {key for pid, key in consumed if pid == pilot_id}
        for key in sorted(keys):
            identity = (pilot_id, key)
            held = cards[key].copies if key in cards else 0
            holdings.append(ReviewHolding(
                pilot_id, labels[key].name, held + consumed[identity],
                active[identity], consumed[identity],
            ))
    pool = db.get(Deck, championship.sponsor_pool_deck_id) if championship.sponsor_pool_deck_id else None
    if championship.sponsor_pool_deck_id and pool is None:
        raise CardError("Pool sponsor mancante")
    pool_cards = {card_key(c.name): c for c in parse_cards(pool.cards)} if pool else {}
    labels.update(pool_cards)
    caps = _pool_caps(db, pool)
    stocks = [PoolStock(labels[key].name, pool_cards[key].copies if key in pool_cards else 0,
                        caps.get(key)) for key in sorted(labels)] if pool else []
    return holdings, stocks, inventories, plays, pool, labels


def save_review_counts(db: Session, championship_id: int, race_id: int,
                       user: User, data: ReviewCountsRequest) -> None:
    """Salva solo la bozza validata del revisore attivo; rollback su qualsiasi errore.

    I conteggi oltre il totale sono conservati come bozza per la successiva
    verifica di dominio. Non modifica inventari, pool, giocate o scadenza.
    """
    try:
        _lock_database(db)
        race = _authorize(db, championship_id, race_id, user)
        race.review_draft = data.model_dump_json()
        db.commit()
    except Exception:
        db.rollback()
        raise


def _apply(db: Session, race_id: int, snapshot, plan: ReviewPlan) -> None:
    """Applica un piano privo di problemi senza commit e senza consumare due volte.

    Aggiorna inventari e pool al saldo finale, poi allinea il registro delle
    giocate. Le giocate eccedenti restano nello storico come annullate.
    """
    holdings, _, inventories, plays, pool, labels = snapshot
    by_identity = {}
    for play in plays:
        by_identity.setdefault((play.pilot_id, card_key(play.card_name)), []).append(play)
    for holding in holdings:
        key = card_key(holding.card_name)
        identity = (holding.pilot_id, key)
        wanted = plan.targets[identity]
        _, cards = inventories[holding.pilot_id]
        if wanted:
            cards[key] = labels[key].model_copy(update={"copies": wanted})
        else:
            cards.pop(key, None)
        used = holding.total - wanted
        previous = by_identity.get(identity, [])
        for index, play in enumerate(previous):
            play.status = STATUS_CONSUMED if index < used else STATUS_UNDONE
        for _ in range(max(0, used - len(previous))):
            db.add(CardPlay(race_id=race_id, pilot_id=holding.pilot_id,
                            card_name=labels[key].name, card_path=labels[key].path,
                            status=STATUS_CONSUMED))
    for deck, cards in inventories.values():
        deck.cards = dump_cards([CardEntry.model_validate(c.model_dump()) for c in cards.values()])
    if pool is not None:
        pool.cards = dump_cards([
            CardEntry(name=labels[key].name, path=labels[key].path, copies=count)
            for key, count in plan.pool_after.items() if count > 0
        ])


def commit_review_counts(db: Session, championship_id: int, race_id: int,
                         user: User, data: ReviewCountsRequest):
    """Conferma tutti i conteggi del revisore attivo in una transazione SQLite.

    Restituisce la gara chiusa. ReviewPlanConflict salva soltanto la bozza,
    lasciando inventari, pool, registro e stato invariati. Gli altri errori
    provocano rollback completo. Nessuna autorizzazione viene dal browser.
    Gli eventi pubblici di invalidazione sono nella stessa transazione e non
    contengono conteggi, nomi delle carte o la bozza del revisore.
    """
    try:
        _lock_database(db)
        race = _authorize(db, championship_id, race_id, user)
        snapshot = _snapshot(db, championship_id, race_id)
        plan = build_review_plan(snapshot[0], snapshot[1], data.to_counts())
        if plan.issues:
            race.review_draft = data.model_dump_json()
            db.commit()
            raise ReviewPlanConflict(plan)
        _apply(db, race.id, snapshot, plan)
        race.review_draft = None
        race.review_closed_at = datetime.now(timezone.utc)
        # Accodamento senza commit: un errore annulla anche inventari, pool e stato.
        append_event(db, EventCreate(
            type="race.review_changed", championship_id=championship_id,
            payload={"race_id": race.id, "action": "counts_confirmed"},
        ))
        append_event(db, EventCreate(
            type="cards.changed", championship_id=championship_id,
            payload={"race_id": race.id},
        ))
        db.commit()
        db.refresh(race)
        return race
    except Exception:
        db.rollback()
        raise
