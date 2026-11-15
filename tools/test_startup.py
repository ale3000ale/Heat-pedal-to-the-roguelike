"""Test di avvio reali di heat.py: setup, migrazioni, test, dev e produzione.

Ogni fase deve uscire con 0 o restare pronta sulle porte attese, e il log non
deve contenere Traceback. Lenti e modificano node_modules/build: si lanciano solo con
HEAT_STARTUP_TESTS=1 e con nessun server Heat acceso su 8000/5173.
  set HEAT_STARTUP_TESTS=1 && python -m unittest tools.test_startup -v
"""
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENABLED = os.environ.get("HEAT_STARTUP_TESTS") == "1"
WINDOWS = os.name == "nt"
SKIP_MSG = "Imposta HEAT_STARTUP_TESTS=1 per i test di avvio reali"


def heat(*args, timeout):
    """Esegue una fase di heat.py e restituisce (codice, output)."""
    with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as log:
        code = subprocess.run(
            [sys.executable, "heat.py", *args], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=timeout
        ).returncode
        log.seek(0)
        return code, log.read()


def spawn(*args):
    """Avvia heat.py in background; l'output va su file per non bloccare la pipe."""
    log = tempfile.TemporaryFile(mode="w+", encoding="utf-8")
    flags = subprocess.CREATE_NEW_PROCESS_GROUP if WINDOWS else 0
    proc = subprocess.Popen(
        [sys.executable, "heat.py", *args], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, creationflags=flags
    )
    return proc, log


def stop(proc, log):
    """Ferma l'intero albero: il launcher venv su Windows ha figli con la stessa riga di comando."""
    if proc.poll() is None:
        if WINDOWS:
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True)
        else:
            proc.kill()
        proc.wait(timeout=30)
    log.close()


def read(log):
    log.seek(0)
    return log.read()


def wait_text(proc, log, text, timeout=180):
    """Attende una riga nel log; se il processo muore prima, fallisce con il log."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        output = read(log)
        if text in output:
            return output
        if proc.poll() is not None:
            raise AssertionError(f"heat.py terminato ({proc.returncode}) prima di '{text}':\n{output}")
        time.sleep(0.5)
    raise AssertionError(f"'{text}' non comparso entro {timeout}s:\n{read(log)}")


def wait_http(url, timeout=120):
    """Restituisce il codice HTTP quando il servizio risponde; errori di rete = non ancora pronto."""
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                return response.status
        except urllib.error.HTTPError as exc:
            return exc.code
        except OSError as exc:
            last = exc
        time.sleep(0.5)
    raise AssertionError(f"{url} non risponde entro {timeout}s: {last}")


def assert_clean(test, code, output, phase):
    test.assertEqual(code, 0, f"fase {phase} fallita:\n{output[-3000:]}")
    test.assertNotIn("Traceback", output, f"fase {phase} con eccezione nel log")


@unittest.skipUnless(ENABLED, SKIP_MSG)
class PhaseTests(unittest.TestCase):
    def test_setup_installs_everything(self):
        code, output = heat("setup", "--skip-seed", "--skip-admin", timeout=1800)
        assert_clean(self, code, output, "setup")
        self.assertIn("Setup completato", output)

    def test_migrations_reach_head(self):
        code, output = heat("migrate", timeout=300)
        assert_clean(self, code, output, "migrate")

    def test_backend_tests_pass(self):
        code, output = heat("test", timeout=900)
        assert_clean(self, code, output, "test")

    def test_frontend_checks_pass(self):
        code, output = heat("check", timeout=900)
        assert_clean(self, code, output, "check")


@unittest.skipUnless(ENABLED, SKIP_MSG)
class StartTests(unittest.TestCase):
    def test_dev_start_serves_backend_and_frontend(self):
        proc, log = spawn("start")
        self.addCleanup(stop, proc, log)
        wait_text(proc, log, "Sviluppo avviato")
        self.assertEqual(wait_http("http://127.0.0.1:8000/health"), 200)
        self.assertEqual(wait_http("http://127.0.0.1:5173/"), 200)
        self.assertNotIn("Traceback", read(log))

    def test_production_start_serves_lan_origin_with_qr(self):
        proc, log = spawn("production")
        self.addCleanup(stop, proc, log)
        output = wait_text(proc, log, "Heat avviato:")
        self.assertIn("QR per aprire Heat", output)
        self.assertNotIn("Traceback", output)
        origin = re.search(r"Heat avviato: (\S+)", output).group(1)
        self.assertEqual(wait_http("http://127.0.0.1:8000/health"), 200)
        self.assertEqual(wait_http(origin + "/"), 200)


if __name__ == "__main__":
    unittest.main()
