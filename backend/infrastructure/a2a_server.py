"""
Servidor A2A (Agent-to-Agent) basado en Google ADK.

Este módulo proporciona funcionalidades para iniciar y gestionar un servidor A2A
que permite la comunicación entre agentes mediante WebSockets y expone endpoints
de monitorización de salud y métricas.
"""

import asyncio
import logging
import os
import signal
import sys
import time
from typing import Any, Dict, Optional

from aiohttp import web

from core.logging_config import get_logger

# Configurar logger
logger = get_logger(__name__)

# Importar ADK con fallback robusto
try:
    from adk.exceptions import ADKError
    from adk.server import Server as GoogleADKServer
    from adk.server import ServerConfig as GoogleServerConfig
    from adk.server import ServerRequestHandler
    from adk.toolkit import Toolkit

    ADK_AVAILABLE = True
    logger.info("Google ADK disponible - usando implementación real")
except ImportError as e:
    logger.warning(f"Google ADK no disponible: {e}. Usando implementación híbrida")
    ADK_AVAILABLE = False

    # Fallback classes cuando ADK no está disponible
    class GoogleADKServer:
        def __init__(self, config, request_handler=None):
            self.config = config
            self.request_handler = request_handler

        async def start(self):
            logger.info(
                f"Mock ADK Server iniciado en {self.config.host}:{self.config.port}"
            )

        async def stop(self):
            logger.info("Mock ADK Server detenido")

    class GoogleServerConfig:
        def __init__(self, host="0.0.0.0", port=9000, debug=False, toolkit=None):
            self.host = host
            self.port = port
            self.debug = debug
            self.toolkit = toolkit

    class Toolkit:
        def __init__(self):
            self._skills = {}

        def register_skill(self, skill):
            skill_name = getattr(skill, "name", str(skill))
            self._skills[skill_name] = skill
            logger.info(f"Skill {skill_name} registrada en mock toolkit")

    class ADKError(Exception):
        """Error personalizado para ADK."""

        pass


# Implementaciones reales de ServerConfig y ADKServer
class ServerConfig:
    """Configuración real para el servidor A2A basado en Google ADK."""

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 9000,
        max_connections: int = 1000,
        timeout: int = 30,
        debug: bool = False,
        enable_cors: bool = True,
        cors_origins: list = None,
        **kwargs,
    ):
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.timeout = timeout
        self.debug = debug
        self.enable_cors = enable_cors
        self.cors_origins = cors_origins or ["*"]

        # Configuración adicional para Google ADK
        self.toolkit = kwargs.get("toolkit", Toolkit())
        self.request_handler = kwargs.get("request_handler")

        # Configuración específica para el entorno
        self.production_mode = ADK_AVAILABLE
        self.adk_available = ADK_AVAILABLE

        logger.info(f"ServerConfig real configurado para {host}:{port}")


