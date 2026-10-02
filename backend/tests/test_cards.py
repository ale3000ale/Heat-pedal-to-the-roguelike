import pytest

from app.services.cards import (
    STARTER_INVENTORY,
    CardEntry,
    CardError,
    dump_cards,
    parse_card_filename,
    parse_cards,
    validate_game_deck,
)


def card(name, copies):
    # Scorciatoia per creare una carta di prova.
    return CardEntry(name=name, path=f"images/cards/{name}.webp", copies=copies)


def test_starter_inventory_ha_quattro_velocita_da_tre_copie():
    assert [c.copies for c in STARTER_INVENTORY] == [3, 3, 3, 3]
    assert len(STARTER_INVENTORY) == 4


def test_dump_e_parse_restituiscono_le_stesse_carte():
    cards = [card("Freni maggiorati", 5), card("Velocità 1", 3)]
    assert parse_cards(dump_cards(cards)) == cards


def test_parse_accetta_testo_vuoto():
    assert parse_cards(None) == []
    assert parse_cards("") == []


def test_parse_rifiuta_json_errato():
    with pytest.raises(CardError):
        parse_cards('[{"name": "x"}]')


def test_parse_rifiuta_nomi_duplicati_anche_con_maiuscole_diverse():
    raw = dump_cards([card("Freni", 1), card("FRENI", 2)])
    with pytest.raises(CardError):
        parse_cards(raw)


def test_mazzo_valido():
    inventory = [card("Velocità 1", 3), card("Freni", 5)]
    validate_game_deck(inventory, [card("Velocità 1", 2), card("Freni", 5)])
    assert True


def test_mazzo_oltre_quindici_carte():
    inventory = [card("Freni", 30)]
    with pytest.raises(CardError):
        validate_game_deck(inventory, [card("Freni", 16)])


def test_mazzo_con_piu_copie_dell_inventario():
    inventory = [card("Freni", 2)]
    with pytest.raises(CardError):
        validate_game_deck(inventory, [card("Freni", 3)])


def test_mazzo_con_carta_non_posseduta():
    with pytest.raises(CardError):
        validate_game_deck([card("Freni", 2)], [card("Turbo", 1)])


def test_nome_file_con_copie():
    assert parse_card_filename("ruota da bagnato_3.png") == ("ruota da bagnato", 3)
    assert parse_card_filename("Velocità 1_12.webp") == ("Velocità 1", 12)


@pytest.mark.parametrize("filename", ["senza-numero.png", "_3.png", "carta_0.png", "carta_x.png"])
def test_nome_file_non_valido(filename):
    with pytest.raises(CardError):
        parse_card_filename(filename)