"""
Constants and defaults for NODE Systems Integration.
Centralizes all configuration constants for A+ level maintainability.
"""

from typing import Dict, List, Any

# Agent identification
AGENT_ID = "node_systems_integration"
AGENT_NAME = "NODE - Systems Integration"
AGENT_VERSION = "2.0.0"
AGENT_DESCRIPTION = (
    "El Coordinador de Sistemas Backend. Especialista en integración de APIs, "
    "automatización de infraestructura y coordinación de servicios distribuidos."
)

# Personality configuration - INTJ (Analytical, systematic, strategic)
PERSONALITY_CONFIG = {
    "mbti_type": "INTJ",
    "voice_model": "systems_integration_expert",
    "pitch": "medium-low",
    "pace": "140-160 WPM",  # Faster for technical efficiency
    "tone": "analytical precision with strategic insight",
    "energy": "focused technical concentration",
    "emotional_range": "methodical analysis to systematic satisfaction",
    "expertise_areas": [
        "systems_integration",
        "api_management",
        "infrastructure",
        "automation",
    ],
    "communication_style": "technical_precision",
    "analytical_level": 0.9,  # High analytical capability
}

# Skills configuration
CORE_SKILLS = [
    "handle_integration_request",
    "manage_automation_workflow",
    "process_api_integration",
    "coordinate_infrastructure",
    "manage_data_pipeline",
    "handle_general_integration",
]

VISUAL_SKILLS = [
    "analyze_system_architecture",
    "verify_integration_status",
    "analyze_data_flow_diagram",
]

CONVERSATIONAL_SKILLS = [
    "integration_consultation",
    "automation_guidance",
    "infrastructure_advisory",
    "api_troubleshooting",
    "systems_optimization",
]

# Performance benchmarks
PERFORMANCE_BENCHMARKS = {
    "max_response_time_ms": 1000,  # Higher for complex integrations
    "target_accuracy": 0.98,  # Higher precision for backend systems
    "max_error_rate": 0.0005,  # Lower tolerance for backend failures
    "target_test_coverage": 0.95,  # Highest standards for infrastructure
    "max_memory_usage_mb": 1024,  # More memory for complex operations
    "max_concurrent_integrations": 20,
}

# Security requirements (Critical for backend infrastructure)
SECURITY_REQUIREMENTS = {
    "encryption_algorithm": "AES-256-GCM",
    "key_rotation_interval_days": 30,  # Frequent rotation for backend
    "audit_log_retention_days": 2555,  # 7 years for compliance
    "max_session_age_minutes": 60,  # Shorter sessions for backend
    "required_compliance": ["SOC2", "ISO27001"],
    "ssl_verification": True,
    "api_key_validation": True,
}

# Integration types and protocols
INTEGRATION_TYPES = {
    "rest_api": {
        "protocols": ["HTTP", "HTTPS"],
        "methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
        "auth_types": ["bearer", "api_key", "oauth2", "basic"],
        "content_types": ["application/json", "application/xml", "text/plain"],
    },
    "graphql": {
        "protocols": ["HTTP", "HTTPS", "WebSocket"],
        "operations": ["query", "mutation", "subscription"],
        "auth_types": ["bearer", "api_key", "oauth2"],
    },
    "websocket": {
        "protocols": ["WS", "WSS"],
        "message_types": ["text", "binary", "ping", "pong"],
        "auth_types": ["token", "query_param", "header"],
    },
    "message_queue": {
        "protocols": ["AMQP", "MQTT", "Redis", "Apache Kafka"],
        "patterns": ["publish_subscribe", "request_response", "push_pull"],
        "serialization": ["JSON", "MessagePack", "Protobuf", "Avro"],
    },
    "database": {
        "types": ["SQL", "NoSQL", "Graph", "Time-series"],
        "operations": ["CREATE", "READ", "UPDATE", "DELETE", "BATCH"],
        "auth_types": ["connection_string", "credentials", "certificate"],
    },
}

# External service timeouts
SERVICE_TIMEOUTS = {
    "rest_api": 15.0,
    "graphql": 20.0,
    "websocket": 30.0,
    "database": 10.0,
    "message_queue": 5.0,
    "cloud_services": 30.0,
    "gemini_api": 20.0,
    "supabase": 10.0,
    "third_party": 30.0,
}

