#!/usr/bin/env python3
import argparse
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
VENV = BACKEND / ".venv"
IS_WIN = os.name == "nt"
VENV_PY = VENV / ("Scripts/python.exe" if IS_WIN else "bin/python")
HOST = "127.0.0.1"
BACKEND_PORT = 8000
FRONTEND_PORT = 5173
MIN_PYTHON = (3, 11)


def info(msg):
    print(f"\n==> {msg}", flush=True)


def fail(msg):
    print(f"\nERRORE: {msg}", file=sys.stderr)
    sys.exit(1)


def run(cmd, cwd):
    result = subprocess.run([str(c) for c in cmd], cwd=cwd)
    if result.returncode != 0:
        fail(f"Comando fallito: {' '.join(str(c) for c in cmd)}")


def has_frontend():
    return (FRONTEND / "package.json").exists()


def find_npm():
    npm = shutil.which("npm")
    if not npm:
        fail("npm non trovato. Installa Node.js da https://nodejs.org")
    return npm


def setup(args):
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

    if not args.skip_seed:
        info("Popolo il prototipo del mazzo")
        run([VENV_PY, "-m", "app.scripts.seed_prototype"], BACKEND)

    if not args.skip_admin:
        info("Creo l'utente admin")
        run([VENV_PY, "-m", "app.scripts.create_admin"], BACKEND)

    if has_frontend():
        npm = find_npm()
        info("Installo le dipendenze del frontend")
        cmd = "ci" if (FRONTEND / "package-lock.json").exists() else "install"
        run([npm, cmd], FRONTEND)
    else:
        info("Cartella frontend/ non ancora presente: salto")

    info("Setup completato. Avvia con start.bat (Windows) o ./start.sh")


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


def start(args):
    if not VENV_PY.exists():
        fail("Ambiente non pronto. Esegui prima il setup")

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
        if has_frontend() and not args.backend_only:
            if not (FRONTEND / "node_modules").exists():
                fail("Dipendenze frontend mancanti. Esegui prima il setup")
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


def main():
    parser = argparse.ArgumentParser(description="Heat: setup e avvio")
    sub = parser.add_subparsers(dest="command", required=True)
    p_setup = sub.add_parser("setup")
    p_setup.add_argument("--skip-admin", action="store_true")
    p_setup.add_argument("--skip-seed", action="store_true")
    p_setup.set_defaults(func=setup)
    p_start = sub.add_parser("start")
    p_start.add_argument("--backend-only", action="store_true")
    p_start.set_defaults(func=start)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()