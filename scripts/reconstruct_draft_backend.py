"""Ricostruisce sorgenti completi in staging; non fa push, test o migrazioni."""
import argparse
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

BASE = "3c0e617f232ebd8e2c659951e4a7586904b9cbb3"
CHECKPOINTS = {
    1: 6391973801, 2: 6391980944, 3: 6391993801,
    4: 6392006637, 5: 6392014606, 6: 6392026520,
    7: 6392037060, 8: 6392047199, 9: 6392060643, 10: 6392086380,
}
BLOBS = {
    "backend/app/services/championship/championships.py": "2297c9f62cee7839819873aebacb7065b5b76156",
    "backend/app/services/pilots/pilot_deck.py": "82323e7242ee1388babb1259d504cf82b05fcf65",
    "backend/app/services/shop/shop_purchase.py": "05c86708006830b6e6ef15fc48bcf590f0d7d429",
    "backend/app/services/cards/admin_pilot_cards.py": "1ea5f92073af7cee2ca1c3e07c4aec1ce36d5a91",
    "backend/app/services/race/races.py": "f6b13f844d6175cfb1d7ca5609749d2a39662462",
    "backend/app/services/draft/draft_preparation.py": "c8e2ecafd56e9e24bfce089522bf8298f3b7a8eb",
    "backend/app/main.py": "a5717972f432f118b35b6a04a155a16793c390a7",
}


def replace_once(source: str, before: str, after: str) -> str:
    """Sostituisce un'ancora esatta una volta; rifiuta assenza o ambiguita."""
    if source.count(before) != 1:
        raise ValueError(f"Ancora assente o ambigua: {before!r}")
    return source.replace(before, after, 1)


def wrap_write(source: str, name: str) -> str:
    """Avvolge una funzione esistente con lock/controllo/rollback conservandone il corpo.

    Analisi strutturale del sorgente, non esecuzione o test del modulo. Rifiuta
    funzioni mancanti/duplicate o docstring iniziali non previste nella base.
    """
    nodes = [n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == name]
    if len(nodes) != 1:
        raise ValueError(f"Funzione non univoca: {name}")
    node = nodes[0]
    if ast.get_docstring(node) is not None:
        raise ValueError(f"Docstring iniziale inattesa: {name}")
    lines = source.splitlines(keepends=True)
    start, end = node.body[0].lineno - 1, node.end_lineno
    original = lines[start:end]
    prefix = ["    try:\n", "        acquire_sqlite_write_lock(db)\n",
              "        require_no_draft(db, championship_id)\n"]
    suffix = ["    except Exception:\n", "        db.rollback()\n", "        raise\n"]
    return "".join(lines[:start] + prefix + ["    " + line for line in original] + suffix + lines[end:])


def read_base(root: Path) -> dict[str, str]:
    """Legge le versioni fissate con git show e ne verifica l'hash blob esatto."""
    result = {}
    for path, expected in BLOBS.items():
        raw = subprocess.run(["git", "show", f"{BASE}:{path}"], cwd=root,
                             check=True, capture_output=True).stdout
        actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        if actual != expected:
            raise ValueError(f"Base inattesa: {path}")
        result[path] = raw.decode("utf-8")
    return result


def checkpoint_files(comments: list[dict]) -> dict[str, str]:
    """Estrae soltanto file Python completi dai nove commenti identificati."""
    indexed = {int(comment["id"]): comment["body"] for comment in comments}
    result = {}
    pattern = r"^### (backend/[^\r\n]+\.py)\r?\n```python\r?\n(.*?)\r?\n```"
    for number, key in CHECKPOINTS.items():
        body = indexed[key]
        if not body.startswith(f"## Checkpoint di ricostruzione backend {number} "):
            raise ValueError(f"Titolo checkpoint inatteso: {key}")
        matches = re.findall(pattern, body, flags=re.M | re.S)
        if not matches:
            raise ValueError(f"Checkpoint senza file: {key}")
        for name, source in matches:
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or name in result:
                raise ValueError(f"Percorso non valido o duplicato: {name}")
            result[name] = source + "\n"
    return result


