from dataclasses import dataclass

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.models.championship import Championship, ChampionshipPilot, ChampionshipStanding
from app.db.models.deck import Deck, DeckPrototype
from app.db.models.pilot import Pilot
from app.db.models.race import Race, RaceResult
from app.db.models.shop import Pack, PackPurchase
from app.services.cards import STARTER_INVENTORY, dump_cards
from app.services.gold import GoldRules, apply_rules, get_defaults, rules_of
from app.services.names import clean_name, name_key
from app.services.pilots import PilotInActiveChampionshipError, get_own_pilot
from app.services.pools import PoolNotFoundError, get_base_pool, pool_for_kind
from app.services.shop_copy import add_packs_from_templates, pack_templates_of
from app.services.teams import pilots_in_active_championship


class ChampionshipNotFoundError(Exception):
    """Il campionato non esiste."""


class ChampionshipNameTakenError(Exception):
    """Esiste già un campionato con questo nome."""


class ChampionshipClosedError(Exception):
    """Il campionato è chiuso (sola lettura)."""

class ChampionshipOpenError(Exception):
    """Il campionato è ancora attivo: va chiuso prima di cancellarlo."""

class PilotWithoutTeamError(Exception):
    """Per iscriversi a un campionato il pilota deve avere un team."""


def list_championships(db: Session) -> list[Championship]:
    # Tutti i campionati, attivi e chiusi, dal più recente.
    stmt = select(Championship).order_by(Championship.date.desc(), Championship.id.desc())
    return list(db.scalars(stmt))


def get_championship(db: Session, championship_id: int) -> Championship:
    championship = db.get(Championship, championship_id)
    if championship is None:
        raise ChampionshipNotFoundError
    return championship


def list_entrants(db: Session, championship_id: int) -> list[Pilot]:
    # Piloti iscritti, in ordine alfabetico (anche quelli poi nascosti dai giocatori:
    # restano nello storico del campionato).
    stmt = (
        select(Pilot)
        .join(ChampionshipPilot, ChampionshipPilot.pilot_id == Pilot.id)
        .where(ChampionshipPilot.championship_id == championship_id)
        .order_by(Pilot.name_key)
    )
    return list(db.scalars(stmt))


def _copy_pool(db: Session, pool: DeckPrototype) -> Deck:
    # Copia indipendente della pool: il campionato non cambia se la pool cambia.
    deck = Deck(cards=pool.base_cards or dump_cards([]), id_prototype=pool.id)
    db.add(deck)
    db.flush()
    return deck


def _reset_pilot(db: Session, pilot: Pilot) -> None:
    # Riporta il pilota allo stato iniziale: inventario di partenza, inventario sponsor
    # vuoto, mazzo da gioco vuoto, gold, sponsor e point a zero. Senza commit.
    db.get(Deck, pilot.inventory_deck_id).cards = dump_cards(STARTER_INVENTORY)
    db.get(Deck, pilot.sponsor_inventory_deck_id).cards = dump_cards([])
    db.get(Deck, pilot.game_deck_id).cards = dump_cards([])
    pilot.gold = 0
    pilot.sponsor = 0
    pilot.point = 0


def create_championship(
    db: Session,
    name: str,
    pool_id: int | None = None,
    sponsor_pool_id: int | None = None,
    shop_template_id: int | None = None,
) -> Championship:
    # Crea un campionato con una copia indipendente della pool delle modifiche e una
    # della pool degli sponsor (le rispettive pool di base se omesse), e con una copia
    # delle impostazioni generali dell'oro: cambiarle dopo non tocca il campionato.
    # Con shop_template_id il negozio parte con una copia dei pacchetti del template di
    # negozio; senza, è vuoto.
    # Errori: ChampionshipNameTakenError, ShopTemplateNotFoundError, ShopTemplateEmptyError,
    # PoolNotFoundError e PoolRuleError per le pool.
    name = clean_name(name)
    key = name_key(name)
    if db.scalar(select(Championship.id).where(Championship.name_key == key)) is not None:
        raise ChampionshipNameTakenError
    shop_pack_templates = (
        pack_templates_of(db, shop_template_id) if shop_template_id is not None else []
    )
    pool = pool_for_kind(db, pool_id, "modifiche")
    if sponsor_pool_id is None:
        # Senza pool di base degli sponsor (non creata) il campionato parte senza.
        try:
            sponsor_pool = get_base_pool(db, "sponsor")
        except PoolNotFoundError:
            sponsor_pool = None
    else:
        sponsor_pool = pool_for_kind(db, sponsor_pool_id, "sponsor")
    deck = _copy_pool(db, pool)
    sponsor_deck = _copy_pool(db, sponsor_pool) if sponsor_pool is not None else None
    championship = Championship(
        name=name,
        name_key=key,
        pool_deck_id=deck.id,
        sponsor_pool_deck_id=sponsor_deck.id if sponsor_deck is not None else None,
    )
    apply_rules(championship, rules_of(get_defaults(db)))
    db.add(championship)
    try:
        db.flush()
        add_packs_from_templates(db, championship.id, shop_pack_templates)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ChampionshipNameTakenError
    db.refresh(championship)
    return championship


def set_gold_rules(db: Session, championship_id: int, rules: GoldRules) -> Championship:
    # Cambia le regole dell'oro di un campionato attivo: valgono dalla prossima gara che
    # si chiude, le gare già chiuse restano come sono.
    championship = get_championship(db, championship_id)
    if championship.is_closed:
        raise ChampionshipClosedError
    apply_rules(championship, rules)
    db.commit()
    db.refresh(championship)
    return championship


