"""
HITL Middleware - Human-in-the-Loop Intervention System
========================================================
Integrates with PurpleLeadOrchestrator._process_task_queue()
Pattern: Intercept after tool execution, before agent analysis
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from config.settings import TEAM_ROSTER
from core.base_agent import AgentTask, SharedState
from core.hitl_types import (
    ConfidenceScore,
    HITLDecision,
    InterventionRequest,
    InterventionResponse,
    InterventionStatus,
    InterventionType,
    RiskLevel,
    get_pending_interventions,
    queue_intervention,
    submit_response,
)

logger = logging.getLogger("cyber-agent.hitl")


# ============================================================
# RISK POLICY CONFIGURATION (Real task types from your codebase)
# ============================================================

TASK_RISK_POLICIES = {
    # Operator Layer - Low Risk, auto-execute
    "network_scan": {
        "risk_level": RiskLevel.LOW,
        "intervention_type": InterventionType.NONE,
        "confidence_threshold": 0.8,
        "timeout_seconds": 300,
    },
    "port_scan": {
        "risk_level": RiskLevel.LOW,
        "intervention_type": InterventionType.NONE,
        "confidence_threshold": 0.8,
        "timeout_seconds": 300,
    },
    "wireless_scan": {
        "risk_level": RiskLevel.LOW,
        "intervention_type": InterventionType.NONE,
        "confidence_threshold": 0.8,
        "timeout_seconds": 300,
    },
    "passive_monitor": {
        "risk_level": RiskLevel.LOW,
        "intervention_type": InterventionType.NONE,
        "confidence_threshold": 0.8,
        "timeout_seconds": 300,
    },
    "physical_recon": {
        "risk_level": RiskLevel.LOW,
        "intervention_type": InterventionType.NONE,
        "confidence_threshold": 0.8,
        "timeout_seconds": 300,
    },
    
    # Analysis Layer - Medium Risk, async review
    "vuln_scan": {
        "risk_level": RiskLevel.MEDIUM,
        "intervention_type": InterventionType.ASYNC_REVIEW,
        "confidence_threshold": 0.8,
        "timeout_seconds": 600,
    },
    "web_scan": {
        "risk_level": RiskLevel.MEDIUM,
        "intervention_type": InterventionType.ASYNC_REVIEW,
        "confidence_threshold": 0.8,
        "timeout_seconds": 600,
    },
    "vuln_analysis": {
        "risk_level": RiskLevel.MEDIUM,
        "intervention_type": InterventionType.ASYNC_REVIEW,
        "confidence_threshold": 0.8,
        "timeout_seconds": 600,
    },
    "asset_correlation": {
        "risk_level": RiskLevel.MEDIUM,
        "intervention_type": InterventionType.ASYNC_REVIEW,
        "confidence_threshold": 0.8,
        "timeout_seconds": 600,
    },
    "credential_check": {
        "risk_level": RiskLevel.MEDIUM,
        "intervention_type": InterventionType.ASYNC_REVIEW,
        "confidence_threshold": 0.8,
        "timeout_seconds": 600,
    },
    "exposure_map": {
        "risk_level": RiskLevel.MEDIUM,
        "intervention_type": InterventionType.ASYNC_REVIEW,
        "confidence_threshold": 0.8,
        "timeout_seconds": 600,
    },
    
    # Decision Layer - High Risk, blocking approval
    "attack_path": {
        "risk_level": RiskLevel.HIGH,
        "intervention_type": InterventionType.BLOCKING_APPROVAL,
        "confidence_threshold": 0.9,
        "timeout_seconds": 300,
    },
    "risk_prioritization": {
        "risk_level": RiskLevel.MEDIUM,
        "intervention_type": InterventionType.ASYNC_REVIEW,
        "confidence_threshold": 0.8,
        "timeout_seconds": 600,
    },
    "detection_gap": {
        "risk_level": RiskLevel.MEDIUM,
        "intervention_type": InterventionType.ASYNC_REVIEW,
        "confidence_threshold": 0.8,
        "timeout_seconds": 600,
    },
    "mitigation_strategy": {
        "risk_level": RiskLevel.MEDIUM,
        "intervention_type": InterventionType.ASYNC_REVIEW,
        "confidence_threshold": 0.8,
        "timeout_seconds": 600,
    },
    "report": {
        "risk_level": RiskLevel.LOW,
        "intervention_type": InterventionType.NONE,
        "confidence_threshold": 0.8,
        "timeout_seconds": 300,
    },
    
    # Exploitation - Critical Risk, mandatory blocking approval
    "exploitation": {
        "risk_level": RiskLevel.CRITICAL,
        "intervention_type": InterventionType.BLOCKING_APPROVAL,
        "confidence_threshold": 0.95,
        "timeout_seconds": 600,
    },
    "metasploit": {
        "risk_level": RiskLevel.CRITICAL,
        "intervention_type": InterventionType.BLOCKING_APPROVAL,
        "confidence_threshold": 0.95,
        "timeout_seconds": 600,
    },
}


def get_task_policy(task_type: str) -> Dict[str, Any]:
    """Get risk policy for a task type, fallback to safe defaults."""
    return TASK_RISK_POLICIES.get(task_type, {
        "risk_level": RiskLevel.MEDIUM,
        "intervention_type": InterventionType.ASYNC_REVIEW,
        "confidence_threshold": 0.8,
        "timeout_seconds": 600,
    })


# ============================================================
# CONFIDENCE ENGINE (Simple heuristic-based)
# ============================================================

def calculate_confidence(task: AgentTask, shared_state: SharedState) -> ConfidenceScore:
    """
    Calculate confidence score based on task context and historical data.
    Simple heuristic: more evidence = higher confidence.
    """
    factors = []
    score = 0.5  # Base confidence
    
    # Factor 1: Tool evidence available
    if shared_state.raw_logs:
        score += 0.2
        factors.append(f"Has {len(shared_state.raw_logs)} raw logs")
    
    # Factor 2: Previous similar tasks completed
    similar_completed = [
        t for t in shared_state.completed_tasks
        if t.get("type") == task.type and t.get("status") == "completed"
    ]
    if similar_completed:
        score += 0.15
        factors.append(f"{len(similar_completed)} similar tasks completed")
    
    # Factor 3: Target specificity
    if task.target and len(task.target) > 3:
        score += 0.1
        factors.append("Target well-defined")
    
    # Factor 4: Task type familiarity (known = higher confidence)
    if task.type in TASK_RISK_POLICIES:
        score += 0.05
        factors.append("Known task type")
    
    # Clamp to 0.0-1.0
    score = max(0.0, min(1.0, score))
    
    reasoning = f"Confidence {score:.2f} based on: " + "; ".join(factors)
    return ConfidenceScore(score=score, reasoning=reasoning, factors=factors)


# ============================================================
# HITL MIDDLEWARE
# ============================================================

class HITLMiddleware:
    """
    Human-in-the-Loop Middleware.
    Integrates with PurpleLeadOrchestrator._process_task_queue()
    """
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.logger = logging.getLogger("cyber-agent.hitl.middleware")
    
    async def evaluate_task(
        self,
        task: AgentTask,
        shared_state: SharedState,
        tool_result: Optional[Dict[str, Any]] = None,
    ) -> HITLDecision:
        """
        Evaluate if human intervention is required.
        Called after tool execution, before agent analysis.
        """
        if not self.enabled:
            return HITLDecision(
                proceed=True,
                intervention_type=InterventionType.NONE,
                reason="HITL disabled",
            )
        
        # Get policy for this task type
        policy = get_task_policy(task.type)
        risk_level = policy["risk_level"]
        intervention_type = policy["intervention_type"]
        confidence_threshold = policy["confidence_threshold"]
        
        # Calculate confidence
        confidence = calculate_confidence(task, shared_state)
        
        # Determine if intervention needed
        if intervention_type == InterventionType.NONE:
            # Low risk tasks auto-execute if confidence is high enough
            if confidence.is_high_confidence(confidence_threshold):
                return HITLDecision(
                    proceed=True,
                    intervention_type=InterventionType.NONE,
                    reason=f"Auto-execute: {task.type} with confidence {confidence.score:.2f}",
                )
            else:
                # Low confidence on low-risk task -> async review
                intervention_type = InterventionType.ASYNC_REVIEW
        
        # Create intervention request
        request = InterventionRequest(
            request_id=str(uuid.uuid4())[:8],
            task_id=task.task_id,
            task_type=task.type,
            target=task.target,
            risk_level=risk_level,
            confidence=confidence,
            intervention_type=intervention_type,
            status=InterventionStatus.PENDING,
            timeout_seconds=policy["timeout_seconds"],
            context={
                "task_description": task.description,
                "tool_result": tool_result,
                "session_id": shared_state.session_id,
            },
        )
        
        # Queue the intervention
        queue_intervention(request)
        self.logger.info(
            f"HITL {intervention_type.name} for task {task.task_id} "
            f"({task.type} - {risk_level.value})"
        )
        
        if intervention_type == InterventionType.BLOCKING_APPROVAL:
            # Blocking: wait for human response
            response = await self._await_human_response(request)
            
            if response and response.approved:
                return HITLDecision(
                    proceed=True,
                    intervention_type=intervention_type,
                    request=request,
                    reason=f"Approved by {response.responder_name}",
                )
            else:
                return HITLDecision(
                    proceed=False,
                    intervention_type=intervention_type,
                    request=request,
                    reason="Rejected or timeout",
                )
        
        else:
            # Async review: queue and continue (or pause based on config)
            # For now, async means we proceed but flag for review
            return HITLDecision(
                proceed=True,
                intervention_type=intervention_type,
                request=request,
                reason=f"Queued for async review (confidence: {confidence.score:.2f})",
            )
    
    async def _await_human_response(
        self,
        request: InterventionRequest,
        check_interval: float = 1.0,
    ) -> Optional[InterventionResponse]:
        """
        Blocking wait for human approval with timeout.
        Polls for response at check_interval seconds.
        """
        import time
        from core.hitl_types import _responses
        
        start_time = datetime.now(timezone.utc)
        timeout = request.timeout_seconds
        
        self.logger.info(
            f"Blocking for approval on {request.request_id} "
            f"(timeout: {timeout}s)"
        )
        
        while True:
            # Check if response received
            if request.request_id in _responses:
                response = _responses[request.request_id]
                self.logger.info(
                    f"Response received for {request.request_id}: "
                    f"{'APPROVED' if response.approved else 'REJECTED'}"
                )
                return response
            
            # Check timeout
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            if elapsed > timeout:
                request.status = InterventionStatus.TIMEOUT
                self.logger.warning(f"Timeout on {request.request_id}")
                return None
            
            # Wait before next check
            await asyncio.sleep(check_interval)
    
    def get_pending_requests(self) -> List[InterventionRequest]:
        """Get all pending intervention requests."""
        return get_pending_interventions()
    
    def submit_human_response(self, response: InterventionResponse) -> bool:
        """Submit human response to an intervention request."""
        return submit_response(response)
    
    def get_intervention_status(self, request_id: str) -> Optional[InterventionRequest]:
        """Get status of a specific intervention request."""
        from core.hitl_types import _intervention_queue
        return _intervention_queue.get(request_id)


# Global middleware instance (singleton pattern)
_hitl_middleware: Optional[HITLMiddleware] = None


def get_hitl_middleware(enabled: bool = True) -> HITLMiddleware:
    """Get or create HITL middleware singleton."""
    global _hitl_middleware
    if _hitl_middleware is None:
        _hitl_middleware = HITLMiddleware(enabled=enabled)
    return _hitl_middleware


def reset_hitl_middleware():
    """Reset middleware (useful for testing)."""
    global _hitl_middleware
    _hitl_middleware = None
