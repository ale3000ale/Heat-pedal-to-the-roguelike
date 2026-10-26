"""Validazione e conservazione esatta degli originali; nessuna scrittura DB."""
import pytest
from pydantic import ValidationError

from app.schemas.draft_snapshot import DraftDeckSnapshot, DraftSnapshot


def snapshot_payload(cards="[]"):
    """Restituisce un nuovo payload indipendente per ciascun caso di prova."""
    return {"format_version": 1, "decks": [{"deck_id": 1, "version": 3, "cards": cards}]}


@pytest.mark.parametrize("raw", [None, "", "[]", ' [ {"name":"Turbo", "path":"cards/turbo.webp", "copies":2} ] '])
def test_round_trip_preserves_original_text(raw):
    original = DraftSnapshot.model_validate(snapshot_payload(raw))
    restored = DraftSnapshot.model_validate_json(original.model_dump_json())
    assert restored == original
    assert restored.decks[0].cards == raw
    assert restored.decks[0].version == 3


@pytest.mark.parametrize("raw", ["not-json", "{}", '[{"name":"Turbo"}]',
    '[{"name":"Turbo","path":"cards/t.webp","copies":0}]',
    '[{"name":"Turbo","path":"cards/t.webp","copies":1},{"name":"turbo","path":"cards/t.webp","copies":1}]'])
def test_invalid_cards_are_rejected(raw):
    with pytest.raises(ValidationError):
        DraftSnapshot.model_validate(snapshot_payload(raw))


@pytest.mark.parametrize("field,value", [("deck_id", 0), ("deck_id", True),
    ("deck_id", "1"), ("version", 0), ("version", True), ("version", "3")])
def test_invalid_deck_metadata_is_rejected(field, value):
    data = snapshot_payload()
    data["decks"][0][field] = value
    with pytest.raises(ValidationError):
        DraftSnapshot.model_validate(data)


def test_duplicate_decks_are_rejected():
    data = snapshot_payload()
    data["decks"].append(dict(data["decks"][0]))
    with pytest.raises(ValidationError):
        DraftSnapshot.model_validate(data)


@pytest.mark.parametrize("version", [0, 2, True, "1"])
def test_unknown_or_coerced_format_is_rejected(version):
    data = snapshot_payload()
    data["format_version"] = version
    with pytest.raises(ValidationError):
        DraftSnapshot.model_validate(data)


def test_extra_fields_are_rejected():
    data = snapshot_payload()
    data["ignored"] = True
    with pytest.raises(ValidationError):
        DraftSnapshot.model_validate(data)
    with pytest.raises(ValidationError):
        DraftDeckSnapshot(deck_id=1, version=1, cards="[]", ignored=True)


def test_empty_snapshot_is_explicitly_valid():
    snapshot = DraftSnapshot(format_version=1, decks=[])
    assert snapshot.decks == []
