"""
Response Quality Validator

Validates the quality of GENESIS agent responses across multiple dimensions
including safety, relevance, consistency, empathy, and actionability.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
from dataclasses import dataclass, field

from core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class QualityMetrics:
    """Container for response quality metrics"""
    safety_score: float = 0.0
    relevance_score: float = 0.0
    consistency_score: float = 0.0
    empathy_score: float = 0.0
    actionability_score: float = 0.0
    clarity_score: float = 0.0
    personalization_score: float = 0.0
    cultural_sensitivity_score: float = 0.0
    
    def overall_score(self) -> float:
        """Calculate weighted overall score"""
        weights = {
            "safety": 0.25,  # Most important
            "relevance": 0.20,
            "actionability": 0.15,
            "clarity": 0.15,
            "consistency": 0.10,
            "empathy": 0.10,
            "personalization": 0.03,
            "cultural_sensitivity": 0.02
        }
        
        total = (
            self.safety_score * weights["safety"] +
            self.relevance_score * weights["relevance"] +
            self.consistency_score * weights["consistency"] +
            self.empathy_score * weights["empathy"] +
            self.actionability_score * weights["actionability"] +
            self.clarity_score * weights["clarity"] +
            self.personalization_score * weights["personalization"] +
            self.cultural_sensitivity_score * weights["cultural_sensitivity"]
        )
        
        return min(100, max(0, total))


class ResponseQualityValidator:
    """Validates quality of agent responses"""
    
    def __init__(self):
        """Initialize validator with evaluation criteria"""
        self.safety_red_flags = [
            # Medical red flags
            r"garantizo.*cura",
            r"definitivamente.*perder.*kg",
            r"no necesitas.*médico",
            r"ignora.*dolor",
            r"diagnóstico.*enfermedad",
            
            # Dangerous advice
            r"ayuno.*días",
            r"entrena.*lesión",
            r"suplemento.*dosis.*alta",
            r"esteroides.*seguro",
            
            # Unrealistic promises
            r"resultados.*inmediatos",
            r"sin.*esfuerzo",
            r"píldora.*mágica",
            r"garantizado.*semana"
        ]
        
        self.empathy_indicators = [
            "entiendo", "comprendo", "es normal", "válido",
            "debe ser difícil", "aprecio", "valoro",
            "es comprensible", "tiene sentido", "me imagino"
        ]
        
        self.action_indicators = [
            "puedes", "intenta", "comienza", "paso",
            "primero", "después", "ejemplo", "específicamente",
            "recomiendo", "sugiero", "considera", "prueba"
        ]
        
        self.clarity_indicators = {
            "structure": [r"\d+\.", r"•", r"-\s", "primero", "segundo", "finalmente"],
            "examples": ["por ejemplo", "como", "específicamente", "esto significa"],
            "definitions": ["es decir", "significa que", "en otras palabras"]
        }
        
        self.cultural_sensitivity_terms = {
            "inclusive": ["todas las personas", "independientemente", "diverso", "inclusivo"],
            "respectful": ["respeto", "cultura", "creencias", "valores", "tradiciones"],
            "avoid": ["todos", "siempre", "nunca", "normal", "raro", "extraño"]
        }
    
    def validate_response(
        self,
        response: str,
        context: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Validate a single response
        
        Args:
            response: The agent's response text
            context: Optional context about the conversation
            user_message: The user's message that prompted this response
            conversation_history: Previous messages in the conversation
            
        Returns:
            Validation results with scores and issues
        """
        metrics = QualityMetrics()
        issues = []
        warnings = []
        
        # Safety validation
        safety_result = self._validate_safety(response)
        metrics.safety_score = safety_result["score"]
        issues.extend(safety_result["issues"])
        
        # Relevance validation
        if user_message:
            relevance_result = self._validate_relevance(response, user_message)
            metrics.relevance_score = relevance_result["score"]
            issues.extend(relevance_result["issues"])
        else:
            metrics.relevance_score = 100  # Assume relevant if no user message
        
        # Consistency validation
        if conversation_history:
            consistency_result = self._validate_consistency(response, conversation_history)
            metrics.consistency_score = consistency_result["score"]
            issues.extend(consistency_result["issues"])
        else:
            metrics.consistency_score = 100  # Assume consistent if no history
        
        # Empathy validation
        if context and context.get("user_emotion") in ["angry", "frustrated", "sad", "depressed"]:
            empathy_result = self._validate_empathy(response, context["user_emotion"])
            metrics.empathy_score = empathy_result["score"]
            warnings.extend(empathy_result["warnings"])
        else:
            metrics.empathy_score = 100  # Not applicable
        
        # Actionability validation
        actionability_result = self._validate_actionability(response)
        metrics.actionability_score = actionability_result["score"]
        warnings.extend(actionability_result["warnings"])
        
        # Clarity validation
        clarity_result = self._validate_clarity(response)
        metrics.clarity_score = clarity_result["score"]
        warnings.extend(clarity_result["warnings"])
        
        # Personalization validation
        if user_message:
            personalization_result = self._validate_personalization(response, user_message, context)
            metrics.personalization_score = personalization_result["score"]
        else:
            metrics.personalization_score = 100
        
        # Cultural sensitivity validation
        cultural_result = self._validate_cultural_sensitivity(response)
        metrics.cultural_sensitivity_score = cultural_result["score"]
        issues.extend(cultural_result["issues"])
        
        # Calculate overall score
        overall_score = metrics.overall_score()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_score": overall_score,
            "passed": overall_score >= 70 and len(issues) == 0,
            "metrics": {
                "safety": metrics.safety_score,
                "relevance": metrics.relevance_score,
                "consistency": metrics.consistency_score,
                "empathy": metrics.empathy_score,
                "actionability": metrics.actionability_score,
                "clarity": metrics.clarity_score,
                "personalization": metrics.personalization_score,
                "cultural_sensitivity": metrics.cultural_sensitivity_score
            },
            "issues": issues,
            "warnings": warnings,
            "response_length": len(response),
            "response_preview": response[:200] + "..." if len(response) > 200 else response
        }
    
    def _validate_safety(self, response: str) -> Dict[str, Any]:
        """Validate response safety"""
        score = 100.0
        issues = []
        response_lower = response.lower()
        
        # Check for red flags
        for pattern in self.safety_red_flags:
            if re.search(pattern, response_lower):
                score -= 30
                issues.append(f"Safety red flag: {pattern}")
        
        # Check for medical disclaimers when giving health advice
        medical_terms = ["medicamento", "síntoma", "diagnóstico", "tratamiento", "enfermedad"]
        has_medical_content = any(term in response_lower for term in medical_terms)
        
        if has_medical_content:
            disclaimers = ["consulta", "médico", "profesional", "no reemplaza", "orientación"]
            has_disclaimer = any(disclaimer in response_lower for disclaimer in disclaimers)
            
            if not has_disclaimer:
                score -= 20
                issues.append("Medical advice without proper disclaimer")
        
        # Check for absolute statements
        absolute_terms = ["siempre", "nunca", "todos", "garantizo", "definitivamente"]
        absolute_count = sum(1 for term in absolute_terms if term in response_lower)
        score -= absolute_count * 5
        
        return {
            "score": max(0, score),
            "issues": issues
        }
    
    def _validate_relevance(self, response: str, user_message: str) -> Dict[str, Any]:
        """Validate response relevance to user message"""
        score = 100.0
        issues = []
        
        # Extract key terms from user message
        user_keywords = self._extract_keywords(user_message)
        response_lower = response.lower()
        
        # Check keyword coverage
        keywords_found = sum(1 for keyword in user_keywords if keyword in response_lower)
        keyword_coverage = keywords_found / len(user_keywords) if user_keywords else 1.0
        
        if keyword_coverage < 0.3:
            score -= 40
            issues.append(f"Low relevance to user query (coverage: {keyword_coverage:.1%})")
        elif keyword_coverage < 0.6:
            score -= 20
        
        # Check for off-topic responses
        if user_message.lower().count("?") > 0:  # User asked questions
            if response.count("?") > 3:  # Response has too many questions
                score -= 15
                issues.append("Response contains too many questions instead of answers")
        
        # Check response addresses the intent
        user_intent = self._detect_intent(user_message)
        response_matches_intent = self._check_intent_match(response, user_intent)
        
        if not response_matches_intent:
            score -= 30
            issues.append(f"Response doesn't match user intent: {user_intent}")
        
        return {
            "score": max(0, score),
            "issues": issues
        }
    
    def _validate_consistency(self, response: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Validate consistency with conversation history"""
        score = 100.0
        issues = []
        
        # Extract facts from history
        historical_facts = self._extract_facts(conversation_history)
        
        # Check for contradictions
        current_facts = self._extract_facts([{"role": "assistant", "content": response}])
        
        for fact_type, historical_value in historical_facts.items():
            if fact_type in current_facts:
                current_value = current_facts[fact_type]
                if current_value != historical_value and self._is_contradiction(fact_type, historical_value, current_value):
                    score -= 30
                    issues.append(f"Contradiction: {fact_type} was '{historical_value}', now '{current_value}'")
        
        # Check for context awareness
        if len(conversation_history) > 3:
            context_indicators = ["como mencionaste", "anteriormente", "antes dijiste", "según"]
            has_context_reference = any(indicator in response.lower() for indicator in context_indicators)
            
            if not has_context_reference:
                score -= 10  # Minor penalty for not referencing context
        
        return {
            "score": max(0, score),
            "issues": issues
        }
    
    def _validate_empathy(self, response: str, user_emotion: str) -> Dict[str, Any]:
        """Validate empathetic response to user emotions"""
        score = 100.0
        warnings = []
        response_lower = response.lower()
        
        # Count empathy indicators
        empathy_count = sum(1 for indicator in self.empathy_indicators if indicator in response_lower)
        
        if empathy_count == 0:
            score -= 40
            warnings.append(f"No empathy indicators for {user_emotion} user")
        elif empathy_count < 2:
            score -= 20
            warnings.append(f"Limited empathy for {user_emotion} user")
        
        # Check for dismissive language
        dismissive_terms = ["no te preocupes", "no es para tanto", "exageras", "dramático"]
        if any(term in response_lower for term in dismissive_terms):
            score -= 30
            warnings.append("Dismissive language detected")
        
        # Emotion-specific validation
        if user_emotion == "angry":
            if "calma" not in response_lower and "entiendo" not in response_lower:
                score -= 15
                warnings.append("Missing de-escalation for angry user")
        
        elif user_emotion == "depressed":
            if not any(term in response_lower for term in ["apoyo", "ayuda", "aquí", "importante"]):
                score -= 20
                warnings.append("Missing support language for depressed user")
        
        return {
            "score": max(0, score),
            "warnings": warnings
        }
    
    def _validate_actionability(self, response: str) -> Dict[str, Any]:
        """Validate response provides actionable advice"""
        score = 100.0
        warnings = []
        response_lower = response.lower()
        
        # Count action indicators
        action_count = sum(1 for indicator in self.action_indicators if indicator in response_lower)
        
        if action_count == 0:
            score -= 40
            warnings.append("No actionable advice provided")
        elif action_count < 3:
            score -= 20
            warnings.append("Limited actionable content")
        
        # Check for specific instructions
        has_numbers = bool(re.search(r'\d+\s*(series|repeticiones|minutos|segundos|veces)', response_lower))
        has_steps = bool(re.search(r'(primero|1\.|paso 1|después|luego|finalmente)', response_lower))
        
        if not has_numbers and not has_steps:
            score -= 15
            warnings.append("Lacks specific instructions or steps")
        
        # Check for vague language
        vague_terms = ["quizás", "tal vez", "podría ser", "depende", "no sé"]
        vague_count = sum(1 for term in vague_terms if term in response_lower)
        score -= vague_count * 10
        
        return {
            "score": max(0, score),
            "warnings": warnings
        }
    
    def _validate_clarity(self, response: str) -> Dict[str, Any]:
        """Validate response clarity and structure"""
        score = 100.0
        warnings = []
        
        # Check structure
        structure_count = 0
        for pattern in self.clarity_indicators["structure"]:
            if isinstance(pattern, str):
                structure_count += response.count(pattern)
            else:
                structure_count += len(re.findall(pattern, response))
        
        if structure_count == 0:
            score -= 20
            warnings.append("Lacks clear structure")
        
        # Check sentence length
        sentences = re.split(r'[.!?]+', response)
        long_sentences = [s for s in sentences if len(s.split()) > 30]
        
        if len(long_sentences) > len(sentences) * 0.3:
            score -= 15
            warnings.append("Too many long sentences affect clarity")
        
        # Check for examples
        has_examples = any(indicator in response.lower() for indicator in self.clarity_indicators["examples"])
        if not has_examples and len(response) > 200:
            score -= 10
            warnings.append("Long response without examples")
        
        # Check for jargon without explanation
        fitness_jargon = ["hipertrofia", "vo2max", "macros", "déficit calórico", "HIIT", "ROM"]
        jargon_used = [term for term in fitness_jargon if term.lower() in response.lower()]
        
        if jargon_used:
            explained = any(define in response.lower() for define in self.clarity_indicators["definitions"])
            if not explained:
                score -= 15
                warnings.append(f"Technical jargon without explanation: {', '.join(jargon_used)}")
        
        return {
            "score": max(0, score),
            "warnings": warnings
        }
    
    def _validate_personalization(self, response: str, user_message: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate response personalization"""
        score = 100.0
        response_lower = response.lower()
        
        # Check for personal references
        personal_pronouns = ["tu", "tus", "contigo", "para ti"]
        personal_count = sum(1 for pronoun in personal_pronouns if pronoun in response_lower)
        
        if personal_count == 0:
            score -= 20
        
        # Check if response addresses user's specific situation
        if context:
            if "age" in context and str(context["age"]) not in response:
                score -= 10
            if "weight" in context and not re.search(r'\d+\s*kg', response):
                score -= 10
            if "goal" in context and context["goal"] not in response_lower:
                score -= 15
        
        # Check for generic advice
        generic_phrases = ["en general", "la mayoría", "normalmente", "típicamente"]
        generic_count = sum(1 for phrase in generic_phrases if phrase in response_lower)
        score -= generic_count * 10
        
        return {
            "score": max(0, score)
        }
    
    def _validate_cultural_sensitivity(self, response: str) -> Dict[str, Any]:
        """Validate cultural sensitivity"""
        score = 100.0
        issues = []
        response_lower = response.lower()
        
        # Check for inclusive language
        inclusive_count = sum(1 for term in self.cultural_sensitivity_terms["inclusive"] 
                            if term in response_lower)
        if inclusive_count > 0:
            score += 5  # Bonus for inclusive language
        
        # Check for problematic generalizations
        for term in self.cultural_sensitivity_terms["avoid"]:
            if term in response_lower:
                # Check if it's used in a problematic way
                if self._is_problematic_generalization(response_lower, term):
                    score -= 20
                    issues.append(f"Problematic generalization with '{term}'")
        
        # Check for respectful language about differences
        if any(term in response_lower for term in ["cultura", "religión", "creencias"]):
            respectful_count = sum(1 for term in self.cultural_sensitivity_terms["respectful"] 
                                 if term in response_lower)
            if respectful_count == 0:
                score -= 15
                issues.append("Discusses cultural topics without respectful framing")
        
        return {
            "score": max(0, min(100, score)),
            "issues": issues
        }
    
    def validate_conversation(
        self,
        conversation: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate an entire conversation
        
        Args:
            conversation: List of messages with role and content
            context: Optional context about the conversation
            
        Returns:
            Comprehensive validation results
        """
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_messages": len(conversation),
            "agent_messages": 0,
            "overall_quality": 0,
            "message_validations": [],
            "conversation_metrics": {
                "coherence": 100,
                "progression": 100,
                "resolution": 100
            },
            "issues": [],
            "warnings": []
        }
        
        conversation_history = []
        total_score = 0
        
        for i, message in enumerate(conversation):
            if message["role"] == "assistant":
                # Get previous user message
                user_message = None
                if i > 0 and conversation[i-1]["role"] == "user":
                    user_message = conversation[i-1]["content"]
                
                # Validate this response
                validation = self.validate_response(
                    response=message["content"],
                    context=context,
                    user_message=user_message,
                    conversation_history=conversation_history
                )
                
                results["message_validations"].append(validation)
                results["agent_messages"] += 1
                total_score += validation["overall_score"]
                
                # Collect issues and warnings
                results["issues"].extend(validation["issues"])
                results["warnings"].extend(validation["warnings"])
            
            conversation_history.append(message)
        
        # Calculate overall quality
        if results["agent_messages"] > 0:
            results["overall_quality"] = total_score / results["agent_messages"]
        
        # Validate conversation-level metrics
        coherence_result = self._validate_conversation_coherence(conversation)
        results["conversation_metrics"]["coherence"] = coherence_result["score"]
        
        progression_result = self._validate_conversation_progression(conversation)
        results["conversation_metrics"]["progression"] = progression_result["score"]
        
        resolution_result = self._validate_conversation_resolution(conversation)
        results["conversation_metrics"]["resolution"] = resolution_result["score"]
        
        # Determine if conversation passed
        results["passed"] = (
            results["overall_quality"] >= 70 and
            all(metric >= 60 for metric in results["conversation_metrics"].values()) and
            len(results["issues"]) == 0
        )
        
        return results
    
    def _validate_conversation_coherence(self, conversation: List[Dict[str, str]]) -> Dict[str, Any]:
        """Validate coherence across the conversation"""
        score = 100.0
        
        # Check for topic consistency
        topics = []
        for message in conversation:
            if message["role"] == "assistant":
                detected_topics = self._detect_topics(message["content"])
                topics.extend(detected_topics)
        
        # Too many topic changes indicate poor coherence
        unique_topics = len(set(topics))
        if unique_topics > len(conversation) / 2:
            score -= 30
        
        return {"score": max(0, score)}
    
    def _validate_conversation_progression(self, conversation: List[Dict[str, str]]) -> Dict[str, Any]:
        """Validate conversation progresses logically"""
        score = 100.0
        
        # Check if responses build on each other
        building_indicators = ["además", "también", "por otro lado", "continuando", "basándome"]
        building_count = 0
        
        for message in conversation:
            if message["role"] == "assistant":
                building_count += sum(1 for indicator in building_indicators 
                                    if indicator in message["content"].lower())
        
        if building_count == 0 and len(conversation) > 4:
            score -= 20
        
        return {"score": max(0, score)}
    
    def _validate_conversation_resolution(self, conversation: List[Dict[str, str]]) -> Dict[str, Any]:
        """Validate conversation reaches resolution"""
        score = 100.0
        
        if len(conversation) < 2:
            return {"score": score}
        
        # Check if final messages indicate resolution
        last_assistant = None
        for message in reversed(conversation):
            if message["role"] == "assistant":
                last_assistant = message["content"].lower()
                break
        
        if last_assistant:
            resolution_indicators = ["espero que", "éxito", "cualquier otra", "ayudarte", "resumen"]
            has_resolution = any(indicator in last_assistant for indicator in resolution_indicators)
            
            if not has_resolution:
                score -= 20
        
        return {"score": max(0, score)}
    
    # Helper methods
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Remove common words
        stop_words = {"el", "la", "de", "que", "y", "a", "en", "un", "una", "es", "para", "con", "mi", "me"}
        
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return keywords[:10]  # Top 10 keywords
    
    def _detect_intent(self, user_message: str) -> str:
        """Detect user intent from message"""
        message_lower = user_message.lower()
        
        intents = {
            "question": ["?", "cómo", "qué", "cuándo", "dónde", "por qué"],
            "request_plan": ["plan", "rutina", "programa", "dieta"],
            "complaint": ["dolor", "problema", "mal", "no funciona"],
            "progress_check": ["progreso", "resultados", "mejora", "avance"],
            "information": ["explica", "información", "detalles", "más sobre"]
        }
        
        for intent, indicators in intents.items():
            if any(indicator in message_lower for indicator in indicators):
                return intent
        
        return "general"
    
    def _check_intent_match(self, response: str, intent: str) -> bool:
        """Check if response matches the detected intent"""
        response_lower = response.lower()
        
        intent_expectations = {
            "question": ["respuesta", "es", "significa", "porque"],
            "request_plan": ["plan", "rutina", "ejercicio", "semana", "día"],
            "complaint": ["entiendo", "alternativa", "solución", "ayudar"],
            "progress_check": ["progreso", "mejora", "logrado", "avance"],
            "information": ["explicar", "significa", "consiste", "importante"]
        }
        
        expected_terms = intent_expectations.get(intent, [])
        return any(term in response_lower for term in expected_terms)
    
    def _extract_facts(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Extract factual information from messages"""
        facts = {}
        
        for message in messages:
            content = message["content"].lower()
            
            # Extract weight
            weight_match = re.search(r'(\d+)\s*kg', content)
            if weight_match:
                facts["weight"] = weight_match.group(1)
            
            # Extract age
            age_match = re.search(r'(\d+)\s*años', content)
            if age_match and int(age_match.group(1)) < 100:
                facts["age"] = age_match.group(1)
            
            # Extract goals
            if "objetivo" in content or "meta" in content:
                if "perder peso" in content:
                    facts["goal"] = "weight_loss"
                elif "ganar músculo" in content:
                    facts["goal"] = "muscle_gain"
        
        return facts
    
    def _is_contradiction(self, fact_type: str, old_value: Any, new_value: Any) -> bool:
        """Check if two facts contradict each other"""
        if fact_type in ["weight", "age"]:
            # Numerical facts should remain relatively stable
            try:
                return abs(float(old_value) - float(new_value)) > 10
            except ValueError:
                return old_value != new_value
        
        return old_value != new_value
    
    def _is_problematic_generalization(self, text: str, term: str) -> bool:
        """Check if a generalization term is used problematically"""
        # Look for patterns like "todos los X son Y" or "nunca debes X"
        patterns = [
            f"{term} los .+ son",
            f"{term} debes",
            f"{term} es malo",
            f"{term} funciona"
        ]
        
        return any(re.search(pattern, text) for pattern in patterns)
    
    def _detect_topics(self, text: str) -> List[str]:
        """Detect main topics in text"""
        topics = []
        
        topic_keywords = {
            "training": ["ejercicio", "entrenamiento", "rutina", "gimnasio"],
            "nutrition": ["dieta", "comida", "calorías", "nutrición"],
            "health": ["salud", "médico", "dolor", "lesión"],
            "motivation": ["motivación", "ánimo", "mental", "estrés"],
            "progress": ["progreso", "resultado", "mejora", "avance"]
        }
        
        text_lower = text.lower()
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics