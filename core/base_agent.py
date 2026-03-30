"""
Cyber Agent Team - Base Agent & Shared State
=============================================
Complete data model for the 3-layer agent architecture:
  Operator → Analysis → Decision

Rebuilt to match the PurpleLeadOrchestrator contract after
A2A kit corruption replaced this file with a skeletal ABC stub.
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger("cyber-agent.base")


# ─── Enums ────────────────────────────────────────────────────────────────────


class AgentLayer(Enum):
    OPERATOR = "operator"
    ANALYSIS = "analysis"
    DECISION = "decision"
    SUPPORT = "support"


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING = "waiting"


# ─── Data Containers ──────────────────────────────────────────────────────────


@dataclass
class AgentTask:
    """A single unit of work queued on the SharedState blackboard."""

    task_id: str
    type: str
    description: str
    priority: int = 1
    target: str = ""
    source_agent: str = "System"
    status: str = "pending"
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "type": self.type,
            "description": self.description,
            "priority": self.priority,
            "target": self.target,
            "source_agent": self.source_agent,
            "status": self.status,
            "created_at": self.created_at,
        }


@dataclass
class TaskResult:
    """Result returned by an agent after executing a task."""

    agent_id: str
    agent_name: str
    layer: str
    task_id: str
    status: str = "completed"  # completed | failed | skipped
    output: str = ""
    findings: list[Any] = field(default_factory=list)
    next_tasks: list[Any] = field(default_factory=list)
    error: str = ""
    duration_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "layer": self.layer,
            "task_id": self.task_id,
            "status": self.status,
            "output": self.output,
            "findings": self.findings,
            "next_tasks": self.next_tasks,
            "error": self.error,
            "duration_ms": self.duration_ms,
        }


@dataclass
class SharedState:
    """
    Blackboard pattern — the single shared context that all agents read/write.
    Tasks flow through task_queue → completed_tasks.
    Evidence accumulates in raw_logs.
    """

    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    target: str = ""
    scope: dict[str, Any] = field(default_factory=dict)

    # Task queue (priority-ordered list of AgentTask dicts)
    task_queue: list[dict[str, Any]] = field(default_factory=list)
    completed_tasks: list[dict[str, Any]] = field(default_factory=list)

    # Evidence / findings accumulated across agents
    raw_logs: list[Any] = field(default_factory=list)
    hosts: list[Any] = field(default_factory=list)
    ports: list[Any] = field(default_factory=list)
    services: list[Any] = field(default_factory=list)
    vulnerabilities: list[Any] = field(default_factory=list)
    attack_paths: list[Any] = field(default_factory=list)
    risk_priority: list[Any] = field(default_factory=list)
    detection_gaps: list[Any] = field(default_factory=list)
    mitigation_plan: list[Any] = field(default_factory=list)

    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def add_task(self, task: AgentTask):
        """Insert task into queue sorted by priority (lowest int = highest priority)."""
        self.task_queue.append(task.to_dict())
        self.task_queue.sort(key=lambda t: t.get("priority", 99))

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "target": self.target,
            "scope": self.scope,
            "task_queue": self.task_queue,
            "completed_tasks": self.completed_tasks,
            "raw_logs_count": len(self.raw_logs),
            "hosts": self.hosts,
            "ports": self.ports,
            "services": self.services,
            "vulnerabilities": self.vulnerabilities,
            "attack_paths": self.attack_paths,
            "risk_priority": self.risk_priority,
            "detection_gaps": self.detection_gaps,
            "mitigation_plan": self.mitigation_plan,
            "created_at": self.created_at,
        }


# ─── Base Agent ───────────────────────────────────────────────────────────────


class BaseAgent:
    """
    Concrete (non-abstract) agent that can be instantiated directly by the
    orchestrator, or subclassed by operator-specific implementations.

    The orchestrator creates agents from TEAM_ROSTER profiles:
        BaseAgent(agent_id=..., name=..., role=..., layer=AgentLayer.X,
                  model=..., description=..., tools=[...])
    """

    def __init__(
        self,
        name: str,
        agent_id: str = "",
        role: str = "",
        layer: AgentLayer = AgentLayer.SUPPORT,
        model: str = "",
        description: str = "",
        tools: list[str] | None = None,
        config: dict[str, Any] | None = None,
        **kwargs,  # absorb any extra keyword args from subclasses
    ):
        self.agent_id = agent_id or str(uuid.uuid4())[:8]
        self.name = name
        self.role = role
        self.layer = layer
        self.model = model
        self.description = description
        self.tools = tools or []
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self._task_count = 0

        self.logger = logging.getLogger(f"cyber-agent.{self.name.lower()}")

    # ── Public API ────────────────────────────────────────────────────────────

    async def execute_task(
        self,
        task: str,
        shared_state: SharedState | None = None,
        tool_result: dict[str, Any] | None = None,
    ) -> TaskResult:
        """
        Execute a task. Subclasses override this for specialised behaviour.
        Default: log the task + tool evidence, return a structured result.
        """
        self.status = AgentStatus.RUNNING
        self._task_count += 1
        task_id = str(uuid.uuid4())[:8]
        start = asyncio.get_event_loop().time()

        self.logger.info(f"[{self.name}] TASK({task_id}): {task[:80]}")

        try:
            output = await self._process(task, shared_state, tool_result)
            duration_ms = int((asyncio.get_event_loop().time() - start) * 1000)
            self.status = AgentStatus.COMPLETED
            return TaskResult(
                agent_id=self.agent_id,
                agent_name=self.name,
                layer=self.layer.value,
                task_id=task_id,
                status="completed",
                output=output,
                duration_ms=duration_ms,
            )
        except Exception as exc:
            self.status = AgentStatus.FAILED
            self.logger.error(f"[{self.name}] FAILED: {exc}")
            return TaskResult(
                agent_id=self.agent_id,
                agent_name=self.name,
                layer=self.layer.value,
                task_id=task_id,
                status="failed",
                error=str(exc),
            )

    def get_status(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "layer": self.layer.value,
            "model": self.model,
            "status": self.status.value,
            "task_count": self._task_count,
            "tools": self.tools,
        }

    # ── For subclass compatibility (legacy sync interface) ────────────────────

    def execute(self, task: str) -> dict[str, Any]:
        """Synchronous execute — kept for backwards compat with operator subclasses."""
        return {"status": "ok", "agent": self.name, "task": task}

    # ── Internal ──────────────────────────────────────────────────────────────

    async def _process(
        self,
        task: str,
        shared_state: SharedState | None,
        tool_result: dict[str, Any] | None,
    ) -> str:
        """
        Default processing logic.
        Subclasses override this to plug in LLM calls or tool-specific logic.
        """
        _ = shared_state
        _ = task
        evidence_summary = ""
        if tool_result:
            tool_name = tool_result.get("tool_name", "tool")
            exit_code = tool_result.get("exit_code", "?")
            stdout_snip = str(tool_result.get("stdout", ""))[:200]
            evidence_summary = (
                f"\n[Evidence from {tool_name}] exit={exit_code}\n{stdout_snip}"
            )

        self.logger.info(
            f"[{self.name}] Processing: {task[:60]}"
            + (" | tool evidence available" if tool_result else " | no tool evidence")
        )

        return (
            f"Agent {self.name} ({self.role}) processed task: '{task}'"
            + evidence_summary
        )
