import pytest
from core.validator import EvidenceValidator

class TestEvidenceValidator:
    """Tests for EvidenceValidator class"""

    def test_validate_open_port_parsed_success(self):
        """Test successful validation using parsed Nmap output"""
        target = "192.168.1.1"
        port = 80
        raw_logs = [
            {
                "tool_name": "nmap",
                "command": f"nmap -p {port} {target}",
                "parsed_output": {
                    "hosts": [
                        {
                            "ip": "192.168.1.1",
                            "ports": [
                                {"port": 80, "state": "open"},
                                {"port": 443, "state": "closed"}
                            ]
                        }
                    ]
                }
            }
        ]
        assert EvidenceValidator.validate_open_port(target, port, raw_logs) is True

    def test_validate_open_port_stdout_success(self):
        """Test successful validation using raw stdout fallback"""
        target = "10.0.0.5"
        port = 22
        raw_logs = [
            {
                "tool_name": "masscan",
                "command": f"masscan -p{port} {target}",
                "stdout": f"Discovered open port {port}/tcp on {target}"
            }
        ]
        assert EvidenceValidator.validate_open_port(target, port, raw_logs) is True

    def test_validate_open_port_wrong_tool(self):
        """Test failure when tool name is not recognized"""
        target = "192.168.1.1"
        port = 80
        raw_logs = [{"tool_name": "unknown_tool", "stdout": "80/tcp open"}]
        assert EvidenceValidator.validate_open_port(target, port, raw_logs) is False

    def test_validate_open_port_wrong_target(self):
        """Test failure when target doesn't match"""
        target = "192.168.1.1"
        port = 80
        raw_logs = [
            {
                "tool_name": "nmap",
                "command": "nmap -p 80 192.168.1.2",
                "parsed_output": {"hosts": [{"ip": "192.168.1.2", "ports": [{"port": 80, "state": "open"}]}]}
            }
        ]
        assert EvidenceValidator.validate_open_port(target, port, raw_logs) is False

    def test_validate_open_port_wrong_port(self):
        """Test failure when port doesn't match"""
        target = "192.168.1.1"
        port = 80
        raw_logs = [
            {
                "tool_name": "nmap",
                "command": f"nmap -p 443 {target}",
                "parsed_output": {"hosts": [{"ip": target, "ports": [{"port": 443, "state": "open"}]}]}
            }
        ]
        assert EvidenceValidator.validate_open_port(target, port, raw_logs) is False

    def test_validate_open_port_not_open(self):
        """Test failure when port state is not 'open'"""
        target = "192.168.1.1"
        port = 80
        raw_logs = [
            {
                "tool_name": "nmap",
                "command": f"nmap -p {port} {target}",
                "parsed_output": {"hosts": [{"ip": target, "ports": [{"port": 80, "state": "closed"}]}]}
            }
        ]
        assert EvidenceValidator.validate_open_port(target, port, raw_logs) is False

    def test_validate_open_port_empty_logs(self):
        """Test handling of empty logs"""
        assert EvidenceValidator.validate_open_port("1.1.1.1", 80, []) is False

    def test_validate_open_port_target_in_parsed_output_only(self):
        """Test success when target is in parsed_output but not in command"""
        target = "192.168.1.1"
        port = 80
        raw_logs = [
            {
                "tool_name": "nmap",
                "command": "nmap -p 80 -iL targets.txt",
                "parsed_output": {
                    "hosts": [
                        {
                            "ip": target,
                            "ports": [{"port": 80, "state": "open"}]
                        }
                    ]
                }
            }
        ]
        assert EvidenceValidator.validate_open_port(target, port, raw_logs) is True

    def test_validate_open_port_target_missing_from_precheck(self):
        """Test failure when target is missing from command and parsed_output (even if in stdout)"""
        target = "192.168.1.1"
        port = 80
        raw_logs = [
            {
                "tool_name": "nmap",
                "command": "nmap -p 80 10.0.0.1",
                "stdout": "192.168.1.1 80/tcp open"
            }
        ]
        # This returns False because target is not in command and parsed_output is None
        assert EvidenceValidator.validate_open_port(target, port, raw_logs) is False

    def test_validate_finding_success(self):
        """Test successful finding validation"""
        finding = {"source_tool": "nmap", "data": "found port 80"}
        raw_logs = [{"tool_name": "nmap", "output": "..."}]
        assert EvidenceValidator.validate_finding(finding, raw_logs) is True

    def test_validate_finding_no_logs(self):
        """Test failure when source tool logs are missing"""
        finding = {"source_tool": "nikto", "data": "vulnerability found"}
        raw_logs = [{"tool_name": "nmap", "output": "..."}]
        assert EvidenceValidator.validate_finding(finding, raw_logs) is False

    def test_validate_finding_no_source(self):
        """Test success when no source tool is specified"""
        finding = {"data": "manual finding"}
        raw_logs = [{"tool_name": "nmap", "output": "..."}]
        assert EvidenceValidator.validate_finding(finding, raw_logs) is True
