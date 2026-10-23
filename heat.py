#!/usr/bin/env python3
import argparse
import os
import platform
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

from tools.production import normalize_origin, start_production

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
TOOLS = ROOT / "tools"
VENV = BACKEND / ".venv"
SYSTEM = platform.system()
IS_WIN = SYSTEM == "Windows"
VENV_PY = VENV / ("Scripts/python.exe" if IS_WIN else "bin/python")
HOST = "127.0.0.1"
BACKEND_PORT = 8000
FRONTEND_PORT = 5173
MIN_PYTHON = (3, 11)


def info(msg):
    print(f"\n==> {msg}", flush=True)


def fail(msg):
    raise SystemExit(f"\nERRORE: {msg}")


def run(cmd, cwd, check=True, env=None):
    result = subprocess.run([str(c) for c in cmd], cwd=cwd, env=env)
    if check and result.returncode != 0:
        fail(f"Comando fallito: {' '.join(str(c) for c in cmd)}")
    return result.returncode


def has_frontend():
    return (FRONTEND / "package.json").exists()


def find_npm():
    npm = shutil.which("npm")
    if not npm:
        fail("npm non trovato. Installa Node.js da https://nodejs.org")
    return npm


def migrate():
    if not VENV_PY.exists():
        fail("Ambiente non pronto. Scegli prima 'Setup'")
    info("Applico le migrazioni del database")
    run([VENV_PY, "-m", "alembic", "upgrade", "head"], BACKEND)


def setup(skip_admin=False, skip_seed=False):
    if sys.version_info < MIN_PYTHON:
        fail(f"Serve Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} o superiore")
    if not VENV_PY.exists():
        info("Creo l'ambiente virtuale backend/.venv")
        run([sys.executable, "-m", "venv", VENV], ROOT)
    else:
        info("Ambiente virtuale gia' presente")
    info("Installo le dipendenze Python")
    run([VENV_PY, "-m", "pip", "install", "--upgrade", "pip"], BACKEND)
    run([VENV_PY, "-m", "pip", "install", "-r", "requirements.txt"], BACKEND)
    migrate()
    if not skip_seed:
        run([VENV_PY, "-m", "app.scripts.seed_prototype"], BACKEND)
    if not skip_admin:
        run([VENV_PY, "-m", "app.scripts.create_admin"], BACKEND)
    if has_frontend():
        lock = (FRONTEND / "package-lock.json").exists()
        run([find_npm(), "ci" if lock else "install"], FRONTEND)
    else:
        info("Cartella frontend/ non presente: salto")
    info("Setup completato")


def spawn(cmd, cwd, env=None):
    cmd = [str(c) for c in cmd]
    if IS_WIN:
        return subprocess.Popen(
            cmd, cwd=cwd, env=env, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
    return subprocess.Popen(cmd, cwd=cwd, env=env, start_new_session=True)


def stop(proc):
    """Arresta il gruppo figlio; attende 8 secondi prima del fallback forzato."""
    if proc.poll() is not None:
        return
    try:
        if IS_WIN:
            proc.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        proc.wait(timeout=8)
    except ProcessLookupError:
        return
    except (subprocess.TimeoutExpired, OSError):
        if IS_WIN:
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"])
        else:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            info(f"Impossibile confermare l'arresto del processo {proc.pid}")


def start(backend_only=False, public_url=None):
    env = os.environ.copy()
    if public_url:
        env["HEAT_PUBLIC_URL"] = normalize_origin(public_url)
    if not VENV_PY.exists():
        fail("Ambiente non pronto. Scegli prima 'Setup'")
    # Comportamento storico dello sviluppo; production non chiama migrate().
    migrate()
    procs = []
    try:
        info(f"Avvio sviluppo su http://{HOST}:{FRONTEND_PORT}")
        procs.append(spawn(
            [VENV_PY, "-m", "uvicorn", "app.main:app", "--reload",
             "--host", HOST, "--port", BACKEND_PORT], BACKEND
        ))
        if has_frontend() and not backend_only:
            if not (FRONTEND / "node_modules").exists():
                fail("Dipendenze frontend mancanti. Scegli prima 'Setup'")
            procs.append(spawn(
                [find_npm(), "run", "dev", "--", "--host", HOST,
                 "--port", FRONTEND_PORT, "--strictPort"], FRONTEND, env=env
            ))
        info("Sviluppo avviato. Premi Ctrl+C per fermare")
        while all(p.poll() is None for p in procs):
            time.sleep(0.5)
        fail("Un processo di sviluppo si e' fermato")
    except KeyboardInterrupt:
        info("Arresto in corso")
    finally:
        for proc in reversed(procs):
            stop(proc)


def production(public_url=None):
    """Avvia build Node e FastAPI senza reload o migrazioni automatiche."""
    start_production(ROOT, VENV_PY, public_url, info, run, spawn, stop)


def production_menu():
    production(input("URL pubblico HTTPS (Invio: solo locale): ").strip() or None)


def run_tests():
    if not VENV_PY.exists():
        fail("Ambiente non pronto. Scegli prima 'Setup'")
    run([VENV_PY, "-m", "pytest", "-q"], BACKEND, check=False)


def run_checks():
    script = TOOLS / "check-frontend.mjs"
    node = shutil.which("node")
    if not script.exists() or not node:
        fail("Servono node e tools/check-frontend.mjs")
    run([node, script], ROOT, check=False)


MENU = [
    ("Setup (installa tutto)", lambda: setup()),
    ("Aggiorna il database (migrazioni)", migrate),
    ("Avvia sviluppo backend e frontend", lambda: start()),
    ("Avvia solo il backend di sviluppo", lambda: start(backend_only=True)),
    ("Esegui i test del backend", run_tests),
    ("Controlli del frontend (format, check, lint, test)", run_checks),
    ("Avvio operativo (build, senza migrazioni automatiche)", production_menu),
]


def menu():
    print(f"Heat - sistema rilevato: {SYSTEM} (Python {platform.python_version()})")
    while True:
        print()
        for i, (label, _) in enumerate(MENU, 1):
            print(f"  {i}) {label}")
        print("  0) Esci")
        choice = input("\nScelta: ").strip()
        if choice == "0":
            return
        if choice.isdigit() and 1 <= int(choice) <= len(MENU):
            try:
                MENU[int(choice) - 1][1]()
            except (SystemExit, ValueError) as exc:
                print(exc)
        else:
            print("Scelta non valida")


def main():
    parser = argparse.ArgumentParser(description="Heat: setup e avvio")
    sub = parser.add_subparsers(dest="command")
    p_setup = sub.add_parser("setup")
    p_setup.add_argument("--skip-admin", action="store_true")
    p_setup.add_argument("--skip-seed", action="store_true")
    p_start = sub.add_parser("start")
    p_start.add_argument("--backend-only", action="store_true")
    p_start.add_argument("--public-url")
    p_production = sub.add_parser("production", help="Build e avvio operativo")
    p_production.add_argument("--public-url", help="Origine HTTPS del tunnel")
    sub.add_parser("migrate")
    sub.add_parser("test")
    sub.add_parser("check")
    args = parser.parse_args()
    try:
        if args.command == "setup":
            setup(args.skip_admin, args.skip_seed)
        elif args.command == "start":
            start(args.backend_only, args.public_url)
        elif args.command == "production":
            production(args.public_url)
        elif args.command == "migrate":
            migrate()
        elif args.command == "test":
            run_tests()
        elif args.command == "check":
            run_checks()
        else:
            menu()
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
