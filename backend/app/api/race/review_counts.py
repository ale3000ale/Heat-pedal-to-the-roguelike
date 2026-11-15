from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Response
from pydantic import ValidationError

from app.api.deps import DbDep, JudgeUser
from app.api.race.race_review import DOMAIN_ERRORS, _http_error, _read
from app.schemas.race.race_review import RaceReviewRead
from app.schemas.race.review_counts import ReviewCountsRequest
from app.services.race.review_commit import (
    ReviewPermissionError, ReviewPlanConflict, _authorize,
    commit_review_counts, save_review_counts,
)

router = APIRouter(tags=["review-counts"])
BASE = "/{championship_id}/races/{race_id}/review"


@router.get(BASE + "/draft", response_model=ReviewCountsRequest | None)
def read_draft(championship_id: int, race_id: int, judge: JudgeUser, db: DbDep):
    """Restituisce la bozza al titolare della revisione attiva; nulla se assente.

    Errori: 403 per ruolo non autorizzato, 404 per riferimenti mancanti,
    409 per revisione non disponibile o JSON della bozza non valido.
    La lettura non consuma carte e non avvia la chiusura alla scadenza.
    """
    try:
        race = _authorize(db, championship_id, race_id, judge)
        return ReviewCountsRequest.model_validate_json(race.review_draft) if race.review_draft else None
    except ValidationError as exc:
        raise HTTPException(409, "Bozza non valida: nessun dato è stato modificato") from exc
    except ReviewPermissionError as exc:
        raise HTTPException(403, "Permesso negato") from exc
    except DOMAIN_ERRORS as exc:
        raise _http_error(exc) from exc


@router.put(BASE + "/draft", status_code=204)
def write_draft(championship_id: int, race_id: int, data: ReviewCountsRequest,
                judge: JudgeUser, db: DbDep) -> Response:
    """Salva i conteggi del revisore senza spostare carte; restituisce 204.

    Errori: 422 per richiesta invalida; 403/404/409 secondo ruolo e stato.
    Non modifica la scadenza e non conferma i conteggi.
    """
    try:
        save_review_counts(db, championship_id, race_id, judge, data)
        return Response(status_code=204)
    except ReviewPermissionError as exc:
        raise HTTPException(403, "Permesso negato") from exc
    except DOMAIN_ERRORS as exc:
        raise _http_error(exc) from exc


@router.post(BASE + "/counts/confirm", response_model=RaceReviewRead)
def confirm_counts(championship_id: int, race_id: int, data: ReviewCountsRequest,
                   judge: JudgeUser, db: DbDep):
    """Conferma atomicamente i conteggi del revisore attivo e restituisce lo stato.

    Un 409 con incongruities conserva solo la bozza. Le altre scritture sono
    annullate in caso di errore; la conferma legacy rimane su /review/confirm.
    """
    try:
        race = commit_review_counts(db, championship_id, race_id, judge, data)
        return _read(db, race)
    except ReviewPlanConflict as exc:
        raise HTTPException(409, {
            "message": "Correggi le incongruenze: la revisione non è stata confermata",
            "incongruities": [asdict(issue) for issue in exc.plan.issues],
        }) from exc
    except ReviewPermissionError as exc:
        raise HTTPException(403, "Permesso negato") from exc
    except DOMAIN_ERRORS as exc:
        raise _http_error(exc) from exc
