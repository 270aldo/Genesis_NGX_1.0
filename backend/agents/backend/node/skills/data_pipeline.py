"""
Data Pipeline Skill
==================

Designs and manages data pipelines.
"""

from typing import Dict, Any, List
from core.logging_config import get_logger

logger = get_logger(__name__)


class DataPipelineSkill:
    """Skill for data pipeline design and management."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "data_pipeline"
        self.description = "Design and manage data pipelines"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design data pipeline.
        
        Args:
            request: Contains sources, transformations, destinations
            
        Returns:
            Data pipeline design and architecture
        """
        try:
            pipeline_data = {
                "sources": request.get("sources", ["database"]),
                "transformations": request.get("transformations", ["clean", "aggregate"]),
                "destinations": request.get("destinations", ["data_warehouse"]),
                "data_volume": request.get("data_volume", "medium"),
                "frequency": request.get("frequency", "daily"),
                "data_types": request.get("data_types", ["structured"])
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_data_pipeline_prompt(pipeline_data)
            
            # Generate pipeline design
            response = await self.agent.generate_response(prompt)
            
            # Create pipeline architecture
            architecture = self._design_architecture(pipeline_data)
            
            return {
                "success": True,
                "pipeline_design": response,
                "skill_used": "data_pipeline",
                "data": {
                    "architecture": architecture,
                    "technology_stack": self._recommend_stack(pipeline_data),
                    "data_quality_checks": self._define_quality_checks(),
                    "monitoring_setup": self._create_monitoring(pipeline_data)
                },
                "metadata": {
                    "confidence": 0.89,
                    "pipeline_type": self._classify_pipeline(pipeline_data),
                    "scalability": self._assess_scalability(pipeline_data)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in data pipeline design: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "data_pipeline"
            }
    
    def _design_architecture(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Design pipeline architecture."""
        volume = data.get("data_volume", "medium")
        frequency = data.get("frequency", "daily")
        
        # Choose architecture pattern
        if frequency in ["realtime", "streaming"]:
            pattern = "streaming"
        elif volume == "high" or frequency == "hourly":
            pattern = "micro_batch"
        else:
            pattern = "batch"
        
        architecture = {
            "pattern": pattern,
            "components": {
                "ingestion": self._design_ingestion(data),
                "processing": self._design_processing(data),
                "storage": self._design_storage(data),
                "orchestration": self._design_orchestration(pattern)
            },
            "data_flow": self._create_data_flow(data)
        }
        
        return architecture
    
    def _design_ingestion(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Design ingestion layer."""
        sources = data.get("sources", [])
        
        ingestion = {
            "method": "pull" if len(sources) <= 3 else "push_pull_hybrid",
            "connectors": [],
            "error_handling": "dead_letter_queue"
        }
        
        # Add connectors based on sources
        for source in sources:
            if "database" in source.lower():
                ingestion["connectors"].append("JDBC")
            elif "api" in source.lower():
                ingestion["connectors"].append("REST")
            elif "file" in source.lower():
                ingestion["connectors"].append("File System")
            elif "stream" in source.lower():
                ingestion["connectors"].append("Kafka")
        
        return ingestion
    
    def _design_processing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Design processing layer."""
        transformations = data.get("transformations", [])
        
        return {
            "engine": "Spark" if data.get("data_volume") == "high" else "Pandas",
            "transformations": transformations,
            "optimization": {
                "partitioning": True,
                "caching": len(transformations) > 5,
                "parallel_processing": True
            }
        }
    
    def _design_storage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Design storage layer."""
        destinations = data.get("destinations", [])
        
        storage = {
            "primary": "data_lake",
            "format": "parquet",
            "partitioning": ["date", "source"],
            "compression": "snappy"
        }
        
        if "data_warehouse" in destinations:
            storage["analytical"] = {
                "type": "columnar",
                "engine": "BigQuery",
                "schema": "star_schema"
            }
        
        return storage
    
    def _design_orchestration(self, pattern: str) -> Dict[str, Any]:
        """Design orchestration layer."""
        if pattern == "streaming":
            return {
                "tool": "Apache Flink",
                "checkpointing": True,
                "exactly_once": True
            }
        else:
            return {
                "tool": "Apache Airflow",
                "scheduling": "cron",
                "dependencies": "DAG"
            }
    
    def _create_data_flow(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Create data flow stages."""
        flow = [
            {"stage": "ingestion", "description": "Extract data from sources"},
            {"stage": "validation", "description": "Validate data quality"},
            {"stage": "transformation", "description": "Apply business logic"},
            {"stage": "enrichment", "description": "Add derived fields"},
            {"stage": "loading", "description": "Load to destinations"}
        ]
        
        if data.get("data_volume") == "high":
            flow.insert(2, {"stage": "partitioning", "description": "Partition for parallel processing"})
        
        return flow
    
    def _recommend_stack(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Recommend technology stack."""
        volume = data.get("data_volume", "medium")
        frequency = data.get("frequency", "daily")
        
        stack = {
            "ingestion": [],
            "processing": [],
            "storage": [],
            "orchestration": [],
            "monitoring": []
        }
        
        # Ingestion tools
        if frequency in ["realtime", "streaming"]:
            stack["ingestion"] = ["Apache Kafka", "AWS Kinesis", "Pub/Sub"]
        else:
            stack["ingestion"] = ["Airbyte", "Fivetran", "Stitch"]
        
        # Processing tools
        if volume == "high":
            stack["processing"] = ["Apache Spark", "Databricks", "EMR"]
        else:
            stack["processing"] = ["Apache Beam", "dbt", "Pandas"]
        
        # Storage
        stack["storage"] = ["S3", "BigQuery", "Snowflake"]
        
        # Orchestration
        stack["orchestration"] = ["Airflow", "Prefect", "Dagster"]
        
        # Monitoring
        stack["monitoring"] = ["DataDog", "Prometheus", "Great Expectations"]
        
        return stack
    
    def _define_quality_checks(self) -> List[Dict[str, Any]]:
        """Define data quality checks."""
        return [
            {
                "check": "completeness",
                "description": "Verify no critical fields are null",
                "action": "reject_record"
            },
            {
                "check": "validity",
                "description": "Validate data types and formats",
                "action": "transform_or_reject"
            },
            {
                "check": "consistency",
                "description": "Check referential integrity",
                "action": "log_warning"
            },
            {
                "check": "timeliness",
                "description": "Ensure data freshness",
                "action": "alert_if_stale"
            },
            {
                "check": "accuracy",
                "description": "Validate business rules",
                "action": "quarantine"
            }
        ]
    
    def _create_monitoring(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create monitoring setup for pipeline."""
        return {
            "metrics": [
                "records_processed",
                "processing_time",
                "error_rate",
                "data_quality_score",
                "pipeline_latency"
            ],
            "alerts": [
                {"metric": "error_rate", "threshold": 5, "window": "5m"},
                {"metric": "processing_time", "threshold": "2x_baseline", "window": "10m"},
                {"metric": "data_quality_score", "threshold": 0.95, "window": "1h"}
            ],
            "dashboards": [
                "pipeline_overview",
                "data_quality",
                "performance_metrics",
                "cost_analysis"
            ]
        }
    
    def _classify_pipeline(self, data: Dict[str, Any]) -> str:
        """Classify pipeline type."""
        frequency = data.get("frequency", "daily")
        volume = data.get("data_volume", "medium")
        
        if frequency in ["realtime", "streaming"]:
            return "streaming_pipeline"
        elif volume == "high":
            return "big_data_pipeline"
        elif len(data.get("transformations", [])) > 5:
            return "complex_etl_pipeline"
        else:
            return "simple_batch_pipeline"
    
    def _assess_scalability(self, data: Dict[str, Any]) -> str:
        """Assess pipeline scalability."""
        volume = data.get("data_volume", "medium")
        sources = len(data.get("sources", []))
        
        if volume == "high" or sources > 5:
            return "highly_scalable"
        elif volume == "medium":
            return "moderately_scalable"
        else:
            return "standard_scalability"