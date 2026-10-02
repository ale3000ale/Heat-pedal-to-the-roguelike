import argparse
from pathlib import Path

from app.config import MEDIA_DIR
from app.services.images import MAX_CARD_SIZE, CardImageError, fit_card_image, load_image

EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def main() -> None:
    # Porta tutte le immagini di una cartella in WebP dentro la scatola massima.
    # Le immagini già a posto non vengono toccate (evita di ricomprimerle a ogni esecuzione).
    parser = argparse.ArgumentParser(description="Ridimensiona le immagini delle carte")
    parser.add_argument("folder", nargs="?", default=str(MEDIA_DIR / "cards"))
    parser.add_argument("--dry-run", action="store_true", help="mostra cosa farebbe")
    args = parser.parse_args()

    for path in sorted(Path(args.folder).rglob("*")):
        if path.suffix.lower() not in EXTENSIONS:
            continue
        try:
            image = load_image(path.read_bytes())
        except CardImageError:
            print(f"SALTATA (non valida): {path}")
            continue
        width, height = image.size
        too_big = width > MAX_CARD_SIZE[0] or height > MAX_CARD_SIZE[1]
        if path.suffix.lower() == ".webp" and not too_big:
            print(f"ok ({width}x{height}): {path}")
            continue
        target = path.with_suffix(".webp")
        print(f"{'DA SISTEMARE' if args.dry_run else 'sistemata'} ({width}x{height}): {path}")
        if not args.dry_run:
            fit_card_image(image).save(target, "WEBP", quality=90, method=6)


if __name__ == "__main__":
    main()