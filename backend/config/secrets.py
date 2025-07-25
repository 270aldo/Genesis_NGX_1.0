"""
Carga y expone credenciales de servicios externos de forma segura.

Este módulo centraliza el acceso a las credenciales y configuraciones sensibles,
cargándolas desde variables de entorno en lugar de almacenarlas en código.

Uso:
    from config.secrets import settings
    gcs_key = settings.GOOGLE_APPLICATION_CREDENTIALS
"""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de credenciales y parámetros de servicios externos."""

    # Gemini / Vertex / Perplexity
    GEMINI_API_KEY: Optional[str] = None
    VERTEX_API_KEY: Optional[str] = None
    PERPLEXITY_API_KEY: Optional[str] = None

    # Google Cloud Storage
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GCS_BUCKET: Optional[str] = None

    # Vertex AI Vector Search
    VERTEX_AI_INDEX_ID: str = "5755708075919015936"
    VERTEX_AI_INDEX_ENDPOINT_ID: str = "9027115808366526464"

    # Supabase
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None

    # Control de reintentos (por servicio)
    MAX_RETRIES: int = 3
    RETRY_BACKOFF: float = 1.5

    # Timeouts (segundos)
    DEFAULT_TIMEOUT: float = 30.0

    class Config:
        """Configuración para cargar variables desde .env"""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignorar campos extra no definidos


@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene la configuración de credenciales con caché LRU.

    Returns:
        Settings: Objeto con las credenciales cargadas desde variables de entorno.
    """
    return Settings()


# Instancia global para uso en toda la aplicación
settings = get_settings()
