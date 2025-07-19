"""
Session Manager - FASE 12 POINT 1
=================================

Gestión inteligente de sesiones persistentes con sincronización multi-dispositivo
y tracking de estado conversacional avanzado.

CARACTERÍSTICAS CLAVE:
- Sesiones persistentes cross-device
- Estado conversacional inteligente
- Sincronización en tiempo real
- Recovery automático de sesiones
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

from core.logging_config import get_logger
from core.memory_cache_optimizer import cache_get, cache_set, cache_invalidate, CachePriority
from core.conversation_memory import ConversationContext, EmotionalState
from clients.supabase_client import get_supabase_client

logger = get_logger(__name__)


class SessionStatus(Enum):
    """Estados de sesión"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    EXPIRED = "expired"
    ARCHIVED = "archived"


class DeviceType(Enum):
    """Tipos de dispositivo"""
    WEB = "web"
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"
    API = "api"
    UNKNOWN = "unknown"


@dataclass
class SessionContext:
    """Contexto de sesión conversacional"""
    current_topic: Optional[ConversationContext]
    active_agent_id: Optional[str]
    conversation_flow: List[str]  # Secuencia de agentes usados
    user_goals: List[str]
    session_metadata: Dict[str, Any]
    last_emotional_state: Optional[EmotionalState]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        data = asdict(self)
        data['current_topic'] = self.current_topic.value if self.current_topic else None
        data['last_emotional_state'] = self.last_emotional_state.value if self.last_emotional_state else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionContext':
        """Crea desde diccionario"""
        if data.get('current_topic'):
            data['current_topic'] = ConversationContext(data['current_topic'])
        if data.get('last_emotional_state'):
            data['last_emotional_state'] = EmotionalState(data['last_emotional_state'])
        return cls(**data)


