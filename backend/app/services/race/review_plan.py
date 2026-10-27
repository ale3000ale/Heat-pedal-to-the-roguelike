from dataclasses import dataclass, field

Counts = dict[tuple[int, str], int]


@dataclass(frozen=True)
class ReviewHolding:
    pilot_id: int
    card_name: str
    total: int
    active: int = 0
    consumed: int = 0


@dataclass(frozen=True)
class PoolStock:
    card_name: str
    current: int
    maximum: int | None


@dataclass(frozen=True)
class ReviewIssue:
    card_name: str
    reason: str
    pool_now: int
    pool_after: int
    pool_max: int | None


@dataclass
class ReviewPlan:
    targets: Counts = field(default_factory=dict)
    pool_after: dict[str, int] = field(default_factory=dict)
    issues: list[ReviewIssue] = field(default_factory=list)


def build_review_plan(
    holdings: list[ReviewHolding], stocks: list[PoolStock], requested: Counts
) -> ReviewPlan:
    """Calcola i conteggi finali senza scritture o modifiche agli argomenti.

    holdings contiene tutte le carte dei piloti: total include le copie già
    consumate; active sono le giocate ancora da applicare. stocks contiene
    la pool attuale e i massimi noti. requested indica i conteggi corretti.
    Le carte omesse mantengono total - consumed - active come destinazione.
    Restituisce il piano completo e le incongruenze raggruppate per carta.
    Solleva ValueError per righe duplicate o chiavi non normalizzate.
    I dati numerici incoerenti diventano incongruenze, mai correzioni implicite.
    """
    def key(name: str) -> str:
        return name.strip().casefold()

    rows = {}
    labels = {}
    reasons: dict[str, list[str]] = {}
    for row in holdings:
        identity = (row.pilot_id, key(row.card_name))
        if identity in rows:
            raise ValueError("Inventario duplicato per pilota e carta")
        rows[identity] = row
        labels[identity[1]] = row.card_name
    pool = {}
    for stock in stocks:
        name = key(stock.card_name)
        if name in pool:
            raise ValueError("Carta duplicata nella pool")
        pool[name] = stock
        labels.setdefault(name, stock.card_name)
    for identity in requested:
        if identity[1] != key(identity[1]):
            raise ValueError("Chiave della carta non normalizzata")
        if identity not in rows:
            name = identity[1]
            labels.setdefault(name, name)
            reasons.setdefault(name, []).append("Carta o pilota non presenti nella revisione")
    result = ReviewPlan()
    deltas: dict[str, int] = {}
    for identity, row in rows.items():
        name = identity[1]
        held = row.total - row.consumed
        initial = held - row.active
        wanted = requested.get(identity, initial)
        valid = all(type(n) is int and n >= 0 for n in (row.total, row.active, row.consumed))
        if not valid or held < 0 or initial < 0:
            reasons.setdefault(name, []).append(f"Pilota {row.pilot_id}: inventario o giocate incoerenti")
        if type(wanted) is not int or not 0 <= wanted <= row.total:
            reasons.setdefault(name, []).append(f"Pilota {row.pilot_id}: quantità fuori da 0..{row.total}")
            continue
        result.targets[identity] = wanted
        deltas[name] = deltas.get(name, 0) + held - wanted
    all_names = set(pool) | set(labels) | set(deltas) | set(reasons)
    for name in sorted(all_names):
        stock = pool.get(name)
        current = stock.current if stock else 0
        maximum = stock.maximum if stock else None
        after = current + deltas.get(name, 0)
        errors = reasons.get(name, []).copy()
        if type(current) is not int or current < 0:
            errors.append("Quantità attuale della pool non valida")
        if maximum is not None and (type(maximum) is not int or maximum < 0):
            errors.append("Massimo della pool non valido")
        if after < 0:
            errors.append(f"La pool avrebbe {after} copie: disponibilità insufficiente")
        if maximum is not None and after > maximum:
            errors.append(f"La pool avrebbe {after} copie su un massimo di {maximum}")
        if stock is None and deltas.get(name, 0) != 0:
            errors.append("Carta assente dai dati della pool: specificare anche le disponibilità zero")
        result.pool_after[name] = after
        if errors:
            result.issues.append(ReviewIssue(labels[name], "; ".join(errors), current, after, maximum))
    return result
