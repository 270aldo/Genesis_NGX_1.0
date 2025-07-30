"""
Servicio de integración con NexusCRM.

Este módulo maneja el envío de eventos de uso de agentes al CRM
para analytics y tracking de límites.
"""

import asyncio
import hashlib
import hmac
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime

import httpx
from core.settings_lazy import settings
from core.logging_config import get_logger

logger = get_logger(__name__)

class CRMIntegrationService:
    """
    Servicio para enviar eventos de uso al CRM de NGX.
    """
    
    def __init__(self):
        self.crm_base_url = getattr(settings, 'CRM_BASE_URL', 'http://localhost:8001')
        self.webhook_secret = getattr(settings, 'CRM_WEBHOOK_SECRET', 'default-secret-change-me')
        self.enabled = getattr(settings, 'CRM_INTEGRATION_ENABLED', True)
        self.batch_size = 10
        self.batch_timeout = 5  # segundos
        self.pending_events = []
        self.last_batch_sent = time.time()
        
    def generate_signature(self, payload: bytes) -> str:
        """
        Genera signature HMAC para autenticar el webhook.
        
        Args:
            payload: Payload en bytes
            
        Returns:
            Signature en formato sha256=<hash>
        """
        signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    async def send_usage_event(
        self,
        user_id: str,
        agent_id: str,
        session_id: str,
        tokens_used: int,
        response_time_ms: int,
        subscription_tier: str,
        organization_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Envía evento de uso individual al CRM.
        
        Args:
            user_id: ID del usuario
            agent_id: ID del agente usado
            session_id: ID de la sesión
            tokens_used: Tokens consumidos
            response_time_ms: Tiempo de respuesta en ms
            subscription_tier: Tier de suscripción
            organization_id: ID de organización (opcional)
            context: Contexto adicional (opcional)
            
        Returns:
            bool: True si se envió exitosamente
        """
        if not self.enabled:
            logger.debug("CRM integration disabled, skipping event")
            return True
            
        try:
            event_data = {
                "user_id": user_id,
                "agent_id": agent_id,
                "session_id": session_id,
                "tokens_used": tokens_used,
                "response_time_ms": response_time_ms,
                "timestamp": datetime.utcnow().isoformat(),
                "subscription_tier": subscription_tier,
                "organization_id": organization_id,
                "context": context or {}
            }
            
            # Agregar a batch para envío optimizado
            self.pending_events.append(event_data)
            
            # Enviar batch si está lleno o ha pasado suficiente tiempo
            if (len(self.pending_events) >= self.batch_size or 
                time.time() - self.last_batch_sent >= self.batch_timeout):
                await self.flush_pending_events()
            
            return True
            
        except Exception as e:
            logger.error(f"Error preparando evento para CRM: {e}")
            return False
    
    async def flush_pending_events(self) -> bool:
        """
        Envía todos los eventos pendientes al CRM.
        
        Returns:
            bool: True si se enviaron exitosamente
        """
        if not self.pending_events:
            return True
            
        try:
            events_to_send = self.pending_events.copy()
            self.pending_events.clear()
            self.last_batch_sent = time.time()
            
            payload = {
                "events": events_to_send,
                "batch_id": f"batch_{int(time.time() * 1000)}",
                "source": "genesis-ngx-agents",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Convertir a JSON y generar signature
            payload_json = json.dumps(payload, separators=(',', ':')).encode('utf-8')
            signature = self.generate_signature(payload_json)
            
            headers = {
                "Content-Type": "application/json",
                "X-Genesis-Signature": signature,
                "X-Genesis-Timestamp": str(int(time.time())),
                "User-Agent": "GENESIS-NGX-Agents/1.0"
            }
            
            # Enviar al CRM
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.crm_base_url}/agent-usage/events",
                    content=payload_json,
                    headers=headers
                )
                
                if response.status_code == 200:
                    logger.info(f"Enviados {len(events_to_send)} eventos al CRM exitosamente")
                    return True
                else:
                    logger.error(
                        f"Error enviando eventos al CRM: {response.status_code} - {response.text}"
                    )
                    # Reencolar eventos para retry
                    self.pending_events.extend(events_to_send)
                    return False
                    
        except Exception as e:
            logger.error(f"Error enviando batch de eventos al CRM: {e}")
            # Reencolar eventos para retry
            if 'events_to_send' in locals():
                self.pending_events.extend(events_to_send)
            return False
    
    async def send_session_end_event(
        self,
        user_id: str,
        session_id: str,
        total_interactions: int,
        total_tokens: int,
        session_duration_ms: int,
        agents_used: list,
        subscription_tier: str
    ) -> bool:
        """
        Envía evento de fin de sesión con resumen de uso.
        
        Args:
            user_id: ID del usuario
            session_id: ID de la sesión
            total_interactions: Total de interacciones en la sesión
            total_tokens: Total de tokens consumidos
            session_duration_ms: Duración total de la sesión
            agents_used: Lista de agentes usados
            subscription_tier: Tier de suscripción
            
        Returns:
            bool: True si se envió exitosamente
        """
        if not self.enabled:
            return True
            
        try:
            session_summary = {
                "event_type": "session_end",
                "user_id": user_id,
                "session_id": session_id,
                "total_interactions": total_interactions,
                "total_tokens": total_tokens,
                "session_duration_ms": session_duration_ms,
                "agents_used": agents_used,
                "subscription_tier": subscription_tier,
                "ended_at": datetime.utcnow().isoformat()
            }
            
            payload_json = json.dumps(session_summary, separators=(',', ':')).encode('utf-8')
            signature = self.generate_signature(payload_json)
            
            headers = {
                "Content-Type": "application/json",
                "X-Genesis-Signature": signature,
                "X-Genesis-Timestamp": str(int(time.time())),
                "User-Agent": "GENESIS-NGX-Agents/1.0"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.crm_base_url}/agent-usage/session-end",
                    content=payload_json,
                    headers=headers
                )
                
                if response.status_code == 200:
                    logger.info(f"Enviado resumen de sesión {session_id} al CRM")
                    return True
                else:
                    logger.error(
                        f"Error enviando resumen de sesión: {response.status_code} - {response.text}"
                    )
                    return False
                    
        except Exception as e:
            logger.error(f"Error enviando resumen de sesión al CRM: {e}")
            return False
    
    async def test_crm_connectivity(self) -> Dict[str, Any]:
        """
        Prueba la conectividad con el CRM.
        
        Returns:
            Dict con resultados de la prueba
        """
        try:
            test_payload = {
                "test": True,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "genesis-ngx-agents"
            }
            
            payload_json = json.dumps(test_payload, separators=(',', ':')).encode('utf-8')
            signature = self.generate_signature(payload_json)
            
            headers = {
                "Content-Type": "application/json",
                "X-Genesis-Signature": signature,
                "X-Genesis-Timestamp": str(int(time.time())),
                "User-Agent": "GENESIS-NGX-Agents/1.0"
            }
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                start_time = time.time()
                response = await client.post(
                    f"{self.crm_base_url}/agent-usage/test",
                    content=payload_json,
                    headers=headers
                )
                response_time = (time.time() - start_time) * 1000
                
                return {
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "response_time_ms": response_time,
                    "crm_url": self.crm_base_url,
                    "response_data": response.json() if response.status_code == 200 else response.text
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "crm_url": self.crm_base_url,
                "response_time_ms": 0
            }
    
    async def get_user_usage_limits(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los límites de uso actuales del usuario desde el CRM.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Dict con límites y uso actual o None si hay error
        """
        if not self.enabled:
            return None
            
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.crm_base_url}/agent-usage/limits/{user_id}",
                    headers={"User-Agent": "GENESIS-NGX-Agents/1.0"}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"No se pudieron obtener límites para usuario {user_id}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error obteniendo límites de usuario del CRM: {e}")
            return None
    
    async def startup(self):
        """
        Inicializa el servicio de integración con CRM.
        """
        try:
            if not self.enabled:
                logger.info("CRM integration disabled")
                return
                
            # Probar conectividad inicial
            connectivity_test = await self.test_crm_connectivity()
            if connectivity_test["success"]:
                logger.info(f"CRM integration initialized successfully - Response time: {connectivity_test['response_time_ms']:.2f}ms")
            else:
                logger.warning(f"CRM connectivity test failed: {connectivity_test.get('error', 'Unknown error')}")
                
            # Iniciar task para flush periódico
            asyncio.create_task(self._periodic_flush())
            
        except Exception as e:
            logger.error(f"Error initializing CRM integration: {e}")
    
    async def shutdown(self):
        """
        Cierra el servicio de integración con CRM.
        """
        try:
            # Enviar eventos pendientes antes de cerrar
            if self.pending_events:
                await self.flush_pending_events()
                logger.info("Enviados eventos pendientes antes del shutdown")
                
        except Exception as e:
            logger.error(f"Error during CRM integration shutdown: {e}")
    
    async def _periodic_flush(self):
        """
        Task que envía eventos pendientes periódicamente.
        """
        while True:
            try:
                await asyncio.sleep(self.batch_timeout)
                
                if (self.pending_events and 
                    time.time() - self.last_batch_sent >= self.batch_timeout):
                    await self.flush_pending_events()
                    
            except Exception as e:
                logger.error(f"Error in periodic flush: {e}")

# Instancia global del servicio
crm_integration_service = CRMIntegrationService()

# Hook para usar en el chat router
async def track_agent_usage(
    user_id: str,
    agent_id: str,
    session_id: str,
    tokens_used: int,
    response_time_ms: int,
    subscription_tier: str = "essential",
    organization_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Función de conveniencia para tracking de uso de agentes.
    
    Esta función puede ser llamada desde el chat router después
    de cada interacción con un agente.
    """
    await crm_integration_service.send_usage_event(
        user_id=user_id,
        agent_id=agent_id,
        session_id=session_id,
        tokens_used=tokens_used,
        response_time_ms=response_time_ms,
        subscription_tier=subscription_tier,
        organization_id=organization_id,
        context=context
    )