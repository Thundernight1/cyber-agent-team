"""
HITL Core Types - Human-in-the-Loop Intervention System
==========================================================
Mirrors patterns from base_agent.py (dataclass, to_dict, enums)
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Dict, List, Optional


class InterventionType(Enum):
    """Types of human intervention required."""
    NONE = auto()           # No intervention, auto-execute
    ASYNC_REVIEW = auto()   # Queue for async human review
    BLOCKING_APPROVAL = auto()  # Pause execution, await approval


class InterventionStatus(Enum):
    """Status of an intervention request."""
    PENDING = auto()        # Awaiting human response
    APPROVED = auto()       # Human approved, proceed
    REJECTED = auto()       # Human rejected, cancel task
    TIMEOUT = auto()        # No response within timeout period
    AUTO_APPROVED = auto()  # Auto-approved based on confidence


class RiskLevel(Enum):
    """Risk classification for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ConfidenceScore:
    """Confidence assessment for a task."""
    score: float  # 0.0 to 1.0
    reasoning: str
    factors: List[str] = field(default_factory=list)
    
    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        return self.score >= threshold
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "reasoning": self.reasoning,
            "factors": self.factors,
        }


@dataclass
class InterventionRequest:
    """
    A request for human intervention.
    Mirrors AgentTask structure from base_agent.py
    """
    request_id: str
    task_id: str
    task_type: str
    target: str
    risk_level: RiskLevel
    confidence: ConfidenceScore
    intervention_type: InterventionType
    status: InterventionStatus
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    timeout_seconds: int = 300  # 5 minutes default
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "task_id": self.task_id,
            "task_type": self.task_type,
            "target": self.target,
            "risk_level": self.risk_level.value,
            "confidence": self.confidence.to_dict(),
            "intervention_type": self.intervention_type.name,
            "status": self.status.name,
            "created_at": self.created_at,
            "timeout_seconds": self.timeout_seconds,
            "context": self.context,
        }


@dataclass
class InterventionResponse:
    """Human response to an intervention request."""
    request_id: str
    approved: bool
    responder_id: str
    responder_name: str
    response_time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    notes: str = ""
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "approved": self.approved,
            "responder_id": self.responder_id,
            "responder_name": self.responder_name,
            "response_time": self.response_time,
            "notes": self.notes,
            "conditions": self.conditions,
        }


@dataclass
class HITLDecision:
    """Final decision from HITL middleware."""
    proceed: bool
    intervention_type: InterventionType
    request: Optional[InterventionRequest] = None
    reason: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "proceed": self.proceed,
            "intervention_type": self.intervention_type.name,
            "request": self.request.to_dict() if self.request else None,
            "reason": self.reason,
        }


# Intervention queue storage (in-memory, can be replaced with Redis)
_intervention_queue: Dict[str, InterventionRequest] = {}
_responses: Dict[str, InterventionResponse] = {}


def queue_intervention(request: InterventionRequest) -> None:
    """Add intervention request to queue."""
    _intervention_queue[request.request_id] = request


def get_intervention(request_id: str) -> Optional[InterventionRequest]:
    """Get intervention request by ID."""
    return _intervention_queue.get(request_id)


def get_pending_interventions() -> List[InterventionRequest]:
    """Get all pending intervention requests."""
    return [
        req for req in _intervention_queue.values()
        if req.status == InterventionStatus.PENDING
    ]


def submit_response(response: InterventionResponse) -> bool:
    """Submit human response to intervention request."""
    request = _intervention_queue.get(response.request_id)
    if not request:
        return False
    
    request.status = InterventionStatus.APPROVED if response.approved else InterventionStatus.REJECTED
    _responses[response.request_id] = response
    return True


def get_response(request_id: str) -> Optional[InterventionResponse]:
    """Get response for an intervention request."""
    return _responses.get(request_id)