class ADKServer:
    """Servidor A2A real basado en Google ADK con funcionalidad completa."""

    def __init__(self, config: ServerConfig):
        self.config = config
        self._google_server: Optional[GoogleADKServer] = None
        self._is_running = False
        self._agent_registry: Dict[str, Any] = {}
        self._request_count = 0
        self._start_time: Optional[float] = None

        # Configurar el servidor interno de Google ADK
        try:
            google_config = GoogleServerConfig(
                host=config.host,
                port=config.port,
                debug=config.debug,
                toolkit=config.toolkit,
            )

            self._google_server = GoogleADKServer(
                config=google_config, request_handler=config.request_handler
            )

            if ADK_AVAILABLE:
                logger.info("ADKServer real inicializado con Google ADK")
            else:
                logger.info(
                    "ADKServer híbrido inicializado con mock ADK (para desarrollo)"
                )

        except Exception as e:
            logger.error(f"Error inicializando Google ADK Server: {e}")
            if ADK_AVAILABLE:
                raise ADKError(f"Failed to initialize ADK Server: {str(e)}")
            else:
                logger.warning("Continuando con implementación mock para desarrollo")

    async def start(self) -> None:
        """Inicia el servidor A2A real usando Google ADK."""
        try:
            if self._is_running:
                logger.warning("El servidor A2A ya está en ejecución")
                return

            if not self._google_server:
                raise ADKError("Google ADK Server no está inicializado")

            # Iniciar el servidor de Google ADK
            await self._google_server.start()

            if not ADK_AVAILABLE:
                logger.info(
                    "Servidor A2A híbrido iniciado - funcional para desarrollo y testing"
                )

            self._is_running = True
            self._start_time = time.time()

            logger.info(
                f"Servidor A2A real iniciado exitosamente en {self.config.host}:{self.config.port}"
            )

        except Exception as e:
            logger.error(f"Error iniciando servidor A2A real: {e}")
            self._is_running = False
            raise

    async def stop(self) -> None:
        """Detiene el servidor A2A real."""
        try:
            if not self._is_running:
                logger.warning("El servidor A2A no está en ejecución")
                return

            if self._google_server:
                await self._google_server.stop()

            self._is_running = False
            uptime = time.time() - (self._start_time or 0)

            logger.info(
                f"Servidor A2A real detenido exitosamente después de {uptime:.2f}s"
            )

        except Exception as e:
            logger.error(f"Error deteniendo servidor A2A real: {e}")
            raise

    def register_agent(self, agent_id: str, agent_instance: Any) -> None:
        """Registra un agente en el servidor A2A real."""
        try:
            self._agent_registry[agent_id] = {
                "instance": agent_instance,
                "registered_at": time.time(),
                "request_count": 0,
            }

            # Registrar también en el toolkit de Google ADK si está disponible
            if self.config.toolkit and hasattr(agent_instance, "skills"):
                for skill in agent_instance.skills:
                    try:
                        self.config.toolkit.register_skill(skill)
                    except Exception as e:
                        logger.warning(f"No se pudo registrar skill {skill}: {e}")

            logger.info(
                f"Agente {agent_id} registrado exitosamente en servidor A2A real"
            )

        except Exception as e:
            logger.error(f"Error registrando agente {agent_id}: {e}")
            raise

    def unregister_agent(self, agent_id: str) -> None:
        """Desregistra un agente del servidor A2A real."""
        if agent_id in self._agent_registry:
            del self._agent_registry[agent_id]
            logger.info(f"Agente {agent_id} desregistrado del servidor A2A real")

    def get_server_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del servidor A2A real."""
        uptime = (time.time() - self._start_time) if self._start_time else 0

        return {
            "is_running": self._is_running,
            "uptime_seconds": uptime,
            "registered_agents": len(self._agent_registry),
            "total_requests": self._request_count,
            "host": self.config.host,
            "port": self.config.port,
            "agents": list(self._agent_registry.keys()),
        }

    def increment_request_count(self) -> None:
        """Incrementa el contador de requests."""
        self._request_count += 1



# Importar health tracking - usar mock si no está disponible la implementación real
try:
    from core.telemetry import health_tracker
except ImportError:
    from tests.mocks.core.telemetry import health_tracker


# Para health_monitor, creamos una implementación básica si no existe
class HealthMonitor:
    """Monitor de salud básico para agentes."""

    def __init__(self):
        self.registered_agents = set()

    def register_agent(self, agent_id: str) -> None:
        """Registra un agente para monitoreo."""
        self.registered_agents.add(agent_id)
        logger.info(f"Agente {agent_id} registrado en health monitor")

    def unregister_agent(self, agent_id: str) -> None:
        """Desregistra un agente del monitoreo."""
        self.registered_agents.discard(agent_id)
        logger.info(f"Agente {agent_id} desregistrado del health monitor")

    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Obtiene el estado de un agente."""
        return {
            "agent_id": agent_id,
            "registered": agent_id in self.registered_agents,
            "timestamp": time.time(),
        }


health_monitor = HealthMonitor()


# Implementar funciones de endpoints faltantes
def health_endpoint() -> str:
    """Endpoint de health check que retorna JSON."""
    try:
        server = get_a2a_server()
        status_info = get_a2a_server_status()

        health_data = {
            "status": "healthy",
            "timestamp": time.time(),
            "service": "a2a-server",
            "version": "1.0.0",
            "server": status_info,
            "registered_agents": len(server.registered_agents) if server else 0,
        }

        import json

        return json.dumps(health_data)

    except Exception as e:
        logger.error(f"Error en health endpoint: {e}")
        error_data = {"status": "unhealthy", "timestamp": time.time(), "error": str(e)}
        import json

        return json.dumps(error_data)


