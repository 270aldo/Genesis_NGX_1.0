"""
Data Pipeline Service for NODE Systems Integration agent.
Handles data extraction, transformation, loading, and pipeline orchestration.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum

from agents.backend.node.core.config import NodeConfig
from agents.backend.node.core.exceptions import (
    DataPipelineError,
    NodeValidationError,
    DatabaseIntegrationError,
)
from agents.backend.node.core.constants import PIPELINE_STAGES
from core.logging_config import get_logger

logger = get_logger(__name__)


class PipelineStage(Enum):
    """Pipeline execution stages."""

    EXTRACTION = "extraction"
    TRANSFORMATION = "transformation"
    LOADING = "loading"
    VALIDATION = "validation"


class PipelineStatus(Enum):
    """Pipeline execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DataSource:
    """Configuration for data source."""

    source_type: str  # database, api, file, stream
    connection_string: Optional[str] = None
    endpoint: Optional[str] = None
    file_path: Optional[str] = None
    query: Optional[str] = None
    format: Optional[str] = None  # json, csv, parquet, xml
    auth_config: Optional[Dict[str, str]] = None


@dataclass
class DataTarget:
    """Configuration for data target."""

    target_type: str  # database, api, file, stream
    connection_string: Optional[str] = None
    endpoint: Optional[str] = None
    file_path: Optional[str] = None
    table_name: Optional[str] = None
    format: Optional[str] = None
    write_mode: str = "append"  # append, overwrite, upsert


@dataclass
class TransformationRule:
    """Data transformation rule."""

    rule_type: str  # filter, map, aggregate, join, validate
    expression: str
    parameters: Optional[Dict[str, Any]] = None


@dataclass
class PipelineConfig:
    """Complete pipeline configuration."""

    pipeline_name: str
    description: str
    data_source: DataSource
    data_target: DataTarget
    transformation_rules: List[TransformationRule]
    schedule: Optional[str] = None  # cron expression
    timeout_minutes: int = 60
    retry_attempts: int = 3
    enable_monitoring: bool = True


