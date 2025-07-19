"""
NOVA Biohacking Integration Service.
External integrations for research databases, wearable devices, and biohacking technologies.
"""

import asyncio
import aiohttp
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from core.logging_config import get_logger
from core.redis_pool import get_redis_connection

logger = get_logger(__name__)


class IntegrationType(Enum):
    """Types of external integrations."""

    RESEARCH_DATABASE = "research_database"
    WEARABLE_DEVICE = "wearable_device"
    SUPPLEMENT_DATABASE = "supplement_database"
    GENETIC_SERVICE = "genetic_service"
    BIOMARKER_LAB = "biomarker_lab"
    PROTOCOL_REPOSITORY = "protocol_repository"


@dataclass
class CircuitBreakerState:
    """Circuit breaker state for external services."""

    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    state: str = "closed"  # closed, open, half_open
    timeout_duration: int = 300  # 5 minutes


@dataclass
class IntegrationResponse:
    """Response from external integration."""

    success: bool
    data: Any = None
    error: Optional[str] = None
    response_time: float = 0.0
    source: str = ""


class BiohackingIntegrationService:
    """
    Integration service for NOVA Biohacking Innovator external connections.

    Manages connections to research databases, wearable devices, supplement databases,
    genetic services, and biomarker laboratories with circuit breaker patterns
    for resilience and performance monitoring.
    """

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self._initialize_integrations()

    def _initialize_integrations(self):
        """Initialize integration configurations."""
        # Research database configurations
        self.research_databases = {
            "pubmed": {
                "base_url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
                "timeout": 10,
                "circuit_breaker_threshold": 3,
            },
            "biomarker_db": {
                "base_url": "https://api.biomarker-research.org",
                "timeout": 15,
                "circuit_breaker_threshold": 3,
            },
            "longevity_research": {
                "base_url": "https://api.longevity-database.org",
                "timeout": 12,
                "circuit_breaker_threshold": 3,
            },
        }

        # Wearable device API configurations
        self.wearable_apis = {
            "oura": {
                "base_url": "https://api.ouraring.com/v2",
                "timeout": 8,
                "rate_limit": 1000,  # requests per hour
            },
            "whoop": {
                "base_url": "https://api.prod.whoop.com/developer/v1",
                "timeout": 8,
                "rate_limit": 500,
            },
            "apple_health": {
                "base_url": "https://developer.apple.com/health-fitness",
                "timeout": 10,
                "rate_limit": 1200,
            },
            "garmin": {
                "base_url": "https://healthapi.garmin.com",
                "timeout": 10,
                "rate_limit": 800,
            },
        }

        # Supplement and protocol databases
        self.supplement_apis = {
            "examine": {
                "base_url": "https://api.examine.com",
                "timeout": 12,
                "circuit_breaker_threshold": 3,
            },
            "labdoor": {
                "base_url": "https://api.labdoor.com",
                "timeout": 10,
                "circuit_breaker_threshold": 3,
            },
        }

        # Initialize circuit breakers
        for service_group in [
            self.research_databases,
            self.wearable_apis,
            self.supplement_apis,
        ]:
            for service_name in service_group.keys():
                self.circuit_breakers[service_name] = CircuitBreakerState()

    async def _ensure_session(self):
        """Ensure aiohttp session is available."""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)

    async def close_session(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None

    def _check_circuit_breaker(self, service_name: str) -> bool:
        """Check if circuit breaker allows request."""
        breaker = self.circuit_breakers.get(service_name)
        if not breaker:
            return True

        if breaker.state == "closed":
            return True
        elif breaker.state == "open":
            # Check if timeout period has passed
            if (
                breaker.last_failure_time
                and datetime.utcnow() - breaker.last_failure_time
                > timedelta(seconds=breaker.timeout_duration)
            ):
                breaker.state = "half_open"
                breaker.failure_count = 0
                return True
            return False
        elif breaker.state == "half_open":
            return True

        return False

    def _record_success(self, service_name: str):
        """Record successful request."""
        breaker = self.circuit_breakers.get(service_name)
        if breaker:
            breaker.failure_count = 0
            breaker.state = "closed"
            breaker.last_failure_time = None

    def _record_failure(self, service_name: str):
        """Record failed request."""
        breaker = self.circuit_breakers.get(service_name)
        if breaker:
            breaker.failure_count += 1
            breaker.last_failure_time = datetime.utcnow()

            # Get threshold from configuration
            threshold = 3  # Default threshold
            for service_group in [self.research_databases, self.supplement_apis]:
                if service_name in service_group:
                    threshold = service_group[service_name].get(
                        "circuit_breaker_threshold", 3
                    )
                    break

            if breaker.failure_count >= threshold:
                breaker.state = "open"
                self.logger.warning(
                    f"Circuit breaker opened for service: {service_name}"
                )

    async def search_research_database(
        self, query: str, database: str = "pubmed", filters: Dict[str, Any] = None
    ) -> IntegrationResponse:
        """
        Search research database for biohacking studies.

        Args:
            query: Search query
            database: Database to search
            filters: Additional search filters

        Returns:
            Integration response with research results
        """
        start_time = time.time()

        try:
            if not self._check_circuit_breaker(database):
                return IntegrationResponse(
                    success=False,
                    error=f"Circuit breaker open for {database}",
                    response_time=time.time() - start_time,
                    source=database,
                )

            await self._ensure_session()

            if database == "pubmed":
                return await self._search_pubmed(query, filters, start_time)
            elif database == "biomarker_db":
                return await self._search_biomarker_db(query, filters, start_time)
            else:
                return await self._search_generic_research_db(
                    database, query, filters, start_time
                )

        except Exception as e:
            self._record_failure(database)
            self.logger.error(f"Error searching {database}: {str(e)}")
            return IntegrationResponse(
                success=False,
                error=str(e),
                response_time=time.time() - start_time,
                source=database,
            )

    async def _search_pubmed(
        self, query: str, filters: Dict[str, Any], start_time: float
    ) -> IntegrationResponse:
        """Search PubMed for research articles."""
        try:
            # Build PubMed query
            search_terms = query.replace(" ", "+")

            # Add biohacking-specific filters
            if filters:
                if filters.get("years"):
                    year_filter = f"+AND+{filters['years']}[dp]"
                    search_terms += year_filter
                if filters.get("study_type"):
                    study_filter = f"+AND+{filters['study_type']}[pt]"
                    search_terms += study_filter

            # Add biohacking-relevant MeSH terms
            biohacking_terms = (
                "+AND+(longevity+OR+biohacking+OR+optimization+OR+enhancement)"
            )
            search_terms += biohacking_terms

            url = f"{self.research_databases['pubmed']['base_url']}/esearch.fcgi"
            params = {
                "db": "pubmed",
                "term": search_terms,
                "retmax": 20,
                "retmode": "json",
                "sort": "relevance",
            }

            timeout = self.research_databases["pubmed"]["timeout"]

            async with self.session.get(
                url, params=params, timeout=timeout
            ) as response:
                if response.status == 200:
                    data = await response.json()

                    # Extract article IDs
                    id_list = data.get("esearchresult", {}).get("idlist", [])

                    # Fetch article details
                    articles = await self._fetch_pubmed_details(
                        id_list[:10]
                    )  # Limit to 10 articles

                    self._record_success("pubmed")
                    return IntegrationResponse(
                        success=True,
                        data={
                            "articles": articles,
                            "total_found": len(id_list),
                            "query": query,
                            "database": "pubmed",
                        },
                        response_time=time.time() - start_time,
                        source="pubmed",
                    )
                else:
                    self._record_failure("pubmed")
                    return IntegrationResponse(
                        success=False,
                        error=f"PubMed API error: {response.status}",
                        response_time=time.time() - start_time,
                        source="pubmed",
                    )

        except Exception as e:
            self._record_failure("pubmed")
            raise

    async def _fetch_pubmed_details(self, id_list: List[str]) -> List[Dict[str, Any]]:
        """Fetch detailed article information from PubMed."""
        if not id_list:
            return []

        try:
            ids = ",".join(id_list)
            url = f"{self.research_databases['pubmed']['base_url']}/efetch.fcgi"
            params = {
                "db": "pubmed",
                "id": ids,
                "retmode": "xml",
                "rettype": "abstract",
            }

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    # In a real implementation, you would parse the XML
                    # For now, return mock data structure
                    articles = []
                    for i, article_id in enumerate(id_list):
                        articles.append(
                            {
                                "id": article_id,
                                "title": f"Biohacking Research Article {i+1}",
                                "authors": ["Author A", "Author B"],
                                "journal": "Journal of Biohacking Research",
                                "year": 2023,
                                "abstract": f"Research on biohacking topic related to query. Article ID: {article_id}",
                                "relevance_score": 0.8 - (i * 0.1),
                            }
                        )
                    return articles
                else:
                    self.logger.warning(
                        f"Failed to fetch PubMed details: {response.status}"
                    )
                    return []

        except Exception as e:
            self.logger.error(f"Error fetching PubMed details: {str(e)}")
            return []

    async def _search_biomarker_db(
        self, query: str, filters: Dict[str, Any], start_time: float
    ) -> IntegrationResponse:
        """Search biomarker database."""
        try:
            # Mock biomarker database search
            # In production, this would connect to a real biomarker database

            biomarker_results = [
                {
                    "biomarker": "HbA1c",
                    "category": "metabolic",
                    "optimal_range": "4.5-5.6%",
                    "optimization_protocols": [
                        "intermittent_fasting",
                        "low_carb_diet",
                        "exercise",
                    ],
                    "research_backing": "Strong evidence for diabetes prevention",
                },
                {
                    "biomarker": "Vitamin D",
                    "category": "nutritional",
                    "optimal_range": "40-80 ng/mL",
                    "optimization_protocols": [
                        "sun_exposure",
                        "supplementation",
                        "dietary_sources",
                    ],
                    "research_backing": "Extensive research on immune function and longevity",
                },
            ]

            # Filter results based on query
            filtered_results = [
                result
                for result in biomarker_results
                if query.lower() in result["biomarker"].lower()
                or query.lower() in result["category"].lower()
            ]

            self._record_success("biomarker_db")
            return IntegrationResponse(
                success=True,
                data={
                    "biomarkers": filtered_results,
                    "total_found": len(filtered_results),
                    "query": query,
                    "database": "biomarker_db",
                },
                response_time=time.time() - start_time,
                source="biomarker_db",
            )

        except Exception as e:
            self._record_failure("biomarker_db")
            raise

    async def _search_generic_research_db(
        self, database: str, query: str, filters: Dict[str, Any], start_time: float
    ) -> IntegrationResponse:
        """Search generic research database."""
        try:
            # Mock generic research database
            mock_results = [
                {
                    "title": f"Research on {query} - Advanced Studies",
                    "authors": ["Dr. Research", "Dr. Innovation"],
                    "journal": "Advanced Biohacking Research",
                    "year": 2023,
                    "abstract": f"Comprehensive study on {query} for optimization purposes",
                    "key_findings": [
                        f"{query} shows promising results for human optimization"
                    ],
                    "relevance_score": 0.85,
                }
            ]

            self._record_success(database)
            return IntegrationResponse(
                success=True,
                data={
                    "studies": mock_results,
                    "total_found": len(mock_results),
                    "query": query,
                    "database": database,
                },
                response_time=time.time() - start_time,
                source=database,
            )

        except Exception as e:
            self._record_failure(database)
            raise

    async def fetch_wearable_data(
        self,
        device_type: str,
        user_credentials: Dict[str, str],
        date_range: Dict[str, str] = None,
    ) -> IntegrationResponse:
        """
        Fetch data from wearable devices.

        Args:
            device_type: Type of wearable device
            user_credentials: User authentication credentials
            date_range: Optional date range for data

        Returns:
            Integration response with wearable data
        """
        start_time = time.time()

        try:
            if device_type not in self.wearable_apis:
                return IntegrationResponse(
                    success=False,
                    error=f"Unsupported device type: {device_type}",
                    response_time=time.time() - start_time,
                    source=device_type,
                )

            if not self._check_circuit_breaker(device_type):
                return IntegrationResponse(
                    success=False,
                    error=f"Circuit breaker open for {device_type}",
                    response_time=time.time() - start_time,
                    source=device_type,
                )

            # Mock wearable data fetching
            # In production, this would make real API calls

            mock_data = self._generate_mock_wearable_data(device_type, date_range)

            self._record_success(device_type)
            return IntegrationResponse(
                success=True,
                data=mock_data,
                response_time=time.time() - start_time,
                source=device_type,
            )

        except Exception as e:
            self._record_failure(device_type)
            self.logger.error(f"Error fetching {device_type} data: {str(e)}")
            return IntegrationResponse(
                success=False,
                error=str(e),
                response_time=time.time() - start_time,
                source=device_type,
            )

    def _generate_mock_wearable_data(
        self, device_type: str, date_range: Dict[str, str]
    ) -> Dict[str, Any]:
        """Generate mock wearable data for testing."""
        base_data = {
            "device_type": device_type,
            "data_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "user_id": "test_user",
        }

        if device_type == "oura":
            base_data.update(
                {
                    "sleep_score": 82,
                    "readiness_score": 78,
                    "activity_score": 85,
                    "hrv": 45.2,
                    "resting_heart_rate": 58,
                    "body_temperature": 98.4,
                }
            )
        elif device_type == "whoop":
            base_data.update(
                {
                    "strain_score": 14.2,
                    "recovery_score": 73,
                    "sleep_performance": 85,
                    "hrv": 42.8,
                    "resting_heart_rate": 56,
                }
            )
        elif device_type == "apple_watch":
            base_data.update(
                {
                    "steps": 8542,
                    "heart_rate_avg": 72,
                    "exercise_minutes": 45,
                    "stand_hours": 10,
                    "calories_burned": 2250,
                }
            )

        return base_data

    async def search_supplement_database(
        self, supplement_name: str, research_focus: str = None
    ) -> IntegrationResponse:
        """
        Search supplement databases for research and recommendations.

        Args:
            supplement_name: Name of supplement to research
            research_focus: Specific research focus area

        Returns:
            Integration response with supplement data
        """
        start_time = time.time()

        try:
            # Check circuit breaker for examine.com
            if not self._check_circuit_breaker("examine"):
                return IntegrationResponse(
                    success=False,
                    error="Circuit breaker open for supplement database",
                    response_time=time.time() - start_time,
                    source="examine",
                )

            # Mock supplement database search
            supplement_data = {
                "supplement_name": supplement_name,
                "research_grade": "A",
                "evidence_level": "Strong",
                "primary_effects": [
                    "Cognitive enhancement",
                    "Neuroprotection",
                    "Antioxidant activity",
                ],
                "dosage_recommendations": {
                    "standard": "500mg daily",
                    "therapeutic": "1000mg daily",
                    "timing": "With meals",
                },
                "safety_profile": "Generally safe for healthy adults",
                "interactions": ["May interact with blood thinners"],
                "research_studies": 25,
                "mechanistic_understanding": "High",
                "cost_effectiveness": "Medium",
            }

            self._record_success("examine")
            return IntegrationResponse(
                success=True,
                data=supplement_data,
                response_time=time.time() - start_time,
                source="examine",
            )

        except Exception as e:
            self._record_failure("examine")
            self.logger.error(f"Error searching supplement database: {str(e)}")
            return IntegrationResponse(
                success=False,
                error=str(e),
                response_time=time.time() - start_time,
                source="examine",
            )

    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all integrations."""
        try:
            status = {
                "research_databases": {},
                "wearable_apis": {},
                "supplement_apis": {},
                "circuit_breakers": {},
                "overall_health": "healthy",
            }

            # Check circuit breaker states
            unhealthy_services = 0
            for service_name, breaker in self.circuit_breakers.items():
                status["circuit_breakers"][service_name] = {
                    "state": breaker.state,
                    "failure_count": breaker.failure_count,
                    "last_failure": (
                        breaker.last_failure_time.isoformat()
                        if breaker.last_failure_time
                        else None
                    ),
                }

                if breaker.state == "open":
                    unhealthy_services += 1

            # Determine overall health
            if unhealthy_services > 0:
                if unhealthy_services >= len(self.circuit_breakers) // 2:
                    status["overall_health"] = "degraded"
                else:
                    status["overall_health"] = "warning"

            # Add service configurations
            status["research_databases"] = {
                name: "configured" for name in self.research_databases.keys()
            }
            status["wearable_apis"] = {
                name: "configured" for name in self.wearable_apis.keys()
            }
            status["supplement_apis"] = {
                name: "configured" for name in self.supplement_apis.keys()
            }

            return status

        except Exception as e:
            self.logger.error(f"Error getting integration status: {str(e)}")
            return {"error": str(e), "overall_health": "error"}
