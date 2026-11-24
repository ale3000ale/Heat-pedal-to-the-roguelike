"""Parser dei codici effetto degli eventi."""
from app.services.championship.event_effects import parse_effect


def test_parse_effect_reads_all_six_codes():
    effect = parse_effect(
        "Descrizione.\nlap-1, hand+2, H-2, St+1, pos1-3+4, S+1"
    )

    assert effect.summary == "Descrizione."
    assert effect.codes == "lap-1, hand+2, H-2, St+1, pos1-3+4, S+1"
    assert (effect.laps, effect.hands, effect.heat, effect.stress) == (-1, 2, -2, 1)
    assert (effect.position_limit, effect.position_points) == (3, 4)
    assert effect.sponsor_points == 1
    assert effect.has_codes
    assert effect.labels == (
        "Giri: -1",
        "Carte in mano: +2",
        "Heat: -2",
        "Stress: +1",
        "Primi 3: +4 punti",
        "Sponsor alle curve: +1 punti",
    )
    assert effect.errors == ()


def test_parse_effect_handles_effect_without_codes():
    effect = parse_effect("Niente.")

    assert effect.summary == "Niente."
    assert effect.codes == ""
    assert not effect.has_codes
    assert effect.labels == ()
    assert effect.position_limit == 0
    assert effect.sponsor_points == 0


def test_parse_effect_reports_unknown_codes_without_losing_valid_ones():
    effect = parse_effect("Testo.\nS+2, sbagliato, pos1-0+3")

    assert effect.sponsor_points == 2
    assert effect.position_limit == 0
    assert effect.errors == (
        "Codice non riconosciuto: sbagliato",
        "Posizione non valida: pos1-0+3",
    )


def test_parse_effect_accepts_missing_or_invalid_value():
    assert parse_effect(None).summary == ""
    assert parse_effect(42).codes == ""
