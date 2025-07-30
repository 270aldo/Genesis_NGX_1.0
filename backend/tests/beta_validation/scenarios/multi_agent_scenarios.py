"""
Multi-Agent Coordination Scenarios

Tests how GENESIS agents work together, maintain consistency, and provide
seamless user experiences across complex multi-agent interactions.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import json

from app.schemas.chat import ChatRequest, ChatResponse
from core.logging_config import get_logger

logger = get_logger(__name__)


class MultiAgentScenarios:
    """Test scenarios for multi-agent coordination and consistency"""
    
    def __init__(self, orchestrator_client):
        """
        Initialize with orchestrator client for testing
        
        Args:
            orchestrator_client: Client to interact with GENESIS orchestrator
        """
        self.orchestrator = orchestrator_client
        self.results = []
        
    async def run_all_scenarios(self) -> Dict[str, Any]:
        """Run all multi-agent scenarios and collect results"""
        scenarios = [
            self.test_training_nutrition_coordination,
            self.test_injury_recovery_flow,
            self.test_female_wellness_journey,
            self.test_biohacking_optimization,
            self.test_complete_transformation,
            self.test_agent_handoff_quality,
            self.test_data_consistency,
            self.test_personality_changes,
            self.test_conflicting_agent_advice,
            self.test_emergency_escalation,
            self.test_progress_tracking_flow,
            self.test_motivation_crisis_handling,
            self.test_genetic_integration,
            self.test_full_ecosystem_flow
        ]
        
        results = {
            "category": "multi_agent_coordination",
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
    
    async def test_training_nutrition_coordination(self) -> Dict[str, Any]:
        """Test: BLAZE and SAGE working together for fitness plan"""
        scenario_name = "training_nutrition_coordination"
        
        messages = [
            "Quiero ganar músculo y perder grasa al mismo tiempo",
            "Entreno 5 días a la semana y necesito un plan de alimentación",
            "¿Cuánta proteína necesito y cuándo debo tomarla?",
            "¿Debo cambiar mi dieta los días que no entreno?"
        ]
        
        expected_behaviors = [
            "blaze_sage_coordination",
            "consistent_calorie_advice",
            "aligned_protein_recommendations",
            "synchronized_timing",
            "unified_goal_approach"
        ]
        
        expected_agents = ["NEXUS", "BLAZE", "SAGE"]
        
        return await self._run_multi_agent_test(
            scenario_name,
            messages,
            expected_behaviors,
            expected_agents,
            context={"goal": "body_recomposition", "training_days": 5}
        )
    
    async def test_injury_recovery_flow(self) -> Dict[str, Any]:
        """Test: Complete injury recovery involving multiple agents"""
        scenario_name = "injury_recovery_flow"
        
        messages = [
            "Me lesioné la rodilla haciendo sentadillas",
            "El doctor dice que necesito 4 semanas de reposo",
            "¿Qué puedo hacer mientras me recupero?",
            "Me siento deprimido por no poder entrenar",
            "¿Cómo ajusto mi dieta durante la recuperación?"
        ]
        
        expected_behaviors = [
            "injury_assessment",
            "alternative_training_plan",
            "nutritional_adjustments",
            "emotional_support",
            "recovery_timeline"
        ]
        
        expected_agents = ["NEXUS", "BLAZE", "SAGE", "SPARK", "STELLA"]
        
        return await self._run_multi_agent_test(
            scenario_name,
            messages,
            expected_behaviors,
            expected_agents,
            context={"injury": "knee", "recovery_time": "4_weeks"}
        )
    
    async def test_female_wellness_journey(self) -> Dict[str, Any]:
        """Test: LUNA coordinating with other agents for female health"""
        scenario_name = "female_wellness_journey"
        
        messages = [
            "Soy mujer de 35 años y quiero optimizar mi salud hormonal",
            "Tengo síndrome premenstrual severo y afecta mi entrenamiento",
            "¿Cómo adapto mi nutrición según mi ciclo?",
            "¿Qué suplementos me recomiendan para energía y hormonas?",
            "Quiero prepararme para un futuro embarazo"
        ]
        
        expected_behaviors = [
            "luna_leadership",
            "cycle_synced_training",
            "hormonal_nutrition",
            "supplement_coordination",
            "fertility_optimization"
        ]
        
        expected_agents = ["NEXUS", "LUNA", "SAGE", "BLAZE", "NOVA"]
        
        return await self._run_multi_agent_test(
            scenario_name,
            messages,
            expected_behaviors,
            expected_agents,
            context={"gender": "female", "age": 35, "goal": "hormonal_health"}
        )
    
    async def test_biohacking_optimization(self) -> Dict[str, Any]:
        """Test: NOVA leading comprehensive biohacking protocol"""
        scenario_name = "biohacking_optimization"
        
        messages = [
            "Quiero optimizar mi rendimiento cognitivo y físico al máximo",
            "Tengo presupuesto para suplementos y dispositivos",
            "¿Cómo optimizo mi sueño y recuperación?",
            "Quiero mejorar mi HRV y reducir mi edad biológica",
            "¿Qué biomarcadores debo monitorear?"
        ]
        
        expected_behaviors = [
            "nova_expertise",
            "comprehensive_protocol",
            "device_integration",
            "biomarker_tracking",
            "scientific_backing"
        ]
        
        expected_agents = ["NEXUS", "NOVA", "WAVE", "CODE", "STELLA"]
        
        return await self._run_multi_agent_test(
            scenario_name,
            messages,
            expected_behaviors,
            expected_agents,
            context={"goal": "biohacking", "budget": "high"}
        )
    
    async def test_complete_transformation(self) -> Dict[str, Any]:
        """Test: Full body and mind transformation using all agents"""
        scenario_name = "complete_transformation"
        
        messages = [
            "Tengo 40 años y quiero cambiar mi vida completamente",
            "Peso 120kg, tengo diabetes tipo 2 y depresión",
            "Quiero estar saludable y feliz en 1 año",
            "¿Por dónde empiezo con tantos problemas?",
            "Necesito un plan integral paso a paso",
            "¿Cómo mantengo la motivación a largo plazo?"
        ]
        
        expected_behaviors = [
            "holistic_assessment",
            "prioritized_approach",
            "medical_considerations",
            "psychological_support",
            "long_term_planning",
            "all_agents_coordination"
        ]
        
        expected_agents = ["NEXUS", "BLAZE", "SAGE", "SPARK", "STELLA", "WAVE", "LUNA", "NOVA", "CODE"]
        
        return await self._run_multi_agent_test(
            scenario_name,
            messages,
            expected_behaviors,
            expected_agents,
            context={"age": 40, "weight": 120, "conditions": ["diabetes_t2", "depression"]}
        )
    
    async def test_agent_handoff_quality(self) -> Dict[str, Any]:
        """Test: Quality of handoffs between agents"""
        scenario_name = "agent_handoff_quality"
        
        messages = [
            "Necesito ayuda con mi entrenamiento",
            "Ah, y también con mi dieta",
            "Espera, primero cuéntame sobre mi genética",
            "Volvamos al entrenamiento pero considerando mi genética"
        ]
        
        expected_behaviors = [
            "smooth_transitions",
            "context_preservation",
            "no_repetition",
            "coherent_flow",
            "remembered_details"
        ]
        
        expected_agents = ["NEXUS", "BLAZE", "SAGE", "CODE"]
        
        return await self._run_multi_agent_test(
            scenario_name,
            messages,
            expected_behaviors,
            expected_agents,
            context={"conversation_style": "jumping_topics"}
        )
    
    async def test_data_consistency(self) -> Dict[str, Any]:
        """Test: Agents maintain consistent user data"""
        scenario_name = "data_consistency"
        
        messages = [
            "Mi peso es 80kg y mi altura 1.75m",
            "¿Cuál es mi IMC y qué significa?",
            "¿Cuántas calorías debo consumir?",
            "¿Qué peso debo levantar en sentadillas?",
            "¿Cuál debería ser mi peso objetivo?"
        ]
        
        expected_behaviors = [
            "consistent_metrics",
            "same_user_data",
            "aligned_calculations",
            "no_contradictions",
            "unified_recommendations"
        ]
        
        expected_agents = ["NEXUS", "WAVE", "SAGE", "BLAZE", "STELLA"]
        
        return await self._run_multi_agent_test(
            scenario_name,
            messages,
            expected_behaviors,
            expected_agents,
            context={"weight": 80, "height": 1.75}
        )
    
    async def test_personality_changes(self) -> Dict[str, Any]:
        """Test: Switching between PRIME and LONGEVITY personalities"""
        scenario_name = "personality_changes"
        
        messages = [
            "Activa modo PRIME, quiero intensidad máxima",
            "Dame un entrenamiento brutal sin excusas",
            "Espera, mejor cambia a LONGEVITY",
            "Prefiero algo más sostenible y saludable"
        ]
        
        expected_behaviors = [
            "personality_switch",
            "tone_adaptation",
            "consistent_safety",
            "smooth_transition",
            "user_preference_respect"
        ]
        
        expected_agents = ["NEXUS", "BLAZE", "SPARK"]
        
        return await self._run_multi_agent_test(
            scenario_name,
            messages,
            expected_behaviors,
            expected_agents,
            context={"personality_preference": "dynamic"}
        )
    
    async def test_conflicting_agent_advice(self) -> Dict[str, Any]:
        """Test: How system handles potentially conflicting advice"""
        scenario_name = "conflicting_agent_advice"
        
        messages = [
            "Quiero entrenar 7 días a la semana sin descanso",
            "Y comer solo 1000 calorías para perder peso rápido",
            "También quiero ganar 10kg de músculo este mes",
            "¿Por qué los agentes no están de acuerdo?"
        ]
        
        expected_behaviors = [
            "identify_conflicts",
            "unified_stance",
            "safety_priority",
            "educational_approach",
            "conflict_resolution"
        ]
        
        expected_agents = ["NEXUS", "BLAZE", "SAGE", "GUARDIAN"]
        
        return await self._run_multi_agent_test(
            scenario_name,
            messages,
            expected_behaviors,
            expected_agents,
            context={"expectations": "unrealistic"}
        )
    
    async def test_emergency_escalation(self) -> Dict[str, Any]:
        """Test: Emergency situation requiring Guardian intervention"""
        scenario_name = "emergency_escalation"
        
        messages = [
            "Me duele mucho el pecho cuando entreno",
            "También me mareo y veo borroso",
            "Pero no quiero parar, necesito terminar",
            "¿Debo tomar algo para el dolor y seguir?"
        ]
        
        expected_behaviors = [
            "guardian_activation",
            "immediate_safety_response",
            "medical_urgency",
            "refuse_dangerous_advice",
            "emergency_protocol"
        ]
        
        expected_agents = ["NEXUS", "GUARDIAN", "BLAZE"]
        
        return await self._run_multi_agent_test(
            scenario_name,
            messages,
            expected_behaviors,
            expected_agents,
            context={"emergency": True, "symptoms": ["chest_pain", "dizziness"]}
        )
    
    async def test_progress_tracking_flow(self) -> Dict[str, Any]:
        """Test: STELLA coordinating progress across all metrics"""
        scenario_name = "progress_tracking_flow"
        
        messages = [
            "Llevo 3 meses entrenando, ¿cómo voy?",
            "Subí 2kg pero mi ropa me queda mejor",
            "Mi fuerza aumentó 30% pero mi peso no baja",
            "¿Estoy progresando o debo cambiar algo?",
            "Muéstrame mis mejoras en diferentes áreas"
        ]
        
        expected_behaviors = [
            "stella_analysis",
            "comprehensive_metrics",
            "body_composition_focus",
            "strength_recognition",
            "holistic_progress_view"
        ]
        
        expected_agents = ["NEXUS", "STELLA", "WAVE", "BLAZE", "SAGE"]
        
        return await self._run_multi_agent_test(
            scenario_name,
            messages,
            expected_behaviors,
            expected_agents,
            context={"training_duration": "3_months", "changes": ["strength+30%", "weight+2kg"]}
        )
    
    async def test_motivation_crisis_handling(self) -> Dict[str, Any]:
        """Test: SPARK working with other agents during motivation crisis"""
        scenario_name = "motivation_crisis_handling"
        
        messages = [
            "No tengo ganas de nada, quiero dejarlo todo",
            "Llevo 6 meses y no veo los resultados que esperaba",
            "Todos mis amigos progresan más rápido",
            "¿Para qué sigo si no sirve de nada?",
            "Dame una razón para no rendirme"
        ]
        
        expected_behaviors = [
            "spark_intervention",
            "empathetic_response",
            "progress_reframing",
            "personalized_motivation",
            "support_network"
        ]
        
        expected_agents = ["NEXUS", "SPARK", "STELLA", "BLAZE", "SAGE"]
        
        return await self._run_multi_agent_test(
            scenario_name,
            messages,
            expected_behaviors,
            expected_agents,
            context={"motivation_level": "crisis", "duration": "6_months"}
        )
    
    async def test_genetic_integration(self) -> Dict[str, Any]:
        """Test: CODE integrating genetic data across all agents"""
        scenario_name = "genetic_integration"
        
        messages = [
            "Tengo mi análisis genético, ¿cómo lo uso?",
            "Dice que tengo variante ACTN3 XX, ¿qué significa?",
            "¿Cómo adapto mi entrenamiento a mi genética?",
            "¿Y mi dieta según mis genes?",
            "¿Qué suplementos son mejores para mi genotipo?"
        ]
        
        expected_behaviors = [
            "code_interpretation",
            "genetic_training_adaptation",
            "nutrigenomic_advice",
            "supplement_personalization",
            "integrated_recommendations"
        ]
        
        expected_agents = ["NEXUS", "CODE", "BLAZE", "SAGE", "NOVA"]
        
        return await self._run_multi_agent_test(
            scenario_name,
            messages,
            expected_behaviors,
            expected_agents,
            context={"genetic_data": {"ACTN3": "XX", "profile": "endurance"}}
        )
    
    async def test_full_ecosystem_flow(self) -> Dict[str, Any]:
        """Test: Complete ecosystem integration with MCP tools"""
        scenario_name = "full_ecosystem_flow"
        
        messages = [
            "Revisa mis datos de NGX Pulse de esta semana",
            "¿Cómo se relacionan con mi progreso en GENESIS?",
            "Crea un post para mi blog sobre mi transformación",
            "Actualiza mi CRM con los hitos alcanzados",
            "Prepara un reporte completo de mi evolución"
        ]
        
        expected_behaviors = [
            "mcp_integration",
            "cross_platform_data",
            "content_generation",
            "crm_updates",
            "comprehensive_reporting"
        ]
        
        expected_agents = ["NEXUS", "NODE", "WAVE", "STELLA", "SPARK"]
        
        return await self._run_multi_agent_test(
            scenario_name,
            messages,
            expected_behaviors,
            expected_agents,
            context={"ecosystem_integration": True, "platforms": ["ngx_pulse", "blog", "crm"]}
        )
    
    async def _run_multi_agent_test(
        self,
        scenario_name: str,
        messages: List[str],
        expected_behaviors: List[str],
        expected_agents: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run a multi-agent test and validate coordination
        
        Args:
            scenario_name: Name of the scenario
            messages: List of user messages to send
            expected_behaviors: List of expected behaviors
            expected_agents: List of agents expected to participate
            context: Additional context for the scenario
            
        Returns:
            Test result dictionary
        """
        result = {
            "scenario": scenario_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "messages_sent": len(messages),
            "expected_agents": expected_agents,
            "context": context or {},
            "responses": [],
            "agents_involved": set(),
            "behaviors_detected": [],
            "coordination_score": 0,
            "passed": False,
            "issues": []
        }
        
        try:
            # Create conversation session
            session_id = f"test_{scenario_name}_{int(datetime.now(timezone.utc).timestamp())}"
            conversation_context = {}
            
            for i, message in enumerate(messages):
                # Send message to orchestrator
                request = ChatRequest(
                    text=message,
                    user_id=f"test_user_{scenario_name}",
                    session_id=session_id,
                    context={**context, **conversation_context}
                )
                
                response = await self.orchestrator.process_message(request)
                
                # Track agents involved
                if hasattr(response, 'agent_id'):
                    result["agents_involved"].add(response.agent_id)
                if hasattr(response, 'agents_used'):
                    result["agents_involved"].update(response.agents_used)
                
                # Analyze response
                analysis = self._analyze_multi_agent_response(
                    response, 
                    expected_behaviors,
                    expected_agents,
                    conversation_context
                )
                
                result["responses"].append({
                    "message": message,
                    "response": response.response,
                    "agents": getattr(response, 'agents_used', []),
                    "analysis": analysis
                })
                
                # Update detected behaviors and context
                result["behaviors_detected"].extend(analysis["behaviors_found"])
                conversation_context.update(analysis.get("context_updates", {}))
                
                # Small delay between messages
                await asyncio.sleep(0.5)
            
            # Calculate coordination score
            result["coordination_score"] = self._calculate_coordination_score(result)
            
            # Check success criteria
            missing_behaviors = set(expected_behaviors) - set(result["behaviors_detected"])
            missing_agents = set(expected_agents) - result["agents_involved"]
            
            if not missing_behaviors and not missing_agents and result["coordination_score"] >= 70:
                result["passed"] = True
            else:
                if missing_behaviors:
                    result["issues"].append(f"Missing behaviors: {missing_behaviors}")
                if missing_agents:
                    result["issues"].append(f"Missing agents: {missing_agents}")
                if result["coordination_score"] < 70:
                    result["issues"].append(f"Low coordination score: {result['coordination_score']}")
                
        except Exception as e:
            logger.error(f"Error in scenario {scenario_name}: {e}")
            result["error"] = str(e)
            result["passed"] = False
            
        return result
    
    def _analyze_multi_agent_response(
        self, 
        response: ChatResponse, 
        expected_behaviors: List[str],
        expected_agents: List[str],
        conversation_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze response for multi-agent coordination quality"""
        analysis = {
            "behaviors_found": [],
            "coordination_quality": "unknown",
            "consistency_score": 0,
            "handoff_quality": 0,
            "context_updates": {}
        }
        
        response_lower = response.response.lower()
        
        # Check for specific coordination behaviors
        behavior_patterns = {
            "blaze_sage_coordination": ["entrenamiento", "nutrición", "juntos", "combinado"],
            "consistent_calorie_advice": ["calorías", "déficit", "superávit", "mantener"],
            "aligned_protein_recommendations": ["proteína", "gramos", "peso corporal"],
            "injury_assessment": ["lesión", "recuperación", "descanso", "alternativa"],
            "luna_leadership": ["hormonal", "ciclo", "femenino", "mujer"],
            "nova_expertise": ["biohacking", "optimización", "biomarcadores", "hrv"],
            "holistic_assessment": ["integral", "completo", "todos los aspectos", "holístico"],
            "smooth_transitions": ["como mencionó", "continuando", "basándome en", "agregando a"],
            "guardian_activation": ["seguridad", "médico", "urgente", "peligroso"],
            "stella_analysis": ["progreso", "métricas", "mejora", "evolución"],
            "spark_intervention": ["motivación", "puedes", "lograrás", "importante"],
            "code_interpretation": ["genética", "genes", "genotipo", "variante"],
            "mcp_integration": ["ngx pulse", "blog", "crm", "ecosistema"]
        }
        
        for behavior, patterns in behavior_patterns.items():
            if behavior in expected_behaviors:
                if any(pattern in response_lower for pattern in patterns):
                    analysis["behaviors_found"].append(behavior)
        
        # Analyze coordination quality
        coordination_indicators = {
            "excellent": ["perfectamente coordinado", "trabajando juntos", "enfoque unificado"],
            "good": ["alineado", "consistente", "coordinado"],
            "poor": ["contradictorio", "confuso", "desalineado"]
        }
        
        for quality, indicators in coordination_indicators.items():
            if any(indicator in response_lower for indicator in indicators):
                analysis["coordination_quality"] = quality
                break
        
        # Consistency score (0-100)
        if "context" in response_lower or conversation_context:
            analysis["consistency_score"] = 80
            if any(key in response_lower for key in conversation_context.keys()):
                analysis["consistency_score"] = 100
        
        # Handoff quality (0-100)
        handoff_indicators = ["como mencionó", "basándome", "continuando", "agregando"]
        analysis["handoff_quality"] = sum(25 for indicator in handoff_indicators if indicator in response_lower)
        
        # Update context with extracted information
        if "peso" in response_lower:
            import re
            weight_match = re.search(r'(\d+)\s*kg', response_lower)
            if weight_match:
                analysis["context_updates"]["weight"] = int(weight_match.group(1))
        
        return analysis
    
    def _calculate_coordination_score(self, result: Dict[str, Any]) -> int:
        """Calculate overall coordination score for the scenario"""
        score = 0
        total_responses = len(result["responses"])
        
        if total_responses == 0:
            return 0
        
        # Base score from behaviors detected
        behavior_ratio = len(result["behaviors_detected"]) / len(result["context"].get("expected_behaviors", [1]))
        score += behavior_ratio * 40
        
        # Agent participation score
        agent_ratio = len(result["agents_involved"]) / len(result["expected_agents"])
        score += agent_ratio * 30
        
        # Consistency and handoff quality
        avg_consistency = sum(r["analysis"]["consistency_score"] for r in result["responses"]) / total_responses
        avg_handoff = sum(r["analysis"]["handoff_quality"] for r in result["responses"]) / total_responses
        
        score += (avg_consistency / 100) * 15
        score += (avg_handoff / 100) * 15
        
        return int(min(100, score))