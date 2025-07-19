"""
Backend Infrastructure Agents

These agents operate as invisible infrastructure services that support
the visible agent ecosystem without direct user interaction.

Backend agents:
- NODE: Systems Integration Operations (API management, automation, infrastructure)
- GUARDIAN: Security Compliance (data protection, audit, compliance monitoring)

These agents are called by other agents or system processes but are not
directly accessible through the main user interface.
"""

from .node.agent import SystemsIntegrationOps as NodeAgent
from .guardian.agent import SecurityComplianceGuardian as GuardianAgent

# Mark as backend/infrastructure agents
BACKEND_AGENTS = {
    "node": {
        "agent_class": NodeAgent,
        "visibility": "backend",
        "description": "Systems integration and infrastructure management",
        "accessible_via": "api_calls_only",
    },
    "guardian": {
        "agent_class": GuardianAgent,
        "visibility": "backend",
        "description": "Security compliance and data protection",
        "accessible_via": "security_events_only",
    },
}

__all__ = ["NodeAgent", "GuardianAgent", "BACKEND_AGENTS"]
