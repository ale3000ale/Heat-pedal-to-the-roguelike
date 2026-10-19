import logging

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.models.race import Race
from app.schemas.review_counts import ReviewCountsRequest
from app.services.cards import CardError, card_key
from app.services.review_commit import _apply, _snapshot
from app.services.review_plan import ReviewPlan, build_review_plan

logger = logging.getLogger(__name__)


def apply_expired_draft(db: Session, race: Race) -> None:
    """Applica le carte coerenti di una bozza scaduta senza commit.

    Richiede il blocco di scrittura già acquisito dal chiamante. Per ogni
    carta incongruente conserva inventari, pool e registro come letti.
    Lascia la bozza in caso di problemi, altrimenti la svuota. Il chiamante
    chiude la gara e conferma la transazione. CardError per JSON non valido;
    qualsiasi errore di scrittura deve causare rollback nel chiamante.
    """
    try:
        data = ReviewCountsRequest.model_validate_json(race.review_draft)
    except ValidationError as exc:
        raise CardError("Bozza di revisione non valida: chiusura automatica sospesa") from exc
    snapshot = _snapshot(db, race.championship_id, race.id)
    holdings, stocks, inventories, plays, pool, labels = snapshot
    plan = build_review_plan(holdings, stocks, data.to_counts())
    blocked = {card_key(issue.card_name) for issue in plan.issues}
    safe = ReviewPlan(
        targets={identity: count for identity, count in plan.targets.items() if identity[1] not in blocked},
        pool_after={key: count for key, count in plan.pool_after.items() if key not in blocked},
    )
    # Per le carte scartate manteniamo la quantità fisica della pool, non il
    # saldo previsto dal piano rifiutato. Nessuna loro giocata viene toccata.
    for stock in stocks:
        key = card_key(stock.card_name)
        if key in blocked:
            safe.pool_after[key] = stock.current
    filtered = (
        [row for row in holdings if card_key(row.card_name) not in blocked],
        stocks, inventories,
        [play for play in plays if card_key(play.card_name) not in blocked],
        pool, labels,
    )
    _apply(db, race.id, filtered, safe)
    if blocked:
        logger.warning("Revisione %s scaduta: carte non applicate %s", race.id, sorted(blocked))
    else:
        race.review_draft = None
