import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.accounts.auth import router as auth_router
from app.db.session import SessionLocal
from app.services.accounts.sessions import purge_expired
from app.api.pilots.teams import router as teams_router
from fastapi.staticfiles import StaticFiles
from app.api.pilots.pilots import router as pilots_router
from app.api.championship.championships import router as championships_router
from app.api.championship.pools import router as pools_router
from app.api.race.races import router as races_router
from app.api.admin.admin import router as admin_router
from app.api.admin.admin_pilot_cards import router as admin_pilot_cards_router
from app.api.cards.packs import router as packs_router
from app.api.shop.shop import router as shop_router
from app.api.shop.shop_play import router as shop_play_router
from app.api.shop.shop_me import router as shop_me_router
from app.api.cards.card_play import router as card_play_router
from app.api.cards.card_gift_seen import router as card_gift_seen_router
from app.api.admin.card_admin import router as card_admin_router
from app.api.race.race_review import router as race_review_router
from app.api.race.review_counts import router as review_counts_router
from app.api.events import router as events_router
from app.api.draft.draft import router as draft_router
from app.api.draft.draft_errors import draft_locked_response
from app.services.draft.draft_guards import DraftLockedError
from app.services.core.cleanup import purge_old_deleted
from app.services.race.review_timer import review_timer

from app.config import MEDIA_DIR


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Esegue manutenzione iniziale e gestisce un timer per worker.

    Parametro: applicazione FastAPI. Il timer usa sessioni brevi e coordina le
    scritture tramite SQLite. All'uscita, anche per errore nel corpo, segnala
    stop e attende il task: non abbandona il giro SQL in corso.
    Errori di startup o del task propagano; non esegue migrazioni automatiche.
    """
    factory = SessionLocal
    with factory() as db:
        purge_expired(db)
        purge_old_deleted(db)
    stop = asyncio.Event()
    task = asyncio.create_task(review_timer(factory, stop), name="heat-review-timer")
    app.state.review_timer_stop = stop
    app.state.review_timer_task = task
    try:
        yield
    finally:
        stop.set()
        await task


app = FastAPI(title="Heat", lifespan=lifespan)
app.add_exception_handler(DraftLockedError, draft_locked_response)


app.include_router(auth_router, prefix="/api/auth")
app.include_router(teams_router, prefix="/api/teams")
app.include_router(pilots_router, prefix="/api/pilots")
app.include_router(pools_router, prefix="/api/pools")
app.include_router(championships_router, prefix="/api/championships")
app.include_router(races_router, prefix="/api/championships")
app.include_router(race_review_router, prefix="/api/championships")
app.include_router(review_counts_router, prefix="/api/championships")
app.include_router(packs_router, prefix="/api/championships")
app.include_router(shop_play_router, prefix="/api/championships")
app.include_router(card_play_router, prefix="/api/championships")
app.include_router(card_gift_seen_router, prefix="/api/championships")
app.include_router(shop_me_router, prefix="/api/me")
app.include_router(card_admin_router, prefix="/api/admin/cards")
app.include_router(admin_router, prefix="/api/admin")
app.include_router(admin_pilot_cards_router, prefix="/api/admin/championships")
app.include_router(shop_router, prefix="/api/shop")
app.include_router(events_router, prefix="/api/events")
app.include_router(draft_router, prefix="/api")

MEDIA_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")


@app.get("/health")
async def read_health():
    return {"status": "ok"}
