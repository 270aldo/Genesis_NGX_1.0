"""
Intent Analysis Skill
====================

Analyzes user intent and determines routing strategy.
"""

from typing import Dict, Any, List, Optional
import json

from agents.base.base_skill import BaseSkill
from core.logging_config import get_logger

logger = get_logger(__name__)


class IntentAnalysisSkill(BaseSkill):
    """Skill for analyzing user intent and determining agent routing."""
    
    def __init__(self, vertex_client, intent_patterns: Dict[str, List[str]]):
        super().__init__(
            name="intent_analysis",
            description="Analyzes user intent and determines appropriate agents"
        )
        self.vertex_client = vertex_client
        self.intent_patterns = intent_patterns
    
    async def execute(self, request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze user intent from their request.
        
        Args:
            request: User's input text
            context: Additional context (user profile, history, etc.)
            
        Returns:
            Intent analysis with recommended agents
        """
        try:
            # First try pattern matching for common intents
            quick_match = self._quick_pattern_match(request.lower())
            if quick_match and quick_match.get("confidence", 0) > 0.8:
                logger.info(f"Quick pattern match found: {quick_match['primary_intent']}")
                return quick_match
            
            # Use AI for complex intent analysis
            prompt = self._build_analysis_prompt(request, context)
            
            response = await self.vertex_client.generate_content(
                prompt,
                temperature=0.3  # Low temperature for consistent analysis
            )
            
            # Parse response
            try:
                analysis = json.loads(response.get("text", "{}"))
            except json.JSONDecodeError:
                # Fallback parsing
                analysis = self._parse_text_response(response.get("text", ""))
            
            # Validate and enhance analysis
            analysis = self._validate_analysis(analysis, request)
            
            # Add confidence score
            analysis["confidence"] = self._calculate_confidence(analysis, quick_match)
            
            return {
                "success": True,
                "analysis": analysis,
                "method": "ai_analysis" if not quick_match else "hybrid"
            }
            
        except Exception as e:
            logger.error(f"Intent analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "fallback": self._get_fallback_analysis(request)
            }
    
    def _quick_pattern_match(self, request_lower: str) -> Optional[Dict[str, Any]]:
        """Quick pattern matching for common intents."""
        # Direct agent mentions
        agent_patterns = {
            "blaze": ["blaze", "entrenamiento", "ejercicio", "workout", "training"],
            "sage": ["sage", "nutrición", "dieta", "comida", "meal", "nutrition"],
            "luna": ["luna", "femenina", "menstrual", "hormonal", "female"],
            "stella": ["stella", "progreso", "métricas", "tracking", "progress"],
            "spark": ["spark", "motivación", "hábitos", "mindset", "motivation"],
            "nova": ["nova", "biohacking", "suplementos", "optimization"],
            "wave": ["wave", "analytics", "análisis", "performance"],
            "code": ["code", "genética", "adn", "genetic", "genes"]
        }
        
        matches = []
        for agent, patterns in agent_patterns.items():
            for pattern in patterns:
                if pattern in request_lower:
                    matches.append({
                        "agent": agent,
                        "pattern": pattern,
                        "score": len(pattern) / len(request_lower)
                    })
        
        if not matches:
            return None
        
        # Sort by score
        matches.sort(key=lambda x: x["score"], reverse=True)
        best_match = matches[0]
        
        # Map to intent
        agent_to_intent = {
            "blaze": "training_query",
            "sage": "nutrition_query",
            "luna": "female_health_query",
            "stella": "progress_query",
            "spark": "motivation_query",
            "nova": "biohacking_query",
            "wave": "analytics_query",
            "code": "genetic_query"
        }
        
        return {
            "primary_intent": agent_to_intent.get(best_match["agent"], "general"),
            "recommended_agents": [f"{best_match['agent']}_agent"],
            "confidence": min(0.9, 0.7 + best_match["score"]),
            "method": "pattern_match"
        }
    
    def _build_analysis_prompt(self, request: str, context: Optional[Dict[str, Any]]) -> str:
        """Build prompt for AI intent analysis."""
        context_info = ""
        if context:
            if context.get("user_program"):
                context_info += f"\nPrograma del usuario: {context['user_program']}"
            if context.get("recent_topics"):
                context_info += f"\nTemas recientes: {', '.join(context['recent_topics'])}"
            if context.get("user_goals"):
                context_info += f"\nObjetivos: {context['user_goals']}"
        
        return f"""Analiza esta solicitud y determina la intención principal:

Solicitud: "{request}"
{context_info}

Agentes disponibles y sus especialidades:
- blaze: Entrenamiento, ejercicios, planes de workout
- sage: Nutrición, dietas, planes de comidas
- luna: Salud femenina, ciclos hormonales
- stella: Seguimiento de progreso, métricas
- spark: Motivación, cambio de hábitos
- nova: Biohacking, optimización, suplementos
- wave: Análisis de rendimiento, estadísticas
- code: Genética, análisis de ADN

Responde en JSON:
{{
    "primary_intent": "categoria_principal",
    "secondary_intents": ["otras_categorias_relevantes"],
    "urgency": "high/medium/low",
    "emotional_state": "estado_emocional_detectado",
    "recommended_agents": ["agente1", "agente2"],
    "reasoning": "explicación breve",
    "keywords": ["palabras_clave_detectadas"]
}}"""
    
    def _validate_analysis(self, analysis: Dict[str, Any], request: str) -> Dict[str, Any]:
        """Validate and enhance the analysis."""
        # Ensure required fields
        required_fields = ["primary_intent", "recommended_agents"]
        for field in required_fields:
            if field not in analysis:
                analysis[field] = self._infer_field(field, request)
        
        # Validate agents exist
        valid_agents = [
            "elite_training_strategist",
            "precision_nutrition_architect",
            "female_wellness_coach",
            "progress_tracker",
            "motivation_behavior_coach",
            "nova_biohacking_innovator",
            "wave_performance_analytics",
            "code_genetic_specialist"
        ]
        
        analysis["recommended_agents"] = [
            agent for agent in analysis.get("recommended_agents", [])
            if agent in valid_agents or agent.replace("_agent", "") in [a.split("_")[0] for a in valid_agents]
        ]
        
        # Default to motivation coach if no agents found
        if not analysis["recommended_agents"]:
            analysis["recommended_agents"] = ["motivation_behavior_coach"]
            analysis["reasoning"] = "No specific intent detected, routing to general wellness coach"
        
        return analysis
    
    def _calculate_confidence(self, analysis: Dict[str, Any], quick_match: Optional[Dict[str, Any]]) -> float:
        """Calculate confidence score for the analysis."""
        confidence = 0.5  # Base confidence
        
        # Boost for clear intent
        if analysis.get("primary_intent") and analysis["primary_intent"] != "general":
            confidence += 0.2
        
        # Boost for multiple signals
        if len(analysis.get("keywords", [])) > 2:
            confidence += 0.1
        
        # Boost for urgency detection
        if analysis.get("urgency") in ["high", "low"]:
            confidence += 0.1
        
        # Boost if quick match agrees
        if quick_match and quick_match.get("primary_intent") == analysis.get("primary_intent"):
            confidence += 0.1
        
        return min(0.95, confidence)
    
    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """Parse non-JSON text response as fallback."""
        # Basic parsing logic
        result = {
            "primary_intent": "general",
            "recommended_agents": ["motivation_behavior_coach"],
            "method": "text_parse_fallback"
        }
        
        # Look for agent names in response
        agent_names = ["blaze", "sage", "luna", "stella", "spark", "nova", "wave", "code"]
        mentioned_agents = []
        
        text_lower = text.lower()
        for agent in agent_names:
            if agent in text_lower:
                mentioned_agents.append(f"{agent}_agent")
        
        if mentioned_agents:
            result["recommended_agents"] = mentioned_agents[:2]  # Max 2 agents
        
        return result
    
    def _infer_field(self, field: str, request: str) -> Any:
        """Infer missing field from request."""
        if field == "primary_intent":
            # Simple keyword-based inference
            request_lower = request.lower()
            if any(word in request_lower for word in ["entrenar", "ejercicio", "workout"]):
                return "training_query"
            elif any(word in request_lower for word in ["comer", "dieta", "nutrición"]):
                return "nutrition_query"
            else:
                return "general"
        
        elif field == "recommended_agents":
            # Default to motivation coach
            return ["motivation_behavior_coach"]
        
        return None
    
    def _get_fallback_analysis(self, request: str) -> Dict[str, Any]:
        """Get fallback analysis when main analysis fails."""
        return {
            "primary_intent": "general",
            "recommended_agents": ["motivation_behavior_coach"],
            "urgency": "medium",
            "confidence": 0.3,
            "method": "fallback",
            "reasoning": "Unable to analyze intent, routing to general assistance"
        }