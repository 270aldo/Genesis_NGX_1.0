# NGX Agents - Plantilla de Arquitectura Estándar A+

## 📋 **ESTRUCTURA DE ARCHIVOS OBLIGATORIA**

```
agents/{agent_name}/
├── __init__.py                     # Exports principales
├── agent.py                        # Coordinación principal (MAX 500 líneas)
├── core/
│   ├── __init__.py
│   ├── dependencies.py             # Inyección de dependencias
│   ├── config.py                   # Configuración del agente
│   ├── constants.py                # Constantes y defaults
│   └── exceptions.py               # Jerarquía de excepciones custom
├── skills/
│   ├── __init__.py
│   ├── core_skills.py              # Skills principales del dominio
│   ├── analysis_skills.py          # Skills de análisis/procesamiento
│   ├── conversational_skills.py    # Skills conversacionales
│   └── advanced_skills.py          # Skills especializados/AI
├── services/
│   ├── __init__.py
│   ├── {domain}_service.py         # Servicios específicos del dominio
│   └── integration_service.py      # Integraciones externas
├── validators/
│   ├── __init__.py
│   └── {domain}_validators.py      # Validadores específicos
├── schemas/
│   ├── __init__.py
│   ├── inputs.py                   # Esquemas de entrada
│   ├── outputs.py                  # Esquemas de salida
│   └── internal.py                 # Modelos internos
└── utils/
    ├── __init__.py
    ├── helpers.py                  # Funciones auxiliares
    └── formatters.py               # Formateadores de respuesta
```

## 🎯 **AGENT.PY PATTERN OBLIGATORIO**

```python
"""
{Agent Name} - {Agent Description}
Implements A+ level standards with comprehensive error handling, 
monitoring, and ultra-personalized responses.
"""

from typing import Dict, Any, Optional, List
import asyncio
from dataclasses import dataclass

from agents.base.adk_agent import ADKAgent
from core.personality.personality_adapter import PersonalityAdapter, PersonalityProfile
from core.telemetry import get_tracer
from .core.dependencies import AgentDependencies
from .core.exceptions import {Agent}Error
from .skills import SkillsManager

tracer = get_tracer(__name__)

@dataclass
class {Agent}Config:
    """Configuration for {Agent} agent."""
    max_response_time: float = 30.0
    retry_attempts: int = 3
    cache_ttl: int = 3600
    enable_personality_adaptation: bool = True

class {Agent}Agent(ADKAgent):
    """
    {Agent Description}
    
    A+ Level Features:
    - Ultra-personalized responses via PersonalityAdapter
    - Comprehensive error handling with circuit breakers
    - Performance monitoring and telemetry
    - Modular architecture with dependency injection
    - 85%+ test coverage with integration tests
    """
    
    def __init__(self, dependencies: AgentDependencies, config: {Agent}Config):
        super().__init__(name="{agent_id}")
        
        # Dependency injection
        self.dependencies = dependencies
        self.config = config
        
        # Core components
        self.personality_adapter = dependencies.personality_adapter
        self.skills_manager = SkillsManager(dependencies, config)
        
        # Telemetry
        self.tracer = tracer
        
        # Skills registration (auto-discovery)
        self._register_skills()
        
    async def initialize(self) -> None:
        """Initialize agent with A+ standards."""
        try:
            with self.tracer.start_as_current_span("agent_initialization"):
                await self.personality_adapter.initialize_profile(
                    agent_id="{agent_id}",
                    personality_type="{MBTI_TYPE}",
                    communication_style="{communication_style}",
                    expertise_areas=["{domain1}", "{domain2}"]
                )
                
                await self.skills_manager.initialize()
                
                self.logger.info(f"{self.name} agent initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.name}: {e}", exc_info=True)
            raise {Agent}Error(f"Initialization failed: {e}")
    
    def _register_skills(self) -> None:
        """Auto-register skills with A+ patterns."""
        self.skills_manager.auto_register_skills()
    
    async def handle_message(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle incoming message with A+ level processing.
        
        Features:
        - Ultra-personalized response adaptation
        - Comprehensive error handling
        - Performance monitoring
        - Audit logging
        """
        
        with self.tracer.start_as_current_span("message_handling") as span:
            try:
                # Add context metadata
                span.set_attributes({
                    "agent.name": self.name,
                    "message.length": len(message),
                    "context.keys": list(context.keys()) if context else []
                })
                
                # Process message
                response = await self.skills_manager.process_message(message, context)
                
                # Apply personality adaptation
                personalized_response = await self._apply_personality_adaptation(
                    response, context
                )
                
                # Audit logging
                await self._log_interaction(message, personalized_response, context)
                
                return personalized_response
                
            except {Agent}Error as e:
                self.logger.error(f"Agent error in {self.name}: {e}")
                return self._create_error_response(e)
            except Exception as e:
                self.logger.error(f"Unexpected error in {self.name}: {e}", exc_info=True)
                return self._create_fallback_response()
    
    async def _apply_personality_adaptation(
        self, 
        response: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Apply ultra-personalized adaptation."""
        
        if not self.config.enable_personality_adaptation:
            return response
            
        try:
            user_profile = await self._extract_user_profile(context)
            
            adapted_response = await self.personality_adapter.adapt_response(
                agent_id="{agent_id}",
                original_message=response.get("content", ""),
                user_profile=user_profile,
                context=context
            )
            
            # Merge adapted content
            response["content"] = adapted_response["adapted_message"]
            response["adaptation_metadata"] = adapted_response.get("metadata", {})
            
            return response
            
        except Exception as e:
            self.logger.warning(f"Personality adaptation failed: {e}")
            return response  # Fallback to original
    
    async def _extract_user_profile(
        self, 
        context: Optional[Dict[str, Any]]
    ) -> PersonalityProfile:
        """Extract user profile for personality adaptation."""
        # Implementation specific to agent
        pass
    
    def _create_error_response(self, error: {Agent}Error) -> Dict[str, Any]:
        """Create user-friendly error response."""
        return {
            "success": False,
            "error_type": error.__class__.__name__,
            "message": "I encountered an issue while processing your request. Please try again.",
            "suggestions": getattr(error, 'suggestions', []),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _create_fallback_response(self) -> Dict[str, Any]:
        """Create fallback response for unexpected errors."""
        return {
            "success": False,
            "message": "I'm experiencing technical difficulties. Please try again in a moment.",
            "fallback": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _log_interaction(
        self, 
        request: str, 
        response: Dict[str, Any], 
        context: Optional[Dict[str, Any]]
    ) -> None:
        """Log interaction for audit and analytics."""
        # Implementation for audit logging
        pass
```

