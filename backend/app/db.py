# backend/app/db.py
# Configurazione del motore SQLAlchemy e gestione delle sessioni verso il DB SQLite HeatDB.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./heat.db"

# check_same_thread=False necessario perche' FastAPI usa thread diversi per le richieste
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# get_db()
# Nessun parametro.
# Genera una sessione DB per la durata della singola richiesta HTTP e la chiude sempre al termine,
# cosi' da evitare connessioni SQLite "leaked" tra le richieste.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
