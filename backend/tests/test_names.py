from app.services.names import clean_name, name_key


def test_clean_name_toglie_spazi_extra():
    assert clean_name("  Scuderia   Rossa ") == "Scuderia Rossa"


def test_name_key_ignora_le_maiuscole():
    assert name_key("Scuderia Rossa") == name_key("SCUDERIA  rossa")


def test_name_key_gestisce_accenti_e_lettere_speciali():
    assert name_key("ÉCURIE") == name_key("écurie")
    assert name_key("Straße") == name_key("STRASSE")


def test_nomi_diversi_hanno_chiavi_diverse():
    assert name_key("Rossa") != name_key("Rosso")