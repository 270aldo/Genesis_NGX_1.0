"""
Node Configuration
==================

Configuration classes for the Node agent.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class NodeConfig(BaseModel):
    """Configuration for Node systems integration agent."""
    
    # Agent identification
    name: str = Field(default="NODE", description="Agent name")
    agent_id: str = Field(default="node", description="Agent ID")
    specialization: str = Field(
        default="Systems Integration and Operations Specialist",
        description="Agent's area of expertise"
    )
    
    # Core capabilities
    capabilities: List[str] = Field(
        default=[
            "systems_integration",
            "workflow_automation",
            "api_management",
            "infrastructure_optimization",
            "data_pipeline_design",
            "service_orchestration",
            "performance_monitoring",
            "deployment_automation",
            "cloud_resource_management",
            "microservices_coordination"
        ],
        description="Agent capabilities"
    )
    
    # Integration platforms
    supported_platforms: List[str] = Field(
        default=[
            "Garmin Connect",
            "Fitbit",
            "Apple HealthKit",
            "Google Fit",
            "Strava",
            "Oura Ring",
            "Whoop",
            "MyFitnessPal",
            "Polar",
            "Suunto"
        ],
        description="Supported integration platforms"
    )
    
    # API configurations
    api_types: List[str] = Field(
        default=["REST", "GraphQL", "WebSocket", "gRPC", "SOAP"],
        description="Supported API types"
    )
    
    # Automation frameworks
    automation_tools: List[str] = Field(
        default=[
            "Zapier",
            "Make (Integromat)",
            "n8n",
            "Apache Airflow",
            "Temporal",
            "Prefect"
        ],
        description="Automation tools supported"
    )
    
    # Infrastructure domains
    infrastructure_domains: List[str] = Field(
        default=[
            "kubernetes",
            "docker",
            "serverless",
            "cloud_native",
            "edge_computing",
            "distributed_systems"
        ],
        description="Infrastructure domains"
    )
    
    # Performance settings
    connection_timeout_seconds: int = Field(
        default=30,
        description="Default timeout for external connections"
    )
    max_concurrent_integrations: int = Field(
        default=10,
        description="Maximum concurrent integration processes"
    )
    retry_max_attempts: int = Field(
        default=3,
        description="Maximum retry attempts for failed operations"
    )
    
    # Monitoring settings
    enable_performance_tracking: bool = Field(
        default=True,
        description="Enable performance metrics tracking"
    )
    metrics_retention_days: int = Field(
        default=30,
        description="Days to retain performance metrics"
    )
    
    # Data pipeline settings
    max_pipeline_stages: int = Field(
        default=20,
        description="Maximum stages in a data pipeline"
    )
    enable_data_validation: bool = Field(
        default=True,
        description="Enable automatic data validation"
    )
    
    # Security settings
    enable_api_authentication: bool = Field(
        default=True,
        description="Require authentication for API access"
    )
    encrypt_sensitive_data: bool = Field(
        default=True,
        description="Encrypt sensitive data in transit"
    )
    
    # Optimization settings
    enable_auto_scaling: bool = Field(
        default=True,
        description="Enable automatic resource scaling"
    )
    cost_optimization_enabled: bool = Field(
        default=True,
        description="Enable cost optimization strategies"
    )
    
    # Metadata
    version: str = Field(default="1.0.0", description="Configuration version")
    environment: str = Field(default="production", description="Environment")
    
    class Config:
        validate_assignment = True