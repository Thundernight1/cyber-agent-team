import io
import logging
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.append(os.getcwd())

from agents.operator.network_operator import NetworkOperator
from agents.operator.passive_operator import PassiveOperator
from agents.operator.wireless_operator import WirelessOperator


class TestOperatorsRefactored(unittest.TestCase):
    def setUp(self):
        # Configure logging to capture output
        self.log_output = io.StringIO()
        self.handler = logging.StreamHandler(self.log_output)
        # Match the logger name in BaseAgent
        self.logger = logging.getLogger("cyber_agent")
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.INFO)

    def tearDown(self):
        self.logger.removeHandler(self.handler)

    def test_network_operator_logging_and_subprocess(self):
        op = NetworkOperator()
        # Mocking the logger inside op specifically if it's not the same instance
        op.logger.addHandler(self.handler)
        op.logger.setLevel(logging.INFO)

        with patch("subprocess.run") as mocked_run:
            mocked_run.return_value = MagicMock(stdout="Nmap scan report", returncode=0)
            op.scan_network("127.0.0.1")

            # Verify logging
            log_contents = self.log_output.getvalue()
            self.assertIn("Starting network scan on 127.0.0.1", log_contents)
            self.assertIn("Network scan completed successfully.", log_contents)

            # Verify subprocess call
            mocked_run.assert_called_once()
            self.assertEqual(mocked_run.call_args[0][0], ["nmap", "-sn", "127.0.0.1"])

    def test_passive_operator_logging_and_timeout(self):
        op = PassiveOperator()
        op.logger.addHandler(self.handler)
        op.logger.setLevel(logging.INFO)

        with patch("subprocess.run") as mocked_run:
            mocked_run.return_value = MagicMock(stdout="Whois data", returncode=0)
            op.run_osint("example.com")

            # Verify logging
            log_contents = self.log_output.getvalue()
            self.assertIn(
                "Starting passive OSINT for domain: example.com", log_contents
            )

            # Verify subprocess call with timeout
            mocked_run.assert_called_once()
            self.assertEqual(mocked_run.call_args[1]["timeout"], 30)

    def test_wireless_operator_parsing(self):
        op = WirelessOperator()
        op.logger.addHandler(self.handler)
        op.logger.setLevel(logging.INFO)

        raw_output = 'Cell 01 - Address: AA:BB:CC:DD:EE:FF\nESSID:"TestWiFi"'
        with patch("subprocess.run") as mocked_run:
            mocked_run.return_value = MagicMock(
                stdout=raw_output, returncode=0, stderr=""
            )
            results = op.scan_wifi("wlan0")

            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["ssid"], "TestWiFi")
            self.assertEqual(results[0]["bssid"], "AA:BB:CC:DD:EE:FF")
            self.assertIn("WiFi scan completed.", self.log_output.getvalue())


if __name__ == "__main__":
    unittest.main()
