"""Test puri del launcher: non avviano processi e non accedono al DB reale."""
import os
import unittest
from unittest.mock import patch

from tools.production import normalize_origin, runtime_environment, wait_ready


class OriginTests(unittest.TestCase):
    def test_local_default(self):
        self.assertEqual(normalize_origin(), "http://127.0.0.1:5173")

    def test_https_normalization(self):
        self.assertEqual(normalize_origin("https://Heat.loca.lt:443/"), "https://heat.loca.lt")

    def test_reject_untrusted_values(self):
        values = ["http://heat.loca.lt", "https://x/a", "https://x?y=1",
                  "https://u:p@x", "https://*.loca.lt", "https://x#",
                  "https://x\\evil", " https://x", "https://x:0", "https://a..b"]
        for value in values:
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_origin(value)

    def test_environment_isolated_and_secure(self):
        with patch.dict(os.environ, {"HOST_HEADER": "evil"}):
            env = runtime_environment("https://heat.loca.lt")
            self.assertNotIn("HOST_HEADER", env)
            self.assertEqual(os.environ["HOST_HEADER"], "evil")
            self.assertEqual(env["HEAT_SESSION_COOKIE_SECURE"], "1")
            self.assertEqual(env["ORIGIN"], "https://heat.loca.lt")
            self.assertTrue(env["HEAT_READY_TOKEN"])
        self.assertEqual(runtime_environment(None)["HEAT_SESSION_COOKIE_SECURE"], "0")

    def test_exited_process_fails_readiness(self):
        class Exited:
            returncode = 9

            def poll(self):
                return self.returncode

        with self.assertRaises(RuntimeError):
            wait_ready(Exited(), "http://127.0.0.1:1", {})


if __name__ == "__main__":
    unittest.main()