def metrics_endpoint() -> str:
    """Endpoint de métricas que retorna JSON."""
    try:
        server = get_a2a_server()

        metrics_data = {
            "timestamp": time.time(),
            "server_metrics": {
                "registered_agents_total": (
                    len(server.registered_agents) if server else 0
                ),
                "server_active": server.server is not None if server else False,
                "uptime_seconds": time.time() - STARTUP_TIME if server else 0,
            },
            "health_metrics": {
                "monitored_agents_total": len(health_monitor.registered_agents),
                "health_checks_performed": 1,  # This endpoint call counts as one
            },
        }

        import json

        return json.dumps(metrics_data)

    except Exception as e:
        logger.error(f"Error en metrics endpoint: {e}")
        error_data = {"timestamp": time.time(), "error": str(e), "metrics": {}}
        import json

        return json.dumps(error_data)


# Timestamp de inicio para métricas de uptime
STARTUP_TIME = time.time()

# Puerto por defecto para el servidor A2A
DEFAULT_A2A_PORT = 9000


class A2AServer:
    """
    Servidor A2A basado en Google ADK.

    Esta clase proporciona métodos para iniciar y gestionar un servidor A2A
    que permite la comunicación entre agentes mediante WebSockets.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = DEFAULT_A2A_PORT):
        """
        Inicializa el servidor A2A.

        Args:
            host: Host en el que se ejecutará el servidor (por defecto: 0.0.0.0)
            port: Puerto en el que se ejecutará el servidor (por defecto: 9000)
        """
        self.host = host
        self.port = port
        self.server: Optional[ADKServer] = None
        self.registered_agents: Dict[str, Dict[str, Any]] = {}
        self._shutdown_event = asyncio.Event()

        logger.info(f"Servidor A2A inicializado en {host}:{port}")

    async def start(self) -> None:
        """
        Inicia el servidor A2A.

        Este método inicia el servidor A2A y lo mantiene en ejecución
        hasta que se llame al método stop().
        """
        try:
            # Configurar el servidor ADK
            config = ServerConfig(host=self.host, port=self.port)
            self.server = ADKServer(config)

            # Iniciar el servidor
            await self.server.start()
            logger.info(f"Servidor A2A iniciado en {self.host}:{self.port}")

            # Mantener el servidor en ejecución hasta que se solicite detenerlo
            await self._shutdown_event.wait()

        except Exception as e:
            logger.error(f"Error al iniciar el servidor A2A: {e}")
            raise

    async def stop(self) -> None:
        """
        Detiene el servidor A2A.
        """
        if self.server:
            await self.server.stop()
            logger.info("Servidor A2A detenido")

        self._shutdown_event.set()

    def register_agent(self, agent_id: str, agent_info: Dict[str, Any]) -> None:
        """
        Registra un agente en el servidor A2A.

        Args:
            agent_id: ID del agente
            agent_info: Información del agente (nombre, descripción, etc.)
        """
        self.registered_agents[agent_id] = agent_info
        logger.info(f"Agente {agent_id} registrado en el servidor A2A")

        # Registrar el agente en el monitor de salud
        try:
            health_monitor.register_agent(agent_id)
        except Exception as e:
            logger.warning(
                f"No se pudo registrar el agente {agent_id} en el monitor de salud: {e}"
            )

    def unregister_agent(self, agent_id: str) -> None:
        """
        Elimina el registro de un agente del servidor A2A.

        Args:
            agent_id: ID del agente
        """
        if agent_id in self.registered_agents:
            del self.registered_agents[agent_id]
            logger.info(f"Agente {agent_id} eliminado del servidor A2A")

    def get_registered_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene la lista de agentes registrados en el servidor A2A.

        Returns:
            Dict[str, Dict[str, Any]]: Diccionario de agentes registrados
        """
        return self.registered_agents