def integrate(base: dict[str, str], recovered: dict[str, str]) -> dict[str, str]:
    """Genera i sette file esistenti aggiornati e i nuovi moduli, senza scriverli."""
    out = dict(recovered)
    path = "backend/app/services/championship/championships.py"
    src = base[path]
    src = replace_once(src, "from dataclasses import dataclass\n",
        "from dataclasses import dataclass\nfrom app.services.draft.draft_guards import require_no_draft\nfrom app.services.core.sqlite_write_lock import acquire_sqlite_write_lock\n")
    for name in ("close_championship", "enroll_pilot", "delete_championship"):
        src = wrap_write(src, name)
    out[path] = src
    path = "backend/app/services/pilots/pilot_deck.py"
    src = replace_once(base[path], "from app.services.pilots.pilots import get_own_pilot\n",
        "from app.services.pilots.pilots import get_own_pilot\nfrom app.services.draft.draft_guards import pilot_has_draft, require_no_pilot_draft\n")
    src = replace_once(src, "            pilot = get_own_pilot(db, user, pilot_id)\n",
        "            pilot = get_own_pilot(db, user, pilot_id)\n            require_no_pilot_draft(db, pilot.id)\n")
    src = replace_once(src, "    return db.scalar(stmt) is not None\n",
        "    # deck_locked comprende la preparazione senza creare una Race.\n    return db.scalar(stmt) is not None or pilot_has_draft(db, pilot.id)\n")
    out[path] = src
    path = "backend/app/services/shop/shop_purchase.py"
    src = replace_once(base[path], "from app.services.race.races import has_race_in_progress\n",
        "from app.services.race.races import has_race_in_progress\nfrom app.services.draft.draft_guards import require_no_draft\nfrom app.services.core.sqlite_write_lock import acquire_sqlite_write_lock\n")
    src = replace_once(src, "            _lock_database(db)\n            result = _purchase",
        "            acquire_sqlite_write_lock(db)\n            result = _purchase")
    src = replace_once(src, "    if has_race_in_progress(db, championship_id):\n",
        "    require_no_draft(db, championship_id)\n    if has_race_in_progress(db, championship_id):\n")
    out[path] = src
    path = "backend/app/services/cards/admin_pilot_cards.py"
    src = replace_once(base[path], "from app.services.race.races import has_race_in_progress\n",
        "from app.services.race.races import has_race_in_progress\nfrom app.services.draft.draft_guards import has_draft\n")
    src = replace_once(src, "    if blocked is None and has_race_in_progress(db, championship_id):\n",
        "    if blocked is None and has_draft(db, championship_id):\n        blocked = \"Preparazione gara attiva\"\n    if blocked is None and has_race_in_progress(db, championship_id):\n")
    out[path] = src
    path = "backend/app/services/race/races.py"
    src = replace_once(base[path], "from app.services.core.event_log import append_event\n",
        "from app.services.core.event_log import append_event\nfrom app.services.draft.draft_guards import require_no_draft\n")
    src = replace_once(src, "        require_ready_championship_decks(db, championship_id)\n",
        "        require_no_draft(db, championship_id)\n        require_ready_championship_decks(db, championship_id)\n")
    out[path] = src
    path = "backend/app/services/draft/draft_preparation.py"
    src = replace_once(base[path], "from app.services.draft.draft_snapshot import capture_snapshot\n",
        "from app.services.draft.draft_snapshot import capture_snapshot\nfrom app.services.draft.draft_notifications import signal_draft_changed\n")
    src = replace_once(src, "        db.add(preparation)\n        db.commit()\n",
        "        db.add(preparation)\n        db.flush()\n        signal_draft_changed(db, preparation, state)\n        db.commit()\n")
    src = replace_once(src, "        row.state_json = state.model_dump_json()\n        db.commit()\n",
        "        row.state_json = state.model_dump_json()\n        signal_draft_changed(db, row, state)\n        db.commit()\n")
    out[path] = src
    path = "backend/app/main.py"
    src = replace_once(base[path], "from app.api.events import router as events_router\n",
        "from app.api.events import router as events_router\nfrom app.api.draft.draft import router as draft_router\nfrom app.api.draft.draft_errors import draft_locked_response\nfrom app.services.draft.draft_guards import DraftLockedError\n")
    src = replace_once(src, "app = FastAPI(title=\"Heat\", lifespan=lifespan)\n",
        "app = FastAPI(title=\"Heat\", lifespan=lifespan)\napp.add_exception_handler(DraftLockedError, draft_locked_response)\n")
    src = replace_once(src, "app.include_router(events_router, prefix=\"/api/events\")\n",
        "app.include_router(events_router, prefix=\"/api/events\")\napp.include_router(draft_router, prefix=\"/api\")\n")
    out[path] = src
    return out


def main() -> None:
    """Legge export commenti e base, poi scrive solo staging e manifest dei contenuti."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--comments", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root, output = args.repository.resolve(), args.output.resolve()
    if output == root or root in output.parents:
        raise ValueError("Lo staging deve essere esterno al repository")
    if output.exists() and any(output.iterdir()):
        raise ValueError("La cartella staging deve essere vuota")
    comments = json.loads(args.comments.read_text(encoding="utf-8"))
    files = integrate(read_base(root), checkpoint_files(comments))
    output.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name, source in sorted(files.items()):
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source, encoding="utf-8", newline="\n")
        manifest[name] = hashlib.sha256(source.encode()).hexdigest()
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
