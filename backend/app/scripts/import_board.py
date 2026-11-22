"""Importa immagini di mappe ed eventi in WebP dentro media/board."""
import argparse
import os
import re
import unicodedata
import webbrowser
from pathlib import Path

from PIL import Image, ImageOps

from app.config import MEDIA_DIR
from app.services.cards.images import CardImageError, load_image, unique_filename

EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
BOARD_DIR = MEDIA_DIR / "board"
# Stessa scatola delle carte: il rapporto dell'immagine non viene deformato.
MAX_SIZE = (560, 870)


def safe_slug(name: str) -> str:
    # Nome di file sicuro: senza accenti, minuscolo, solo lettere, numeri e trattini.
    ascii_text = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug or "immagine"


def resolve_destination(value: str, root: Path = BOARD_DIR) -> Path:
    # Accetta events, maps o una sottocartella; rifiuta percorsi fuori da media/board.
    root = root.resolve()
    candidate = Path(value)
    resolved = (candidate if candidate.is_absolute() else root / candidate).resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError("La destinazione deve stare dentro backend/media/board")
    return resolved


def collect_sources(values) -> list[Path]:
    # Raccoglie file e cartelle, anche ricorsive, senza duplicati e in ordine.
    found: dict[Path, None] = {}
    for value in values:
        path = Path(value)
        if path.is_dir():
            for item in sorted(path.rglob("*")):
                if item.is_file() and item.suffix.lower() in EXTENSIONS:
                    found[item] = None
        elif path.is_file() and path.suffix.lower() in EXTENSIONS:
            found[path] = None
        else:
            raise ValueError(f"File o cartella non valida: {value}")
    if not found:
        raise ValueError("Nessuna immagine trovata")
    return list(found)


def fit_image(image: Image.Image) -> Image.Image:
    # Riduce dentro la scatola massima mantenendo le proporzioni, senza tagliare.
    fitted = ImageOps.exif_transpose(image)
    if fitted.mode not in ("RGB", "RGBA"):
        fitted = fitted.convert("RGBA")
    fitted.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
    return fitted


def show_image(path: Path) -> None:
    # Apre l'anteprima nel visualizzatore predefinito del sistema.
    try:
        if hasattr(os, "startfile"):
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            webbrowser.open(path.as_uri())
    except OSError:
        print(f"Anteprima non disponibile: {path}")


def target_path(destination: Path, slug: str, source: Path) -> Path:
    # Un WebP già presente nella destinazione viene riscritto solo se è la sorgente.
    direct = destination / f"{slug}.webp"
    if direct.resolve() == source.resolve():
        return direct
    return destination / unique_filename(destination, slug)


def import_images(
    sources,
    destination: Path,
    *,
    keep_name: bool = False,
    preview: bool = True,
    dry_run: bool = False,
    remove_source: bool = False,
    ask=input,
    show=show_image,
    log=print,
) -> dict[str, int]:
    # Importa le immagini una alla volta; l'originale si elimina solo dopo la verifica.
    counts = {"salvate": 0, "non_valide": 0, "errori": 0, "rimosse": 0}
    for source in sources:
        try:
            image = load_image(source.read_bytes())
        except (CardImageError, OSError):
            counts["non_valide"] += 1
            log(f"SALTATA (non valida): {source}")
            continue
        if preview:
            show(source)
        proposed = source.stem
        if keep_name:
            name = proposed
        else:
            answer = ask(f"Nome per {source.name} [{proposed}]: ").strip()
            name = answer or proposed
        target = target_path(destination, safe_slug(name), source)
        if dry_run:
            log(f"DA SALVARE: {source} -> {target}")
            counts["salvate"] += 1
            continue
        temporary = None
        try:
            destination.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(target.name + ".tmp")
            fit_image(image).save(temporary, "WEBP", quality=90, method=6)
            with Image.open(temporary) as check:
                check.verify()
            os.replace(temporary, target)
        except (OSError, ValueError) as exc:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
            counts["errori"] += 1
            log(f"ERRORE su {source}: {exc}")
            continue
        counts["salvate"] += 1
        log(f"SALVATA: {target}")
        if remove_source and source.resolve() != target.resolve():
            source.unlink()
            counts["rimosse"] += 1
            log(f"RIMOSSA: {source}")
    return counts


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        description="Importa immagini di mappe ed eventi in WebP, con anteprima e rinomina"
    )
    parser.add_argument("sources", nargs="+", help="file o cartelle di immagini")
    parser.add_argument(
        "--dest",
        required=True,
        help="events, maps o una sottocartella di backend/media/board",
    )
    parser.add_argument(
        "--keep-name",
        action="store_true",
        help="usa il nome del file senza chiedere (importazione non interattiva)",
    )
    parser.add_argument("--no-preview", action="store_true", help="non aprire l'anteprima")
    parser.add_argument(
        "--remove-source",
        action="store_true",
        help="elimina l'originale dopo un WebP salvato e verificato",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="mostra cosa farebbe senza scrivere"
    )
    args = parser.parse_args(argv)

    try:
        destination = resolve_destination(args.dest)
        sources = collect_sources(args.sources)
    except ValueError as exc:
        parser.error(str(exc))

    counts = import_images(
        sources,
        destination,
        keep_name=args.keep_name,
        preview=not args.no_preview,
        dry_run=args.dry_run,
        remove_source=args.remove_source,
    )
    print(
        f"Riepilogo: {counts['salvate']} salvate, {counts['rimosse']} originali rimossi, "
        f"{counts['non_valide']} non valide, {counts['errori']} errori"
    )


if __name__ == "__main__":
    main()
