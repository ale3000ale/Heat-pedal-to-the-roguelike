"""Parser dei codici effetto delle carte evento.

Il campo ``effetto`` di ``events.json`` ha due righe: la descrizione e, quando
presente, i codici separati da virgole definiti in ``regole effetti eventi.txt``.
Qui i codici vengono tradotti in valori utilizzabili dall'app e in etichette
italiane per l'interfaccia. Un codice non riconosciuto viene segnalato senza
interrompere la lettura degli altri.
"""
import re
from dataclasses import dataclass

_LAP = re.compile(r"^lap([+-]\d+)$")
_HAND = re.compile(r"^hand([+-]\d+)$")
_HEAT = re.compile(r"^H([+-]\d+)$")
_STRESS = re.compile(r"^St([+-]\d+)$")
_POSITION = re.compile(r"^pos1-(\d+)\+(\d+)$")
_SPONSOR = re.compile(r"^S\+(\d+)$")


@dataclass(frozen=True)
class EventEffects:
    """Effetto di una carta evento, con etichette già tradotte in italiano."""

    raw: str = ""
    summary: str = ""
    codes: str = ""
    laps: int | None = None
    hands: int | None = None
    heat: int | None = None
    stress: int | None = None
    position_limit: int = 0
    position_points: int = 0
    sponsor_points: int = 0
    labels: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    @property
    def has_codes(self) -> bool:
        return bool(self.codes)


def _signed(value: str) -> str:
    return value if value.startswith(("+", "-")) else f"+{value}"


def parse_effect(value: object) -> EventEffects:
    """Legge descrizione e codici di un effetto; non solleva errori sui codici.

    @param value Contenuto del campo ``effetto`` di events.json.
    @returns Effetto strutturato; campi vuoti e ``errors`` se i codici non sono validi.
    """
    if not isinstance(value, str):
        return EventEffects()
    raw = value
    lines = value.splitlines()
    summary = lines[0].strip() if lines else ""
    codes = lines[1].strip() if len(lines) > 1 else ""
    if not codes:
        return EventEffects(raw=raw, summary=summary)

    laps = hands = heat = stress = None
    position_limit = position_points = sponsor_points = 0
    labels: list[str] = []
    errors: list[str] = []
    for token in codes.split(","):
        code = token.strip()
        if not code:
            continue
        if match := _LAP.fullmatch(code):
            laps = int(match.group(1))
            labels.append(f"Giri: {_signed(match.group(1))}")
        elif match := _HAND.fullmatch(code):
            hands = int(match.group(1))
            labels.append(f"Carte in mano: {_signed(match.group(1))}")
        elif match := _HEAT.fullmatch(code):
            heat = int(match.group(1))
            labels.append(f"Heat: {_signed(match.group(1))}")
        elif match := _STRESS.fullmatch(code):
            stress = int(match.group(1))
            labels.append(f"Stress: {_signed(match.group(1))}")
        elif match := _POSITION.fullmatch(code):
            limit, points = int(match.group(1)), int(match.group(2))
            if limit < 1:
                errors.append(f"Posizione non valida: {code}")
                continue
            position_limit, position_points = limit, points
            labels.append(f"Primi {limit}: +{points} punti")
        elif match := _SPONSOR.fullmatch(code):
            sponsor_points = int(match.group(1))
            labels.append(f"Sponsor alle curve: +{sponsor_points} punti")
        else:
            errors.append(f"Codice non riconosciuto: {code}")

    return EventEffects(
        raw=raw,
        summary=summary,
        codes=codes,
        laps=laps,
        hands=hands,
        heat=heat,
        stress=stress,
        position_limit=position_limit,
        position_points=position_points,
        sponsor_points=sponsor_points,
        labels=tuple(labels),
        errors=tuple(errors),
    )
