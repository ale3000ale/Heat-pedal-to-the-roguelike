"""Timer revisioni: modulo indipendente, da collegare al lifespan dopo gli eventi."""
import asyncio
import logging
import math
from datetime import datetime, timedelta, timezone
from time import monotonic

from sqlalchemy import select
from starlette.concurrency import run_in_threadpool

from app.db.models import Championship, Race, RaceResult
from app.services.championships import ChampionshipNotFoundError
from app.services.event_log import purge_expired_events
from app.services.race_review import REVIEW_MINUTES, settle_expired_reviews

logger = logging.getLogger(__name__)


def run_review_sweep(factory, now: datetime | None = None, cleanup: bool = False) -> int:
    """Elabora scadenze con sessioni brevi e isolamento degli errori per campionato.

    Parametri: factory SQLAlchemy, istante UTC opzionale, richiesta di pulizia.
    Ritorna quante revisioni sono state chiuse. Il servizio esistente acquisisce
    il blocco SQLite e ricontrolla lo stato prima del commit di ciascuna gara.
    Errori per campionato sono registrati con traceback; errori nella ricerca o
    pulizia propagano al ciclo. Non modifica le regole della revisione.
    """
    current = now if now is not None else datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    current = current.astimezone(timezone.utc)
    cutoff = (current - timedelta(minutes=REVIEW_MINUTES)).replace(tzinfo=None)
    with factory() as db:
        has_results = select(RaceResult.id).where(RaceResult.race_id == Race.id).exists()
        statement = select(Race.championship_id).join(
            Championship, Championship.id == Race.championship_id
        ).where(
            Championship.is_closed.is_(False),
            Race.review_closed_at.is_(None),
            Race.review_started_at <= cutoff,
            has_results,
        ).distinct()
        championship_ids = list(db.scalars(statement))
    settled = 0
    for championship_id in championship_ids:
        try:
            with factory() as db:
                settled += settle_expired_reviews(db, championship_id, current)
        except ChampionshipNotFoundError:
            logger.info("Campionato %s rimosso prima del controllo revisioni", championship_id)
        except Exception:
            logger.exception("Errore nel timer revisioni del campionato %s", championship_id)
    if cleanup:
        with factory() as db:
            purge_expired_events(db, current)
            db.commit()
    return settled


async def review_timer(factory, stop: asyncio.Event, interval: float = 5.0,
                       cleanup_interval: float = 3600.0) -> None:
    """Controlla ogni 5 s e pulisce ogni ora; stop cooperativo, senza task figli.

    Parametri: factory, evento di arresto, intervalli positivi e finiti in secondi.
    Il primo giro include la pulizia. SQL nel thread pool, mai durante le attese.
    L'arresto attende il giro SQL in corso; non interrompe transazioni a meta'.
    ValueError per intervalli invalidi. Gli errori di giro sono loggati e ritentati;
    la cancellazione del task non viene inghiottita. Nessun avvio implicito.
    """
    if not all(math.isfinite(value) and value > 0 for value in (interval, cleanup_interval)):
        raise ValueError("Intervalli del timer non validi")
    next_cleanup = 0.0
    while not stop.is_set():
        cleanup = monotonic() >= next_cleanup
        try:
            await run_in_threadpool(run_review_sweep, factory, None, cleanup)
            if cleanup:
                next_cleanup = monotonic() + cleanup_interval
        except Exception:
            logger.exception("Errore nel giro del timer revisioni")
        if stop.is_set():
            return
        try:
            await asyncio.wait_for(stop.wait(), timeout=interval)
        except asyncio.TimeoutError:
            pass
