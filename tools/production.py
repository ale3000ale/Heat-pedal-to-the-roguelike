"""Avvio operativo locale: processi sorvegliati, nessuna migrazione automatica."""
import json
import os
import re
import secrets
import shutil
import socket
import time
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, build_opener


def normalize_origin(value=None):
    """Restituisce un'origine HTTPS o HTTP loopback:5173; ValueError se non valida.

    value: URL pubblico senza credenziali, query o percorso; None usa loopback.
    Non accetta wildcard, header inoltrati o indirizzi HTTP della rete locale.
    """
    value = value or "http://127.0.0.1:5173"
    if any(c.isspace() for c in value) or any(c in value for c in "\\?#@"):
        raise ValueError("URL pubblico non valido: niente credenziali, query o frammenti")
    parsed = urlsplit(value)
    host = parsed.hostname or ""
    port = parsed.port
    if parsed.path not in ("", "/") or not re.fullmatch(
        r"[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?", host
    ):
        raise ValueError("Specificare solo l'origine, ad esempio https://nome.loca.lt")
    if any(not label or len(label) > 63 or label.startswith("-")
           or label.endswith("-") for label in host.split(".")):
        raise ValueError("Hostname non valido")
    if port is not None and not 1 <= port <= 65535:
        raise ValueError("Porta non valida")
    if parsed.scheme == "http":
        if host not in ("127.0.0.1", "localhost") or port != 5173:
            raise ValueError("HTTP consentito solo su localhost o 127.0.0.1:5173")
    elif parsed.scheme != "https":
        raise ValueError("L'URL pubblico deve usare HTTPS")
    suffix = f":{port}" if port and not (parsed.scheme == "https" and port == 443) else ""
    return f"{parsed.scheme}://{host.lower()}{suffix}"


def runtime_environment(origin):
    """Copia l'ambiente e impone origine e cookie; non modifica os.environ."""
    origin = normalize_origin(origin)
    env = os.environ.copy()
    for key in ("HOST_HEADER", "PROTOCOL_HEADER", "PORT_HEADER", "ADDRESS_HEADER"):
        env.pop(key, None)
    env.update(
        NODE_ENV="production", ORIGIN=origin, HEAT_PUBLIC_URL=origin,
        HEAT_SESSION_COOKIE_SECURE="1" if origin.startswith("https://") else "0",
        HEAT_READY_TOKEN=secrets.token_urlsafe(24),
    )
    return env


def require_free_ports():
    """Controlla le porte loopback 8000/5173; non termina processi esistenti."""
    for port in (8000, 5173):
        with socket.socket() as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError as exc:
                raise ValueError(f"Porta {port} occupata: ferma prima l'altra istanza") from exc


def wait_ready(proc, url, expected, timeout=30):
    """Attende JSON atteso dal figlio; fallisce su uscita o scadenza, senza proxy."""
    opener = build_opener(ProxyHandler({}))
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"Processo terminato con codice {proc.returncode}")
        try:
            with opener.open(url, timeout=1) as response:
                if json.load(response) == expected:
                    return
        except (OSError, ValueError):
            pass
        time.sleep(0.2)
    raise RuntimeError(f"Avvio non confermato entro {timeout} secondi: {url}")


DB_CHECK = '''
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text
from app.config import DATABASE_URL
if DATABASE_URL != "sqlite:///./heat.db":
    raise SystemExit("Configurazione DB diversa da quella verificata: avvio interrotto")
engine = create_engine("sqlite:///file:heat.db?mode=ro&uri=true")
with engine.connect() as connection:
    current = set(connection.execute(text("SELECT version_num FROM alembic_version")).scalars())
expected = set(ScriptDirectory.from_config(Config("alembic.ini")).get_heads())
engine.dispose()
if current != expected:
    raise SystemExit("DB non allineato. Eseguire backup e migrazioni separatamente prima di production")
'''


def start_production(root, python, public_url, info, run, spawn, stop):
    """Costruisce e avvia Node/FastAPI; parametri callback forniti da heat.py.

    root e python sono Path assoluti. Non installa dipendenze o migrazioni.
    Errori di preflight/build propagano prima dell'avvio. Ogni figlio avviato
    viene arrestato in ordine inverso su Ctrl+C, errore o uscita inattesa.
    """
    origin = normalize_origin(public_url)
    env = runtime_environment(origin)
    backend, frontend = root / "backend", root / "frontend"
    node, npm = shutil.which("node"), shutil.which("npm")
    if not python.is_file() or not node or not npm:
        raise ValueError("Servono backend/.venv, Node.js e npm: eseguire prima setup")
    if not (frontend / "node_modules/@sveltejs/adapter-node/package.json").is_file():
        raise ValueError("Dipendenze mancanti: eseguire npm ci dentro frontend")
    if not (backend / "heat.db").is_file():
        raise ValueError("backend/heat.db assente: production non crea database")
    require_free_ports()
    info("Verifico le revisioni DB in sola lettura, senza applicare migrazioni")
    run([python, "-c", DB_CHECK], backend, env=env)
    info("Costruisco il frontend operativo")
    run([npm, "run", "build"], frontend, env=env)
    if not (frontend / "build/handler.js").is_file():
        raise RuntimeError("Build Node mancante: atteso frontend/build/handler.js")
    info("Modalita' operativa non equivale a certificazione di sicurezza: audit residui aperti")
    procs = []
    try:
        procs.append(spawn(
            [python, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1",
             "--port", "8000", "--workers", "1", "--no-proxy-headers"],
            backend, env=env,
        ))
        wait_ready(procs[0], "http://127.0.0.1:8000/health", {"status": "ok"})
        procs.append(spawn([node, "production-server.mjs"], frontend, env=env))
        wait_ready(procs[1], "http://127.0.0.1:5173/__heat_ready",
                   {"token": env["HEAT_READY_TOKEN"]})
        info(f"Operativa su {origin}; ingresso locale 127.0.0.1:5173. Ctrl+C per fermare")
        if origin.startswith("https://"):
            info("Tunnel separato: npx localtunnel --port 5173. L'URL deve coincidere")
        while all(proc.poll() is None for proc in procs):
            time.sleep(0.5)
        raise RuntimeError("Un processo operativo si e' fermato; consultare il log precedente")
    except KeyboardInterrupt:
        info("Arresto operativo in corso")
    finally:
        for proc in reversed(procs):
            stop(proc)
