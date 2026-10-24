"""Integrazione launcher LAN con processi, build e DB simulati."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from tools.production import normalize_origin, production_origin, runtime_environment, start_production


class ProductionLanTests(unittest.TestCase):
    def test_normalization(self):
        self.assertEqual(normalize_origin(), "http://127.0.0.1:5173")
        self.assertEqual(normalize_origin("https://Heat.loca.lt:443/"), "https://heat.loca.lt")
        for ip in ("10.1.2.3", "172.16.0.1", "192.168.1.50"):
            self.assertEqual(normalize_origin(f"http://{ip}:5173/"), f"http://{ip}:5173")
        for value in ("http://8.8.8.8:5173", "http://192.168.1.2:80", "http://192.168.1.2:5173/x",
                      "http://169.254.1.2:5173", "http://0.0.0.0:5173", "http://192.168.01.2:5173",
                      "https://x?y=1", "https://u:p@x", "https://x#", "https://a..b"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_origin(value)

    @patch("tools.production.select_lan_ip", return_value="192.168.1.50")
    def test_automatic_lan(self, select):
        self.assertEqual(production_origin(), ("http://192.168.1.50:5173", "192.168.1.50"))
        select.assert_called_once()

    @patch("tools.production.require_local_ip", return_value="10.0.0.2")
    def test_explicit_lan(self, require):
        self.assertEqual(production_origin("http://10.0.0.2:5173"), ("http://10.0.0.2:5173", "10.0.0.2"))
        require.assert_called_once_with("10.0.0.2")

    def test_explicit_loopback_and_https(self):
        for value in ("https://heat.loca.lt", "http://127.0.0.1:5173", "http://localhost:5173"):
            self.assertEqual(production_origin(value), (value, "127.0.0.1"))

    def test_environment(self):
        with patch.dict(os.environ, {"HOST_HEADER": "evil"}):
            env = runtime_environment("http://192.168.1.50:5173")
            self.assertEqual(env["HEAT_SESSION_COOKIE_SECURE"], "0")
            self.assertEqual(env["ORIGIN"], "http://192.168.1.50:5173")
            self.assertNotIn("HOST_HEADER", env)
            self.assertEqual(os.environ["HOST_HEADER"], "evil")
            self.assertTrue(env["HEAT_READY_TOKEN"])
        self.assertEqual(runtime_environment("https://heat.loca.lt")["HEAT_SESSION_COOKIE_SECURE"], "1")

    def exercise_start(self, readiness_error=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for path in ("backend/.venv/python", "backend/heat.db",
                         "frontend/node_modules/@sveltejs/adapter-node/package.json", "frontend/build/handler.js"):
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.touch()
            children = [Mock(), Mock()]
            for child in children:
                child.poll.return_value = None
            run, stop, info = Mock(), Mock(), Mock()
            spawn = Mock(side_effect=children)
            with patch("tools.production.shutil.which", side_effect=lambda name: name), \
                 patch("tools.production.production_origin", return_value=("http://192.168.1.50:5173", "192.168.1.50")), \
                 patch("tools.production.require_free_ports") as ports, \
                 patch("tools.production.wait_ready") as ready, \
                 patch("tools.production.time.sleep", side_effect=KeyboardInterrupt):
                if readiness_error:
                    ready.side_effect = [None, RuntimeError("not ready")]
                    with self.assertRaises(RuntimeError):
                        start_production(root, root / "backend/.venv/python", None, info, run, spawn, stop)
                else:
                    start_production(root, root / "backend/.venv/python", None, info, run, spawn, stop)
                ports.assert_called_once_with("192.168.1.50")
                self.assertEqual(ready.call_args_list[1].args[1], "http://192.168.1.50:5173/__heat_ready")
                backend_args = spawn.call_args_list[0].args[0]
                self.assertEqual(backend_args[backend_args.index("--host") + 1], "127.0.0.1")
                self.assertEqual(backend_args[backend_args.index("--workers") + 1], "1")
                self.assertEqual([call.args[0] for call in stop.call_args_list], list(reversed(children)))
                self.assertEqual(run.call_count, 2)
                self.assertIn("mode=ro", run.call_args_list[0].args[0][2])
                self.assertEqual(run.call_args_list[1].args[0], ["npm", "run", "build"])

    def test_start_and_shutdown(self):
        self.exercise_start()

    def test_readiness_failure_stops_both(self):
        self.exercise_start(readiness_error=True)


if __name__ == "__main__":
    unittest.main()
