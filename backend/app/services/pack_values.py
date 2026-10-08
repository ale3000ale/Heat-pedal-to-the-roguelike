from app.services.pack_images import (
    DEFAULT_FOLDER,
    PackImageError,
    is_available_pack_image,
    list_pack_images,
)

# Caratteristiche comuni a template di pacchetto e pacchetti del campionato.
PACK_FIELDS = (
    "name",
    "image_path",
    "currency",
    "cost",
    "modifiche_count",
    "sponsor_count",
    "filter_enabled",
    "filter_text",
)


def resolve_image(image_path: str | None) -> str:
    # Restituisce il percorso dell'immagine da salvare. Senza percorso usa la prima
    # immagine predefinita.
    # Errori: PackImageError se il percorso non è tra le immagini disponibili o se non
    # c'è nessuna immagine predefinita.
    if image_path is None:
        defaults = [p for p in list_pack_images() if p.startswith(f"{DEFAULT_FOLDER}/")]
        if not defaults:
            raise PackImageError("Nessuna immagine predefinita disponibile")
        return defaults[0]
    if not is_available_pack_image(image_path):
        raise PackImageError("Immagine non disponibile")
    return image_path


def values_of(source) -> dict:
    # Legge le caratteristiche da un template o da un pacchetto.
    return {field: getattr(source, field) for field in PACK_FIELDS}


def apply_pack_values(target, values: dict) -> None:
    # Copia le caratteristiche del pacchetto su un template o su un pacchetto.
    # Senza commit: lo fa chi chiama.
    for field in PACK_FIELDS:
        setattr(target, field, values[field])
