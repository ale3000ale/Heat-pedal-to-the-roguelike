from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User

ASSIGNABLE_ROLES = ("player", "judge")


class UserNotFoundError(Exception):
    """L'utente non esiste."""


class AdminRoleLockedError(Exception):
    """Il ruolo di un admin non si può cambiare (nemmeno il proprio)."""


def list_users(db: Session) -> list[User]:
    # Tutti gli utenti, in ordine alfabetico.
    return list(db.scalars(select(User).order_by(User.username)))


def set_role(db: Session, user_id: int, role: str) -> User:
    # Assegna o toglie il ruolo di giudice. Gli admin non si toccano.
    if role not in ASSIGNABLE_ROLES:
        raise ValueError(role)
    user = db.get(User, user_id)
    if user is None:
        raise UserNotFoundError
    if user.role == "admin":
        raise AdminRoleLockedError
    user.role = role
    db.commit()
    db.refresh(user)
    return user
