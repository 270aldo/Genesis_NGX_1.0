"""
Configuration and fixtures for staging tests.

This module provides common fixtures and configuration for all staging tests,
including real GCP credentials and service connections.
"""

import asyncio
import os
from pathlib import Path
from typing import Any, Dict

import pytest
from dotenv import load_dotenv

# Load staging environment
env_path = Path(__file__).parent.parent.parent / ".env.staging"
load_dotenv(env_path)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def staging_config() -> Dict[str, Any]:
    """Load staging configuration from environment."""
    return {
        "environment": os.getenv("ENVIRONMENT", "staging"),
        "gcp_project_id": os.getenv("GCP_PROJECT_ID"),
        "vertex_location": os.getenv("VERTEX_LOCATION", "us-central1"),
        "vertex_model": os.getenv("VERTEX_MODEL_NAME", "gemini-1.5-flash"),
        "a2a_server_url": os.getenv("A2A_SERVER_URL", "http://localhost:9000"),
        "redis_url": os.getenv("REDIS_URL"),
        "supabase_url": os.getenv("SUPABASE_URL"),
        "supabase_key": os.getenv("SUPABASE_SERVICE_KEY"),
    }


@pytest.fixture(scope="session")
def gcp_credentials():
    """Ensure GCP credentials are available."""
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path or not Path(credentials_path).exists():
        pytest.skip(
            "GCP credentials not found. Please set GOOGLE_APPLICATION_CREDENTIALS"
        )

    return credentials_path


@pytest.fixture
def agent_config() -> Dict[str, Any]:
    """Common configuration for all agents."""
    return {
        "project_id": os.getenv("GCP_PROJECT_ID"),
        "location": os.getenv("VERTEX_LOCATION", "us-central1"),
        "model_name": os.getenv("VERTEX_MODEL_NAME", "gemini-1.5-flash"),
        "max_output_tokens": int(os.getenv("VERTEX_MAX_OUTPUT_TOKENS", "8192")),
        "temperature": float(os.getenv("VERTEX_TEMPERATURE", "0.7")),
        "top_p": float(os.getenv("VERTEX_TOP_P", "0.95")),
        "top_k": int(os.getenv("VERTEX_TOP_K", "40")),
        "timeout": int(os.getenv("AGENT_REQUEST_TIMEOUT", "30")),
    }


@pytest.fixture
def performance_thresholds() -> Dict[str, float]:
    """Performance thresholds for staging tests."""
    return {
        "simple_response_time": 3.0,  # seconds
        "complex_response_time": 5.0,  # seconds
        "a2a_overhead": 0.1,  # seconds
        "multi_agent_flow": 10.0,  # seconds
        "streaming_first_token": 1.0,  # seconds
        "error_rate": 0.001,  # 0.1%
        "availability": 0.999,  # 99.9%
    }


@pytest.fixture
async def verify_gcp_connection(staging_config):
    """Verify GCP connection is working."""
    try:
        import google.cloud.aiplatform as aiplatform

        aiplatform.init(
            project=staging_config["gcp_project_id"],
            location=staging_config["vertex_location"],
        )

        # Try to list models to verify connection
        _ = aiplatform.Model.list(limit=1)
        return True
    except Exception as e:
        pytest.fail(f"Failed to connect to GCP: {e}")


@pytest.fixture
async def verify_redis_connection(staging_config):
    """Verify Redis connection is working."""
    if not staging_config.get("redis_url"):
        pytest.skip("Redis URL not configured")

    try:
        import redis.asyncio as redis

        client = redis.from_url(staging_config["redis_url"])
        await client.ping()
        await client.close()
        return True
    except Exception as e:
        pytest.fail(f"Failed to connect to Redis: {e}")


@pytest.fixture
async def verify_supabase_connection(staging_config):
    """Verify Supabase connection is working."""
    if not staging_config.get("supabase_url") or not staging_config.get("supabase_key"):
        pytest.skip("Supabase credentials not configured")

    try:
        from supabase import create_client

        client = create_client(
            staging_config["supabase_url"], staging_config["supabase_key"]
        )

        # Try a simple query to verify connection
        _ = await client.table("agents").select("id").limit(1).execute()
        return True
    except Exception as e:
        pytest.fail(f"Failed to connect to Supabase: {e}")