## 🛡️ **ERROR HANDLING PATTERN OBLIGATORIO**

```python
# core/exceptions.py
class {Agent}Error(Exception):
    """Base exception for {Agent} agent."""
    
    def __init__(self, message: str, suggestions: Optional[List[str]] = None):
        super().__init__(message)
        self.suggestions = suggestions or []

class {Agent}ValidationError({Agent}Error):
    """Validation error in {Agent} processing."""
    pass

class {Agent}ProcessingError({Agent}Error):
    """Processing error in {Agent} logic."""
    pass

class {Agent}ExternalServiceError({Agent}Error):
    """External service integration error."""
    pass

# Circuit breaker pattern
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def _call_external_service(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """Call external service with retry logic."""
    try:
        # Service call implementation
        pass
    except Exception as e:
        raise {Agent}ExternalServiceError(f"External service failed: {e}")
```

## 🧪 **TESTING PATTERN OBLIGATORIO**

```python
# tests/agents/{agent_name}/conftest.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.{agent_name}.agent import {Agent}Agent
from agents.{agent_name}.core.dependencies import AgentDependencies
from agents.{agent_name}.core.config import {Agent}Config

@pytest.fixture
async def agent_dependencies():
    """Create mock dependencies for testing."""
    return AgentDependencies(
        personality_adapter=AsyncMock(),
        gemini_client=AsyncMock(),
        # ... other dependencies
    )

@pytest.fixture
async def agent_config():
    """Create test configuration."""
    return {Agent}Config(
        max_response_time=5.0,
        retry_attempts=1,
        enable_personality_adaptation=True
    )

@pytest.fixture
async def agent(agent_dependencies, agent_config):
    """Create agent instance for testing."""
    agent = {Agent}Agent(agent_dependencies, agent_config)
    await agent.initialize()
    return agent

# TARGET: 85%+ test coverage
# TYPES: Unit, Integration, Performance, Security
```

## 📊 **MÉTRICAS A+ OBLIGATORIAS**

- ✅ **Cobertura de Tests**: ≥ 85%
- ✅ **Tiempo de Respuesta**: ≤ 500ms (skills simples)
- ✅ **Tasa de Error**: ≤ 0.1%
- ✅ **Líneas por Archivo**: ≤ 500 líneas
- ✅ **Complejidad Ciclomática**: ≤ 10
- ✅ **Type Annotations**: 100%
- ✅ **Documentación**: ≥ 95% coverage

## 🔒 **SEGURIDAD A+ OBLIGATORIA**

- ✅ **Encriptación**: Datos sensibles end-to-end
- ✅ **Audit Logging**: Todas las interacciones registradas
- ✅ **Rate Limiting**: Protección contra abuso
- ✅ **Input Validation**: Sanitización completa
- ✅ **Error Sanitization**: No exposición de datos internos
- ✅ **GDPR/HIPAA**: Compliance según el dominio