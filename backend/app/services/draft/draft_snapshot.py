"""Primitive interne; transazione, autorizzazioni e lock appartengono al chiamante."""
from collections.abc import Mapping, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.deck import Deck
from app.schemas.draft.draft_snapshot import DraftDeckSnapshot, DraftSnapshot


class DraftSnapshotConflictError(ValueError):
    """Snapshot non applicabile senza rischiare di perdere modifiche."""


def _require_clean(db: Session) -> None:
    """Rifiuta modifiche pendenti per evitare flush impliciti o ripristini parziali."""
    if db.new or db.dirty or db.deleted:
        raise DraftSnapshotConflictError("La sessione contiene modifiche pendenti")


def capture_snapshot(db: Session, deck_ids: Sequence[int]) -> DraftSnapshot:
    """Legge originali e versioni senza scrivere o fare commit.

    Parametri: sessione pulita sotto lock condiviso gia acquisito, ID distinti.
    Ritorna snapshot validato. ID non validi, mancanti o ripetuti generano
    DraftSnapshotConflictError; errori carte e SQL propagano al chiamante.
    Il chiamante mantiene il lock fino al salvataggio della preparazione.
    """
    _require_clean(db)
    ids = list(deck_ids)
    if any(type(value) is not int or value < 1 for value in ids) or len(set(ids)) != len(ids):
        raise DraftSnapshotConflictError("Identificativi mazzi non validi o ripetuti")
    rows = db.execute(select(Deck.id, Deck.version, Deck.cards).where(Deck.id.in_(ids))).all()
    by_id = {row.id: row for row in rows}
    if set(by_id) != set(ids):
        raise DraftSnapshotConflictError("Uno o piu mazzi non esistono")
    return DraftSnapshot(format_version=1, decks=[
        DraftDeckSnapshot(deck_id=key, version=by_id[key].version, cards=by_id[key].cards)
        for key in ids
    ])


def stage_snapshot_restore(
    db: Session, snapshot: DraftSnapshot, expected_versions: Mapping[int, int]
) -> None:
    """Prepara il ripristino solo dopo aver verificato tutti i mazzi.

    Parametri: sessione pulita sotto lock, snapshot originale, versioni correnti
    attese registrate dalla preparazione dopo le proprie scritture. Le versioni
    iniziali dello snapshot non sostituiscono quelle correnti attese.
    Ritorna None, senza flush/commit: il chiamante salva ripristino e cancellazione
    della preparazione nella stessa transazione e fa rollback su ogni errore.
    DraftSnapshotConflictError per conflitti o riferimenti incompleti. Nessuna
    modifica ORM prima della verifica completa; mai decrementare Deck.version.
    Non acquisisce lock e non autorizza utenti: non esporre direttamente via API.
    """
    _require_clean(db)
    snapshot = DraftSnapshot.model_validate(snapshot.model_dump())
    ids = [item.deck_id for item in snapshot.decks]
    if set(expected_versions) != set(ids) or any(
        type(key) is not int or type(value) is not int or value < 1
        for key, value in expected_versions.items()
    ):
        raise DraftSnapshotConflictError("Versioni attese incomplete o non valide")
    decks = db.scalars(select(Deck).where(Deck.id.in_(ids)).execution_options(populate_existing=True)).all()
    by_id = {deck.id: deck for deck in decks}
    if set(by_id) != set(ids) or any(
        by_id[key].version != expected_versions[key] for key in ids
    ):
        raise DraftSnapshotConflictError("Mazzi modificati o mancanti: ripristino non applicato")
    for item in snapshot.decks:
        by_id[item.deck_id].cards = item.cards