@pytest.fixture
def test_prompts() -> Dict[str, Dict[str, str]]:
    """Test prompts for each agent."""
    return {
        "orchestrator": {
            "simple": "¿Cómo puedo mejorar mi condición física?",
            "complex": "Necesito un plan completo de fitness y nutrición para perder 10kg en 3 meses",
            "edge_case": "No sé qué hacer, ayúdame",
        },
        "elite_training": {
            "simple": "Dame un ejercicio para piernas",
            "complex": "Crea un plan de entrenamiento de 12 semanas para maratón",
            "edge_case": "Tengo dolor en la rodilla derecha, ¿qué ejercicios puedo hacer?",
        },
        "nutrition": {
            "simple": "¿Qué debo comer después de entrenar?",
            "complex": "Diseña un plan nutricional vegano de 2500 calorías para ganar masa muscular",
            "edge_case": "Soy alérgico a todo, ¿qué como?",
        },
        "genetic": {
            "simple": "¿Qué es el gen ACTN3?",
            "complex": "Analiza cómo mi genotipo AA en ACTN3 afecta mi entrenamiento",
            "edge_case": "¿Puedo cambiar mis genes con ejercicio?",
        },
        "analytics": {
            "simple": "¿Cuál es mi progreso esta semana?",
            "complex": "Analiza mis métricas de los últimos 3 meses y proyecta mi rendimiento",
            "edge_case": "No tengo datos, ¿qué hago?",
        },
        "wellness": {
            "simple": "¿Cómo afecta el ciclo menstrual al entrenamiento?",
            "complex": "Crea un plan de wellness considerando mi embarazo de 5 meses",
            "edge_case": "Tengo 60 años y estoy en menopausia, ¿puedo hacer pesas?",
        },
        "progress": {
            "simple": "¿Cuánto he mejorado este mes?",
            "complex": "Compara mi progreso actual con mis objetivos anuales",
            "edge_case": "No veo progreso, ¿qué está mal?",
        },
        "motivation": {
            "simple": "Necesito motivación para entrenar hoy",
            "complex": "Ayúdame a crear hábitos duraderos de ejercicio y alimentación",
            "edge_case": "Odio el ejercicio pero quiero estar saludable",
        },
        "biohacking": {
            "simple": "¿Qué suplementos recomiendas para energía?",
            "complex": "Diseña un protocolo de biohacking para optimizar mi sueño y recuperación",
            "edge_case": "Quiero vivir 150 años, ¿cómo empiezo?",
        },
        "guardian": {
            "simple": "¿Mis datos están seguros?",
            "complex": "Audita el cumplimiento GDPR de mi información genética",
            "edge_case": "Alguien hackeó mi cuenta, ¿qué hago?",
        },
        "node": {
            "simple": "Conecta mi Garmin",
            "complex": "Sincroniza todos mis dispositivos y crea un dashboard unificado",
            "edge_case": "Mi dispositivo no es compatible, ¿hay alternativas?",
        },
    }


@pytest.fixture
def expected_response_patterns() -> Dict[str, Dict[str, Any]]:
    """Expected response patterns for validation."""
    return {
        "greeting": ["hola", "bienvenid", "gusto", "ayudar"],
        "training": ["ejercicio", "entrenamiento", "serie", "repeticion", "descanso"],
        "nutrition": ["caloria", "proteina", "carbohidrato", "grasa", "macro"],
        "safety": ["segur", "cuidado", "consult", "medico", "precaucion"],
        "motivation": ["puedes", "lograr", "objetivo", "excelente", "progreso"],
    }


@pytest.fixture
def metrics_collector():
    """Collect metrics during tests."""

    class MetricsCollector:
        def __init__(self):
            self.response_times = []
            self.error_count = 0
            self.success_count = 0
            self.tokens_used = 0

        def record_response(self, agent: str, time: float, tokens: int = 0):
            self.response_times.append({"agent": agent, "time": time, "tokens": tokens})
            self.success_count += 1
            self.tokens_used += tokens

        def record_error(self, agent: str, error: str):
            self.error_count += 1

        def get_summary(self) -> Dict[str, Any]:
            if not self.response_times:
                return {"error": "No data collected"}

            times = [r["time"] for r in self.response_times]
            return {
                "total_requests": self.success_count + self.error_count,
                "success_rate": (
                    self.success_count / (self.success_count + self.error_count)
                    if (self.success_count + self.error_count) > 0
                    else 0
                ),
                "avg_response_time": sum(times) / len(times) if times else 0,
                "max_response_time": max(times) if times else 0,
                "min_response_time": min(times) if times else 0,
                "total_tokens": self.tokens_used,
                "errors": self.error_count,
            }

    return MetricsCollector()


# Markers for test categorization
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "staging: mark test as staging environment test")
    config.addinivalue_line("markers", "agent: mark test as agent-specific test")
    config.addinivalue_line(
        "markers", "interaction: mark test as agent interaction test"
    )
    config.addinivalue_line("markers", "e2e: mark test as end-to-end test")
    config.addinivalue_line("markers", "performance: mark test as performance test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line(
        "markers", "requires_gcp: mark test as requiring GCP connection"
    )
    config.addinivalue_line(
        "markers", "requires_redis: mark test as requiring Redis connection"
    )
    config.addinivalue_line(
        "markers", "requires_supabase: mark test as requiring Supabase connection"
    )
