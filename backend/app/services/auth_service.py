# backend/app/services/auth_service.py
# Logica di business per registrazione e login utente.

from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, verify_password


# get_user_by_username(db, username)
# db: sessione SQLAlchemy attiva; username: username da cercare.
# Ricerca un utente per username, usato sia in login che in fase di registrazione (controllo duplicati).
def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


# create_user(db, username, password, role)
# db: sessione SQLAlchemy; username/password: credenziali scelte dall'utente; role: 'user' o 'admin'.
# Crea un nuovo utente con password hashata e lo salva nel DB.
# Passaggio critico: la password viene hashata con bcrypt prima del salvataggio, mai in chiaro.
def create_user(db: Session, username: str, password: str, role: str = "user") -> User:
    user = User(username=username, password=hash_password(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# authenticate_user(db, username, password)
# db: sessione SQLAlchemy; username/password: credenziali inviate dal form di login.
# Verifica esistenza utente e corrispondenza password; ritorna l'utente se valido, altrimenti None.
def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.password):
        return None
    return user
