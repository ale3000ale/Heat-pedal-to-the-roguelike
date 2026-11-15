import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session as DbSession

from app.db.models import Session, User

SESSION_DURATION = timedelta(days=7)


def _now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_session(db: DbSession, user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    db.add(
        Session(
            token_hash=_hash_token(token),
            user_id=user_id,
            expires_at=_now() + SESSION_DURATION,
        )
    )
    db.commit()
    return token


def get_user_by_token(db: DbSession, token: str) -> User | None:
    stmt = (
        select(User)
        .join(Session, Session.user_id == User.id)
        .where(Session.token_hash == _hash_token(token))
        .where(Session.expires_at > _now())
    )
    return db.execute(stmt).scalar_one_or_none()


def delete_session(db: DbSession, token: str) -> None:
    db.execute(delete(Session).where(Session.token_hash == _hash_token(token)))
    db.commit()


def purge_expired(db: DbSession) -> int:
    result = db.execute(delete(Session).where(Session.expires_at <= _now()))
    db.commit()
    return result.rowcount