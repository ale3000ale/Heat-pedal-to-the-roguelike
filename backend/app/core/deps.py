# backend/app/core/deps.py
# Dependency injection FastAPI: recupero utente corrente dal token, controllo ruolo admin.

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


# get_current_user(token, db)
# token: JWT opzionale letto dall'header Authorization (None se richiesta anonima).
# db: sessione SQLAlchemy iniettata da get_db.
# Ritorna l'utente autenticato o None se la richiesta e' anonima; usato dagli endpoint
# che devono comportarsi diversamente "con login / senza login".
def get_current_user_optional(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User | None:
    if token is None:
        return None
    payload = decode_access_token(token)
    if payload is None:
        return None
    username = payload.get("sub")
    if username is None:
        return None
    return db.query(User).filter(User.username == username).first()


# get_current_user_required(token, db)
# token: JWT obbligatorio letto dall'header Authorization.
# db: sessione SQLAlchemy iniettata da get_db.
# Solleva 401 se il token e' assente/invalido; usato dagli endpoint che richiedono login.
def get_current_user_required(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    user = get_current_user_optional(token, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticazione richiesta",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# require_admin(current_user)
# current_user: utente autenticato ottenuto da get_current_user_required.
# Solleva 403 se l'utente non ha ruolo 'admin'; usato per le operazioni di gestione avanzata.
def require_admin(current_user: User = Depends(get_current_user_required)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operazione riservata agli amministratori",
        )
    return current_user