def close_championship(db: Session, championship_id: int) -> Championship:
    # Chiude il campionato (anche con gare non finite): da qui in poi è in sola lettura.
    # Congela la classifica e reimposta i soli piloti iscritti a questo campionato.
    championship = get_championship(db, championship_id)
    if championship.is_closed:
        raise ChampionshipClosedError
    championship.is_closed = True
    _freeze_standings(db, championship)
    for pilot in list_entrants(db, championship.id):
        _reset_pilot(db, pilot)
    db.commit()
    db.refresh(championship)
    return championship


def enroll_pilot(db: Session, user: User, championship_id: int, pilot_id: int) -> Pilot:
    # Iscrive un pilota dell'utente e lo reimposta: inventario iniziale, inventario
    # sponsor vuoto, mazzo da gioco vuoto, gold, sponsor e point a zero.
    championship = get_championship(db, championship_id)
    if championship.is_closed:
        raise ChampionshipClosedError
    pilot = get_own_pilot(db, user, pilot_id)
    if pilot.team_id is None:
        raise PilotWithoutTeamError
    if pilots_in_active_championship(db, [pilot.id]):
        raise PilotInActiveChampionshipError
    _reset_pilot(db, pilot)
    db.add(ChampionshipPilot(championship_id=championship.id, pilot_id=pilot.id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise PilotInActiveChampionshipError
    db.refresh(pilot)
    return pilot

def delete_championship(db: Session, championship_id: int) -> None:
    # Cancella un campionato chiuso con tutto il suo storico: risultati, gare, iscrizioni,
    # pacchetti del negozio, storico acquisti e le copie delle pool. I piloti restano.
    # Tutto in un'unica transazione.
    championship = get_championship(db, championship_id)
    if not championship.is_closed:
        raise ChampionshipOpenError
    race_ids = select(Race.id).where(Race.championship_id == championship.id)
    db.execute(delete(RaceResult).where(RaceResult.race_id.in_(race_ids)))
    db.execute(delete(Race).where(Race.championship_id == championship.id))
    db.execute(
        delete(ChampionshipPilot).where(ChampionshipPilot.championship_id == championship.id)
    )
    db.execute(
        delete(ChampionshipStanding).where(ChampionshipStanding.championship_id == championship.id)
    )
    db.execute(delete(PackPurchase).where(PackPurchase.championship_id == championship.id))
    db.execute(delete(Pack).where(Pack.championship_id == championship.id))
    pool_deck_ids = [
        deck_id
        for deck_id in (championship.pool_deck_id, championship.sponsor_pool_deck_id)
        if deck_id is not None
    ]
    db.delete(championship)
    db.flush()
    for deck_id in pool_deck_ids:
        deck = db.get(Deck, deck_id)
        if deck is not None:
            db.delete(deck)
    db.commit()

@dataclass
class StandingRow:
    # Una riga di classifica: pilot_id è None per i campionati chiusi.
    rank: int
    pilot_id: int | None
    pilot_name: str
    points: int
    races_played: int


def pilot_totals(db: Session, championship_id: int) -> dict[int, tuple[int, int]]:
    # Per pilota: (punti totali, gare disputate) nel campionato.
    stmt = (
        select(RaceResult.pilot_id, func.sum(RaceResult.points), func.count())
        .select_from(RaceResult)
        .join(Race, Race.id == RaceResult.race_id)
        .where(Race.championship_id == championship_id)
        .group_by(RaceResult.pilot_id)
    )
    return {pilot_id: (int(points), int(races)) for pilot_id, points, races in db.execute(stmt)}


def live_standings(db: Session, championship_id: int) -> list[tuple[int, Pilot, int, int]]:
    # Classifica calcolata dai risultati: (posizione, pilota, punti, gare disputate).
    # A pari punti stessa posizione; l'ordine alfabetico serve solo alla visualizzazione.
    totals = pilot_totals(db, championship_id)
    entrants = sorted(
        list_entrants(db, championship_id),
        key=lambda p: (-totals.get(p.id, (0, 0))[0], p.name_key),
    )
    all_points = [totals.get(p.id, (0, 0))[0] for p in entrants]
    rows = []
    for pilot in entrants:
        points, races = totals.get(pilot.id, (0, 0))
        rank = 1 + sum(1 for other in all_points if other > points)
        rows.append((rank, pilot, points, races))
    return rows


def _freeze_standings(db: Session, championship: Championship) -> None:
    # Salva la classifica finale (solo nome, posizione, punti), senza commit.
    for rank, pilot, points, races in live_standings(db, championship.id):
        db.add(
            ChampionshipStanding(
                championship_id=championship.id,
                pilot_name=pilot.name,
                rank=rank,
                points=points,
                races_played=races,
            )
        )


def standings(db: Session, championship_id: int) -> list[StandingRow]:
    # Campionato chiuso: classifica congelata. Attivo: calcolata dai risultati.
    championship = get_championship(db, championship_id)
    if championship.is_closed:
        frozen = list(
            db.scalars(
                select(ChampionshipStanding)
                .where(ChampionshipStanding.championship_id == championship_id)
                .order_by(ChampionshipStanding.rank, ChampionshipStanding.id)
            )
        )
        if frozen:
            return [
                StandingRow(s.rank, None, s.pilot_name, s.points, s.races_played) for s in frozen
            ]
    return [
        StandingRow(rank, pilot.id, pilot.name, points, races)
        for rank, pilot, points, races in live_standings(db, championship_id)
    ]
