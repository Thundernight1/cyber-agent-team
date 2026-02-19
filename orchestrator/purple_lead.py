"""
Purple Team Orchestrator - Team Lead
Coordinates all agents, assigns tasks, and merges results.
Three-layer workflow: Operator → Analysis → Decision
"""
import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from core.base_agent import (
    BaseAgent, AgentLayer, AgentStatus, SharedState, TaskResult
)
from core.llm_client import get_llm_client
from config.settings import TEAM_ROSTER, MODEL_ASSIGNMENTS
from tools.security_tools import ToolFactory

logger = logging.getLogger("cyber-agent.orchestrator")


class AgentTeam:
    """Manages and initializes the agent team."""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}

    def initialize(self):
        """Create all agents from TEAM_ROSTER."""
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
            logger.info(f"Agent created: {profile.name} ({profile.role})")

        return self.agents

    def get_by_layer(self, layer: str) -> List[BaseAgent]:
        target_layer = {
            "operator": AgentLayer.OPERATOR,
            "analysis": AgentLayer.ANALYSIS,
            "decision": AgentLayer.DECISION,
            "support": AgentLayer.SUPPORT,
        }.get(layer)
        return [a for a in self.agents.values() if a.layer == target_layer]

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        return self.agents.get(agent_id)

    def status_all(self) -> List[Dict]:
        return [agent.get_status() for agent in self.agents.values()]