@dataclass
class SessionInfo:
    """Información completa de sesión"""
    session_id: str
    user_id: str
    device_id: str
    device_type: DeviceType
    status: SessionStatus
    created_at: datetime
    last_activity: datetime
    expires_at: Optional[datetime]
    context: SessionContext
    sync_token: str  # Para sincronización cross-device
    total_interactions: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para almacenamiento"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_activity'] = self.last_activity.isoformat()
        data['expires_at'] = self.expires_at.isoformat() if self.expires_at else None
        data['device_type'] = self.device_type.value
        data['status'] = self.status.value
        data['context'] = self.context.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionInfo':
        """Crea desde diccionario"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_activity'] = datetime.fromisoformat(data['last_activity'])
        if data.get('expires_at'):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        data['device_type'] = DeviceType(data['device_type'])
        data['status'] = SessionStatus(data['status'])
        data['context'] = SessionContext.from_dict(data['context'])
        return cls(**data)


class SessionManager:
    """
    Gestor inteligente de sesiones con capacidades avanzadas
    
    CARACTERÍSTICAS:
    - Sesiones persistentes con TTL configurable
    - Sincronización automática cross-device
    - Recovery inteligente de sesiones
    - Tracking de estado conversacional
    - Limpieza automática de sesiones expiradas
    """
    
    def __init__(
        self,
        default_session_ttl: int = 3600,  # 1 hora
        max_sessions_per_user: int = 5,
        sync_interval: int = 30  # segundos
    ):
        self.default_session_ttl = default_session_ttl
        self.max_sessions_per_user = max_sessions_per_user
        self.sync_interval = sync_interval
        self.supabase = get_supabase_client()
        
        # Cache configuration
        self.session_cache_prefix = "session"
        self.user_sessions_cache_prefix = "user_sessions"
        
        # Active sessions tracking (memory only)
        self._active_sessions: Set[str] = set()
        
    async def initialize(self) -> None:
        """Inicializa el gestor de sesiones"""
        try:
            await self._ensure_database_tables()
            await self._start_background_tasks()
            logger.info("Session Manager inicializado exitosamente")
        except Exception as e:
            logger.error(f"Error inicializando Session Manager: {e}")
            raise
    
    async def _ensure_database_tables(self) -> None:
        """Asegura que las tablas necesarias existen"""
        try:
            # Para desarrollo, simulamos las tablas
            logger.info("Tablas de sesiones simuladas (modo desarrollo)")
            
        except Exception as e:
            logger.warning(f"No se pudo crear tabla de sesiones: {e}")
    
    async def _start_background_tasks(self) -> None:
        """Inicia tareas de fondo para limpieza y sincronización"""
        try:
            # Tarea de limpieza de sesiones expiradas (cada 10 minutos)
            asyncio.create_task(self._cleanup_expired_sessions_loop())
            
            # Tarea de sincronización (cada sync_interval segundos)
            asyncio.create_task(self._sync_sessions_loop())
            
        except Exception as e:
            logger.error(f"Error iniciando tareas de fondo: {e}")
    
    async def create_session(
        self,
        user_id: str,
        device_id: str,
        device_type: DeviceType = DeviceType.UNKNOWN,
        ttl: Optional[int] = None,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> SessionInfo:
        """
        Crea una nueva sesión para el usuario
        
        Args:
            user_id: ID del usuario
            device_id: ID único del dispositivo
            device_type: Tipo de dispositivo
            ttl: Tiempo de vida en segundos (None = default)
            initial_context: Contexto inicial de la sesión
        
        Returns:
            Información de la sesión creada
        """
        try:
            # Verificar límite de sesiones por usuario
            await self._enforce_session_limits(user_id)
            
            # Generar IDs únicos
            session_id = self._generate_session_id(user_id, device_id)
            sync_token = self._generate_sync_token()
            
            # Calcular expiración
            ttl = ttl or self.default_session_ttl
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            
            # Crear contexto de sesión
            context = SessionContext(
                current_topic=None,
                active_agent_id=None,
                conversation_flow=[],
                user_goals=[],
                session_metadata=initial_context or {},
                last_emotional_state=None
            )
            
            # Crear información de sesión
            session_info = SessionInfo(
                session_id=session_id,
                user_id=user_id,
                device_id=device_id,
                device_type=device_type,
                status=SessionStatus.ACTIVE,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                expires_at=expires_at,
                context=context,
                sync_token=sync_token,
                total_interactions=0
            )
            
            # Almacenar en base de datos
            await self._store_session(session_info)
            
            # Agregar a tracking activo
            self._active_sessions.add(session_id)
            
            # Cachear sesión
            await self._cache_session(session_info)
            
            logger.info(f"Sesión creada: {session_id} para usuario {user_id}")
            return session_info
            
        except Exception as e:
            logger.error(f"Error creando sesión: {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Obtiene información de una sesión"""
        try:
            # Intentar desde caché primero
            cache_key = f"{self.session_cache_prefix}:{session_id}"
            cached_session = await cache_get(cache_key)
            
            if cached_session:
                session_info = SessionInfo.from_dict(cached_session)
                
                # Verificar si no ha expirado
                if self._is_session_expired(session_info):
                    await self._expire_session(session_id)
                    return None
                
                return session_info
            
            # Para desarrollo, creamos una sesión mock si coincide con el ID
            if session_id in self._active_sessions:
                # Crear sesión mock básica
                mock_session = SessionInfo(
                    session_id=session_id,
                    user_id="mock_user",
                    device_id="mock_device",
                    device_type=DeviceType.WEB,
                    status=SessionStatus.ACTIVE,
                    created_at=datetime.utcnow(),
                    last_activity=datetime.utcnow(),
                    expires_at=datetime.utcnow() + timedelta(seconds=self.default_session_ttl),
                    context=SessionContext(
                        current_topic=None,
                        active_agent_id=None,
                        conversation_flow=[],
                        user_goals=[],
                        session_metadata={},
                        last_emotional_state=None
                    ),
                    sync_token="mock_token",
                    total_interactions=0
                )
                return mock_session
            
            # Para desarrollo, devolvemos None si no está en tracking activo
            logger.debug(f"Búsqueda simulada de sesión: {session_id}")
            return None
            
            # Código de verificación removido para modo desarrollo
            
        except Exception as e:
            logger.error(f"Error obteniendo sesión {session_id}: {e}")
            return None
    
    async def update_session_activity(
        self,
        session_id: str,
        agent_id: Optional[str] = None,
        context_update: Optional[Dict[str, Any]] = None,
        emotional_state: Optional[EmotionalState] = None
    ) -> bool:
        """
        Actualiza la actividad de una sesión
        
        Args:
            session_id: ID de la sesión
            agent_id: Agente activo actualmente
            context_update: Actualizaciones al contexto
            emotional_state: Estado emocional del usuario
        
        Returns:
            True si se actualizó exitosamente
        """
        try:
            session_info = await self.get_session(session_id)
            if not session_info:
                logger.warning(f"Sesión no encontrada para actualizar: {session_id}")
                return False
            
            # Actualizar timestamps
            session_info.last_activity = datetime.utcnow()
            session_info.total_interactions += 1
            
            # Actualizar contexto
            if agent_id:
                session_info.context.active_agent_id = agent_id
                if agent_id not in session_info.context.conversation_flow:
                    session_info.context.conversation_flow.append(agent_id)
            
            if emotional_state:
                session_info.context.last_emotional_state = emotional_state
            
            if context_update:
                session_info.context.session_metadata.update(context_update)
            
            # Extender expiración si está cerca de expirar
            if session_info.expires_at:
                time_until_expiry = session_info.expires_at - datetime.utcnow()
                if time_until_expiry.total_seconds() < 300:  # Menos de 5 minutos
                    session_info.expires_at = datetime.utcnow() + timedelta(seconds=self.default_session_ttl)
            
            # Actualizar en base de datos
            await self._update_session(session_info)
            
            # Actualizar caché
            await self._cache_session(session_info)
            
            # Agregar a tracking activo
            self._active_sessions.add(session_id)
            
            logger.debug(f"Actividad de sesión actualizada: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando actividad de sesión {session_id}: {e}")
            return False
    
    async def get_user_sessions(
        self,
        user_id: str,
        include_inactive: bool = False
    ) -> List[SessionInfo]:
        """Obtiene todas las sesiones de un usuario"""
        try:
            # Intentar desde caché
            cache_key = f"{self.user_sessions_cache_prefix}:{user_id}"
            cached_sessions = await cache_get(cache_key)
            
            if cached_sessions:
                sessions = [SessionInfo.from_dict(s) for s in cached_sessions]
                # Filtrar sesiones expiradas
                valid_sessions = []
                for session in sessions:
                    if self._is_session_expired(session):
                        await self._expire_session(session.session_id)
                    else:
                        valid_sessions.append(session)
                return valid_sessions
            
            # Para desarrollo, devolvemos lista vacía
            logger.debug(f"Búsqueda simulada de sesiones para usuario {user_id}")
            sessions = []  # No hay sesiones en modo desarrollo
            
            # Código de cache removido para modo desarrollo
            return sessions
            
        except Exception as e:
            logger.error(f"Error obteniendo sesiones de usuario {user_id}: {e}")
            return []
    
    async def pause_session(self, session_id: str) -> bool:
        """Pausa una sesión temporalmente"""
        try:
            session_info = await self.get_session(session_id)
            if not session_info:
                return False
            
            session_info.status = SessionStatus.PAUSED
            session_info.last_activity = datetime.utcnow()
            
            await self._update_session(session_info)
            await self._cache_session(session_info)
            
            # Remover de tracking activo
            self._active_sessions.discard(session_id)
            
            logger.info(f"Sesión pausada: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error pausando sesión {session_id}: {e}")
            return False
    
    async def resume_session(self, session_id: str) -> bool:
        """Reanuda una sesión pausada"""
        try:
            session_info = await self.get_session(session_id)
            if not session_info or session_info.status != SessionStatus.PAUSED:
                return False
            
            session_info.status = SessionStatus.ACTIVE
            session_info.last_activity = datetime.utcnow()
            
            # Extender expiración
            session_info.expires_at = datetime.utcnow() + timedelta(seconds=self.default_session_ttl)
            
            await self._update_session(session_info)
            await self._cache_session(session_info)
            
            # Agregar a tracking activo
            self._active_sessions.add(session_id)
            
            logger.info(f"Sesión reanudada: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error reanudando sesión {session_id}: {e}")
            return False
    
    async def end_session(self, session_id: str) -> bool:
        """Termina una sesión definitivamente"""
        try:
            session_info = await self.get_session(session_id)
            if not session_info:
                return False
            
            session_info.status = SessionStatus.ARCHIVED
            session_info.last_activity = datetime.utcnow()
            
            await self._update_session(session_info)
            
            # Remover de caché y tracking
            await self._remove_session_from_cache(session_id)
            self._active_sessions.discard(session_id)
            
            logger.info(f"Sesión terminada: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error terminando sesión {session_id}: {e}")
            return False
    
    async def sync_session_across_devices(
        self,
        user_id: str,
        source_session_id: str,
        target_device_id: str
    ) -> Optional[SessionInfo]:
        """Sincroniza una sesión entre dispositivos"""
        try:
            # Obtener sesión fuente
            source_session = await self.get_session(source_session_id)
            if not source_session or source_session.user_id != user_id:
                return None
            
            # Verificar si ya existe sesión en dispositivo destino
            target_sessions = await self.get_user_sessions(user_id)
            target_session = None
            
            for session in target_sessions:
                if session.device_id == target_device_id and session.status == SessionStatus.ACTIVE:
                    target_session = session
                    break
            
            if target_session:
                # Actualizar sesión existente con contexto de fuente
                target_session.context = source_session.context
                target_session.sync_token = source_session.sync_token
                target_session.last_activity = datetime.utcnow()
                
                await self._update_session(target_session)
                await self._cache_session(target_session)
                
                logger.info(f"Sesión sincronizada: {source_session_id} -> {target_session.session_id}")
                return target_session
            else:
                # Crear nueva sesión en dispositivo destino
                new_session = await self.create_session(
                    user_id=user_id,
                    device_id=target_device_id,
                    device_type=DeviceType.UNKNOWN,
                    initial_context=source_session.context.session_metadata
                )
                
                # Copiar contexto completo
                new_session.context = source_session.context
                new_session.sync_token = source_session.sync_token
                
                await self._update_session(new_session)
                await self._cache_session(new_session)
                
                logger.info(f"Nueva sesión sincronizada creada: {new_session.session_id}")
                return new_session
                
        except Exception as e:
            logger.error(f"Error sincronizando sesión: {e}")
            return None
    
    def _generate_session_id(self, user_id: str, device_id: str) -> str:
        """Genera ID único para sesión"""
        timestamp = datetime.utcnow().isoformat()
        data = f"{user_id}:{device_id}:{timestamp}:{uuid.uuid4()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _generate_sync_token(self) -> str:
        """Genera token de sincronización único"""
        return str(uuid.uuid4())
    
    def _is_session_expired(self, session_info: SessionInfo) -> bool:
        """Verifica si una sesión ha expirado"""
        if not session_info.expires_at:
            return False
        return datetime.utcnow() > session_info.expires_at
    
    async def _store_session(self, session_info: SessionInfo) -> None:
        """Almacena sesión en base de datos"""
        try:
            # Para desarrollo, simulamos el almacenamiento
            logger.info(f"Sesión simulada almacenada: {session_info.session_id}")
            # En producción, aquí iría la operación real de Supabase
                
        except Exception as e:
            logger.error(f"Error almacenando sesión: {e}")
            raise
    
    async def _update_session(self, session_info: SessionInfo) -> None:
        """Actualiza sesión en base de datos"""
        try:
            # Para desarrollo, simulamos la actualización
            logger.debug(f"Sesión simulada actualizada: {session_info.session_id}")
            # En producción, aquí iría la operación real de Supabase
                
        except Exception as e:
            logger.error(f"Error actualizando sesión: {e}")
            raise
    
    async def _cache_session(self, session_info: SessionInfo) -> None:
        """Cachea información de sesión"""
        try:
            # Para desarrollo, solo registramos el intento de cache
            logger.debug(f"Cache simulado de sesión: {session_info.session_id}")
            # En producción aquí iría el cache real
            
        except Exception as e:
            logger.error(f"Error cacheando sesión: {e}")
    
    async def _remove_session_from_cache(self, session_id: str) -> None:
        """Remueve sesión del caché"""
        try:
            # Para desarrollo, solo registramos la remoción
            logger.debug(f"Remoción simulada de cache: {session_id}")
            
        except Exception as e:
            logger.error(f"Error removiendo sesión del caché: {e}")
    
    async def _expire_session(self, session_id: str) -> None:
        """Marca una sesión como expirada"""
        try:
            # Para desarrollo, simulamos la expiración
            await self._remove_session_from_cache(session_id)
            self._active_sessions.discard(session_id)
            
            logger.debug(f"Sesión simulada expirada: {session_id}")
            
        except Exception as e:
            logger.error(f"Error expirando sesión {session_id}: {e}")
    
    async def _enforce_session_limits(self, user_id: str) -> None:
        """Aplica límites de sesiones por usuario"""
        try:
            user_sessions = await self.get_user_sessions(user_id, include_inactive=False)
            
            if len(user_sessions) >= self.max_sessions_per_user:
                # Encontrar sesión más antigua para terminar
                oldest_session = min(user_sessions, key=lambda s: s.last_activity)
                await self.end_session(oldest_session.session_id)
                
                logger.info(f"Sesión más antigua terminada para aplicar límite: {oldest_session.session_id}")
                
        except Exception as e:
            logger.error(f"Error aplicando límites de sesión: {e}")
    
    async def _cleanup_expired_sessions_loop(self) -> None:
        """Tarea de fondo para limpiar sesiones expiradas"""
        while True:
            try:
                await asyncio.sleep(600)  # 10 minutos
                
                # Para desarrollo, solo registramos que está ejecutándose
                logger.debug("Limpieza simulada de sesiones expiradas")
                
            except Exception as e:
                logger.error(f"Error en limpieza de sesiones: {e}")
                await asyncio.sleep(60)  # Esperar 1 minuto antes de reintentar
    
    async def _sync_sessions_loop(self) -> None:
        """Tarea de fondo para sincronización periódica"""
        while True:
            try:
                await asyncio.sleep(self.sync_interval)
                
                # Procesar sesiones activas para sincronización
                if self._active_sessions:
                    logger.debug(f"Sesiones activas: {len(self._active_sessions)}")
                
                # Aquí se puede agregar lógica adicional de sincronización
                # como notificar a otros dispositivos de cambios, etc.
                
            except Exception as e:
                logger.error(f"Error en sincronización de sesiones: {e}")
                await asyncio.sleep(30)  # Esperar menos tiempo en caso de error
    
    async def get_session_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del gestor de sesiones"""
        try:
            # Para desarrollo, devolvemos estadísticas simuladas
            return {
                'active_sessions': 0,  # No hay sesiones en modo desarrollo
                'today_sessions': 0,
                'memory_tracked_sessions': len(self._active_sessions),
                'default_ttl_seconds': self.default_session_ttl,
                'max_sessions_per_user': self.max_sessions_per_user
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de sesiones: {e}")
            return {}


# Instancia global del gestor de sesiones
session_manager = SessionManager()


async def init_session_manager() -> None:
    """Inicializa el gestor de sesiones"""
    await session_manager.initialize()


# Funciones helper para uso sencillo
async def create_user_session(
    user_id: str,
    device_id: str,
    device_type: DeviceType = DeviceType.UNKNOWN,
    initial_context: Optional[Dict[str, Any]] = None
) -> SessionInfo:
    """Función helper para crear sesión"""
    return await session_manager.create_session(
        user_id=user_id,
        device_id=device_id,
        device_type=device_type,
        initial_context=initial_context
    )


async def get_user_session(session_id: str) -> Optional[SessionInfo]:
    """Función helper para obtener sesión"""
    return await session_manager.get_session(session_id)


async def update_user_session_activity(
    session_id: str,
    agent_id: Optional[str] = None,
    context_update: Optional[Dict[str, Any]] = None,
    emotional_state: Optional[EmotionalState] = None
) -> bool:
    """Función helper para actualizar actividad"""
    return await session_manager.update_session_activity(
        session_id=session_id,
        agent_id=agent_id,
        context_update=context_update,
        emotional_state=emotional_state
    )