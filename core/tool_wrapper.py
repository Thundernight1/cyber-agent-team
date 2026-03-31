"""
Tool Wrapper - Subprocess Execution Handler
Enforces the "No-Fake" mandate by ensuring all agent findings are backed by real tool execution logs.
"""
from __future__ import annotations

import asyncio
import json
import logging
import shutil
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger("cyber-agent.tool_wrapper")


@dataclass
class ToolResult:
    """Standardized output for all tool executions."""

    tool_name: str
    command: str
    exit_code: int
    stdout: str
    stderr: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_ms: int = 0
    parsed_output: dict[str, object] | list[object] | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "tool_name": self.tool_name,
            "command": self.command,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "timestamp": self.timestamp,
            "duration_ms": self.duration_ms,
            "parsed_output": self.parsed_output,
            "error": self.error,
        }


class ToolWrapper:
    """
    Executes system commands and captures output.
    Ensures no simulation/hallucination by running actual binaries.
    """

    def __init__(self, log_dir: str = "logs/tools"):
        self.log_dir = log_dir
        import os

        os.makedirs(log_dir, exist_ok=True)

    async def run(
        self,
        tool_name: str,
        command: list[str],
        timeout: int = 300,
        parse_json: bool = False,
        env: dict[str, str] | None = None,
    ) -> ToolResult:
        """
        Run a command and return the result.

        Args:
            tool_name: Name of the tool (e.g., "nmap")
            command: List of command arguments (e.g., ["nmap", "-sS", "target"])
            timeout: Execution timeout in seconds
            parse_json: Attempt to parse stdout as JSON
            env: Environment variables override
        """
        start_time = datetime.now()
        cmd_str = " ".join(command)
        logger.info(f"Executing tool: {tool_name} -> {cmd_str}")

        # Check if binary exists
        binary = command[0]
        if not shutil.which(binary):
            return ToolResult(
                tool_name=tool_name,
                command=cmd_str,
                exit_code=127,
                stdout="",
                stderr=f"Binary not found: {binary}",
                error=f"Tool binary '{binary}' is missing from system path.",
            )

        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )

            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(process.communicate(), timeout=timeout)
            except asyncio.TimeoutError:
                process.kill()
                return ToolResult(
                    tool_name=tool_name,
                    command=cmd_str,
                    exit_code=124,  # Timeout
                    stdout="",
                    stderr="Execution timed out",
                    error=f"Tool execution timed out after {timeout}s",
                )

            stdout = stdout_bytes.decode("utf-8", errors="replace")
            stderr = stderr_bytes.decode("utf-8", errors="replace")
            exit_code = process.returncode
            duration = int((datetime.now() - start_time).total_seconds() * 1000)

            parsed = None
            if parse_json and stdout.strip():
                try:
                    parsed = json.loads(stdout)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse JSON output for {tool_name}")

            # Log to file
            self._write_log(tool_name, cmd_str, stdout, stderr)

            return ToolResult(
                tool_name=tool_name,
                command=cmd_str,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                duration_ms=duration,
                parsed_output=parsed,
            )

        except Exception as e:
            return ToolResult(
                tool_name=tool_name,
                command=cmd_str,
                exit_code=1,
                stdout="",
                stderr=str(e),
                error=f"Exception during execution: {str(e)}",
            )

    def _write_log(self, tool: str, cmd: str, out: str, err: str):
        """Write execution log to disk."""
        import os

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.log_dir, f"{tool}_{timestamp}.log")

        with open(filename, "w") as f:
            f.write(f"COMMAND: {cmd}\n")
            f.write(f"TIMESTAMP: {datetime.now().isoformat()}\n")
            f.write("-" * 40 + "\n")
            f.write("STDOUT:\n")
            f.write(out)
            f.write("\n" + "-" * 40 + "\n")
            f.write("STDERR:\n")
            f.write(err)
