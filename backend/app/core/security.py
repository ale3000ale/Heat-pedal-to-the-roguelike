# backend/app/core/security.py
# Funzioni di hashing password e creazione/verifica JWT.

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# hash_password(password)
# password: stringa in chiaro scelta dall'utente in fase di registrazione.
# Restituisce l'hash bcrypt da salvare nel campo User.password. Non salvare MAI la password in chiaro.
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# verify_password(plain_password, hashed_password)
# plain_password: password digitata al login; hashed_password: hash salvato nel DB.
# Confronta le due stringhe tramite bcrypt e ritorna True/False. Usato per validare il login.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# create_access_token(data, expires_delta)
# data: dizionario da includere nel payload del token (es. {"sub": username, "role": role}).
# expires_delta: durata personalizzata di validita' del token (opzionale).
# Crea e firma un JWT con scadenza: e' il token che il frontend salva in localStorage.
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# decode_access_token(token)
# token: stringa JWT ricevuta nell'header Authorization della richiesta.
# Verifica firma e scadenza del token e ritorna il payload, oppure None se non valido.
# Passaggio critico: se la firma non corrisponde o il token e' scaduto, l'accesso viene negato.
def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
