"""
Node Systems Integration Agent
==============================

Systems integration and operations specialist.
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

# Core imports
from agents.base.base_ngx_agent import BaseNGXAgent
from agents.base.adk_agent import ADKAgent
from adk import Skill
from infrastructure.adapters.a2a_adapter import a2a_adapter
from core.logging_config import get_logger

# Node-specific imports
from .config import NodeConfig
from .prompts import NodePrompts
from .skills import (
    IntegrationRequestSkill,
    AutomationRequestSkill,
    ApiManagementSkill,
    InfrastructureOptimizationSkill,
    DataPipelineSkill,
    ServiceOrchestrationSkill,
    PerformanceMonitoringSkill
)

# Services
from .services.systems_integration_service import SystemsIntegrationService
from .services.infrastructure_automation_service import InfrastructureAutomationService
from .services.data_pipeline_service import DataPipelineService

logger = get_logger(__name__)


class SystemsIntegrationOps(BaseNGXAgent, ADKAgent):
    """
    Node agent specializing in systems integration and operations.
    
    Inherits from both BaseNGXAgent and ADKAgent for full compatibility
    with the NGX ecosystem and Google ADK framework.
    """
    
    def __init__(self, agent_id: Optional[str] = None):
        """Initialize Node agent with configuration."""
        # Load configuration
        self.config = NodeConfig()
        
        # Generate ID if not provided
        if not agent_id:
            agent_id = f"node_{uuid.uuid4().hex[:8]}"
        
        # Initialize base classes
        BaseNGXAgent.__init__(
            self,
            agent_id=agent_id,
            name=self.config.name,
            specialization=self.config.specialization,
            system_prompt=NodePrompts.get_base_instructions()
        )
        
        # Initialize ADKAgent
        ADKAgent.__init__(self, agent_id=agent_id)
        
        # Initialize prompts manager
        self.prompts = NodePrompts()
        
        # Initialize services
        self._init_services()
        
        # Initialize skills
        self._init_skills()
        
        # Register ADK skills
        self.adk_skills = self._create_adk_skills()
        
        logger.info(f"Node agent initialized: {self.name}")
    
    def _init_services(self):
        """Initialize Node services."""
        self.integration_service = SystemsIntegrationService()
        self.automation_service = InfrastructureAutomationService()
        self.pipeline_service = DataPipelineService()
    
    def _init_skills(self):
        """Initialize Node skills."""
        self.integration_skill = IntegrationRequestSkill(self)
        self.automation_skill = AutomationRequestSkill(self)
        self.api_skill = ApiManagementSkill(self)
        self.infrastructure_skill = InfrastructureOptimizationSkill(self)
        self.pipeline_skill = DataPipelineSkill(self)
        self.orchestration_skill = ServiceOrchestrationSkill(self)
        self.monitoring_skill = PerformanceMonitoringSkill(self)
    
    def _create_adk_skills(self) -> List[Skill]:
        """Create ADK skill definitions."""
        return [
            Skill(
                name="integration_request",
                description="Handle system integration requests",
                handler=self._handle_integration_request
            ),
            Skill(
                name="automation_request",
                description="Design workflow automations",
                handler=self._handle_automation_request
            ),
            Skill(
                name="api_management",
                description="Manage API design and implementation",
                handler=self._handle_api_management
            ),
            Skill(
                name="infrastructure_optimization",
                description="Optimize infrastructure and cloud resources",
                handler=self._handle_infrastructure_optimization
            ),
            Skill(
                name="data_pipeline",
                description="Design and manage data pipelines",
                handler=self._handle_data_pipeline
            ),
            Skill(
                name="service_orchestration",
                description="Orchestrate microservices",
                handler=self._handle_service_orchestration
            ),
            Skill(
                name="performance_monitoring",
                description="Set up performance monitoring",
                handler=self._handle_performance_monitoring
            )
        ]
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming request and route to appropriate skill.
        
        Args:
            request: Request containing user input and context
            
        Returns:
            Response from skill execution
        """
        try:
            # Log integration request
            await self.integration_service.log_request(
                agent_id=self.agent_id,
                request=request
            )
            
            # Analyze request type
            skill_type = self._analyze_request_type(request)
            
            # Route to appropriate skill
            response = await self._route_to_skill(skill_type, request)
            
            # Track metrics
            await self._track_metrics(skill_type, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }
    
    def _analyze_request_type(self, request: Dict[str, Any]) -> str:
        """Analyze request to determine skill type."""
        query = request.get("message", "").lower()
        
        # Keyword-based routing
        if any(word in query for word in ["integrate", "connect", "sync", "garmin", "fitbit"]):
            return "integration_request"
        elif any(word in query for word in ["automate", "workflow", "trigger", "action"]):
            return "automation_request"
        elif any(word in query for word in ["api", "endpoint", "rest", "graphql"]):
            return "api_management"
        elif any(word in query for word in ["infrastructure", "cloud", "optimize", "scale"]):
            return "infrastructure_optimization"
        elif any(word in query for word in ["pipeline", "etl", "data flow", "transform"]):
            return "data_pipeline"
        elif any(word in query for word in ["microservice", "orchestrate", "service mesh"]):
            return "service_orchestration"
        elif any(word in query for word in ["monitor", "metric", "performance", "observability"]):
            return "performance_monitoring"
        else:
            return "integration_request"  # Default
    
    async def _route_to_skill(self, skill_type: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to appropriate skill."""
        skill_map = {
            "integration_request": self.integration_skill,
            "automation_request": self.automation_skill,
            "api_management": self.api_skill,
            "infrastructure_optimization": self.infrastructure_skill,
            "data_pipeline": self.pipeline_skill,
            "service_orchestration": self.orchestration_skill,
            "performance_monitoring": self.monitoring_skill
        }
        
        skill = skill_map.get(skill_type)
        if skill:
            return await skill.execute(request)
        else:
            return await self.integration_skill.execute(request)
    
    async def _track_metrics(self, skill_type: str, response: Dict[str, Any]):
        """Track performance metrics."""
        try:
            metrics = {
                "skill_type": skill_type,
                "success": response.get("success", False),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Log metrics (simplified for now)
            logger.info(f"Metrics: {metrics}")
            
        except Exception as e:
            logger.error(f"Error tracking metrics: {str(e)}")
    
    # ADK Handler Methods
    async def _handle_integration_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """ADK handler for integration requests."""
        return await self.integration_skill.execute(request)
    
    async def _handle_automation_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """ADK handler for automation requests."""
        return await self.automation_skill.execute(request)
    
    async def _handle_api_management(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """ADK handler for API management."""
        return await self.api_skill.execute(request)
    
    async def _handle_infrastructure_optimization(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """ADK handler for infrastructure optimization."""
        return await self.infrastructure_skill.execute(request)
    
    async def _handle_data_pipeline(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """ADK handler for data pipeline design."""
        return await self.pipeline_skill.execute(request)
    
    async def _handle_service_orchestration(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """ADK handler for service orchestration."""
        return await self.orchestration_skill.execute(request)
    
    async def _handle_performance_monitoring(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """ADK handler for performance monitoring."""
        return await self.monitoring_skill.execute(request)
    
    # A2A Integration
    async def handle_a2a_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle A2A protocol requests."""
        try:
            # Validate request
            if not self._validate_a2a_request(request):
                return {
                    "success": False,
                    "error": "Invalid A2A request format"
                }
            
            # Process through standard flow
            return await self.process_request(request)
            
        except Exception as e:
            logger.error(f"A2A request error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }
    
    def _validate_a2a_request(self, request: Dict[str, Any]) -> bool:
        """Validate A2A request format."""
        required_fields = ["user_id", "session_id", "message"]
        return all(field in request for field in required_fields)
    
    # Integration status
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get status of active integrations."""
        return await self.integration_service.get_active_integrations()
    
    # Pipeline status
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get status of data pipelines."""
        return await self.pipeline_service.get_pipeline_status()
    
    # Infrastructure metrics
    async def get_infrastructure_metrics(self) -> Dict[str, Any]:
        """Get infrastructure performance metrics."""
        return await self.automation_service.get_metrics()


# Alias for backward compatibility
NODE = SystemsIntegrationOps