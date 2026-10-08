import argparse
import os
from pathlib import Path

from app.config import MEDIA_DIR
from app.services.images import MAX_CARD_SIZE, CardImageError, fit_card_image, load_image

EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
# Cartelle trattate se non se ne indica nessuna: carte e immagini dei pacchetti.
DEFAULT_FOLDERS = (MEDIA_DIR / "cards", MEDIA_DIR / "pack")


def process_image(path: Path, dry_run: bool = False) -> str:
    # Porta una sola immagine in WebP dentro la scatola massima.
    # Restituisce: "ok" (già a posto), "sistemata", "gia_convertita" (esiste già la
    # versione WebP di un file png/jpg, che non viene toccato) o "non_valida".
    # L'originale png/jpg non viene mai cancellato; il WebP si scrive in un file
    # temporaneo e poi si sostituisce, così un errore non lascia file a metà.
    try:
        image = load_image(path.read_bytes())
    except (CardImageError, OSError):
        return "non_valida"
    is_webp = path.suffix.lower() == ".webp"
    too_big = image.width > MAX_CARD_SIZE[0] or image.height > MAX_CARD_SIZE[1]
    if is_webp and not too_big:
        return "ok"
    target = path.with_suffix(".webp")
    if not is_webp and target.exists():
        return "gia_convertita"
    if not dry_run:
        temporary = target.with_name(target.name + ".tmp")
        fit_card_image(image).save(temporary, "WEBP", quality=90, method=6)
        os.replace(temporary, target)
    return "sistemata"


def process_folder(folder: Path, dry_run: bool = False, log=print) -> dict[str, int]:
    # Tratta tutte le immagini di una cartella e delle sue sottocartelle.
    # Restituisce il numero di immagini per esito; una cartella mancante dà solo zeri.
    counts = {"ok": 0, "sistemata": 0, "gia_convertita": 0, "non_valida": 0}
    if not folder.is_dir():
        log(f"CARTELLA NON TROVATA: {folder}")
        return counts
    for path in sorted(folder.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        outcome = process_image(path, dry_run)
        counts[outcome] += 1
        label = {
            "ok": "ok",
            "sistemata": "DA SISTEMARE" if dry_run else "sistemata",
            "gia_convertita": "già convertita",
            "non_valida": "SALTATA (non valida)",
        }[outcome]
        log(f"{label}: {path}")
    return counts


def main() -> None:
    # Porta in WebP, dentro la scatola massima, le immagini delle carte e dei pacchetti.
    # Le immagini già a posto non vengono toccate (nessuna ricompressione a ogni
    # esecuzione) e gli originali png/jpg restano dove sono.
    parser = argparse.ArgumentParser(
        description="Ridimensiona e converte in WebP le immagini di carte e pacchetti"
    )
    parser.add_argument(
        "folders",
        nargs="*",
        help="cartelle da trattare (predefinite: media/cards e media/pack)",
    )
    parser.add_argument("--dry-run", action="store_true", help="mostra cosa farebbe")
    args = parser.parse_args()

    folders = [Path(f) for f in args.folders] or list(DEFAULT_FOLDERS)
    totals = {"ok": 0, "sistemata": 0, "gia_convertita": 0, "non_valida": 0}
    for folder in folders:
        for key, value in process_folder(folder, args.dry_run).items():
            totals[key] += value
    print(
        f"Riepilogo: {totals['ok']} già a posto, {totals['sistemata']} sistemate, "
        f"{totals['gia_convertita']} già convertite, {totals['non_valida']} non valide"
    )


if __name__ == "__main__":
    main()