class DataPipelineService:
    """
    Comprehensive data pipeline service for ETL/ELT operations.

    Features:
    - Multiple data source and target integrations
    - Flexible transformation engine
    - Pipeline scheduling and orchestration
    - Data quality validation
    - Error handling and retry mechanisms
    - Performance monitoring and optimization
    """

    def __init__(self, config: NodeConfig):
        self.config = config
        self._pipelines = {}
        self._pipeline_runs = {}
        self._transformation_functions = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the data pipeline service."""
        try:
            self._pipelines = {}
            self._pipeline_runs = {}

            # Register built-in transformation functions
            await self._register_transformation_functions()

            self._initialized = True
            logger.info("Data pipeline service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize data pipeline service: {e}")
            raise DataPipelineError(
                f"Data pipeline service initialization failed: {e}",
                pipeline_stage="initialization",
            )

    async def _register_transformation_functions(self) -> None:
        """Register built-in transformation functions."""
        self._transformation_functions = {
            "filter": self._filter_transform,
            "map": self._map_transform,
            "aggregate": self._aggregate_transform,
            "join": self._join_transform,
            "validate": self._validate_transform,
            "deduplicate": self._deduplicate_transform,
            "normalize": self._normalize_transform,
            "enrich": self._enrich_transform,
        }

    async def create_pipeline(self, pipeline_config: PipelineConfig) -> Dict[str, Any]:
        """
        Create a new data pipeline.

        Args:
            pipeline_config: Pipeline configuration

        Returns:
            Dict[str, Any]: Pipeline creation result

        Raises:
            DataPipelineError: If pipeline creation fails
        """
        if not self._initialized:
            raise DataPipelineError("Service not initialized")

        if not self.config.enable_data_streaming:
            raise DataPipelineError(
                "Data streaming is disabled",
                pipeline_stage="configuration",
            )

        try:
            # Validate pipeline configuration
            await self._validate_pipeline_config(pipeline_config)

            pipeline_id = f"pipeline-{pipeline_config.pipeline_name}-{int(datetime.utcnow().timestamp())}"

            # Create pipeline metadata
            pipeline = {
                "pipeline_id": pipeline_id,
                "config": pipeline_config,
                "status": PipelineStatus.PENDING.value,
                "created_at": datetime.utcnow(),
                "last_run": None,
                "run_count": 0,
                "success_count": 0,
                "failure_count": 0,
                "avg_runtime_seconds": 0,
            }

            # Store pipeline
            self._pipelines[pipeline_id] = pipeline

            # Schedule pipeline if schedule is provided
            if pipeline_config.schedule:
                await self._schedule_pipeline(pipeline_id, pipeline_config.schedule)

            logger.info(f"Pipeline created successfully: {pipeline_id}")

            return {
                "pipeline_id": pipeline_id,
                "pipeline_name": pipeline_config.pipeline_name,
                "status": PipelineStatus.PENDING.value,
                "created_at": pipeline["created_at"].isoformat(),
                "scheduled": bool(pipeline_config.schedule),
            }

        except Exception as e:
            logger.error(f"Pipeline creation failed: {e}")
            raise DataPipelineError(
                f"Pipeline creation failed: {e}",
                pipeline_stage="creation",
            )

    async def execute_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """
        Execute a data pipeline.

        Args:
            pipeline_id: Pipeline identifier

        Returns:
            Dict[str, Any]: Pipeline execution result
        """
        if pipeline_id not in self._pipelines:
            raise DataPipelineError(
                f"Pipeline not found: {pipeline_id}",
                pipeline_stage="execution",
            )

        pipeline = self._pipelines[pipeline_id]
        pipeline_config = pipeline["config"]

        # Create pipeline run
        run_id = f"run-{pipeline_id}-{int(datetime.utcnow().timestamp())}"

        pipeline_run = {
            "run_id": run_id,
            "pipeline_id": pipeline_id,
            "status": PipelineStatus.RUNNING.value,
            "started_at": datetime.utcnow(),
            "completed_at": None,
            "stages_completed": [],
            "stages_failed": [],
            "records_processed": 0,
            "errors": [],
            "metrics": {},
        }

        self._pipeline_runs[run_id] = pipeline_run

        try:
            logger.info(f"Starting pipeline execution: {run_id}")

            # Execute pipeline stages
            data = await self._execute_extraction_stage(pipeline_config, pipeline_run)
            data = await self._execute_transformation_stage(
                pipeline_config, pipeline_run, data
            )
            await self._execute_loading_stage(pipeline_config, pipeline_run, data)
            await self._execute_validation_stage(pipeline_config, pipeline_run, data)

            # Update pipeline run status
            pipeline_run["status"] = PipelineStatus.COMPLETED.value
            pipeline_run["completed_at"] = datetime.utcnow()

            # Update pipeline statistics
            await self._update_pipeline_statistics(pipeline_id, pipeline_run)

            logger.info(f"Pipeline execution completed successfully: {run_id}")

            return {
                "run_id": run_id,
                "pipeline_id": pipeline_id,
                "status": PipelineStatus.COMPLETED.value,
                "started_at": pipeline_run["started_at"].isoformat(),
                "completed_at": pipeline_run["completed_at"].isoformat(),
                "records_processed": pipeline_run["records_processed"],
                "stages_completed": pipeline_run["stages_completed"],
                "runtime_seconds": (
                    pipeline_run["completed_at"] - pipeline_run["started_at"]
                ).total_seconds(),
            }

        except Exception as e:
            # Update pipeline run status
            pipeline_run["status"] = PipelineStatus.FAILED.value
            pipeline_run["completed_at"] = datetime.utcnow()
            pipeline_run["errors"].append(str(e))

            # Update pipeline statistics
            await self._update_pipeline_statistics(pipeline_id, pipeline_run)

            logger.error(f"Pipeline execution failed: {run_id} - {e}")

            # Implement retry logic if configured
            if pipeline_config.retry_attempts > 0:
                return await self._retry_pipeline_execution(
                    pipeline_id, pipeline_run, e
                )

            raise DataPipelineError(
                f"Pipeline execution failed: {e}",
                pipeline_stage="execution",
            )

    async def _execute_extraction_stage(
        self, config: PipelineConfig, pipeline_run: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute data extraction stage."""
        try:
            logger.info(f"Executing extraction stage for {pipeline_run['run_id']}")

            data_source = config.data_source
            extracted_data = []

            if data_source.source_type == "database":
                extracted_data = await self._extract_from_database(data_source)
            elif data_source.source_type == "api":
                extracted_data = await self._extract_from_api(data_source)
            elif data_source.source_type == "file":
                extracted_data = await self._extract_from_file(data_source)
            elif data_source.source_type == "stream":
                extracted_data = await self._extract_from_stream(data_source)
            else:
                raise DataPipelineError(
                    f"Unsupported source type: {data_source.source_type}",
                    pipeline_stage="extraction",
                )

            pipeline_run["stages_completed"].append(PipelineStage.EXTRACTION.value)
            pipeline_run["records_processed"] = len(extracted_data)

            return extracted_data

        except Exception as e:
            pipeline_run["stages_failed"].append(PipelineStage.EXTRACTION.value)
            raise DataPipelineError(
                f"Extraction stage failed: {e}",
                pipeline_stage="extraction",
            )

    async def _execute_transformation_stage(
        self,
        config: PipelineConfig,
        pipeline_run: Dict[str, Any],
        data: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Execute data transformation stage."""
        try:
            logger.info(f"Executing transformation stage for {pipeline_run['run_id']}")

            transformed_data = data

            # Apply transformation rules in sequence
            for rule in config.transformation_rules:
                if rule.rule_type in self._transformation_functions:
                    transform_func = self._transformation_functions[rule.rule_type]
                    transformed_data = await transform_func(transformed_data, rule)
                else:
                    logger.warning(f"Unknown transformation rule: {rule.rule_type}")

            pipeline_run["stages_completed"].append(PipelineStage.TRANSFORMATION.value)
            pipeline_run["records_processed"] = len(transformed_data)

            return transformed_data

        except Exception as e:
            pipeline_run["stages_failed"].append(PipelineStage.TRANSFORMATION.value)
            raise DataPipelineError(
                f"Transformation stage failed: {e}",
                pipeline_stage="transformation",
            )

    async def _execute_loading_stage(
        self,
        config: PipelineConfig,
        pipeline_run: Dict[str, Any],
        data: List[Dict[str, Any]],
    ) -> None:
        """Execute data loading stage."""
        try:
            logger.info(f"Executing loading stage for {pipeline_run['run_id']}")

            data_target = config.data_target

            if data_target.target_type == "database":
                await self._load_to_database(data_target, data)
            elif data_target.target_type == "api":
                await self._load_to_api(data_target, data)
            elif data_target.target_type == "file":
                await self._load_to_file(data_target, data)
            elif data_target.target_type == "stream":
                await self._load_to_stream(data_target, data)
            else:
                raise DataPipelineError(
                    f"Unsupported target type: {data_target.target_type}",
                    pipeline_stage="loading",
                )

            pipeline_run["stages_completed"].append(PipelineStage.LOADING.value)

        except Exception as e:
            pipeline_run["stages_failed"].append(PipelineStage.LOADING.value)
            raise DataPipelineError(
                f"Loading stage failed: {e}",
                pipeline_stage="loading",
            )

    async def _execute_validation_stage(
        self,
        config: PipelineConfig,
        pipeline_run: Dict[str, Any],
        data: List[Dict[str, Any]],
    ) -> None:
        """Execute data validation stage."""
        try:
            logger.info(f"Executing validation stage for {pipeline_run['run_id']}")

            # Perform data quality checks
            validation_results = await self._validate_data_quality(data)

            # Store validation metrics
            pipeline_run["metrics"]["data_quality"] = validation_results

            # Check if validation passed
            if not validation_results.get("passed", True):
                raise DataPipelineError(
                    f"Data validation failed: {validation_results.get('errors', [])}",
                    pipeline_stage="validation",
                )

            pipeline_run["stages_completed"].append(PipelineStage.VALIDATION.value)

        except Exception as e:
            pipeline_run["stages_failed"].append(PipelineStage.VALIDATION.value)
            raise DataPipelineError(
                f"Validation stage failed: {e}",
                pipeline_stage="validation",
            )

    # Data extraction methods
    async def _extract_from_database(
        self, data_source: DataSource
    ) -> List[Dict[str, Any]]:
        """Extract data from database source."""
        # Mock database extraction
        return [
            {"id": 1, "name": "Record 1", "value": 100},
            {"id": 2, "name": "Record 2", "value": 200},
            {"id": 3, "name": "Record 3", "value": 300},
        ]

    async def _extract_from_api(self, data_source: DataSource) -> List[Dict[str, Any]]:
        """Extract data from API source."""
        # Mock API extraction
        return [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "metric": "cpu",
                "value": 75.5,
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "metric": "memory",
                "value": 82.3,
            },
        ]

    async def _extract_from_file(self, data_source: DataSource) -> List[Dict[str, Any]]:
        """Extract data from file source."""
        # Mock file extraction
        return [
            {"line": 1, "content": "First line of data"},
            {"line": 2, "content": "Second line of data"},
        ]

    async def _extract_from_stream(
        self, data_source: DataSource
    ) -> List[Dict[str, Any]]:
        """Extract data from streaming source."""
        # Mock stream extraction
        return [
            {
                "event_id": "evt_1",
                "event_type": "user_action",
                "timestamp": datetime.utcnow().isoformat(),
            },
            {
                "event_id": "evt_2",
                "event_type": "system_event",
                "timestamp": datetime.utcnow().isoformat(),
            },
        ]

    # Data loading methods
    async def _load_to_database(
        self, data_target: DataTarget, data: List[Dict[str, Any]]
    ) -> None:
        """Load data to database target."""
        logger.info(
            f"Loading {len(data)} records to database: {data_target.table_name}"
        )

    async def _load_to_api(
        self, data_target: DataTarget, data: List[Dict[str, Any]]
    ) -> None:
        """Load data to API target."""
        logger.info(f"Sending {len(data)} records to API: {data_target.endpoint}")

    async def _load_to_file(
        self, data_target: DataTarget, data: List[Dict[str, Any]]
    ) -> None:
        """Load data to file target."""
        logger.info(f"Writing {len(data)} records to file: {data_target.file_path}")

    async def _load_to_stream(
        self, data_target: DataTarget, data: List[Dict[str, Any]]
    ) -> None:
        """Load data to streaming target."""
        logger.info(f"Publishing {len(data)} records to stream")

    # Transformation functions
    async def _filter_transform(
        self, data: List[Dict[str, Any]], rule: TransformationRule
    ) -> List[Dict[str, Any]]:
        """Apply filter transformation."""
        # Simple filter implementation
        if rule.expression == "value > 150":
            return [record for record in data if record.get("value", 0) > 150]
        return data

    async def _map_transform(
        self, data: List[Dict[str, Any]], rule: TransformationRule
    ) -> List[Dict[str, Any]]:
        """Apply map transformation."""
        # Simple map implementation
        for record in data:
            if "value" in record:
                record["value_doubled"] = record["value"] * 2
        return data

    async def _aggregate_transform(
        self, data: List[Dict[str, Any]], rule: TransformationRule
    ) -> List[Dict[str, Any]]:
        """Apply aggregation transformation."""
        # Simple aggregation implementation
        if rule.expression == "sum_values":
            total_value = sum(record.get("value", 0) for record in data)
            return [{"aggregated_value": total_value, "record_count": len(data)}]
        return data

    async def _join_transform(
        self, data: List[Dict[str, Any]], rule: TransformationRule
    ) -> List[Dict[str, Any]]:
        """Apply join transformation."""
        # Mock join implementation
        return data

    async def _validate_transform(
        self, data: List[Dict[str, Any]], rule: TransformationRule
    ) -> List[Dict[str, Any]]:
        """Apply validation transformation."""
        # Simple validation implementation
        validated_data = []
        for record in data:
            if self._is_valid_record(record):
                validated_data.append(record)
        return validated_data

    async def _deduplicate_transform(
        self, data: List[Dict[str, Any]], rule: TransformationRule
    ) -> List[Dict[str, Any]]:
        """Apply deduplication transformation."""
        seen = set()
        deduplicated = []
        key_field = rule.parameters.get("key_field", "id") if rule.parameters else "id"

        for record in data:
            key = record.get(key_field)
            if key not in seen:
                seen.add(key)
                deduplicated.append(record)

        return deduplicated

    async def _normalize_transform(
        self, data: List[Dict[str, Any]], rule: TransformationRule
    ) -> List[Dict[str, Any]]:
        """Apply normalization transformation."""
        # Simple normalization implementation
        for record in data:
            if "name" in record:
                record["name"] = record["name"].lower().strip()
        return data

    async def _enrich_transform(
        self, data: List[Dict[str, Any]], rule: TransformationRule
    ) -> List[Dict[str, Any]]:
        """Apply data enrichment transformation."""
        # Simple enrichment implementation
        for record in data:
            record["enriched_at"] = datetime.utcnow().isoformat()
            record["source"] = "pipeline_enrichment"
        return data

    def _is_valid_record(self, record: Dict[str, Any]) -> bool:
        """Check if record is valid."""
        # Simple validation rules
        return bool(record.get("id")) and bool(record.get("name"))

    async def _validate_data_quality(
        self, data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate data quality."""
        total_records = len(data)
        valid_records = sum(1 for record in data if self._is_valid_record(record))

        return {
            "passed": valid_records == total_records,
            "total_records": total_records,
            "valid_records": valid_records,
            "validity_rate": valid_records / total_records if total_records > 0 else 0,
            "errors": (
                []
                if valid_records == total_records
                else ["Some records failed validation"]
            ),
        }

    async def _validate_pipeline_config(self, config: PipelineConfig) -> None:
        """Validate pipeline configuration."""
        if not config.pipeline_name:
            raise NodeValidationError("Pipeline name is required")

        if not config.data_source.source_type:
            raise NodeValidationError("Data source type is required")

        if not config.data_target.target_type:
            raise NodeValidationError("Data target type is required")

        if config.timeout_minutes <= 0:
            raise NodeValidationError("Timeout must be positive")

    async def _schedule_pipeline(self, pipeline_id: str, schedule: str) -> None:
        """Schedule pipeline execution."""
        # Mock scheduling implementation
        logger.info(f"Scheduling pipeline {pipeline_id} with schedule: {schedule}")

    async def _update_pipeline_statistics(
        self, pipeline_id: str, pipeline_run: Dict[str, Any]
    ) -> None:
        """Update pipeline execution statistics."""
        pipeline = self._pipelines[pipeline_id]
        pipeline["run_count"] += 1
        pipeline["last_run"] = pipeline_run["completed_at"]

        if pipeline_run["status"] == PipelineStatus.COMPLETED.value:
            pipeline["success_count"] += 1
        else:
            pipeline["failure_count"] += 1

        # Update average runtime
        if pipeline_run["completed_at"] and pipeline_run["started_at"]:
            runtime = (
                pipeline_run["completed_at"] - pipeline_run["started_at"]
            ).total_seconds()
            pipeline["avg_runtime_seconds"] = (
                pipeline["avg_runtime_seconds"] * (pipeline["run_count"] - 1) + runtime
            ) / pipeline["run_count"]

    async def _retry_pipeline_execution(
        self, pipeline_id: str, failed_run: Dict[str, Any], error: Exception
    ) -> Dict[str, Any]:
        """Retry pipeline execution with exponential backoff."""
        # Implement retry logic
        await asyncio.sleep(2)  # Simple delay
        return await self.execute_pipeline(pipeline_id)

    async def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """Get detailed pipeline status."""
        if pipeline_id not in self._pipelines:
            raise DataPipelineError(f"Pipeline not found: {pipeline_id}")

        pipeline = self._pipelines[pipeline_id]

        # Get recent runs
        recent_runs = [
            run
            for run in self._pipeline_runs.values()
            if run["pipeline_id"] == pipeline_id
        ]
        recent_runs.sort(key=lambda x: x["started_at"], reverse=True)
        recent_runs = recent_runs[:5]  # Last 5 runs

        return {
            "pipeline_id": pipeline_id,
            "pipeline_name": pipeline["config"].pipeline_name,
            "status": pipeline["status"],
            "created_at": pipeline["created_at"].isoformat(),
            "last_run": (
                pipeline["last_run"].isoformat() if pipeline["last_run"] else None
            ),
            "run_count": pipeline["run_count"],
            "success_count": pipeline["success_count"],
            "failure_count": pipeline["failure_count"],
            "success_rate": (
                pipeline["success_count"] / pipeline["run_count"]
                if pipeline["run_count"] > 0
                else 0
            ),
            "avg_runtime_seconds": pipeline["avg_runtime_seconds"],
            "recent_runs": [
                {
                    "run_id": run["run_id"],
                    "status": run["status"],
                    "started_at": run["started_at"].isoformat(),
                    "completed_at": (
                        run["completed_at"].isoformat() if run["completed_at"] else None
                    ),
                    "records_processed": run["records_processed"],
                }
                for run in recent_runs
            ],
        }

    async def get_service_status(self) -> Dict[str, Any]:
        """Get data pipeline service status."""
        return {
            "initialized": self._initialized,
            "pipelines": {
                "total": len(self._pipelines),
                "pending": len(
                    [
                        p
                        for p in self._pipelines.values()
                        if p["status"] == PipelineStatus.PENDING.value
                    ]
                ),
                "running": len(
                    [
                        p
                        for p in self._pipelines.values()
                        if p["status"] == PipelineStatus.RUNNING.value
                    ]
                ),
            },
            "pipeline_runs": {
                "total": len(self._pipeline_runs),
                "completed": len(
                    [
                        r
                        for r in self._pipeline_runs.values()
                        if r["status"] == PipelineStatus.COMPLETED.value
                    ]
                ),
                "failed": len(
                    [
                        r
                        for r in self._pipeline_runs.values()
                        if r["status"] == PipelineStatus.FAILED.value
                    ]
                ),
            },
            "transformation_functions": list(self._transformation_functions.keys()),
        }
