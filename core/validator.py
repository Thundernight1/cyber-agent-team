"""
Core Validator - Evidence Verification System
Enforces the "No-Fake" mandate by cross-referencing Agent Findings with Raw Tool Logs.
"""

import logging
from typing import Dict, List

logger = logging.getLogger("cyber-agent.validator")


class EvidenceValidator:
    """
    Validates that findings are backed by raw evidence.
    """

    @staticmethod
    def validate_open_port(target: str, port: int, raw_logs: List[Dict]) -> bool:
        """
        Verify that a claimed open port exists in Nmap/Masscan logs.
        """
        for log in raw_logs:
            # Check if log is from a network scanner
            if log.get("tool_name") not in ["nmap", "masscan", "network_scanner"]:
                continue

            # Check if target matches (simplified)
            # In a real system, we'd need robust IP matching
            cmd = log.get("command", "")
            if target not in cmd and target not in str(log.get("parsed_output")):
                continue

            # Check parsed output
            output = log.get("parsed_output") or log.get("output")
            if not output:
                continue

            # Nmap XML parsed structure
            if isinstance(output, dict) and "hosts" in output:
                for host in output["hosts"]:
                    if host.get("ip") == target:
                        for p in host.get("ports", []):
                            if int(p.get("port")) == int(port) and "open" in p.get(
                                "state", ""
                            ):
                                return True

            # Raw string check (fallback)
            if log.get("stdout") and f"{port}/tcp open" in log["stdout"]:
                return True

        return False

    @staticmethod
    def validate_finding(finding: Dict, raw_logs: List[Dict]) -> bool:
        """
        Generic validation for a finding.
        """
        # If finding has a source tool, check if that tool ran
        source_tool = finding.get("source_tool")
        if source_tool:
            has_log = any(log.get("tool_name") == source_tool for log in raw_logs)
            if not has_log:
                logger.warning(
                    f"Finding claims source {source_tool} but no logs found."
                )
                return False

        return True
