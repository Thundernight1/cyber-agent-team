import pytest
from unittest.mock import MagicMock, patch
from agents.operator.wireless_operator import WirelessOperator

class TestWirelessOperator:
    @pytest.fixture
    def operator(self):
        return WirelessOperator(name="TestWirelessOperator")

    @pytest.mark.unit
    def test_scan_wifi_default(self, operator):
        """Test scan_wifi with default parameters"""
        results = operator.scan_wifi()
        assert "networks" in results
        assert isinstance(results["networks"], list)
        assert len(results["networks"]) == 0

    @pytest.mark.unit
    def test_scan_wifi_custom_interface(self, operator):
        """Test scan_wifi with a custom interface"""
        results = operator.scan_wifi(interface="wlan1")
        assert "networks" in results
        assert isinstance(results["networks"], list)

    @pytest.mark.unit
    def test_scan_wifi_exception(self, operator):
        """Test scan_wifi error handling"""
        # Mocking logger.debug because it's inside the try block
        with patch.object(operator.logger, 'debug', side_effect=Exception("Scan failed")):
            results = operator.scan_wifi()
            assert results["status"] == "error"
            assert "Scan failed" in results["message"]
