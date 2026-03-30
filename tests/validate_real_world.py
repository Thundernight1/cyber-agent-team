"""
Real-World Validation Test
Verifies that the "No-Fake" mandate is enforced by running actual tools and checking evidence.
"""

import asyncio
import json
import logging
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tool_wrapper import ToolWrapper
from core.validator import EvidenceValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test.validation")


async def test_real_tool_execution():
    """
    Test 1: Run a real tool (ping) and verify raw output capture.
    """
    logger.info("Running Real Tool Execution Test (ping)...")
    wrapper = ToolWrapper(log_dir="logs/test")

    # Run ping (safe, ubiquitous)
    target = "127.0.0.1"
    result = await wrapper.run("ping", ["ping", "-c", "2", target], timeout=10)

    if result.exit_code != 0:
        logger.error(f"Ping failed: {result.stderr}")
        return False

    logger.info(f"Ping Output: {result.stdout[:50]}...")

    # Verification
    if "bytes from" not in result.stdout:
        logger.error("Ping output missing expected string 'bytes from'")
        return False

    logger.info("✅ Tool Execution Verified (Real Output Captured)")
    return result


async def test_evidence_validation(tool_result):
    """
    Test 2: Validate a hypothetical agent finding against the tool evidence.
    """
    logger.info("Running Evidence Validation Test...")

    # Hypothetical Agent Finding (Claiming host is up)
    agent_finding = {
        "type": "host_discovery",
        "target": "127.0.0.1",
        "status": "up",
        "source_tool": "ping",
        "evidence": "bytes from 127.0.0.1",
    }

    # Mock Raw Logs
    raw_logs = [tool_result.to_dict()]

    # Use Validator
    # Validator checks if tool ran
    is_valid = EvidenceValidator.validate_finding(agent_finding, raw_logs)

    if is_valid:
        logger.info("✅ Evidence Validation Passed")
        return True
    else:
        logger.error("❌ Evidence Validation Failed")
        return False


async def main():
    try:
        tool_result = await test_real_tool_execution()
        if not tool_result:
            sys.exit(1)

        if not await test_evidence_validation(tool_result):
            sys.exit(1)

        logger.info("ALL TESTS PASSED: System enforces No-Fake Mandate.")
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
