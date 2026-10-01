from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session as DbSession

from app.config import SESSION_COOKIE_NAME, SESSION_COOKIE_SECURE
from app.db.models import User
from app.db.session import get_db
from app.services.sessions import SESSION_DURATION, get_user_by_token

DbDep = Annotated[DbSession, Depends(get_db)]


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=int(SESSION_DURATION.total_seconds()),
        httponly=True,
        samesite="lax",
        secure=SESSION_COOKIE_SECURE,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        httponly=True,
        samesite="lax",
        secure=SESSION_COOKIE_SECURE,
        path="/",
    )


def get_current_user(
    db: DbDep,
    heat_session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
) -> User:
    user = get_user_by_token(db, heat_session) if heat_session else None
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Non autenticato")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_admin(user: CurrentUser) -> User:
    if user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Permesso negato")
    return user


AdminUser = Annotated[User, Depends(require_admin)]