"""
Configuración global de credenciales de Google Cloud para NGX Agents.

Este módulo centraliza la configuración de credenciales de Google Cloud
para que estén disponibles en toda la aplicación.
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class GoogleCredentialsManager:
    """
    Gestor centralizado de credenciales de Google Cloud.

    Asegura que las credenciales estén disponibles globalmente
    en toda la aplicación NGX Agents.
    """

    _instance = None
    _credentials_path: Optional[str] = None
    _project_id: Optional[str] = None
    _location: Optional[str] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(
        self,
        credentials_path: Optional[str] = None,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
    ) -> bool:
        """
        Inicializa las credenciales de Google Cloud.

        Args:
            credentials_path: Ruta al archivo de credenciales JSON
            project_id: ID del proyecto de Google Cloud
            location: Ubicación/región de Google Cloud

        Returns:
            bool: True si se inicializó correctamente
        """
        try:
            # Configurar credenciales desde parámetros o variables de entorno
            self._credentials_path = (
                credentials_path
                or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                or "/Users/aldoolivas/ngx-agents01/prototipo/credentials.json"
            )

            self._project_id = (
                project_id
                or os.getenv("GCP_PROJECT_ID")
                or os.getenv("VERTEX_PROJECT_ID")
                or "agentes-ngx"
            )

            self._location = (
                location
                or os.getenv("VERTEX_LOCATION")
                or os.getenv("GCP_REGION")
                or "us-central1"
            )

            # Verificar que el archivo de credenciales existe
            if not Path(self._credentials_path).exists():
                raise FileNotFoundError(
                    f"Credentials file not found: {self._credentials_path}"
                )

            # Configurar variable de entorno global
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self._credentials_path
            os.environ["GCP_PROJECT_ID"] = self._project_id
            os.environ["VERTEX_PROJECT_ID"] = self._project_id
            os.environ["VERTEX_LOCATION"] = self._location
            os.environ["GCS_BUCKET_NAME"] = "agents_ngx"
            os.environ["GCS_BUCKET_LOCATION"] = "us"

            # Inicializar Vertex AI globalmente
            try:
                import vertexai

                vertexai.init(project=self._project_id, location=self._location)
                logger.info(
                    f"Vertex AI initialized for project {self._project_id} in {self._location}"
                )
            except ImportError:
                logger.warning("Vertex AI not available - running in mock mode")
            except Exception as e:
                logger.error(f"Error initializing Vertex AI: {e}")
                return False

            self._initialized = True
            logger.info("Google Cloud credentials configured successfully")
            return True

        except Exception as e:
            logger.error(f"Error initializing Google credentials: {e}")
            return False

    @property
    def credentials_path(self) -> Optional[str]:
        """Ruta al archivo de credenciales."""
        return self._credentials_path

    @property
    def project_id(self) -> Optional[str]:
        """ID del proyecto de Google Cloud."""
        return self._project_id

    @property
    def location(self) -> Optional[str]:
        """Ubicación/región de Google Cloud."""
        return self._location

    @property
    def is_initialized(self) -> bool:
        """Indica si las credenciales están inicializadas."""
        return self._initialized

    def get_config(self) -> dict:
        """
        Obtiene la configuración actual de credenciales.

        Returns:
            dict: Configuración de credenciales
        """
        return {
            "credentials_path": self._credentials_path,
            "project_id": self._project_id,
            "location": self._location,
            "initialized": self._initialized,
            "env_vars": {
                "GOOGLE_APPLICATION_CREDENTIALS": os.getenv(
                    "GOOGLE_APPLICATION_CREDENTIALS"
                ),
                "GCP_PROJECT_ID": os.getenv("GCP_PROJECT_ID"),
                "VERTEX_PROJECT_ID": os.getenv("VERTEX_PROJECT_ID"),
                "VERTEX_LOCATION": os.getenv("VERTEX_LOCATION"),
            },
        }

    def ensure_initialized(self) -> bool:
        """
        Asegura que las credenciales estén inicializadas.

        Returns:
            bool: True si están inicializadas o se inicializaron correctamente
        """
        if not self._initialized:
            return self.initialize()
        return True


# Instancia global del gestor de credenciales
google_credentials = GoogleCredentialsManager()


def init_google_credentials() -> bool:
    """
    Función de conveniencia para inicializar credenciales.

    Returns:
        bool: True si se inicializó correctamente
    """
    return google_credentials.initialize()


def get_google_config() -> dict:
    """
    Obtiene la configuración actual de Google Cloud.

    Returns:
        dict: Configuración de credenciales
    """
    google_credentials.ensure_initialized()
    return google_credentials.get_config()
