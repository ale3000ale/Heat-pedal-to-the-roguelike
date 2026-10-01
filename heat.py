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

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
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


def run(cmd, cwd, check=True):
    result = subprocess.run([str(c) for c in cmd], cwd=cwd)
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


def setup(skip_admin=False, skip_seed=False):
    if sys.version_info < MIN_PYTHON:
        fail(f"Serve Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} o superiore")

    if not VENV_PY.exists():
        info("Creo l'ambiente virtuale backend/.venv")
        run([sys.executable, "-m", "venv", VENV], ROOT)
    else:
        info("Ambiente virtuale già presente")

    info("Installo le dipendenze Python")
    run([VENV_PY, "-m", "pip", "install", "--upgrade", "pip"], BACKEND)
    run([VENV_PY, "-m", "pip", "install", "-r", "requirements.txt"], BACKEND)

    info("Applico le migrazioni del database")
    run([VENV_PY, "-m", "alembic", "upgrade", "head"], BACKEND)

    if not skip_seed:
        info("Popolo il prototipo del mazzo")
        run([VENV_PY, "-m", "app.scripts.seed_prototype"], BACKEND)

    if not skip_admin:
        info("Creo l'utente admin")
        run([VENV_PY, "-m", "app.scripts.create_admin"], BACKEND)

    if has_frontend():
        npm = find_npm()
        info("Installo le dipendenze del frontend")
        lock = (FRONTEND / "package-lock.json").exists()
        run([npm, "ci" if lock else "install"], FRONTEND)
    else:
        info("Cartella frontend/ non ancora presente: salto")

    info("Setup completato")


def spawn(cmd, cwd):
    cmd = [str(c) for c in cmd]
    if IS_WIN:
        return subprocess.Popen(
            cmd, cwd=cwd, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
    return subprocess.Popen(cmd, cwd=cwd, start_new_session=True)


def stop(proc):
    if proc.poll() is not None:
        return
    if IS_WIN:
        subprocess.run(
            ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except ProcessLookupError:
            return
    try:
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        if not IS_WIN:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass


def start(backend_only=False):
    if not VENV_PY.exists():
        fail("Ambiente non pronto. Scegli prima 'Setup'")

    procs = []
    try:
        info(f"Avvio il backend su http://{HOST}:{BACKEND_PORT}")
        procs.append(
            spawn(
                [VENV_PY, "-m", "uvicorn", "app.main:app", "--reload",
                 "--host", HOST, "--port", BACKEND_PORT],
                BACKEND,
            )
        )
        if has_frontend() and not backend_only:
            if not (FRONTEND / "node_modules").exists():
                fail("Dipendenze frontend mancanti. Scegli prima 'Setup'")
            info(f"Avvio il frontend su http://{HOST}:{FRONTEND_PORT}")
            procs.append(
                spawn(
                    [find_npm(), "run", "dev", "--", "--host", HOST,
                     "--port", FRONTEND_PORT, "--strictPort"],
                    FRONTEND,
                )
            )
        info("Tutto avviato. Premi Ctrl+C per fermare")
        while all(p.poll() is None for p in procs):
            time.sleep(0.5)
        info("Un processo si è fermato: chiudo tutto")
    except KeyboardInterrupt:
        info("Arresto in corso")
    finally:
        for p in procs:
            stop(p)


def run_tests():
    if not VENV_PY.exists():
        fail("Ambiente non pronto. Scegli prima 'Setup'")
    run([VENV_PY, "-m", "pytest", "-q"], BACKEND, check=False)


MENU = [
    ("Setup (installa tutto)", lambda: setup()),
    ("Avvia backend e frontend", lambda: start()),
    ("Avvia solo il backend", lambda: start(backend_only=True)),
    ("Esegui i test del backend", run_tests),
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
            except SystemExit as exc:
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
    sub.add_parser("test")
    args = parser.parse_args()

    if args.command == "setup":
        setup(args.skip_admin, args.skip_seed)
    elif args.command == "start":
        start(args.backend_only)
    elif args.command == "test":
        run_tests()
    else:
        menu()


if __name__ == "__main__":
    main()