class PurpleLeadOrchestrator:
    """
    Purple Team Lead - main orchestrator.

    Workflow:
    1. Define target and scope
    2. Run Operator agents in parallel (data collection)
    3. Run Analysis agents in parallel (analysis)
    4. Run Decision agents sequentially (decisions)
    5. Merge results and generate report
    """

    def __init__(self):
        self.team = AgentTeam()
        self.state = SharedState()
        self.llm = get_llm_client()
        self.session_id = str(uuid.uuid4())[:8]
        self.workflow_history: List[Dict] = []
        self._initialized = False

    async def initialize(self, shodan_api_key: str = None):
        """Initialize team and tools."""
        shodan_api_key = shodan_api_key or os.getenv("SHODAN_API_KEY")
        logger.info("=" * 60)
        logger.info("PURPLE TEAM ORCHESTRATOR STARTING")
        logger.info("=" * 60)

        # Initialize tools
        ToolFactory.initialize(shodan_api_key=shodan_api_key)

        # Initialize agents
        self.team.initialize()

        # LLM health check
        health = await self.llm.health_check()
        logger.info(f"LLM Health - Cloud: {health['cloud']}, Local: {health['local']}")

        self._initialized = True
        logger.info(f"Session ID: {self.session_id}")
        logger.info(f"Total Agents: {len(self.team.agents)}")
        logger.info("=" * 60)

        return {
            "session_id": self.session_id,
            "agents": len(self.team.agents),
            "tools": ToolFactory.status_report(),
            "llm_health": health,
        }

    # =========================================================
    # FULL PENTEST WORKFLOW
    # =========================================================

    async def run_full_assessment(
        self,
        target: str,
        scope: Dict = None,
        options: Dict = None,
    ) -> Dict:
        """
        Full pentest workflow.

        Args:
            target: Target IP/domain/network
            scope: Scope details {"networks": [...], "domains": [...]}
            options: Extra options
        """
        if not self._initialized:
            await self.initialize()

        self.state = SharedState(
            session_id=self.session_id,
            target=target,
            scope=scope or {},
        )

        logger.info(f"FULL ASSESSMENT STARTED - Target: {target}")
        assessment_start = datetime.now()

        results = {
            "session_id": self.session_id,
            "target": target,
            "started_at": assessment_start.isoformat(),
            "layers": {},
        }

        # LAYER 1: OPERATOR (Parallel data collection)
        logger.info("─── LAYER 1: OPERATOR (Data Collection) ───")
        operator_results = await self._run_operator_layer(target, scope)
        results["layers"]["operator"] = operator_results

        # LAYER 2: ANALYSIS (Parallel analysis)
        logger.info("─── LAYER 2: ANALYSIS (Analysis) ───")
        analysis_results = await self._run_analysis_layer()
        results["layers"]["analysis"] = analysis_results

        # LAYER 3: DECISION (Sequential decision)
        logger.info("─── LAYER 3: DECISION (Decision) ───")
        decision_results = await self._run_decision_layer()
        results["layers"]["decision"] = decision_results

        # Merge results
        duration = int((datetime.now() - assessment_start).total_seconds())
        results["completed_at"] = datetime.now().isoformat()
        results["duration_seconds"] = duration
        results["summary"] = self._generate_summary()

        logger.info(f"FULL ASSESSMENT COMPLETED - Duration: {duration}s")

        return results

    async def _run_operator_layer(self, target: str, scope: Dict) -> List[Dict]:
        """Run operator agents in parallel."""
        operators = self.team.get_by_layer("operator")
        tasks = []

        for agent in operators:
            task_desc = self._operator_task_for(agent.agent_id, target, scope)
            tasks.append(agent.execute_task(task_desc, self.state))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return [
            r.to_dict() if isinstance(r, TaskResult)
            else {"error": str(r)}
            for r in results
        ]

    async def _run_analysis_layer(self) -> List[Dict]:
        """Run analysis agents in parallel."""
        analysts = self.team.get_by_layer("analysis")
        tasks = []

        for agent in analysts:
            task_desc = self._analysis_task_for(agent.agent_id)
            tasks.append(agent.execute_task(task_desc, self.state))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return [
            r.to_dict() if isinstance(r, TaskResult)
            else {"error": str(r)}
            for r in results
        ]

    async def _run_decision_layer(self) -> List[Dict]:
        """Run decision agents sequentially (dependent ordering)."""
        decision_order = [
            "attack_path",
            "risk_prioritization",
            "detection_gap",
            "mitigation_strategy",
            "report_agent",
        ]

        results = []
        for agent_id in decision_order:
            agent = self.team.get_agent(agent_id)
            if agent:
                task_desc = self._decision_task_for(agent_id)
                result = await agent.execute_task(task_desc, self.state)
                results.append(result.to_dict())

        return results

    # =========================================================
    # SINGLE AGENT EXECUTION
    # =========================================================

    async def run_single_agent(
        self, agent_id: str, task: str, context: Dict = None
    ) -> TaskResult:
        """Run a single agent with a specific task."""
        agent = self.team.get_agent(agent_id)
        if not agent:
            return TaskResult(
                agent_id=agent_id,
                agent_name="unknown",
                layer="unknown",
                task_id="err",
                status="error",
                error=f"Agent not found: {agent_id}",
            )

        if context:
            for key, value in context.items():
                if hasattr(self.state, key):
                    setattr(self.state, key, value)

        return await agent.execute_task(task, self.state)

    # =========================================================
    # SPECIALIZED WORKFLOWS
    # =========================================================

    async def run_recon_only(self, target: str) -> Dict:
        """Recon only (Operator layer)."""
        self.state = SharedState(target=target)
        results = await self._run_operator_layer(target, {})
        return {"target": target, "recon_results": results, "state": self.state.get_layer_data("operator")}

    async def run_vuln_assessment(self, target: str) -> Dict:
        """Operator + Analysis (vulnerability assessment)."""
        self.state = SharedState(target=target)
        op_results = await self._run_operator_layer(target, {})
        an_results = await self._run_analysis_layer()
        return {
            "target": target,
            "operator": op_results,
            "analysis": an_results,
            "vulnerabilities": self.state.vulnerabilities,
        }

    async def run_tool_scan(self, tool_name: str, **kwargs) -> Dict:
        """Run a specific tool directly."""
        tool = ToolFactory.get(tool_name)
        if not tool:
            return {"error": f"Tool not found: {tool_name}"}
        if not tool.is_available:
            return {"error": f"Tool not installed: {tool_name}"}

        result = await tool.run(**kwargs)
        return result.to_dict()

    # =========================================================
    # HELPERS
    # =========================================================

    def _operator_task_for(self, agent_id: str, target: str, scope: Dict) -> str:
        tasks = {
            "network_operator": f"Perform network discovery on target {target}. Identify open ports, running services, and OS fingerprints. Return JSON with hosts[], ports[], services[].",
            "wireless_operator": f"Scan wireless networks around target {target}. Identify access points, clients, and encryption types. Return JSON with access_points[], clients[].",
            "passive_operator": f"Monitor passive traffic on target {target}. Identify protocols, auth patterns, and unencrypted comms. Return JSON with protocols[], observations[].",
            "physical_operator": f"Assess physical security observations for target {target}. Note device accessibility, network jacks, signal leakage. Return JSON with observations[].",
        }
        return tasks.get(agent_id, f"Collect data for target {target}.")

    def _analysis_task_for(self, agent_id: str) -> str:
        tasks = {
            "asset_correlation": "Combine network, wireless, and physical data from the Operator layer. Build a unified attack surface and identify overlaps.",
            "vulnerability_analysis": "Analyze detected services and configurations for vulnerabilities. Map CVEs and classify by CVSS score. Return JSON with vulnerabilities[].",
            "credential_analysis": "Analyze authentication mechanisms. Evaluate default creds, weak passwords, and lateral movement potential. Return JSON with credential_risks[].",
            "exposure_analysis": "Prioritize externally reachable services and risks. Return JSON with exposure_map.",
        }
        return tasks.get(agent_id, "Analyze the current data.")

    def _decision_task_for(self, agent_id: str) -> str:
        tasks = {
            "attack_path": "Build realistic attack chains from discovered vulnerabilities. Provide success likelihood and impact for each path. Return JSON with attack_paths[].",
            "risk_prioritization": "Prioritize technical risks by business impact. Classify as Critical/High/Medium/Low. Return JSON with risk_priority[].",
            "detection_gap": "Identify gaps in security controls and logging. Return JSON with detection_gaps[].",
            "mitigation_strategy": "Produce remediation recommendations per finding. Separate short-term and long-term actions. Return JSON with mitigation_plan[].",
            "report_agent": "Combine all layers into a structured pentest report with executive summary, technical findings, risk matrix, and recommendations.",
        }
        return tasks.get(agent_id, "Make decisions based on current findings.")

    def _generate_summary(self) -> Dict:
        return {
            "total_hosts": len(self.state.hosts),
            "total_ports": len(self.state.ports),
            "total_services": len(self.state.services),
            "total_vulnerabilities": len(self.state.vulnerabilities),
            "total_attack_paths": len(self.state.attack_paths),
            "critical_risks": len([
                r for r in self.state.risk_priority
                if r.get("severity") == "critical"
            ]),
            "detection_gaps": len(self.state.detection_gaps),
            "mitigations": len(self.state.mitigation_plan),
        }

    def get_state(self) -> Dict:
        return self.state.to_dict()

    def get_team_status(self) -> List[Dict]:
        return self.team.status_all()

    def get_tool_status(self) -> List[Dict]:
        return ToolFactory.status_report()
