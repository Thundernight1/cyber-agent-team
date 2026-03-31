# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false
"""
Core Validator - Evidence Verification System
Enforces the "No-Fake" mandate by cross-referencing Agent Findings with Raw Tool Logs.
"""

from __future__ import annotations

import logging

logger = logging.getLogger("cyber-agent.validator")


class EvidenceValidator:
    """
    Validates that findings are backed by raw evidence.
    """

    @staticmethod
    def _host_has_open_port(host: dict[str, object], target: str, port: int) -> bool:
        """Check a single host entry for the given open port."""
        if host.get("ip") != target:
            return False
        ports = host.get("ports")
        if not isinstance(ports, list):
            return False
        for p in ports:
            if not isinstance(p, dict):
                continue
            p_num = p.get("port")
            p_state = p.get("state", "")
            if int(str(p_num)) == int(port) and "open" in str(p_state):
                return True
        return False

    @staticmethod
    def _check_nmap_hosts(output: dict[str, object], target: str, port: int) -> bool:
        """Check Nmap XML parsed structure for open port."""
        hosts = output.get("hosts")
        if not isinstance(hosts, list):
            return False
        for host in hosts:
            if not isinstance(host, dict):
                continue
            if EvidenceValidator._host_has_open_port(host, target, port):
                return True
        return False

    @staticmethod
    def validate_open_port(target: str, port: int, raw_logs: list[dict[str, object]]) -> bool:
        """
        Verify that a claimed open port exists in Nmap/Masscan logs.
        """
        for log in raw_logs:
            # Check if log is from a network scanner
            if log.get("tool_name") not in ("nmap", "masscan", "network_scanner"):
                continue

            # Check if target matches
            cmd = str(log.get("command", ""))
            parsed = str(log.get("parsed_output", ""))
            if target not in cmd and target not in parsed:
                continue

            # Check parsed output
            output = log.get("parsed_output") or log.get("output")
            if not output:
                continue

            # Nmap XML parsed structure
            if isinstance(output, dict) and EvidenceValidator._check_nmap_hosts(output, target, port):
                return True

            # Raw string check (fallback)
            stdout = log.get("stdout")
            if isinstance(stdout, str) and f"{port}/tcp open" in stdout:
                return True

        return False

    @staticmethod
    def validate_finding(finding: dict[str, object], raw_logs: list[dict[str, object]]) -> bool:
        """
        Generic validation for a finding.
        """
        source_tool = finding.get("source_tool")
        if source_tool:
            has_log = any(log.get("tool_name") == source_tool for log in raw_logs)
            if not has_log:
                logger.warning(f"Finding claims source {source_tool} but no logs found.")
                return False

        return True
