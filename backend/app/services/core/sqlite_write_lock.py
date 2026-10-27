"""Lock SQLite condiviso per operazioni che devono rileggere lo stato prima di scrivere."""
from sqlalchemy.orm import Session


class SQLiteWriteLockError(ValueError):
    """Dialetto non supportato o modifiche pendenti prima del lock."""


def acquire_sqlite_write_lock(db: Session) -> None:
    """Riserva la scrittura e invalida le letture ORM precedenti, senza commit.

    Parametro: sessione SQLite prima di qualunque modifica pendente.
    Ritorno: None. Errori: SQLiteWriteLockError se il contratto e' violato;
    OperationalError di SQLite se il lock/snapshot non e' acquisibile.
    Una transazione nativa gia' aperta viene promossa con UPDATE senza righe:
    nessuna carta o versione viene modificata. Il chiamante deve gestire
    commit/rollback e tradurre gli eventuali conflitti; nessun retry interno.
    """
    if db.new or db.dirty or db.deleted:
        raise SQLiteWriteLockError("Acquisire il lock prima delle modifiche pendenti")
    connection = db.connection()
    if connection.dialect.name != "sqlite":
        raise SQLiteWriteLockError("Questa operazione richiede SQLite")
    if connection.connection.driver_connection.in_transaction:
        connection.exec_driver_sql("UPDATE deck SET version = version WHERE 0")
    else:
        connection.exec_driver_sql("BEGIN IMMEDIATE")
    db.expire_all()