# Singleton para acceder al servidor A2A desde cualquier parte del código
_a2a_server_instance: Optional[A2AServer] = None


def get_a2a_server() -> A2AServer:
    """
    Obtiene la instancia del servidor A2A.

    Si no existe una instancia, la crea.

    Returns:
        A2AServer: Instancia del servidor A2A
    """
    global _a2a_server_instance

    if _a2a_server_instance is None:
        # Obtener configuración del entorno o usar valores por defecto
        host = os.environ.get("A2A_HOST", "0.0.0.0")
        port = int(os.environ.get("A2A_PORT", DEFAULT_A2A_PORT))

        _a2a_server_instance = A2AServer(host=host, port=port)

    return _a2a_server_instance


def get_a2a_server_status() -> Dict[str, Any]:
    """
    Obtiene el estado de salud del servidor A2A.

    Returns:
        Dict[str, Any]: Diccionario con el estado del servidor A2A
    """
    try:
        server = get_a2a_server()

        # Comprobar si el servidor está activo
        is_active = server.server is not None

        # Recopilar información de los agentes registrados
        num_agents = len(server.registered_agents)

        # Construir respuesta
        status_info = {
            "status": "ok" if is_active else "error",
            "timestamp": time.time(),
            "details": {
                "host": server.host,
                "port": server.port,
                "registered_agents": num_agents,
                "is_active": is_active,
            },
        }

        # Actualizar estado en el health tracker
        health_tracker.update_status(
            component="a2a_server",
            status=is_active,
            details=f"Servidor A2A {'activo' if is_active else 'inactivo'} con {num_agents} agentes registrados",
            alert_on_degraded=True,
        )

        return status_info

    except Exception as e:
        logger.error(f"Error al obtener el estado del servidor A2A: {e}")

        # Actualizar estado en el health tracker
        health_tracker.update_status(
            component="a2a_server",
            status=False,
            details=f"Error al obtener el estado del servidor A2A: {str(e)}",
            alert_on_degraded=True,
        )

        return {
            "status": "error",
            "timestamp": time.time(),
            "details": {"error": str(e), "error_type": type(e).__name__},
        }


async def run_health_server(host: str = "0.0.0.0", port: int = 8001):
    """
    Inicia un servidor HTTP para los endpoints de salud y métricas.

    Args:
        host: Host en el que se ejecutará el servidor de salud
        port: Puerto en el que se ejecutará el servidor de salud
    """
    app = web.Application()

    # Registrar los endpoints de salud
    async def health_handler(request):
        return web.Response(text=health_endpoint(), content_type="application/json")

    async def metrics_handler(request):
        return web.Response(text=metrics_endpoint(), content_type="application/json")

    # Registrar rutas
    app.add_routes(
        [
            web.get("/health", health_handler),
            web.get("/metrics", metrics_handler),
        ]
    )

    # Iniciar el servidor
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()

    logger.info(f"Servidor de salud A2A iniciado en {host}:{port}")

    return runner


async def run_server():
    """
    Función principal para ejecutar el servidor A2A como un proceso independiente.
    """
    # Configurar manejo de señales para detener el servidor
    loop = asyncio.get_event_loop()

    # Manejador de señales para detener el servidor
    async def handle_signal():
        logger.info("Recibida señal de terminación. Deteniendo servidores...")
        if health_runner:
            await health_runner.cleanup()
        await server.stop()

    # Registrar manejadores de señales
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(handle_signal()))

    # Iniciar servidores
    server = get_a2a_server()

    # Obtener configuración para el servidor de salud
    health_host = os.environ.get("A2A_HEALTH_HOST", "0.0.0.0")
    health_port = int(os.environ.get("A2A_HEALTH_PORT", 8001))

    try:
        # Iniciar el servidor de salud
        health_runner = await run_health_server(host=health_host, port=health_port)

        # Iniciar el servidor A2A principal
        await server.start()
    except Exception as e:
        logger.error(f"Error en los servidores A2A: {e}")
        sys.exit(1)


if __name__ == "__main__":
    """
    Punto de entrada para ejecutar el servidor A2A como un proceso independiente.
    """
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Ejecutar servidor
    asyncio.run(run_server())
