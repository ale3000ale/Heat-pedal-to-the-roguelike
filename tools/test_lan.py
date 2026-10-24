"""Test LAN isolati: nessuna rete reale e nessun database."""
import socket
import unittest
from unittest.mock import MagicMock, patch
from tools.lan import detect_lan_ips, require_local_ip, select_lan_ip, validate_lan_ip


class LanTests(unittest.TestCase):
    def test_private_ranges(self):
        for value in ("10.0.0.1", "172.16.0.1", "172.31.255.254", "192.168.1.50"):
            with self.subTest(value=value):
                self.assertEqual(validate_lan_ip(value), value)

    def test_reject_other_addresses(self):
        for value in ("127.0.0.1", "0.0.0.0", "8.8.8.8", "169.254.1.2",
                      "172.15.0.1", "172.32.0.1", "localhost", "::1",
                      "192.168.001.2", "192.168.1.2:5173", "192.168.1.2/24", ""):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_lan_ip(value)

    @patch("tools.lan.socket.getaddrinfo")
    def test_detection_filters_sorts_and_deduplicates(self, resolve):
        resolve.return_value = [(socket.AF_INET, 1, 6, "", (ip, 0)) for ip in
                                ("192.168.1.10", "127.0.0.1", "192.168.1.2", "192.168.1.10")]
        self.assertEqual(detect_lan_ips(), ["192.168.1.2", "192.168.1.10"])

    @patch("tools.lan.socket.getaddrinfo", side_effect=OSError("unavailable"))
    def test_detection_failure(self, resolve):
        self.assertEqual(detect_lan_ips(), [])

    @patch("tools.lan.socket.socket")
    def test_local_bind(self, factory):
        self.assertEqual(require_local_ip("192.168.1.2"), "192.168.1.2")
        factory.return_value.__enter__.return_value.bind.assert_called_once_with(("192.168.1.2", 0))

    @patch("tools.lan.socket.socket")
    def test_nonlocal_rejected(self, factory):
        factory.return_value.__enter__.return_value.bind.side_effect = OSError("not assigned")
        with self.assertRaises(ValueError):
            require_local_ip("192.168.1.2")

    @patch("tools.lan.require_local_ip", side_effect=lambda value: value)
    @patch("tools.lan.detect_lan_ips")
    def test_selection(self, detect, require):
        prompt, report = MagicMock(), MagicMock()
        self.assertEqual(select_lan_ip("10.0.0.2", prompt, report), "10.0.0.2")
        detect.assert_not_called()
        detect.return_value = ["192.168.1.2"]
        self.assertEqual(select_lan_ip(prompt=prompt), "192.168.1.2")
        prompt.assert_not_called()
        detect.return_value = ["192.168.1.2", "10.0.0.2"]
        prompt.return_value = "2"
        self.assertEqual(select_lan_ip(prompt=prompt, report=report), "10.0.0.2")
        detect.return_value = []
        prompt.return_value = "192.168.1.3"
        self.assertEqual(select_lan_ip(prompt=prompt, report=report), "192.168.1.3")


if __name__ == "__main__":
    unittest.main()
