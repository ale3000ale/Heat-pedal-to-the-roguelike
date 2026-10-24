"""Cambio password e revoca sessioni in un'unica transazione SQLite."""
import hashlib
import sqlite3

from sqlalchemy import delete
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session as DbSession

from app.db.models import Session
from app.schemas.password_change import ChangePasswordRequest
from app.security import hash_password, verify_password
from app.services.sessions import get_user_by_token
from app.services.sqlite_write_lock import acquire_sqlite_write_lock


class PasswordSessionError(ValueError):
    """Sessione revocata o scaduta prima della scrittura autorevole."""


class InvalidCurrentPasswordError(ValueError):
    """La password attuale non corrisponde all'hash salvato."""


class PasswordChangeConflictError(ValueError):
    """SQLite occupato: nessun retry automatico della scrittura."""


def change_own_password(
    db: DbSession, user_id: int, token: str, data: ChangePasswordRequest
) -> None:
    """Cambia l'hash e revoca tutte le sessioni tranne quella indicata.

    Parametri: sessione DB senza modifiche pendenti, ID autenticato, token
    corrente e DTO validato. Ritorno: None. Dopo il lock rilegge utente e
    sessione per evitare di fidarsi della lettura preliminare della rotta.
    Non rinnova token/scadenza e non modifica altri account. Errori: quelli
    di dominio sopra, oppure errore originale con rollback. Nessun segreto
    viene scritto nei messaggi, nel registro eventi o nei log del servizio.
    """
    try:
        acquire_sqlite_write_lock(db)
        user = get_user_by_token(db, token)
        if user is None or user.id != user_id:
            raise PasswordSessionError("Non autenticato")
        if not verify_password(data.current_password.get_secret_value(), user.password):
            raise InvalidCurrentPasswordError("Password attuale non corretta")
        user.password = hash_password(data.new_password.get_secret_value())
        current_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        db.execute(
            delete(Session).where(
                Session.user_id == user_id, Session.token_hash != current_hash
            )
        )
        db.commit()
    except OperationalError as exc:
        db.rollback()
        code = getattr(exc.orig, "sqlite_errorcode", None)
        if code is not None and code & 0xFF in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED):
            raise PasswordChangeConflictError(
                "Database occupato: riprova manualmente"
            ) from exc
        raise
    except Exception:
        db.rollback()
        raise
