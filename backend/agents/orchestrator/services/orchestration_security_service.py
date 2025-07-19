"""
NEXUS ENHANCED - Orchestration Security Service
==============================================

Servicio de seguridad especializado para orchestration y client success.
Maneja encriptación, audit logging, compliance y protección de datos sensibles.

Arquitectura A+ - Services Layer
Líneas objetivo: <300
"""

import hashlib
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
import logging
from cryptography.fernet import Fernet
import base64

from ..core.exceptions import NexusError, ConfigurationError, DependencyError

logger = logging.getLogger(__name__)


@dataclass
class AuditLogEntry:
    """Entrada de audit log para orchestration."""

    timestamp: datetime
    event_type: str
    user_id: Optional[str]
    session_id: Optional[str]
    agent_id: str
    operation: str
    intent: Optional[str]
    success: bool
    response_time_ms: float
    error_code: Optional[str] = None
    sensitive_data_types: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para almacenamiento."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class OrchestrationSecurityService:
    """
    Servicio de seguridad para orchestration y client success.

    Responsabilidades:
    - Encriptación de conversaciones sensibles
    - Audit logging de todas las operaciones
    - Compliance GDPR/HIPAA para datos de salud
    - Anonimización de datos para analytics
    - Validación de input para prevenir inyecciones
    """

    def __init__(self, encryption_key: Optional[str] = None):
        """
        Inicializa el servicio de seguridad.

        Args:
            encryption_key: Clave de encriptación (se genera si no se proporciona)
        """
        self._setup_encryption(encryption_key)
        self._audit_logs: List[AuditLogEntry] = []
        self._sensitive_data_patterns = self._compile_sensitive_patterns()
        logger.info("OrchestrationSecurityService inicializado")

    def _setup_encryption(self, key: Optional[str] = None):
        """Configura la encriptación Fernet."""
        try:
            if key:
                # Usar clave proporcionada
                key_bytes = base64.urlsafe_b64decode(key.encode())
                self._fernet = Fernet(key_bytes)
            else:
                # Generar nueva clave
                key_bytes = Fernet.generate_key()
                self._fernet = Fernet(key_bytes)
                logger.warning(
                    "Clave de encriptación generada automáticamente - persistir en producción"
                )
        except Exception as e:
            logger.error(f"Error configurando encriptación: {e}")
            raise ConfigurationError("encryption_key", str(e))

    def _compile_sensitive_patterns(self) -> Dict[str, List[str]]:
        """Compila patrones para detectar datos sensibles."""
        return {
            "health_data": [
                r"\b(?:weight|peso)\s*:?\s*\d+",
                r"\b(?:blood pressure|presión)\s*:?\s*\d+/\d+",
                r"\b(?:heart rate|frecuencia)\s*:?\s*\d+",
                r"\b(?:glucose|glucosa)\s*:?\s*\d+",
                r"\b(?:medication|medicamento|medicine)\b",
            ],
            "personal_info": [
                r"\b(?:age|edad)\s*:?\s*\d+",
                r"\b(?:birthday|cumpleaños|fecha de nacimiento)\b",
                r"\b\d{3}-\d{2}-\d{4}\b",  # SSN pattern
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
            ],
            "genetic_data": [
                r"\b(?:DNA|genetic|genético|gen)\b",
                r"\b[ATCG]{10,}\b",  # DNA sequence
                r"\b(?:allele|alelo|mutation|mutación)\b",
            ],
        }

    def sanitize_input(
        self, input_text: str, user_id: Optional[str] = None
    ) -> Tuple[str, List[str]]:
        """
        Sanitiza input del usuario y detecta datos sensibles.

        Args:
            input_text: Texto a sanitizar
            user_id: ID del usuario para logging

        Returns:
            Tuple[str, List[str]]: Texto sanitizado y tipos de datos sensibles detectados
        """
        try:
            # Detectar datos sensibles
            sensitive_types = []
            for data_type, patterns in self._sensitive_data_patterns.items():
                for pattern in patterns:
                    import re

                    if re.search(pattern, input_text, re.IGNORECASE):
                        sensitive_types.append(data_type)
                        break

            # Sanitizar para prevenir inyecciones
            sanitized = input_text.replace("<script>", "&lt;script&gt;")
            sanitized = sanitized.replace("javascript:", "")
            sanitized = sanitized.replace("eval(", "")

            # Log si se detectaron datos sensibles
            if sensitive_types:
                logger.info(
                    f"Datos sensibles detectados para usuario {user_id}: {sensitive_types}"
                )

            return sanitized, sensitive_types

        except Exception as e:
            logger.error(f"Error sanitizando input: {e}")
            raise NexusError(f"Error en sanitización de input: {e}")

    def encrypt_conversation(self, conversation_data: Dict[str, Any]) -> str:
        """
        Encripta datos de conversación.

        Args:
            conversation_data: Datos de conversación a encriptar

        Returns:
            str: Datos encriptados como string base64
        """
        try:
            # Convertir a JSON y encriptar
            json_data = json.dumps(conversation_data).encode()
            encrypted_data = self._fernet.encrypt(json_data)
            return base64.urlsafe_b64encode(encrypted_data).decode()

        except Exception as e:
            logger.error(f"Error encriptando conversación: {e}")
            raise NexusError(f"Error en encriptación: {e}")

    def decrypt_conversation(self, encrypted_data: str) -> Dict[str, Any]:
        """
        Desencripta datos de conversación.

        Args:
            encrypted_data: Datos encriptados como string base64

        Returns:
            Dict[str, Any]: Datos de conversación desencriptados
        """
        try:
            # Decodificar y desencriptar
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self._fernet.decrypt(encrypted_bytes)
            return json.loads(decrypted_data.decode())

        except Exception as e:
            logger.error(f"Error desencriptando conversación: {e}")
            raise NexusError(f"Error en desencriptación: {e}")

    def log_orchestration_event(
        self,
        event_type: str,
        operation: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        agent_id: str = "nexus_enhanced",
        intent: Optional[str] = None,
        success: bool = True,
        response_time_ms: float = 0.0,
        error_code: Optional[str] = None,
        sensitive_data_types: Optional[List[str]] = None,
    ) -> str:
        """
        Registra evento de orchestration en audit log.

        Args:
            event_type: Tipo de evento (intent_analysis, agent_routing, etc.)
            operation: Operación específica realizada
            user_id: ID del usuario
            session_id: ID de sesión
            agent_id: ID del agente involucrado
            intent: Intención detectada
            success: Si la operación fue exitosa
            response_time_ms: Tiempo de respuesta en ms
            error_code: Código de error si aplica
            sensitive_data_types: Tipos de datos sensibles detectados

        Returns:
            str: ID único del log entry
        """
        try:
            log_entry = AuditLogEntry(
                timestamp=datetime.now(),
                event_type=event_type,
                user_id=user_id,
                session_id=session_id,
                agent_id=agent_id,
                operation=operation,
                intent=intent,
                success=success,
                response_time_ms=response_time_ms,
                error_code=error_code,
                sensitive_data_types=sensitive_data_types or [],
            )

            # Agregar a logs en memoria (en producción usar base de datos)
            self._audit_logs.append(log_entry)

            # Log crítico para eventos de seguridad
            if not success or sensitive_data_types:
                logger.warning(f"Evento de seguridad: {event_type} - {operation}")

            # Generar ID único para el log
            log_id = hashlib.md5(
                f"{log_entry.timestamp.isoformat()}{operation}{user_id}".encode()
            ).hexdigest()

            return log_id

        except Exception as e:
            logger.error(f"Error registrando evento de audit: {e}")
            # No lanzar excepción para no interrumpir operación principal
            return "logging_failed"

    def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene logs de audit con filtros.

        Args:
            user_id: Filtrar por usuario específico
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            event_types: Tipos de evento a incluir

        Returns:
            List[Dict[str, Any]]: Lista de logs filtrados
        """
        try:
            filtered_logs = self._audit_logs.copy()

            # Filtrar por usuario
            if user_id:
                filtered_logs = [log for log in filtered_logs if log.user_id == user_id]

            # Filtrar por rango de fechas
            if start_date:
                filtered_logs = [
                    log for log in filtered_logs if log.timestamp >= start_date
                ]
            if end_date:
                filtered_logs = [
                    log for log in filtered_logs if log.timestamp <= end_date
                ]

            # Filtrar por tipos de evento
            if event_types:
                filtered_logs = [
                    log for log in filtered_logs if log.event_type in event_types
                ]

            # Convertir a diccionarios
            return [log.to_dict() for log in filtered_logs]

        except Exception as e:
            logger.error(f"Error obteniendo audit logs: {e}")
            return []

    def anonymize_data(
        self, data: Dict[str, Any], fields_to_anonymize: List[str]
    ) -> Dict[str, Any]:
        """
        Anonimiza datos para analytics preservando utilidad.

        Args:
            data: Datos a anonimizar
            fields_to_anonymize: Campos que deben ser anonimizados

        Returns:
            Dict[str, Any]: Datos anonimizados
        """
        try:
            anonymized = data.copy()

            for field in fields_to_anonymize:
                if field in anonymized:
                    # Crear hash consistente para el campo
                    original_value = str(anonymized[field])
                    hash_value = hashlib.sha256(original_value.encode()).hexdigest()[:8]
                    anonymized[field] = f"anon_{hash_value}"

            # Agregar timestamp de anonimización
            anonymized["_anonymized_at"] = datetime.now().isoformat()

            return anonymized

        except Exception as e:
            logger.error(f"Error anonimizando datos: {e}")
            return data  # Retornar datos originales si falla anonimización

    def check_compliance_requirements(
        self, operation: str, data_types: List[str]
    ) -> Dict[str, Any]:
        """
        Verifica requisitos de compliance para operación.

        Args:
            operation: Operación a verificar
            data_types: Tipos de datos involucrados

        Returns:
            Dict[str, Any]: Estado de compliance y acciones requeridas
        """
        compliance_status = {
            "compliant": True,
            "requirements": [],
            "actions_required": [],
            "warnings": [],
        }

        # GDPR requirements
        if "personal_info" in data_types:
            compliance_status["requirements"].append("GDPR_consent_required")
            if operation in ["store", "process", "share"]:
                compliance_status["actions_required"].append("obtain_explicit_consent")

        # HIPAA requirements for health data
        if "health_data" in data_types or "genetic_data" in data_types:
            compliance_status["requirements"].append("HIPAA_compliance_required")
            compliance_status["actions_required"].extend(
                [
                    "encrypt_at_rest",
                    "encrypt_in_transit",
                    "audit_access",
                    "minimum_necessary_standard",
                ]
            )

        # Data retention requirements
        compliance_status["actions_required"].append("apply_retention_policy")

        # Check if all requirements can be met
        if len(compliance_status["actions_required"]) > 0:
            compliance_status["warnings"].append(
                f"Operation requires compliance actions: {', '.join(compliance_status['actions_required'])}"
            )

        return compliance_status

    def generate_compliance_report(self, days: int = 30) -> Dict[str, Any]:
        """
        Genera reporte de compliance para período especificado.

        Args:
            days: Número de días hacia atrás para el reporte

        Returns:
            Dict[str, Any]: Reporte de compliance
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            logs = self.get_audit_logs(start_date=start_date)

            # Análisis de compliance
            total_operations = len(logs)
            sensitive_operations = len(
                [log for log in logs if log.get("sensitive_data_types")]
            )
            failed_operations = len(
                [log for log in logs if not log.get("success", True)]
            )

            report = {
                "report_period": f"{days} days",
                "generated_at": datetime.now().isoformat(),
                "summary": {
                    "total_operations": total_operations,
                    "sensitive_data_operations": sensitive_operations,
                    "failed_operations": failed_operations,
                    "compliance_rate": (total_operations - failed_operations)
                    / max(total_operations, 1)
                    * 100,
                },
                "data_types_processed": {},
                "security_events": [],
                "recommendations": [],
            }

            # Análizar tipos de datos procesados
            for log in logs:
                sensitive_types = log.get("sensitive_data_types", [])
                for data_type in sensitive_types:
                    report["data_types_processed"][data_type] = (
                        report["data_types_processed"].get(data_type, 0) + 1
                    )

            # Identificar eventos de seguridad
            security_events = [log for log in logs if not log.get("success", True)]
            report["security_events"] = security_events[:10]  # Últimos 10 eventos

            # Generar recomendaciones
            if failed_operations > total_operations * 0.05:  # >5% error rate
                report["recommendations"].append("Investigate high error rate")

            if sensitive_operations > 0:
                report["recommendations"].append(
                    "Review sensitive data handling procedures"
                )

            return report

        except Exception as e:
            logger.error(f"Error generando reporte de compliance: {e}")
            return {"error": str(e)}
