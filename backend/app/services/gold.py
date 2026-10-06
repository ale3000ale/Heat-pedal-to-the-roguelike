from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.db.models.championship import GOLD_FIELDS, ChampionshipDefaults
from app.db.models.pilot import Pilot

# Posizioni con un modificatore proprio; dalla successiva vale quello "other".
GOLD_POSITIONS = 6
MAX_GOLD_BASE = 10000
MAX_GOLD_MODIFIER = 1000
DEFAULTS_ROW_ID = 1


@dataclass(frozen=True)
class GoldRules:
    # base: oro a tutti gli iscritti; positions: modificatori per le posizioni 1-6;
    # other: modificatore per tutte le posizioni dalla 7ª in poi.
    base: int
    positions: tuple[int, ...]
    other: int


def rules_of(source) -> GoldRules:
    # Legge le regole da un campionato o dalle impostazioni generali.
    values = [getattr(source, field) for field in GOLD_FIELDS]
    return GoldRules(
        base=values[0],
        positions=tuple(values[1 : 1 + GOLD_POSITIONS]),
        other=values[-1],
    )


def apply_rules(target, rules: GoldRules) -> None:
    # Scrive le regole su un campionato o sulle impostazioni generali (senza commit).
    values = [rules.base, *rules.positions, rules.other]
    for field, value in zip(GOLD_FIELDS, values):
        setattr(target, field, value)


def get_defaults(db: Session) -> ChampionshipDefaults:
    # Le impostazioni generali; se la riga manca (database nuovo) la crea con i valori base.
    defaults = db.get(ChampionshipDefaults, DEFAULTS_ROW_ID)
    if defaults is None:
        defaults = ChampionshipDefaults(id=DEFAULTS_ROW_ID)
        db.add(defaults)
        db.flush()
    return defaults


def set_defaults(db: Session, rules: GoldRules) -> ChampionshipDefaults:
    # Cambia le impostazioni generali: valgono solo per i campionati creati dopo.
    defaults = get_defaults(db)
    apply_rules(defaults, rules)
    db.commit()
    db.refresh(defaults)
    return defaults


def race_gold(rules: GoldRules, position: int | None) -> int:
    # Oro di un pilota per una gara: base più il modificatore della posizione (nessuno
    # per chi non ha corso), mai sotto zero.
    if position is None:
        bonus = 0
    elif position <= GOLD_POSITIONS:
        bonus = rules.positions[position - 1]
    else:
        bonus = rules.other
    return max(0, rules.base + bonus)


def award_race_gold(entrants: list[Pilot], rules: GoldRules, order: list[int]) -> None:
    # Dà l'oro a tutti gli iscritti. `order` sono gli id dei piloti nell'ordine di arrivo.
    positions = {pilot_id: place for place, pilot_id in enumerate(order, start=1)}
    for pilot in entrants:
        pilot.gold += race_gold(rules, positions.get(pilot.id))
