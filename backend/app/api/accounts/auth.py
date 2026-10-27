from typing import Annotated

from fastapi import APIRouter, Body, Cookie, HTTPException, Response, status
from pydantic import ValidationError

from app.api.deps import (
    CurrentUser,
    DbDep,
    clear_session_cookie,
    set_session_cookie,
)
from app.config import SESSION_COOKIE_NAME
from app.schemas.accounts.auth import LoginRequest, RegisterRequest, UserRead
from app.schemas.accounts.password_change import ChangePasswordRequest
from app.services.accounts.password_changes import (
    InvalidCurrentPasswordError,
    PasswordChangeConflictError,
    PasswordSessionError,
    change_own_password,
)
from app.services.accounts.sessions import create_session, delete_session
from app.services.accounts.users import (
    InvalidCredentialsError,
    UsernameTakenError,
    authenticate,
    register_user,
)

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: DbDep, response: Response):
    try:
        user = register_user(db, data.username, data.password)
    except UsernameTakenError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username già in uso")
    set_session_cookie(response, create_session(db, user.id))
    return user


@router.post("/login", response_model=UserRead)
def login(data: LoginRequest, db: DbDep, response: Response):
    try:
        user = authenticate(db, data.username, data.password)
    except InvalidCredentialsError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenziali non valide")
    set_session_cookie(response, create_session(db, user.id))
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    db: DbDep,
    response: Response,
    heat_session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
):
    if heat_session:
        delete_session(db, heat_session)
    clear_session_cookie(response)


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser):
    return user


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    data: Annotated[object, Body()],
    user: CurrentUser,
    db: DbDep,
    response: Response,
    heat_session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
):
    """Aggiorna solo il proprio account; conserva la sessione del chiamante.

    La validazione manuale Pydantic evita che gli errori standard includano
    le password nella risposta 422. Nessun campo del corpo sceglie l'utente.
    Successo 204; 401 sessione assente, 403 password attuale errata, 409 lock,
    422 corpo non valido. Non vengono restituiti hash, token o password.
    """
    response.headers["Cache-Control"] = "no-store"
    try:
        parsed = ChangePasswordRequest.model_validate(data)
    except ValidationError:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "Controlla i campi: nuova password di 8-128 caratteri e conferma identica",
            headers={"Cache-Control": "no-store"},
        ) from None
    if not heat_session:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Non autenticato")
    try:
        change_own_password(db, user.id, heat_session, parsed)
    except PasswordSessionError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Non autenticato") from None
    except InvalidCurrentPasswordError:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Password attuale non corretta"
        ) from None
    except PasswordChangeConflictError:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Database occupato: riprova manualmente"
        ) from None
