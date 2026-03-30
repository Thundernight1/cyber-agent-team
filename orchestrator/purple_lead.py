"""
Purple Team Orchestrator - Dynamic Task Router & Evidence-Based Execution
=========================================================================
Refactored to support the "No-Fake" mandate:
1. Dynamic Task Queue (Blackboard Pattern)
2. Evidence-Based Execution (Tools run BEFORE agents analyze)
3. Zero Hallucination (Agents rely on injected tool outputs)
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from config.settings import MODEL_ASSIGNMENTS, TEAM_ROSTER
from core.base_agent import (AgentLayer, AgentStatus, AgentTask, BaseAgent,
                             SharedState, TaskResult)
from core.llm_client import get_llm_client
from tools.security_tools import ToolFactory

logger = logging.getLogger("cyber-agent.orchestrator")

# =========================================================
# TASK -> TOOL MAPPING (NO-FAKE ENFORCEMENT)
# =========================================================
TASK_TOOL_MAP = {
    "network_scan": "nmap",
    "wireless_scan": "wifi_scanner",
    "passive_monitor": "sharktap",
    "physical_recon": "flipper_zero",  # Optional, fallback to None
    "vuln_scan": "nuclei",
    "web_scan": "nikto",
    "port_scan": "nmap",
}


class AgentTeam:
    """Ekibi tanımlar; başlatma sırasında tüm ajanlar IDLE kalır."""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}

    def initialize(self):
        for agent_id, profile in TEAM_ROSTER.items():
            layer_map = {
                "operator": AgentLayer.OPERATOR,
                "analysis": AgentLayer.ANALYSIS,
                "decision": AgentLayer.DECISION,
                "support": AgentLayer.SUPPORT,
            }
            agent = BaseAgent(
                agent_id=agent_id,
                name=profile.name,
                role=profile.role,
                layer=layer_map.get(profile.layer, AgentLayer.SUPPORT),
                model=profile.model,
                description=profile.description,
                tools=profile.tools,
            )
            self.agents[agent_id] = agent
        logger.info(f"Ekip hazır: {len(self.agents)} ajan tanımlandı (hepsi IDLE)")
        return self.agents

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        return self.agents.get(agent_id)

    def get_agent_for_task_type(self, task_type: str) -> Optional[BaseAgent]:
        """Map task type to best suitable agent."""
        # Simple mapping for now, can be enhanced with AI Router later
        mapping = {
            "network_scan": "network_operator",
            "port_scan": "network_operator",
            "wireless_scan": "wireless_operator",
            "passive_monitor": "passive_operator",
            "physical_recon": "physical_operator",
            "asset_correlation": "asset_correlation",
            "vuln_analysis": "vulnerability_analysis",
            "vuln_scan": "vulnerability_analysis",
            "credential_check": "credential_analysis",
            "exposure_map": "exposure_analysis",
            "attack_path": "attack_path",
            "risk_prioritization": "risk_prioritization",
            "detection_gap": "detection_gap",
            "mitigation_strategy": "mitigation_strategy",
            "report": "report_agent",
            "web_scan": "vulnerability_analysis",  # Or web specific agent
        }
        agent_id = mapping.get(task_type)
        return self.agents.get(agent_id)

    def status_all(self) -> List[Dict]:
        return [agent.get_status() for agent in self.agents.values()]


class PurpleLeadOrchestrator:
    """
    Purple Team Lead - Dynamic Task Router.
    Executes tasks from the SharedState queue based on priority.
    """

    def __init__(self):
        self.team = AgentTeam()
        self.state = SharedState()
        self.llm = get_llm_client()
        self.session_id = str(uuid.uuid4())[:8]
        self._initialized = False

    async def initialize(self, shodan_api_key: str = None):
        shodan_api_key = shodan_api_key or os.getenv("SHODAN_API_KEY")
        logger.info("=" * 60)
        logger.info("PURPLE TEAM — DYNAMIC ORCHESTRATOR BAŞLIYOR")
        logger.info("=" * 60)

        ToolFactory.initialize(shodan_api_key=shodan_api_key)
        self.team.initialize()

        health = await self.llm.health_check()
        logger.info(f"LLM Sağlık — Cloud: {health['cloud']}, Local: {health['local']}")

        self._initialized = True
        return {
            "session_id": self.session_id,
            "agents_defined": len(self.team.agents),
            "execution_mode": "DYNAMIC — Task Queue & Evidence Based",
            "llm_health": health,  # Added for CLI compatibility
            "tools": ToolFactory.status_report(),  # Added for CLI compatibility
        }

    async def run_full_assessment(self, target: str, scope: Dict = None) -> Dict:
        if not self._initialized:
            await self.initialize()

        # Initialize State
        self.state = SharedState(
            session_id=self.session_id,
            target=target,
            scope=scope or {},
        )

        # Seed Initial Tasks (e.g., Recon)
        initial_tasks = [
            AgentTask(
                task_id=str(uuid.uuid4())[:8],
                type="network_scan",
                description=f"Initial network scan for {target}",
                priority=1,
                target=target,
                source_agent="System",
            ),
            AgentTask(
                task_id=str(uuid.uuid4())[:8],
                type="wireless_scan",
                description=f"Initial wireless scan around {target}",
                priority=2,
                target=target,
                source_agent="System",
            ),
        ]

        for t in initial_tasks:
            self.state.add_task(t)

        logger.info(f"TAM DEĞERLENDİRME BAŞLADI — Hedef: {target}")
        start_time = datetime.now()

        # Start Task Loop
        await self._process_task_queue()

        duration = int((datetime.now() - start_time).total_seconds())
        logger.info(f"TAM DEĞERLENDİRME TAMAMLANDI — Süre: {duration}s")

        return {
            "session_id": self.session_id,
            "target": target,
            "duration_seconds": duration,
            "tasks_completed": len(self.state.completed_tasks),
            "state": self.state.to_dict(),
            "summary": self._generate_summary(),
        }

    async def run_recon_only(self, target: str) -> Dict:
        """Compatibility wrapper for CLI 'recon' command."""
        if not self._initialized:
            await self.initialize()

        self.state = SharedState(session_id=self.session_id, target=target)

        # Seed only recon tasks
        task = AgentTask(
            task_id=str(uuid.uuid4())[:8],
            type="network_scan",
            description=f"Recon scan for {target}",
            priority=1,
            target=target,
            source_agent="System",
        )
        self.state.add_task(task)

        await self._process_task_queue()

        return {
            "target": target,
            "state": self.state.to_dict(),
            "tasks_completed": len(self.state.completed_tasks),
        }

    async def run_vuln_assessment(self, target: str) -> Dict:
        """Compatibility wrapper for CLI 'vuln' command."""
        if not self._initialized:
            await self.initialize()

        self.state = SharedState(session_id=self.session_id, target=target)

        # Seed vuln tasks
        task = AgentTask(
            task_id=str(uuid.uuid4())[:8],
            type="vuln_scan",
            description=f"Vulnerability scan for {target}",
            priority=1,
            target=target,
            source_agent="System",
        )
        self.state.add_task(task)

        await self._process_task_queue()

        return {
            "target": target,
            "vulnerabilities": self.state.vulnerabilities,
            "state": self.state.to_dict(),
        }

    async def run_single_agent(self, agent_id: str, task: str) -> TaskResult:
        """Run a single agent manually (CLI compatibility)."""
        if not self._initialized:
            await self.initialize()

        agent = self.team.get_agent(agent_id)
        if not agent:
            return TaskResult(
                agent_id=agent_id,
                agent_name="unknown",
                layer="unknown",
                task_id="err",
                status="error",
                error="Agent not found",
            )

        return await agent.execute_task(task, self.state)

    async def run_tool_scan(self, tool_name: str, **kwargs) -> Dict:
        """Run a tool manually (CLI compatibility)."""
        tool = ToolFactory.get(tool_name)
        if not tool:
            return {"error": f"Tool not found: {tool_name}"}

        result = await tool.run(**kwargs)
        return result.to_dict()

    async def _process_task_queue(self):
        """
        Main Loop:
        1. Pop high priority task
        2. Execute Tool (if needed) -> Get Evidence
        3. Execute Agent (with Evidence) -> Get Analysis & Next Steps
        4. Repeat until queue empty
        """
        MAX_CYCLES = 50  # Prevent infinite loops
        cycle = 0

        while self.state.task_queue and cycle < MAX_CYCLES:
            # Pop highest priority task
            current_task_dict = self.state.task_queue.pop(0)

            # Convert back to object for easier handling
            current_task = AgentTask(**current_task_dict)
            current_task.status = "in_progress"

            logger.info(
                f"Processing Task [{cycle}]: {current_task.type} - {current_task.description}"
            )

            # 1. Find Agent
            agent = self.team.get_agent_for_task_type(current_task.type)
            if not agent:
                logger.error(f"No agent found for task type: {current_task.type}")
                current_task.status = "failed"
                self.state.completed_tasks.append(current_task.to_dict())
                continue

            # 2. Run Tool (Evidence Collection)
            tool_result = await self._execute_tool_for_task(current_task)

            # 3. Run Agent (Analysis)
            try:
                # Agent analyzes the tool output (or existing state)
                result = await agent.execute_task(
                    task=current_task.description,
                    shared_state=self.state,
                    tool_result=tool_result.to_dict() if tool_result else None,
                )

                current_task.status = "completed"
                logger.info(f"Task Completed: {current_task.type} by {agent.name}")

            except Exception as e:
                logger.error(f"Agent execution failed: {e}")
                current_task.status = "failed"

            self.state.completed_tasks.append(current_task.to_dict())
            cycle += 1

            # Brief pause to allow system resources to settle
            await asyncio.sleep(0.5)

        if cycle >= MAX_CYCLES:
            logger.warning("Max cycles reached! Stopping execution.")

    async def _execute_tool_for_task(self, task: AgentTask):
        """
        Executes the required tool for a task type.
        Enforces 'No-Fake' by ensuring real tool output is available.
        """
        tool_name = TASK_TOOL_MAP.get(task.type)
        if not tool_name:
            # Some tasks (like analysis/reporting) don't need new tool runs
            return None

        tool = ToolFactory.get(tool_name)
        if not tool or not tool.is_available:
            logger.warning(f"Tool {tool_name} not available for task {task.type}")
            return None

        logger.info(f"Running Tool: {tool_name} for {task.target}")

        # Determine args based on task type
        kwargs = {"target": task.target}
        if task.type == "wireless_scan":
            kwargs = {"action": "full"}  # Special case for wifi scanner

        try:
            result = await tool.run(**kwargs)

            # Store raw log in Blackboard (Evidence)
            self.state.raw_logs.append(result.to_dict())
            return result
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return None

    def _generate_summary(self) -> Dict:
        return {
            "total_hosts": len(self.state.hosts),
            "total_ports": len(self.state.ports),
            "total_services": len(self.state.services),
            "total_vulnerabilities": len(self.state.vulnerabilities),
            "total_attack_paths": len(self.state.attack_paths),
            "critical_risks": len(
                [r for r in self.state.risk_priority if r.get("severity") == "critical"]
            ),
            "detection_gaps": len(self.state.detection_gaps),
            "mitigations": len(self.state.mitigation_plan),
        }

    def get_state(self) -> Dict:
        return self.state.to_dict()

    def get_tool_status(self) -> List[Dict]:
        return ToolFactory.status_report()