# Circuit breaker configuration
CIRCUIT_BREAKER_CONFIG = {
    "failure_threshold": 5,
    "timeout_seconds": 60,
    "half_open_max_calls": 3,
    "services": [
        "external_api",
        "database",
        "message_queue",
        "cloud_service",
        "third_party_integration",
    ],
}

# Cache configuration
CACHE_CONFIG = {
    "integration_results_ttl": 1800,  # 30 minutes
    "api_responses_ttl": 300,  # 5 minutes
    "system_status_ttl": 60,  # 1 minute
    "configuration_ttl": 3600,  # 1 hour
    "credentials_ttl": 900,  # 15 minutes
}

# Monitoring and metrics
MONITORING_CONFIG = {
    "health_check_interval": 30,
    "metrics_collection_interval": 15,
    "performance_alert_threshold": 2000,  # ms
    "error_rate_alert_threshold": 0.001,
    "memory_usage_alert_threshold": 85,  # percentage
    "integration_success_rate_threshold": 0.99,
}

# Feature flags defaults
FEATURE_FLAGS = {
    "enable_real_integrations": True,
    "enable_rest_api_integration": True,
    "enable_graphql_integration": True,
    "enable_websocket_integration": True,
    "enable_message_queue_integration": True,
    "enable_database_integration": True,
    "enable_cloud_services_integration": True,
    "enable_monitoring_integration": True,
    "enable_infrastructure_automation": True,
    "enable_deployment_automation": True,
    "enable_scaling_automation": True,
    "enable_backup_automation": True,
    "enable_async_processing": True,
    "enable_batch_operations": True,
    "enable_data_streaming": True,
    "enable_visual_analysis": True,
}

# Error messages
ERROR_MESSAGES = {
    "integration_failed": "System integration request failed",
    "api_connection_error": "Unable to establish API connection",
    "authentication_failed": "Integration authentication failed",
    "timeout_exceeded": "Integration request timed out",
    "rate_limit_exceeded": "API rate limit exceeded",
    "invalid_configuration": "Integration configuration is invalid",
    "service_unavailable": "External service is temporarily unavailable",
    "circuit_breaker_open": "Circuit breaker is open for this service",
    "data_validation_failed": "Integration data validation failed",
    "insufficient_permissions": "Insufficient permissions for integration",
}

# User communication templates (INTJ analytical style)
COMMUNICATION_TEMPLATES = {
    "integration_greeting": "Systems integration ready. Analyzing your infrastructure requirements.",
    "automation_greeting": "Automation systems online. Ready to optimize your workflows.",
    "analysis_starting": "Initiating system analysis with comprehensive diagnostic protocols...",
    "analysis_complete": "Integration analysis complete. Here are the optimized system recommendations:",
    "error_notification": "System integration encountered an issue. Implementing recovery protocols.",
    "success_confirmation": "Integration successfully deployed. All systems operating within parameters.",
    "optimization_suggestion": "I've identified several optimization opportunities for your infrastructure.",
    "security_notice": "All integration requests are validated and logged for security compliance.",
}

# Integration patterns and best practices
INTEGRATION_PATTERNS = {
    "api_gateway": {
        "description": "Centralized API management and routing",
        "use_cases": ["microservices", "rate_limiting", "authentication"],
        "benefits": ["unified_interface", "security", "monitoring"],
    },
    "event_driven": {
        "description": "Asynchronous event-based communication",
        "use_cases": ["real_time_updates", "decoupling", "scalability"],
        "benefits": ["loose_coupling", "scalability", "resilience"],
    },
    "circuit_breaker": {
        "description": "Fault tolerance for external service calls",
        "use_cases": ["service_protection", "cascade_failure_prevention"],
        "benefits": ["resilience", "fast_failure", "recovery"],
    },
    "retry_pattern": {
        "description": "Automatic retry with exponential backoff",
        "use_cases": ["transient_failures", "network_issues"],
        "benefits": ["reliability", "fault_tolerance", "user_experience"],
    },
    "bulkhead": {
        "description": "Resource isolation for critical operations",
        "use_cases": ["resource_protection", "performance_isolation"],
        "benefits": ["fault_isolation", "predictable_performance"],
    },
}

