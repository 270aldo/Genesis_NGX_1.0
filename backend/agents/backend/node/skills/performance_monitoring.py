"""
Performance Monitoring Skill
===========================

Sets up performance monitoring and observability.
"""

from typing import Dict, Any, List
from core.logging_config import get_logger

logger = get_logger(__name__)


class PerformanceMonitoringSkill:
    """Skill for performance monitoring setup."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "performance_monitoring"
        self.description = "Set up performance monitoring"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set up performance monitoring.
        
        Args:
            request: Contains systems, metrics, sla_requirements
            
        Returns:
            Monitoring setup and configuration
        """
        try:
            monitoring_data = {
                "systems": request.get("systems", ["application", "infrastructure"]),
                "key_metrics": request.get("key_metrics", ["latency", "throughput"]),
                "sla_requirements": request.get("sla_requirements", {}),
                "alerting_channels": request.get("alerting_channels", ["email", "slack"]),
                "retention_days": request.get("retention_days", 30)
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_performance_monitoring_prompt(monitoring_data)
            
            # Generate monitoring setup
            response = await self.agent.generate_response(prompt)
            
            # Create monitoring architecture
            architecture = self._design_monitoring_architecture(monitoring_data)
            
            return {
                "success": True,
                "monitoring_setup": response,
                "skill_used": "performance_monitoring",
                "data": {
                    "architecture": architecture,
                    "metrics_collection": self._define_metrics_collection(monitoring_data),
                    "alerting_rules": self._create_alerting_rules(monitoring_data),
                    "dashboards": self._design_dashboards(monitoring_data)
                },
                "metadata": {
                    "confidence": 0.92,
                    "monitoring_maturity": self._assess_maturity(monitoring_data),
                    "observability_score": 0.85
                }
            }
            
        except Exception as e:
            logger.error(f"Error in performance monitoring: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "performance_monitoring"
            }
    
    def _design_monitoring_architecture(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Design monitoring architecture."""
        systems = data.get("systems", [])
        
        architecture = {
            "collection_layer": {
                "agents": self._select_agents(systems),
                "protocols": ["OpenTelemetry", "StatsD"],
                "sampling_rate": 0.1 if len(systems) > 10 else 1.0
            },
            "storage_layer": {
                "metrics": "Prometheus",
                "logs": "Elasticsearch",
                "traces": "Jaeger",
                "retention": f"{data.get('retention_days', 30)} days"
            },
            "visualization_layer": {
                "primary": "Grafana",
                "secondary": "Kibana",
                "custom_dashboards": True
            },
            "alerting_layer": {
                "engine": "AlertManager",
                "channels": data.get("alerting_channels", ["email"])
            }
        }
        
        return architecture
    
    def _select_agents(self, systems: List[str]) -> List[str]:
        """Select monitoring agents based on systems."""
        agents = []
        
        for system in systems:
            if "application" in system.lower():
                agents.extend(["APM agent", "Custom metrics SDK"])
            elif "infrastructure" in system.lower():
                agents.extend(["Node exporter", "cAdvisor"])
            elif "database" in system.lower():
                agents.append("Database exporter")
            elif "kubernetes" in system.lower():
                agents.extend(["kube-state-metrics", "metrics-server"])
        
        return list(set(agents))
    
    def _define_metrics_collection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Define metrics collection strategy."""
        metrics = data.get("key_metrics", [])
        
        collection = {
            "application_metrics": [],
            "infrastructure_metrics": [],
            "business_metrics": [],
            "custom_metrics": []
        }
        
        # Standard application metrics
        collection["application_metrics"] = [
            {"name": "request_rate", "unit": "req/s", "aggregation": "sum"},
            {"name": "error_rate", "unit": "errors/s", "aggregation": "sum"},
            {"name": "response_time", "unit": "ms", "aggregation": "p50,p95,p99"},
            {"name": "throughput", "unit": "ops/s", "aggregation": "avg"}
        ]
        
        # Infrastructure metrics
        collection["infrastructure_metrics"] = [
            {"name": "cpu_usage", "unit": "percent", "aggregation": "avg"},
            {"name": "memory_usage", "unit": "percent", "aggregation": "avg"},
            {"name": "disk_io", "unit": "MB/s", "aggregation": "sum"},
            {"name": "network_io", "unit": "MB/s", "aggregation": "sum"}
        ]
        
        # Add custom metrics based on requirements
        if "latency" in metrics:
            collection["custom_metrics"].append({
                "name": "service_latency",
                "unit": "ms",
                "aggregation": "histogram"
            })
        
        return collection
    
    def _create_alerting_rules(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create alerting rules based on SLA."""
        sla = data.get("sla_requirements", {})
        
        rules = [
            {
                "name": "high_error_rate",
                "condition": "error_rate > 1%",
                "duration": "5m",
                "severity": "critical",
                "action": "page_oncall"
            },
            {
                "name": "high_latency",
                "condition": f"p95_latency > {sla.get('latency_ms', 1000)}ms",
                "duration": "5m",
                "severity": "warning",
                "action": "notify_team"
            },
            {
                "name": "low_availability",
                "condition": f"availability < {sla.get('availability', 99.9)}%",
                "duration": "10m",
                "severity": "critical",
                "action": "escalate"
            },
            {
                "name": "resource_exhaustion",
                "condition": "cpu_usage > 80% OR memory_usage > 85%",
                "duration": "15m",
                "severity": "warning",
                "action": "auto_scale"
            }
        ]
        
        return rules
    
    def _design_dashboards(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Design monitoring dashboards."""
        dashboards = [
            {
                "name": "Executive Overview",
                "panels": [
                    "Service Health Score",
                    "SLA Compliance",
                    "Cost Metrics",
                    "User Experience Score"
                ],
                "refresh": "5m"
            },
            {
                "name": "Service Performance",
                "panels": [
                    "Request Rate",
                    "Error Rate",
                    "Response Time Distribution",
                    "Top Endpoints by Latency"
                ],
                "refresh": "1m"
            },
            {
                "name": "Infrastructure Health",
                "panels": [
                    "CPU/Memory Usage",
                    "Network I/O",
                    "Disk Usage",
                    "Container Health"
                ],
                "refresh": "30s"
            },
            {
                "name": "Application Insights",
                "panels": [
                    "Trace Analysis",
                    "Error Details",
                    "Database Performance",
                    "Cache Hit Rate"
                ],
                "refresh": "1m"
            }
        ]
        
        # Add custom dashboards based on metrics
        if "custom" in str(data.get("key_metrics", [])):
            dashboards.append({
                "name": "Custom Metrics",
                "panels": ["Custom KPIs", "Business Metrics"],
                "refresh": "5m"
            })
        
        return dashboards
    
    def _assess_maturity(self, data: Dict[str, Any]) -> str:
        """Assess monitoring maturity level."""
        metrics_count = len(data.get("key_metrics", []))
        systems_count = len(data.get("systems", []))
        has_sla = bool(data.get("sla_requirements"))
        
        score = 0
        if metrics_count > 5:
            score += 1
        if systems_count > 3:
            score += 1
        if has_sla:
            score += 1
        if "traces" in str(data.get("key_metrics", [])):
            score += 1
        
        if score >= 3:
            return "advanced"
        elif score >= 2:
            return "intermediate"
        else:
            return "basic"