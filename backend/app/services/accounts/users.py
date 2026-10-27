from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DbSession

from app.db.models import User
from app.security import hash_password, verify_password

_DUMMY_HASH = hash_password("dummy-password-for-timing")


class UsernameTakenError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


def get_user_by_username(db: DbSession, username: str) -> User | None:
    return db.execute(
        select(User).where(User.username == username.strip().lower())
    ).scalar_one_or_none()


def register_user(db: DbSession, username: str, password: str) -> User:
    if get_user_by_username(db, username) is not None:
        raise UsernameTakenError
    user = User(
    username=username.strip().lower(),
    password=hash_password(password),
    role="player",
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise UsernameTakenError
    db.refresh(user)
    return user


def authenticate(db: DbSession, username: str, password: str) -> User:
    user = get_user_by_username(db, username)
    stored_hash = user.password if user is not None else _DUMMY_HASH
    password_ok = verify_password(password, stored_hash)
    if user is None or not password_ok:
        raise InvalidCredentialsError
    return user