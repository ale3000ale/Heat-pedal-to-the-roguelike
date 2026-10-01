from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException, Response, status

from app.api.deps import (
    CurrentUser,
    DbDep,
    clear_session_cookie,
    set_session_cookie,
)
from app.config import SESSION_COOKIE_NAME
from app.schemas.auth import LoginRequest, RegisterRequest, UserRead
from app.services.sessions import create_session, delete_session
from app.services.users import (
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