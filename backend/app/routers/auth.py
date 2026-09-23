# backend/app/routers/auth.py
# Endpoint di registrazione e login.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.auth import UserRegister, UserLogin, Token, UserOut
from app.services.auth_service import get_user_by_username, create_user, authenticate_user
from app.core.security import create_access_token
from app.core.deps import get_current_user_required
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


# register(payload, db)
# payload: username + password (min 8 caratteri) validati da Pydantic; db: sessione SQLAlchemy.
# Crea un nuovo utente con ruolo 'user' se lo username non e' gia' in uso.
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    if get_user_by_username(db, payload.username) is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Username gia' in uso")
    user = create_user(db, payload.username, payload.password, role="user")
    return user


# login(payload, db)
# payload: username + password inviati dal form di login; db: sessione SQLAlchemy.
# Verifica le credenziali e, se valide, genera un JWT contenente username e ruolo.
# Passaggio critico: il token generato e' cio' che il frontend salvera' in localStorage per le richieste successive.
@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.username, payload.password)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Username o password non validi")
    token = create_access_token({"sub": user.username, "role": user.role})
    return Token(access_token=token, role=user.role, username=user.username)


# me(current_user)
# current_user: utente autenticato ottenuto dal token JWT.
# Ritorna i dati base dell'utente loggato, usato dal frontend per idratare lo store auth.
@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user_required)):
    return current_user
