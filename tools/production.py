"""Avvio operativo LAN o loopback, senza installazioni o migrazioni automatiche."""
import json
import os
import re
import secrets
import shutil
import socket
import time
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, build_opener

from tools.lan import require_local_ip, select_lan_ip, validate_lan_ip


def normalize_origin(value=None):
    """Normalizza HTTPS o HTTP locale/IPv4 RFC1918:5173; ValueError se invalido.

    None mantiene il default loopback per i chiamanti esistenti. La scelta
    automatica LAN avviene solo in production_origin, non in questa funzione.
    """
    value = value or "http://127.0.0.1:5173"
    if any(c.isspace() for c in value) or any(c in value for c in "\\?#@"):
        raise ValueError("URL non valido: niente credenziali, query o frammenti")
    parsed = urlsplit(value)
    host = parsed.hostname or ""
    port = parsed.port
    if parsed.path not in ("", "/") or not re.fullmatch(
        r"[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?", host
    ):
        raise ValueError("Specificare solo l'origine, senza percorso")
    if any(not label or len(label) > 63 or label.startswith("-")
           or label.endswith("-") for label in host.split(".")):
        raise ValueError("Hostname non valido")
    if port is not None and not 1 <= port <= 65535:
        raise ValueError("Porta non valida")
    if parsed.scheme == "http":
        if port != 5173:
            raise ValueError("HTTP locale richiede la porta 5173")
        if host not in ("127.0.0.1", "localhost"):
            validate_lan_ip(host)
    elif parsed.scheme != "https":
        raise ValueError("Le origini pubbliche richiedono HTTPS")
    suffix = f":{port}" if port and not (parsed.scheme == "https" and port == 443) else ""
    return f"{parsed.scheme}://{host.lower()}{suffix}"


def production_origin(value=None, report=print):
    """Restituisce (origine, bind IPv4); valida gli IP LAN sul PC.

    value assente seleziona la LAN. HTTP privato esplicito verifica il bind;
    HTTPS e loopback esplicito mantengono il gateway su 127.0.0.1.
    """
    if not value:
        address = select_lan_ip(report=report)
        return f"http://{address}:5173", address
    origin = normalize_origin(value)
    parsed = urlsplit(origin)
    if parsed.scheme == "http" and parsed.hostname not in ("127.0.0.1", "localhost"):
        return origin, require_local_ip(parsed.hostname)
    return origin, "127.0.0.1"


def runtime_environment(origin):
    """Copia ambiente e impone origine/cookie senza modificare os.environ."""
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


def require_free_ports(frontend_host="127.0.0.1"):
    """Verifica le porte sugli indirizzi effettivi; non termina altri processi."""
    for host, port in (("127.0.0.1", 8000), (frontend_host, 5173)):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((host, port))
            except OSError as exc:
                raise ValueError(f"Indirizzo/porta {host}:{port} non disponibile: {exc}") from exc


def wait_ready(proc, url, expected, timeout=30):
    """Attende JSON del figlio senza proxy; fallisce su uscita o scadenza."""
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


DB_CHECK = '\nfrom alembic.config import Config\nfrom alembic.script import ScriptDirectory\nfrom sqlalchemy import create_engine, text\nfrom app.config import DATABASE_URL\nif DATABASE_URL != "sqlite:///./heat.db":\n    raise SystemExit("Configurazione DB diversa da quella verificata: avvio interrotto")\nengine = create_engine("sqlite:///file:heat.db?mode=ro&uri=true")\nwith engine.connect() as connection:\n    current = set(connection.execute(text("SELECT version_num FROM alembic_version")).scalars())\nexpected = set(ScriptDirectory.from_config(Config("alembic.ini")).get_heads())\nengine.dispose()\nif current != expected:\n    raise SystemExit("DB non allineato. Eseguire backup e migrazioni separatamente prima di production")\n'


def start_production(root, python, public_url, info, run, spawn, stop):
    """Build e avvio Node/FastAPI; callback di heat.py e percorsi assoluti.

    Non installa dipendenze o migra il DB. Il backend resta loopback con un
    worker. Ogni figlio viene arrestato su errore, uscita inattesa o Ctrl+C.
    """
    backend, frontend = root / "backend", root / "frontend"
    node, npm = shutil.which("node"), shutil.which("npm")
    if not python.is_file() or not node or not npm:
        raise ValueError("Servono backend/.venv, Node.js e npm: eseguire prima setup")
    if not (frontend / "node_modules/@sveltejs/adapter-node/package.json").is_file():
        raise ValueError("Dipendenze mancanti: eseguire npm ci dentro frontend")
    if not (backend / "heat.db").is_file():
        raise ValueError("backend/heat.db assente: production non crea database")
    origin, frontend_host = production_origin(public_url, report=info)
    env = runtime_environment(origin)
    require_free_ports(frontend_host)
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
        wait_ready(procs[1], f"http://{frontend_host}:5173/__heat_ready",
                   {"token": env["HEAT_READY_TOKEN"]})
        info(f"Heat avviato: {origin} - Ctrl+C per fermare")
        if frontend_host != "127.0.0.1":
            info("Apri lo stesso indirizzo sul PC e sugli altri dispositivi della rete Wi-Fi/LAN.")
            info("Solo rete fidata: HTTP non cifra il traffico. Non aprire porte sul router.")
            info("Se necessario, consenti TCP 5173 nel firewall solo sulla rete privata.")
            info("Il PC deve restare acceso; reti ospiti o isolamento client possono bloccare l'accesso.")
        while all(proc.poll() is None for proc in procs):
            time.sleep(0.5)
        raise RuntimeError("Un processo operativo si e' fermato; consultare il log precedente")
    except KeyboardInterrupt:
        info("Arresto operativo in corso")
    finally:
        for proc in reversed(procs):
            stop(proc)
