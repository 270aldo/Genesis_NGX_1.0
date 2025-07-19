"""
NOVA Biohacking Data Service.
Data management for biohacking protocols, research, biomarkers, and wearable analysis.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

from core.logging_config import get_logger
from core.redis_pool import get_redis_connection

logger = get_logger(__name__)


class DataType(Enum):
    """Types of biohacking data."""

    BIOMARKER = "biomarker"
    WEARABLE = "wearable"
    PROTOCOL = "protocol"
    RESEARCH = "research"
    SUPPLEMENT = "supplement"
    ANALYSIS = "analysis"


@dataclass
class BiohackingDataEntry:
    """Data entry for biohacking information."""

    user_id: str
    data_type: DataType
    content: Dict[str, Any]
    timestamp: datetime
    tags: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ResearchEntry:
    """Research entry for biohacking protocols."""

    title: str
    authors: List[str]
    journal: str
    year: int
    doi: Optional[str] = None
    abstract: Optional[str] = None
    key_findings: List[str] = None
    relevance_score: float = 0.0

    def __post_init__(self):
        if self.key_findings is None:
            self.key_findings = []


@dataclass
class ProtocolEntry:
    """Protocol entry for biohacking interventions."""

    protocol_id: str
    name: str
    category: str
    description: str
    steps: List[Dict[str, Any]]
    duration: str
    difficulty: str
    safety_rating: float
    research_citations: List[str] = None
    contraindications: List[str] = None

    def __post_init__(self):
        if self.research_citations is None:
            self.research_citations = []
        if self.contraindications is None:
            self.contraindications = []


class BiohackingDataService:
    """
    Data service for NOVA Biohacking Innovator operations.

    Manages storage, retrieval, and analysis of biohacking data including
    biomarkers, wearable data, protocols, research citations, and user analyses.
    """

    def __init__(self, cache_ttl_seconds: int = 1800, max_cache_size: int = 200):
        self.logger = get_logger(self.__class__.__name__)
        self.cache_ttl = cache_ttl_seconds
        self.max_cache_size = max_cache_size
        self._initialize_data_patterns()

    def _initialize_data_patterns(self):
        """Initialize data processing patterns."""
        self.biomarker_categories = {
            "metabolic": ["glucose", "insulin", "hba1c", "lipids", "ketones"],
            "hormonal": [
                "testosterone",
                "cortisol",
                "growth_hormone",
                "thyroid",
                "melatonin",
            ],
            "inflammatory": ["crp", "esr", "il6", "tnf_alpha", "cytokines"],
            "cardiovascular": ["blood_pressure", "resting_hr", "hrv", "cholesterol"],
            "nutritional": ["vitamin_d", "b12", "iron", "magnesium", "omega3"],
            "aging": ["telomere_length", "biological_age", "nad", "sirtuins"],
            "neurological": ["neurotransmitters", "bdnf", "acetylcholine", "dopamine"],
        }

        self.wearable_metrics = {
            "oura": ["sleep_score", "readiness", "activity", "hrv", "temperature"],
            "whoop": ["strain", "recovery", "sleep_performance", "hrv", "rhr"],
            "apple_watch": ["heart_rate", "steps", "exercise_minutes", "stand_hours"],
            "garmin": ["stress_score", "body_battery", "vo2_max", "training_load"],
            "cgm": ["glucose_levels", "glucose_variability", "time_in_range"],
        }

    def store_biohacking_data(
        self,
        user_id: str,
        data_type: DataType,
        content: Dict[str, Any],
        tags: List[str] = None,
    ) -> str:
        """
        Store biohacking data entry.

        Args:
            user_id: User identifier
            data_type: Type of biohacking data
            content: Data content
            tags: Optional tags for categorization

        Returns:
            Data entry ID
        """
        try:
            entry = BiohackingDataEntry(
                user_id=user_id,
                data_type=data_type,
                content=content,
                timestamp=datetime.utcnow(),
                tags=tags or [],
                metadata={"source": "nova_agent", "version": "2.0.0-A+"},
            )

            # Generate entry ID
            entry_id = f"{data_type.value}_{user_id}_{int(entry.timestamp.timestamp())}"

            # Store in cache
            cache_key = f"biohacking_data:{entry_id}"
            entry_data = asdict(entry)
            entry_data["timestamp"] = entry.timestamp.isoformat()

            try:
                with get_redis_connection() as redis_client:
                    redis_client.setex(
                        cache_key, self.cache_ttl, json.dumps(entry_data)
                    )

                    # Add to user's data index
                    user_index_key = f"user_data_index:{user_id}"
                    redis_client.lpush(user_index_key, entry_id)
                    redis_client.expire(user_index_key, 7 * 24 * 3600)  # 7 days

            except Exception as redis_error:
                self.logger.warning(
                    f"Failed to cache biohacking data: {str(redis_error)}"
                )

            self.logger.info(f"Stored biohacking data entry: {entry_id}")
            return entry_id

        except Exception as e:
            self.logger.error(f"Error storing biohacking data: {str(e)}")
            raise

    def retrieve_biohacking_data(
        self,
        user_id: str,
        data_type: DataType = None,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 50,
    ) -> List[BiohackingDataEntry]:
        """
        Retrieve biohacking data entries.

        Args:
            user_id: User identifier
            data_type: Optional data type filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of entries to return

        Returns:
            List of biohacking data entries
        """
        try:
            entries = []

            # Get user's data index
            user_index_key = f"user_data_index:{user_id}"

            try:
                with get_redis_connection() as redis_client:
                    entry_ids = redis_client.lrange(user_index_key, 0, limit - 1)

                    for entry_id in entry_ids:
                        if isinstance(entry_id, bytes):
                            entry_id = entry_id.decode("utf-8")

                        # Apply data type filter
                        if data_type and not entry_id.startswith(data_type.value):
                            continue

                        cache_key = f"biohacking_data:{entry_id}"
                        entry_data = redis_client.get(cache_key)

                        if entry_data:
                            if isinstance(entry_data, bytes):
                                entry_data = entry_data.decode("utf-8")

                            parsed_data = json.loads(entry_data)

                            # Convert timestamp back to datetime
                            parsed_data["timestamp"] = datetime.fromisoformat(
                                parsed_data["timestamp"]
                            )
                            parsed_data["data_type"] = DataType(
                                parsed_data["data_type"]
                            )

                            entry = BiohackingDataEntry(**parsed_data)

                            # Apply date filters
                            if start_date and entry.timestamp < start_date:
                                continue
                            if end_date and entry.timestamp > end_date:
                                continue

                            entries.append(entry)

            except Exception as redis_error:
                self.logger.warning(
                    f"Failed to retrieve data from cache: {str(redis_error)}"
                )

            # Sort by timestamp (newest first)
            entries.sort(key=lambda x: x.timestamp, reverse=True)

            self.logger.info(
                f"Retrieved {len(entries)} biohacking data entries for user {user_id}"
            )
            return entries[:limit]

        except Exception as e:
            self.logger.error(f"Error retrieving biohacking data: {str(e)}")
            return []

    def analyze_biomarker_patterns(
        self, user_id: str, analysis_type: str
    ) -> Dict[str, Any]:
        """
        Analyze biomarker patterns for optimization insights.

        Args:
            user_id: User identifier
            analysis_type: Type of analysis to perform

        Returns:
            Analysis results with patterns and insights
        """
        try:
            # Retrieve biomarker data
            biomarker_data = self.retrieve_biohacking_data(
                user_id=user_id,
                data_type=DataType.BIOMARKER,
                start_date=datetime.utcnow() - timedelta(days=180),  # 6 months
            )

            if not biomarker_data:
                return {
                    "analysis_type": analysis_type,
                    "data_points": 0,
                    "patterns": [],
                    "insights": ["No biomarker data available for analysis"],
                    "recommendations": [
                        "Start collecting biomarker data to enable analysis"
                    ],
                }

            analysis_results = {
                "analysis_type": analysis_type,
                "data_points": len(biomarker_data),
                "date_range": {
                    "start": min(
                        entry.timestamp for entry in biomarker_data
                    ).isoformat(),
                    "end": max(entry.timestamp for entry in biomarker_data).isoformat(),
                },
                "patterns": [],
                "insights": [],
                "recommendations": [],
            }

            # Categorize biomarkers
            categorized_data = self._categorize_biomarkers(biomarker_data)

            # Perform specific analysis
            if analysis_type == "optimization_opportunities":
                analysis_results.update(
                    self._analyze_optimization_opportunities(categorized_data)
                )
            elif analysis_type == "trend_analysis":
                analysis_results.update(
                    self._analyze_biomarker_trends(categorized_data)
                )
            elif analysis_type == "correlations":
                analysis_results.update(
                    self._analyze_biomarker_correlations(categorized_data)
                )
            elif analysis_type == "risk_assessment":
                analysis_results.update(self._analyze_biomarker_risks(categorized_data))
            else:
                analysis_results.update(
                    self._perform_general_analysis(categorized_data)
                )

            return analysis_results

        except Exception as e:
            self.logger.error(f"Error analyzing biomarker patterns: {str(e)}")
            return {
                "analysis_type": analysis_type,
                "error": f"Analysis failed: {str(e)}",
                "patterns": [],
                "insights": [],
                "recommendations": [],
            }

    def _categorize_biomarkers(
        self, biomarker_data: List[BiohackingDataEntry]
    ) -> Dict[str, List]:
        """Categorize biomarkers by type."""
        categorized = {category: [] for category in self.biomarker_categories.keys()}
        categorized["uncategorized"] = []

        for entry in biomarker_data:
            biomarker_name = entry.content.get("name", "").lower()
            categorized_flag = False

            for category, markers in self.biomarker_categories.items():
                if any(marker in biomarker_name for marker in markers):
                    categorized[category].append(entry)
                    categorized_flag = True
                    break

            if not categorized_flag:
                categorized["uncategorized"].append(entry)

        return categorized

    def _analyze_optimization_opportunities(
        self, categorized_data: Dict[str, List]
    ) -> Dict[str, Any]:
        """Analyze optimization opportunities from biomarker data."""
        opportunities = []
        insights = []
        recommendations = []

        for category, entries in categorized_data.items():
            if not entries:
                continue

            # Analyze category-specific opportunities
            if category == "metabolic" and len(entries) >= 2:
                opportunities.append(
                    f"Metabolic optimization potential detected with {len(entries)} data points"
                )
                insights.append(
                    "Consistent metabolic tracking enables precision optimization"
                )
                recommendations.append(
                    "Consider adding continuous glucose monitoring for real-time feedback"
                )

            elif category == "hormonal" and len(entries) >= 2:
                opportunities.append(
                    f"Hormonal optimization opportunities with {len(entries)} measurements"
                )
                insights.append(
                    "Hormonal patterns show potential for targeted interventions"
                )
                recommendations.append(
                    "Implement circadian optimization protocols for hormonal balance"
                )

            elif category == "inflammatory" and len(entries) >= 1:
                opportunities.append(
                    f"Inflammatory status monitoring with {len(entries)} markers"
                )
                insights.append(
                    "Inflammation markers guide recovery and longevity protocols"
                )
                recommendations.append(
                    "Add anti-inflammatory interventions based on marker trends"
                )

        return {
            "optimization_opportunities": opportunities,
            "insights": insights,
            "recommendations": recommendations,
        }

    def _analyze_biomarker_trends(
        self, categorized_data: Dict[str, List]
    ) -> Dict[str, Any]:
        """Analyze trends in biomarker data."""
        trends = []
        insights = []

        for category, entries in categorized_data.items():
            if len(entries) < 2:
                continue

            # Sort by timestamp
            entries.sort(key=lambda x: x.timestamp)

            # Basic trend analysis
            if len(entries) >= 3:
                trends.append(
                    f"{category.title()} biomarkers: {len(entries)} measurements over time"
                )
                insights.append(
                    f"Sufficient data for {category} trend analysis and optimization"
                )

        return {"trends": trends, "trend_insights": insights}

    def _analyze_biomarker_correlations(
        self, categorized_data: Dict[str, List]
    ) -> Dict[str, Any]:
        """Analyze correlations between biomarker categories."""
        correlations = []

        active_categories = [
            cat for cat, entries in categorized_data.items() if entries
        ]

        if len(active_categories) >= 2:
            correlations.append(
                f"Multi-system tracking across {len(active_categories)} biomarker categories"
            )
            correlations.append(
                "Cross-category analysis enables comprehensive optimization"
            )

        return {"correlations": correlations}

    def _analyze_biomarker_risks(
        self, categorized_data: Dict[str, List]
    ) -> Dict[str, Any]:
        """Analyze potential risks from biomarker data."""
        risk_factors = []

        for category, entries in categorized_data.items():
            if entries:
                risk_factors.append(
                    f"{category.title()} monitoring enables proactive risk management"
                )

        return {"risk_factors": risk_factors}

    def _perform_general_analysis(
        self, categorized_data: Dict[str, List]
    ) -> Dict[str, Any]:
        """Perform general biomarker analysis."""
        total_entries = sum(len(entries) for entries in categorized_data.values())
        active_categories = [
            cat for cat, entries in categorized_data.items() if entries
        ]

        return {
            "general_insights": [
                f"Total biomarker measurements: {total_entries}",
                f"Active tracking categories: {len(active_categories)}",
                "Consistent biomarker tracking enables personalized optimization",
            ]
        }

    def store_research_entry(self, research: ResearchEntry) -> str:
        """Store research entry for protocol development."""
        try:
            research_id = f"research_{research.year}_{hash(research.title)}_{int(datetime.utcnow().timestamp())}"

            # Store in cache
            cache_key = f"research_entry:{research_id}"
            research_data = asdict(research)

            try:
                with get_redis_connection() as redis_client:
                    redis_client.setex(
                        cache_key,
                        self.cache_ttl * 2,  # Research data cached longer
                        json.dumps(research_data),
                    )

                    # Add to research index
                    research_index_key = (
                        f"research_index:{research.journal.lower().replace(' ', '_')}"
                    )
                    redis_client.lpush(research_index_key, research_id)
                    redis_client.expire(research_index_key, 30 * 24 * 3600)  # 30 days

            except Exception as redis_error:
                self.logger.warning(
                    f"Failed to cache research entry: {str(redis_error)}"
                )

            self.logger.info(f"Stored research entry: {research_id}")
            return research_id

        except Exception as e:
            self.logger.error(f"Error storing research entry: {str(e)}")
            raise

    def store_protocol_entry(self, protocol: ProtocolEntry) -> str:
        """Store biohacking protocol entry."""
        try:
            # Store in cache
            cache_key = f"protocol_entry:{protocol.protocol_id}"
            protocol_data = asdict(protocol)

            try:
                with get_redis_connection() as redis_client:
                    redis_client.setex(
                        cache_key,
                        self.cache_ttl * 3,  # Protocol data cached longest
                        json.dumps(protocol_data),
                    )

                    # Add to protocol category index
                    category_index_key = (
                        f"protocol_category:{protocol.category.lower()}"
                    )
                    redis_client.lpush(category_index_key, protocol.protocol_id)
                    redis_client.expire(category_index_key, 30 * 24 * 3600)  # 30 days

            except Exception as redis_error:
                self.logger.warning(
                    f"Failed to cache protocol entry: {str(redis_error)}"
                )

            self.logger.info(f"Stored protocol entry: {protocol.protocol_id}")
            return protocol.protocol_id

        except Exception as e:
            self.logger.error(f"Error storing protocol entry: {str(e)}")
            raise

    def get_service_statistics(self) -> Dict[str, Any]:
        """Get biohacking data service statistics."""
        try:
            stats = {
                "cache_ttl_seconds": self.cache_ttl,
                "max_cache_size": self.max_cache_size,
                "supported_data_types": [dt.value for dt in DataType],
                "biomarker_categories": list(self.biomarker_categories.keys()),
                "wearable_devices": list(self.wearable_metrics.keys()),
                "service_status": "operational",
            }

            # Get cache statistics if available
            try:
                with get_redis_connection() as redis_client:
                    info = redis_client.info("memory")
                    stats["cache_memory_usage"] = info.get(
                        "used_memory_human", "unknown"
                    )

            except Exception:
                stats["cache_memory_usage"] = "unavailable"

            return stats

        except Exception as e:
            self.logger.error(f"Error getting service statistics: {str(e)}")
            return {"error": str(e)}
