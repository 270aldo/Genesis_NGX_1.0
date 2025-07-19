"""
Automation Request Skill
=======================

Handles workflow automation requests.
"""

from typing import Dict, Any, List
from core.logging_config import get_logger

logger = get_logger(__name__)


class AutomationRequestSkill:
    """Skill for workflow automation design."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "automation_request"
        self.description = "Design workflow automations"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design workflow automation.
        
        Args:
            request: Contains workflow, triggers, actions
            
        Returns:
            Automation design and implementation plan
        """
        try:
            automation_data = {
                "workflow": request.get("workflow", {}),
                "triggers": request.get("triggers", ["manual"]),
                "actions": request.get("actions", []),
                "conditions": request.get("conditions", []),
                "frequency": request.get("frequency", "on_demand")
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_automation_request_prompt(automation_data)
            
            # Generate automation design
            response = await self.agent.generate_response(prompt)
            
            # Create workflow structure
            workflow_structure = self._create_workflow_structure(automation_data)
            
            return {
                "success": True,
                "automation_design": response,
                "skill_used": "automation_request",
                "data": {
                    "workflow_structure": workflow_structure,
                    "automation_tools": self._recommend_automation_tools(automation_data),
                    "estimated_runtime": self._estimate_runtime(workflow_structure),
                    "monitoring_setup": self._create_monitoring_setup()
                },
                "metadata": {
                    "confidence": 0.90,
                    "automation_type": self._classify_automation(automation_data),
                    "scalability": "high"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in automation request: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "automation_request"
            }
    
    def _create_workflow_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create workflow structure from automation data."""
        structure = {
            "triggers": data["triggers"],
            "steps": [],
            "error_handling": {
                "retry_count": 3,
                "retry_delay": 60,
                "fallback_action": "notify_admin"
            }
        }
        
        # Add steps based on actions
        for i, action in enumerate(data.get("actions", [])):
            step = {
                "order": i + 1,
                "action": action,
                "conditions": data.get("conditions", []),
                "on_success": "continue",
                "on_failure": "retry"
            }
            structure["steps"].append(step)
        
        return structure
    
    def _recommend_automation_tools(self, data: Dict[str, Any]) -> List[str]:
        """Recommend automation tools based on requirements."""
        tools = []
        
        # Simple automations
        if len(data.get("actions", [])) <= 5:
            tools.extend(["Zapier", "IFTTT", "Make (Integromat)"])
        
        # Complex workflows
        if len(data.get("actions", [])) > 5 or data.get("conditions"):
            tools.extend(["n8n", "Apache Airflow", "Temporal"])
        
        # High frequency
        if data.get("frequency") in ["realtime", "minute"]:
            tools.append("Apache Kafka")
        
        return list(set(tools))
    
    def _estimate_runtime(self, workflow: Dict[str, Any]) -> str:
        """Estimate workflow runtime."""
        steps = len(workflow.get("steps", []))
        
        if steps <= 3:
            return "< 1 minute"
        elif steps <= 10:
            return "1-5 minutes"
        else:
            return "> 5 minutes"
    
    def _create_monitoring_setup(self) -> Dict[str, Any]:
        """Create monitoring setup for automation."""
        return {
            "metrics": [
                "execution_time",
                "success_rate",
                "error_count",
                "throughput"
            ],
            "alerts": [
                {"type": "failure", "threshold": 3, "window": "5m"},
                {"type": "latency", "threshold": "5m", "window": "10m"}
            ],
            "logging": {
                "level": "INFO",
                "retention": "30d",
                "structured": True
            }
        }
    
    def _classify_automation(self, data: Dict[str, Any]) -> str:
        """Classify the type of automation."""
        triggers = data.get("triggers", [])
        actions = data.get("actions", [])
        
        if "schedule" in str(triggers):
            return "scheduled_automation"
        elif "webhook" in str(triggers) or "api" in str(triggers):
            return "event_driven_automation"
        elif len(actions) > 10:
            return "complex_workflow"
        else:
            return "simple_automation"