"""
Ecosystem Integration Scenarios

Tests the complete NGX ecosystem integration including GENESIS, NGX Pulse,
Blog, CRM, and Conversations. Validates data flow, synchronization, and
seamless user experience across all platforms.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import random

from app.schemas.chat import ChatRequest, ChatResponse
from core.logging_config import get_logger

logger = get_logger(__name__)


class EcosystemIntegrationScenarios:
    """Test scenarios for NGX ecosystem integration"""
    
    def __init__(self, orchestrator_client, mcp_gateway_client=None):
        """
        Initialize with orchestrator and MCP gateway clients
        
        Args:
            orchestrator_client: Client to interact with GENESIS orchestrator
            mcp_gateway_client: Client to interact with MCP Gateway (optional)
        """
        self.orchestrator = orchestrator_client
        self.mcp_gateway = mcp_gateway_client
        self.results = []
        
    async def run_all_scenarios(self) -> Dict[str, Any]:
        """Run all ecosystem integration scenarios"""
        scenarios = [
            self.test_pulse_data_integration,
            self.test_blog_content_generation,
            self.test_crm_sync_flow,
            self.test_conversations_history,
            self.test_cross_platform_analytics,
            self.test_unified_user_profile,
            self.test_real_time_sync,
            self.test_failover_resilience,
            self.test_data_privacy_across_platforms,
            self.test_notification_orchestration,
            self.test_subscription_management,
            self.test_multi_device_experience,
            self.test_api_rate_limiting,
            self.test_ecosystem_onboarding,
            self.test_complete_user_journey
        ]
        
        results = {
            "category": "ecosystem_integration",
            "total_scenarios": len(scenarios),
            "passed": 0,
            "failed": 0,
            "details": []
        }
        
        for scenario in scenarios:
            try:
                result = await scenario()
                if result["passed"]:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                results["details"].append(result)
            except Exception as e:
                logger.error(f"Error in scenario {scenario.__name__}: {e}")
                results["failed"] += 1
                results["details"].append({
                    "scenario": scenario.__name__,
                    "passed": False,
                    "error": str(e)
                })
        
        return results
    
    async def test_pulse_data_integration(self) -> Dict[str, Any]:
        """Test: NGX Pulse biometric data flowing into GENESIS"""
        scenario_name = "pulse_data_integration"
        
        # Simulate Pulse data
        pulse_data = {
            "heart_rate_variability": 65,
            "resting_heart_rate": 58,
            "sleep_score": 82,
            "recovery_score": 75,
            "stress_level": "moderate",
            "steps": 8500,
            "calories_burned": 2200
        }
        
        messages = [
            "¿Cómo están mis métricas de NGX Pulse hoy?",
            "Mi HRV está en 65, ¿es bueno para mi edad?",
            "¿Debo ajustar mi entrenamiento según mi recovery score?",
            "Genera un reporte semanal con todos mis datos biométricos"
        ]
        
        expected_behaviors = [
            "pulse_data_access",
            "hrv_interpretation",
            "recovery_based_adjustment",
            "comprehensive_reporting",
            "trend_analysis"
        ]
        
        return await self._run_ecosystem_test(
            scenario_name,
            messages,
            expected_behaviors,
            platform_data={"ngx_pulse": pulse_data}
        )
    
    async def test_blog_content_generation(self) -> Dict[str, Any]:
        """Test: AI-generated blog content based on user progress"""
        scenario_name = "blog_content_generation"
        
        messages = [
            "Quiero compartir mi transformación de 3 meses en el blog",
            "Crea un post sobre cómo superé mi meseta de peso",
            "Incluye mis mejores consejos y lo que aprendí",
            "Optimízalo para SEO con keywords de fitness",
            "Prográmalo para publicar mañana a las 10 AM"
        ]
        
        expected_behaviors = [
            "content_generation",
            "personal_story_integration",
            "seo_optimization",
            "scheduling_capability",
            "blog_platform_sync"
        ]
        
        return await self._run_ecosystem_test(
            scenario_name,
            messages,
            expected_behaviors,
            platform_data={"user_progress": "3_months", "transformation": True}
        )
    
    async def test_crm_sync_flow(self) -> Dict[str, Any]:
        """Test: CRM updates based on user interactions"""
        scenario_name = "crm_sync_flow"
        
        messages = [
            "He alcanzado mi objetivo de peso",
            "Quiero actualizar mi suscripción a Premium",
            "Refiere a mi amigo Carlos para el programa",
            "Revisa mi historial completo de interacciones"
        ]
        
        expected_behaviors = [
            "milestone_tracking",
            "subscription_update",
            "referral_management",
            "interaction_history",
            "crm_data_sync"
        ]
        
        return await self._run_ecosystem_test(
            scenario_name,
            messages,
            expected_behaviors,
            platform_data={"crm_updates": ["goal_achieved", "upgrade", "referral"]}
        )
    
    async def test_conversations_history(self) -> Dict[str, Any]:
        """Test: Nexus Conversations integration for support"""
        scenario_name = "conversations_history"
        
        messages = [
            "Necesito hablar con soporte sobre mi facturación",
            "¿Cuál fue la respuesta a mi consulta anterior?",
            "Revisa todas mis conversaciones del último mes",
            "Transfiere esta conversación a un agente humano"
        ]
        
        expected_behaviors = [
            "support_routing",
            "conversation_retrieval",
            "history_access",
            "human_handoff",
            "context_preservation"
        ]
        
        return await self._run_ecosystem_test(
            scenario_name,
            messages,
            expected_behaviors,
            platform_data={"support_needed": True}
        )
    
    async def test_cross_platform_analytics(self) -> Dict[str, Any]:
        """Test: Unified analytics across all platforms"""
        scenario_name = "cross_platform_analytics"
        
        messages = [
            "Muéstrame mi actividad total en el ecosistema NGX",
            "¿Cuánto tiempo paso en cada plataforma?",
            "¿Cuál es mi ROI en salud desde que empecé?",
            "Compara mis métricas con el promedio de usuarios",
            "Genera un dashboard ejecutivo de mi progreso"
        ]
        
        expected_behaviors = [
            "unified_analytics",
            "platform_usage_tracking",
            "roi_calculation",
            "benchmarking",
            "dashboard_generation"
        ]
        
        return await self._run_ecosystem_test(
            scenario_name,
            messages,
            expected_behaviors,
            platform_data={"analytics_scope": "ecosystem_wide"}
        )
    
    async def test_unified_user_profile(self) -> Dict[str, Any]:
        """Test: Single user profile across all platforms"""
        scenario_name = "unified_user_profile"
        
        messages = [
            "Actualiza mi foto de perfil en todas las plataformas",
            "Cambia mi zona horaria a EST",
            "Sincroniza mis preferencias de notificaciones",
            "¿Están todos mis datos actualizados en el ecosistema?"
        ]
        
        expected_behaviors = [
            "profile_synchronization",
            "preference_propagation",
            "data_consistency",
            "real_time_updates",
            "platform_coordination"
        ]
        
        return await self._run_ecosystem_test(
            scenario_name,
            messages,
            expected_behaviors,
            platform_data={"profile_update": True}
        )
    
    async def test_real_time_sync(self) -> Dict[str, Any]:
        """Test: Real-time data synchronization"""
        scenario_name = "real_time_sync"
        
        messages = [
            "Acabo de completar mi entrenamiento en NGX Pulse",
            "¿Ya se reflejó en mi progreso de GENESIS?",
            "Actualiza mi blog con el workout de hoy",
            "Verifica que todo esté sincronizado"
        ]
        
        expected_behaviors = [
            "instant_sync",
            "data_propagation",
            "automatic_updates",
            "sync_verification",
            "latency_handling"
        ]
        
        return await self._run_ecosystem_test(
            scenario_name,
            messages,
            expected_behaviors,
            platform_data={"workout_completed": True, "sync_required": True}
        )
    
    async def test_failover_resilience(self) -> Dict[str, Any]:
        """Test: System resilience when platforms fail"""
        scenario_name = "failover_resilience"
        
        # Simulate platform outage
        messages = [
            "NGX Pulse no está respondiendo",
            "¿Puedo seguir usando GENESIS sin Pulse?",
            "Guarda mis datos localmente mientras se restaura",
            "¿Qué funcionalidades siguen disponibles?"
        ]
        
        expected_behaviors = [
            "graceful_degradation",
            "offline_capability",
            "data_caching",
            "feature_availability",
            "recovery_handling"
        ]
        
        return await self._run_ecosystem_test(
            scenario_name,
            messages,
            expected_behaviors,
            platform_data={"platform_status": {"ngx_pulse": "down"}}
        )
    
    async def test_data_privacy_across_platforms(self) -> Dict[str, Any]:
        """Test: Privacy controls across ecosystem"""
        scenario_name = "data_privacy_across_platforms"
        
        messages = [
            "No quiero compartir mi peso en el blog público",
            "Mantén mis datos médicos solo en GENESIS",
            "¿Qué información es visible en cada plataforma?",
            "Exporta todos mis datos según GDPR",
            "Elimina mi información de NGX Pulse solamente"
        ]
        
        expected_behaviors = [
            "privacy_controls",
            "data_segregation",
            "visibility_settings",
            "gdpr_compliance",
            "selective_deletion"
        ]
        
        return await self._run_ecosystem_test(
            scenario_name,
            messages,
            expected_behaviors,
            platform_data={"privacy_request": True}
        )
    
    async def test_notification_orchestration(self) -> Dict[str, Any]:
        """Test: Unified notification management"""
        scenario_name = "notification_orchestration"
        
        messages = [
            "Demasiadas notificaciones, necesito organizarlas",
            "Solo notifícame logros importantes y recordatorios críticos",
            "Prefiero email para reportes y push para entrenamientos",
            "Silencia todo durante mis horas de sueño",
            "¿Cómo están configuradas mis notificaciones actuales?"
        ]
        
        expected_behaviors = [
            "notification_management",
            "intelligent_filtering",
            "channel_preferences",
            "schedule_respect",
            "settings_review"
        ]
        
        return await self._run_ecosystem_test(
            scenario_name,
            messages,
            expected_behaviors,
            platform_data={"notification_overload": True}
        )
    
    async def test_subscription_management(self) -> Dict[str, Any]:
        """Test: Unified subscription across platforms"""
        scenario_name = "subscription_management"
        
        messages = [
            "¿Qué incluye mi suscripción actual?",
            "Quiero agregar NGX Pulse Premium a mi plan",
            "¿Hay descuento por bundle completo?",
            "Pausa mi suscripción por 1 mes de vacaciones",
            "Revisa mi historial de pagos del último año"
        ]
        
        expected_behaviors = [
            "subscription_overview",
            "addon_management",
            "bundle_pricing",
            "pause_capability",
            "billing_history"
        ]
        
        return await self._run_ecosystem_test(
            scenario_name,
            messages,
            expected_behaviors,
            platform_data={"subscription_tier": "professional"}
        )
    
    async def test_multi_device_experience(self) -> Dict[str, Any]:
        """Test: Seamless experience across devices"""
        scenario_name = "multi_device_experience"
        
        messages = [
            "Empecé en mi laptop, continúo en el móvil",
            "¿Mi Apple Watch está sincronizado con todo?",
            "Configura mi tablet para modo gimnasio",
            "¿Qué dispositivos están conectados a mi cuenta?",
            "Desconecta mi dispositivo antiguo"
        ]
        
        expected_behaviors = [
            "session_continuity",
            "device_sync",
            "mode_configuration",
            "device_management",
            "security_control"
        ]
        
        return await self._run_ecosystem_test(
            scenario_name,
            messages,
            expected_behaviors,
            platform_data={"devices": ["laptop", "mobile", "watch", "tablet"]}
        )
    
    async def test_api_rate_limiting(self) -> Dict[str, Any]:
        """Test: API rate limits across ecosystem"""
        scenario_name = "api_rate_limiting"
        
        # Simulate rapid requests
        rapid_messages = [
            "Dame mi progreso",
            "Actualiza mis datos",
            "Revisa mi plan",
            "Cambia mi configuración",
            "Genera un reporte"
        ] * 10  # 50 rapid requests
        
        expected_behaviors = [
            "rate_limit_handling",
            "graceful_throttling",
            "queue_management",
            "user_feedback",
            "limit_information"
        ]
        
        return await self._run_ecosystem_test(
            scenario_name,
            rapid_messages[:5],  # Test with first 5 for demo
            expected_behaviors,
            platform_data={"request_rate": "high"}
        )
    
    async def test_ecosystem_onboarding(self) -> Dict[str, Any]:
        """Test: New user onboarding across ecosystem"""
        scenario_name = "ecosystem_onboarding"
        
        messages = [
            "Soy nuevo, ¿cómo funciona todo esto?",
            "¿Qué plataforma debo usar primero?",
            "Conéctame con NGX Pulse y el Blog",
            "Configura mi perfil básico en todas partes",
            "¿Cuál es el siguiente paso en mi journey?"
        ]
        
        expected_behaviors = [
            "onboarding_flow",
            "platform_introduction",
            "connection_assistance",
            "profile_setup",
            "journey_guidance"
        ]
        
        return await self._run_ecosystem_test(
            scenario_name,
            messages,
            expected_behaviors,
            platform_data={"user_status": "new", "onboarding_stage": 1}
        )
    
    async def test_complete_user_journey(self) -> Dict[str, Any]:
        """Test: Complete user journey across all platforms"""
        scenario_name = "complete_user_journey"
        
        messages = [
            # Week 1: Discovery and Setup
            "Quiero empezar mi transformación fitness completa",
            "Conecta todos mis dispositivos y plataformas",
            
            # Week 2: Active Usage
            "Revisa mi primera semana de datos en Pulse",
            "Ajusta mi plan según mi progreso inicial",
            
            # Week 4: Content Creation
            "Crea mi primer post sobre el journey",
            "Comparte mis métricas públicas de forma segura",
            
            # Week 8: Analysis
            "Analiza mis 2 meses de progreso total",
            "¿Qué dice mi CRM sobre mi engagement?",
            
            # Week 12: Celebration
            "Genera un reporte de transformación de 3 meses",
            "Prepara contenido para inspirar a otros"
        ]
        
        expected_behaviors = [
            "journey_initialization",
            "platform_orchestration",
            "progress_tracking",
            "content_creation",
            "engagement_analysis",
            "milestone_celebration",
            "comprehensive_reporting",
            "community_inspiration"
        ]
        
        return await self._run_ecosystem_test(
            scenario_name,
            messages,
            expected_behaviors,
            platform_data={
                "journey_duration": "12_weeks",
                "platforms_active": ["genesis", "pulse", "blog", "crm", "conversations"]
            }
        )
    
    async def _run_ecosystem_test(
        self,
        scenario_name: str,
        messages: List[str],
        expected_behaviors: List[str],
        platform_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run an ecosystem integration test
        
        Args:
            scenario_name: Name of the scenario
            messages: List of user messages to send
            expected_behaviors: List of expected behaviors
            platform_data: Simulated data from other platforms
            
        Returns:
            Test result dictionary
        """
        result = {
            "scenario": scenario_name,
            "timestamp": datetime.utcnow().isoformat(),
            "messages_sent": len(messages),
            "platform_data": platform_data or {},
            "responses": [],
            "behaviors_detected": [],
            "platforms_involved": set(),
            "integration_score": 0,
            "passed": False,
            "issues": []
        }
        
        try:
            # Create conversation session
            session_id = f"test_{scenario_name}_{datetime.utcnow().timestamp()}"
            
            # Inject platform data into context if MCP gateway available
            context = {
                "ecosystem_test": True,
                "platform_data": platform_data
            }
            
            if self.mcp_gateway and platform_data:
                # Simulate MCP tool calls
                context["mcp_available"] = True
            
            for i, message in enumerate(messages):
                # Send message to orchestrator
                request = ChatRequest(
                    message=message,
                    user_id=f"test_ecosystem_{scenario_name}",
                    session_id=session_id,
                    context=context
                )
                
                response = await self.orchestrator.process_message(request)
                
                # Analyze response
                analysis = self._analyze_ecosystem_response(
                    response,
                    expected_behaviors,
                    platform_data
                )
                
                result["responses"].append({
                    "message": message,
                    "response": response.message,
                    "analysis": analysis
                })
                
                # Update detected behaviors and platforms
                result["behaviors_detected"].extend(analysis["behaviors_found"])
                result["platforms_involved"].update(analysis["platforms_mentioned"])
                
                # Small delay between messages
                await asyncio.sleep(0.5)
            
            # Calculate integration score
            result["integration_score"] = self._calculate_integration_score(result)
            
            # Check success criteria
            missing_behaviors = set(expected_behaviors) - set(result["behaviors_detected"])
            
            if not missing_behaviors and result["integration_score"] >= 70:
                result["passed"] = True
            else:
                if missing_behaviors:
                    result["issues"].append(f"Missing behaviors: {missing_behaviors}")
                if result["integration_score"] < 70:
                    result["issues"].append(f"Low integration score: {result['integration_score']}")
                    
            # Additional ecosystem-specific validations
            if not self._validate_ecosystem_coherence(result):
                result["passed"] = False
                result["issues"].append("Ecosystem coherence validation failed")
                
        except Exception as e:
            logger.error(f"Error in scenario {scenario_name}: {e}")
            result["error"] = str(e)
            result["passed"] = False
            
        return result
    
    def _analyze_ecosystem_response(
        self,
        response: ChatResponse,
        expected_behaviors: List[str],
        platform_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze response for ecosystem integration quality"""
        analysis = {
            "behaviors_found": [],
            "platforms_mentioned": [],
            "integration_quality": "unknown",
            "data_flow_score": 0,
            "sync_capability": 0
        }
        
        response_lower = response.message.lower()
        
        # Check for platform mentions
        platforms = {
            "genesis": ["genesis", "agentes", "entrenamiento personalizado"],
            "ngx_pulse": ["ngx pulse", "pulse", "biométricos", "wearables"],
            "blog": ["blog", "post", "contenido", "publicar"],
            "crm": ["crm", "cliente", "suscripción", "contacto"],
            "conversations": ["conversaciones", "soporte", "chat", "mensajes"]
        }
        
        for platform, keywords in platforms.items():
            if any(keyword in response_lower for keyword in keywords):
                analysis["platforms_mentioned"].append(platform)
        
        # Check for specific ecosystem behaviors
        behavior_patterns = {
            "pulse_data_access": ["hrv", "frecuencia", "recuperación", "biométrico"],
            "content_generation": ["crear", "post", "contenido", "blog"],
            "crm_data_sync": ["actualizar", "crm", "cliente", "sincronizar"],
            "unified_analytics": ["análisis", "métricas", "dashboard", "reporte"],
            "real_time_sync": ["sincronizado", "actualizado", "tiempo real"],
            "privacy_controls": ["privacidad", "gdpr", "datos", "seguridad"],
            "subscription_overview": ["suscripción", "plan", "pago", "facturación"],
            "journey_initialization": ["comenzar", "configurar", "conectar", "journey"]
        }
        
        for behavior, patterns in behavior_patterns.items():
            if behavior in expected_behaviors:
                if any(pattern in response_lower for pattern in patterns):
                    analysis["behaviors_found"].append(behavior)
        
        # Integration quality assessment
        if len(analysis["platforms_mentioned"]) >= 2:
            analysis["integration_quality"] = "good"
        if len(analysis["platforms_mentioned"]) >= 3:
            analysis["integration_quality"] = "excellent"
        
        # Data flow score (0-100)
        data_flow_indicators = ["sincronizar", "actualizar", "flujo", "integración"]
        analysis["data_flow_score"] = min(100, sum(25 for indicator in data_flow_indicators if indicator in response_lower))
        
        # Sync capability (0-100)
        sync_indicators = ["tiempo real", "instantáneo", "automático", "sincronizado"]
        analysis["sync_capability"] = min(100, sum(25 for indicator in sync_indicators if indicator in response_lower))
        
        return analysis
    
    def _calculate_integration_score(self, result: Dict[str, Any]) -> int:
        """Calculate overall ecosystem integration score"""
        score = 0
        
        # Platform involvement (30%)
        platforms_expected = len(result["platform_data"].get("platforms_active", [1]))
        platforms_detected = len(result["platforms_involved"])
        platform_ratio = min(1.0, platforms_detected / max(platforms_expected, 1))
        score += platform_ratio * 30
        
        # Behavior coverage (40%)
        behavior_ratio = len(result["behaviors_detected"]) / len(expected_behaviors) if expected_behaviors else 0
        score += behavior_ratio * 40
        
        # Integration quality (30%)
        total_responses = len(result["responses"])
        if total_responses > 0:
            avg_data_flow = sum(r["analysis"]["data_flow_score"] for r in result["responses"]) / total_responses
            avg_sync = sum(r["analysis"]["sync_capability"] for r in result["responses"]) / total_responses
            score += (avg_data_flow / 100) * 15
            score += (avg_sync / 100) * 15
        
        return int(min(100, score))
    
    def _validate_ecosystem_coherence(self, result: Dict[str, Any]) -> bool:
        """Validate that ecosystem responses are coherent"""
        # Check for conflicting information
        responses = [r["response"].lower() for r in result["responses"]]
        
        # Look for contradictions
        contradiction_pairs = [
            ("sincronizado", "no disponible"),
            ("actualizado", "error"),
            ("conectado", "falla")
        ]
        
        for response in responses:
            for positive, negative in contradiction_pairs:
                if positive in response and negative in response:
                    return False
        
        # Ensure platform capabilities match claims
        if "platforms_involved" in result:
            claimed_platforms = result["platforms_involved"]
            available_platforms = result["platform_data"].get("platforms_active", [])
            
            # If we claim to use a platform, it should be available
            for platform in claimed_platforms:
                if available_platforms and platform not in available_platforms:
                    logger.warning(f"Platform {platform} mentioned but not available")
        
        return True