# Data pipeline stages
PIPELINE_STAGES = {
    "extraction": {
        "description": "Data source extraction and ingestion",
        "validations": ["format", "schema", "completeness"],
        "error_handling": ["retry", "dead_letter", "notification"],
    },
    "transformation": {
        "description": "Data cleaning, mapping, and enrichment",
        "validations": ["data_quality", "business_rules", "schema_compliance"],
        "error_handling": ["validation_failure", "transformation_error"],
    },
    "loading": {
        "description": "Data loading into target systems",
        "validations": ["target_availability", "capacity", "constraints"],
        "error_handling": ["rollback", "partial_load", "notification"],
    },
    "validation": {
        "description": "End-to-end data validation and quality checks",
        "validations": ["data_integrity", "business_logic", "completeness"],
        "error_handling": ["quality_alert", "reprocessing", "manual_review"],
    },
}

# Cloud service providers and services
CLOUD_SERVICES = {
    "aws": {
        "compute": ["EC2", "Lambda", "ECS", "EKS"],
        "storage": ["S3", "EBS", "EFS"],
        "database": ["RDS", "DynamoDB", "Redshift"],
        "messaging": ["SQS", "SNS", "EventBridge"],
        "monitoring": ["CloudWatch", "X-Ray"],
    },
    "gcp": {
        "compute": ["Compute Engine", "Cloud Functions", "GKE"],
        "storage": ["Cloud Storage", "Persistent Disk"],
        "database": ["Cloud SQL", "Firestore", "BigQuery"],
        "messaging": ["Pub/Sub", "Cloud Tasks"],
        "monitoring": ["Cloud Monitoring", "Cloud Trace"],
    },
    "azure": {
        "compute": ["Virtual Machines", "Functions", "AKS"],
        "storage": ["Blob Storage", "Disk Storage"],
        "database": ["SQL Database", "Cosmos DB"],
        "messaging": ["Service Bus", "Event Grid"],
        "monitoring": ["Monitor", "Application Insights"],
    },
}

# Automation workflows
AUTOMATION_WORKFLOWS = {
    "deployment": {
        "stages": ["build", "test", "staging", "production"],
        "validations": ["code_quality", "security_scan", "performance_test"],
        "rollback_triggers": [
            "health_check_fail",
            "error_rate_spike",
            "manual_trigger",
        ],
    },
    "scaling": {
        "triggers": ["cpu_usage", "memory_usage", "request_count", "queue_length"],
        "strategies": ["horizontal", "vertical", "predictive"],
        "constraints": ["min_instances", "max_instances", "budget_limits"],
    },
    "backup": {
        "schedules": ["daily", "weekly", "monthly", "on_demand"],
        "types": ["full", "incremental", "differential"],
        "retention": ["7_days", "30_days", "1_year", "indefinite"],
    },
    "monitoring": {
        "metrics": ["performance", "availability", "errors", "business_kpis"],
        "alerts": ["threshold", "anomaly", "pattern", "correlation"],
        "responses": ["notification", "auto_remediation", "escalation"],
    },
}

# Compliance frameworks
COMPLIANCE_CONFIG = {
    "soc2": {
        "type_1": {
            "security": True,
            "availability": True,
            "processing_integrity": True,
        },
        "type_2": {"confidentiality": True, "privacy": True},
        "controls": ["access_control", "audit_logging", "encryption", "monitoring"],
    },
    "iso27001": {
        "domains": ["information_security", "risk_management", "compliance"],
        "controls": [
            "asset_management",
            "access_control",
            "cryptography",
            "incident_management",
        ],
        "requirements": [
            "documentation",
            "training",
            "audit",
            "continuous_improvement",
        ],
    },
    "gdpr": {
        "principles": ["lawfulness", "data_minimization", "accuracy", "accountability"],
        "rights": ["access", "rectification", "erasure", "portability"],
        "requirements": ["consent", "privacy_by_design", "breach_notification"],
    },
}

# Visual analysis capabilities
VISUAL_ANALYSIS_CONFIG = {
    "supported_formats": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".pdf"],
    "diagram_types": [
        "system_architecture",
        "data_flow",
        "network_topology",
        "integration_map",
        "deployment_diagram",
        "sequence_diagram",
    ],
    "analysis_features": [
        "component_identification",
        "connection_mapping",
        "bottleneck_detection",
        "security_assessment",
        "optimization_suggestions",
    ],
}
