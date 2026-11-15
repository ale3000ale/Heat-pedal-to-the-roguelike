"""API draft da registrare insieme ai blocchi e agli eventi transazionali."""
from fastapi import APIRouter, Response, status

from app.api.deps import CurrentUser, DbDep, JudgeUser
from app.api.draft.draft_errors import draft_request
from app.schemas.draft.draft import (
    DraftActionRead, DraftAttendanceCommand, DraftChoiceCommand, DraftMoveCommand,
    DraftOrderCommand, DraftPilotDeckRead, DraftPreviewCommand, DraftRead,
    DraftReadyCommand, DraftVersionCommand,
)
from app.services.draft.draft_commands import (
    begin_picking, change_order, choose_card, confirm_attendance, move_draft_card, share_preview,
)
from app.services.draft.draft_completion import already_disputed, ready_pilot
from app.services.draft.draft_preparation import open_preparation, set_attendance
from app.services.draft.draft_transaction import cancel_preparation
from app.services.draft.draft_view import list_my_drafts, read_draft, read_draft_deck
from app.services.race.race_review import settle_expired_reviews

router = APIRouter(tags=["draft"])


@router.get("/drafts", response_model=list[DraftRead])
def list_current(user: CurrentUser, db: DbDep):
    """Modal pertinenti all'utente da qualsiasi pagina."""
    return draft_request(db, lambda: list_my_drafts(db, user.id))


@router.post("/championships/{championship_id}/draft", response_model=DraftRead,
             status_code=status.HTTP_201_CREATED)
def open_draft(championship_id: int, judge: JudgeUser, db: DbDep):
    """Elabora revisioni scadute e apre la preparazione senza creare Race."""
    actor = judge.id
    def operation():
        settle_expired_reviews(db, championship_id)
        row = open_preparation(db, championship_id, actor)
        return read_draft(db, row.id, actor)
    return draft_request(db, operation)


@router.get("/drafts/{draft_id}", response_model=DraftRead)
def detail(draft_id: int, user: CurrentUser, db: DbDep):
    """Recupera fase e turno di una preparazione autorizzata."""
    return draft_request(db, lambda: read_draft(db, draft_id, user.id))


@router.get("/drafts/{draft_id}/pilots/{pilot_id}/deck", response_model=DraftPilotDeckRead)
def deck(draft_id: int, pilot_id: int, user: CurrentUser, db: DbDep):
    """Legge inventario e mazzo del proprio presente nella fase dedicata."""
    return draft_request(db, lambda: read_draft_deck(db, draft_id, user.id, pilot_id))


def _updated(db, draft_id, user_id, command):
    """Esegue il comando transazionale e serializza solo il DTO pubblico."""
    command()
    return read_draft(db, draft_id, user_id)


@router.post("/drafts/{draft_id}/attendance", response_model=DraftRead)
def attendance(draft_id: int, data: DraftAttendanceCommand, user: CurrentUser, db: DbDep):
    """Include/esclude; il servizio verifica creatore e versione."""
    actor = user.id
    return draft_request(db, lambda: _updated(db, draft_id, actor,
        lambda: set_attendance(db, draft_id, actor, data.version, data.pilot_id, data.present)))


@router.post("/drafts/{draft_id}/attendance/confirm", response_model=DraftRead)
def confirm(draft_id: int, data: DraftVersionCommand, user: CurrentUser, db: DbDep):
    """Conferma presenze e passa a ordine oppure mazzi."""
    actor = user.id
    return draft_request(db, lambda: _updated(db, draft_id, actor,
        lambda: confirm_attendance(db, draft_id, actor, data.version)))


@router.post("/drafts/{draft_id}/order", response_model=DraftRead)
def order(draft_id: int, data: DraftOrderCommand, user: CurrentUser, db: DbDep):
    """Salva l'ordine del creatore."""
    actor = user.id
    return draft_request(db, lambda: _updated(db, draft_id, actor,
        lambda: change_order(db, draft_id, actor, data.version, data.pilot_ids)))


@router.post("/drafts/{draft_id}/start", response_model=DraftRead)
def start(draft_id: int, data: DraftVersionCommand, user: CurrentUser, db: DbDep):
    """Riserva le copie e avvia i turni."""
    actor = user.id
    return draft_request(db, lambda: _updated(db, draft_id, actor,
        lambda: begin_picking(db, draft_id, actor, data.version)))


@router.post("/drafts/{draft_id}/preview", response_model=DraftRead)
def enlarge(draft_id: int, data: DraftPreviewCommand, user: CurrentUser, db: DbDep):
    """Anteprima condivisa del solo proprietario di turno."""
    actor = user.id
    return draft_request(db, lambda: _updated(db, draft_id, actor,
        lambda: share_preview(db, draft_id, actor, data.version, data.slot_id)))


@router.post("/drafts/{draft_id}/choice", response_model=DraftRead)
def pick(draft_id: int, data: DraftChoiceCommand, user: CurrentUser, db: DbDep):
    """Sceglie una copia con trasferimento atomico all'inventario."""
    actor = user.id
    return draft_request(db, lambda: _updated(db, draft_id, actor,
        lambda: choose_card(db, draft_id, actor, data.version, data.slot_id)))


@router.post("/drafts/{draft_id}/deck/move", response_model=DraftRead)
def move(draft_id: int, data: DraftMoveCommand, user: CurrentUser, db: DbDep):
    """Sposta una copia nel mazzo del proprio presente non pronto."""
    actor = user.id
    return draft_request(db, lambda: _updated(db, draft_id, actor,
        lambda: move_draft_card(db, draft_id, actor, data.version, data.pilot_id, data.path, data.to_game)))


@router.post("/drafts/{draft_id}/ready", response_model=DraftActionRead)
def ready(draft_id: int, data: DraftReadyCommand, user: CurrentUser, db: DbDep):
    """Conferma/revoca pronto; l'ultimo pronto restituisce la gara creata."""
    actor = user.id
    def operation():
        result = ready_pilot(db, draft_id, actor, data.version, data.pilot_id, data.ready)
        state = read_draft(db, draft_id, actor) if result.preparation_id is not None else None
        return DraftActionRead(preparation=state, race_id=result.race_id)
    return draft_request(db, operation)


@router.post("/drafts/{draft_id}/already-disputed", response_model=DraftActionRead)
def disputed(draft_id: int, data: DraftVersionCommand, user: CurrentUser, db: DbDep):
    """Crea una gara normale dal modal iniziale, saltando draft e READY."""
    actor = user.id
    def operation():
        result = already_disputed(db, draft_id, actor, data.version)
        return DraftActionRead(preparation=None, race_id=result.race_id)
    return draft_request(db, operation)


@router.post("/drafts/{draft_id}/cancel", status_code=status.HTTP_204_NO_CONTENT)
def cancel(draft_id: int, data: DraftVersionCommand, user: CurrentUser, db: DbDep):
    """Annulla e ripristina; solo creatore, dopo revoca del proprio READY."""
    draft_request(db, lambda: cancel_preparation(db, draft_id, user.id, data.version))
    return Response(status_code=204)
