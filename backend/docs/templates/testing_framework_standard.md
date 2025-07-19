# NGX Agents - Framework de Testing Estándar A+

## 🎯 **OBJETIVO: 85%+ COVERAGE OBLIGATORIO**

### 📊 **MÉTRICAS DE TESTING A+**
- **Cobertura de Líneas**: ≥ 85%
- **Cobertura de Ramas**: ≥ 80%
- **Cobertura de Funciones**: ≥ 90%
- **Tests de Mutación**: ≥ 75%

## 🏗️ **ESTRUCTURA OBLIGATORIA DE TESTING**

```
tests/agents/{agent_name}/
├── conftest.py                     # Fixtures comunes
├── unit/
│   ├── test_core_skills.py         # Skills principales
│   ├── test_analysis_skills.py     # Skills de análisis
│   ├── test_conversational_skills.py
│   ├── test_personality_adapter.py  # PersonalityAdapter
│   ├── test_error_handling.py      # Manejo de errores
│   └── test_validation.py          # Validaciones
├── integration/
│   ├── test_skill_chains.py        # Workflows multi-skill
│   ├── test_external_apis.py       # APIs externas
│   ├── test_personality_flows.py   # Flujos PRIME/LONGEVITY
│   └── test_full_agent_flows.py    # End-to-end
├── performance/
│   ├── test_load_scenarios.py      # Testing de carga
│   ├── test_response_times.py      # Benchmarks de tiempo
│   └── test_memory_usage.py        # Uso de memoria
├── security/
│   ├── test_input_sanitization.py  # Sanitización de entrada
│   ├── test_data_encryption.py     # Encriptación
│   └── test_audit_logging.py       # Logging de auditoría
├── fixtures/
│   ├── sample_data.py              # Datos de prueba
│   ├── mock_responses.py           # Respuestas mock
│   └── test_profiles.py            # Perfiles de usuario
└── property_based/
    ├── test_input_properties.py    # Property-based testing
    └── test_output_invariants.py   # Invariantes de salida
```

## 🧪 **PATRONES DE TESTING OBLIGATORIOS**

### **1. CONFTEST.PY - FIXTURES BASE**

```python
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

from agents.{agent_name}.agent import {Agent}Agent
from agents.{agent_name}.core.dependencies import AgentDependencies
from agents.{agent_name}.core.config import {Agent}Config
from core.personality.personality_adapter import PersonalityAdapter, PersonalityProfile

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for testing."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_personality_adapter():
    """Mock PersonalityAdapter with realistic responses."""
    adapter = AsyncMock(spec=PersonalityAdapter)
    
    # Configure realistic responses
    adapter.adapt_response.return_value = {
        "adapted_message": "Adapted response content",
        "confidence_score": 0.95,
        "adaptation_type": "PRIME",
        "metadata": {
            "program_type": "NGX_PRIME",
            "adaptation_applied": True,
            "processing_time_ms": 150
        }
    }
    
    adapter.initialize_profile.return_value = True
    return adapter

@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client with realistic AI responses."""
    client = AsyncMock()
    
    # Standard successful response
    client.generate_content.return_value = {
        "content": "Generated AI content",
        "confidence": 0.9,
        "model_version": "gemini-pro-1.5",
        "processing_time_ms": 200
    }
    
    return client

@pytest.fixture
def test_dependencies(mock_personality_adapter, mock_gemini_client):
    """Create test dependencies with mocks."""
    return AgentDependencies(
        personality_adapter=mock_personality_adapter,
        gemini_client=mock_gemini_client,
        program_classification_service=AsyncMock(),
        telemetry_service=MagicMock(),
        cache_service=AsyncMock()
    )

@pytest.fixture
def test_config():
    """Create test configuration."""
    return {Agent}Config(
        max_response_time=5.0,
        retry_attempts=1,
        cache_ttl=60,
        enable_personality_adaptation=True,
        debug_mode=True
    )

@pytest.fixture
async def agent(test_dependencies, test_config):
    """Create and initialize agent for testing."""
    agent = {Agent}Agent(test_dependencies, test_config)
    await agent.initialize()
    return agent

@pytest.fixture
def sample_user_context():
    """Sample user context for testing."""
    return {
        "user_id": "test_user_123",
        "program_type": "NGX_PRIME",
        "user_profile": {
            "age": 30,
            "experience_level": "intermediate",
            "goals": ["muscle_gain", "strength"],
            "preferences": {"intensity": "high"}
        },
        "session_context": {
            "conversation_history": [],
            "current_phase": "planning"
        }
    }

@pytest.fixture
def prime_user_profile():
    """PRIME user profile for testing."""
    return PersonalityProfile(
        program_type="NGX_PRIME",
        user_traits={
            "communication_style": "direct",
            "detail_preference": "concise",
            "motivation_type": "achievement"
        },
        context_preferences={
            "language_complexity": "advanced",
            "technical_depth": "high"
        }
    )

@pytest.fixture
def longevity_user_profile():
    """LONGEVITY user profile for testing."""
    return PersonalityProfile(
        program_type="NGX_LONGEVITY",
        user_traits={
            "communication_style": "nurturing",
            "detail_preference": "comprehensive", 
            "motivation_type": "wellness"
        },
        context_preferences={
            "language_complexity": "accessible",
            "technical_depth": "moderate"
        }
    )
```

### **2. UNIT TESTS - SKILLS PRINCIPALES**

```python
# tests/unit/test_core_skills.py
import pytest
from unittest.mock import AsyncMock, patch
from agents.{agent_name}.skills.core_skills import {MainSkill}

class Test{MainSkill}:
    """Comprehensive tests for {MainSkill}."""
    
    @pytest.mark.asyncio
    async def test_skill_success_path(self, agent, sample_user_context):
        """Test successful skill execution."""
        # Arrange
        input_data = {
            "query": "Test query",
            "parameters": {"key": "value"}
        }
        
        # Act
        result = await agent.skills_manager.execute_skill(
            "{main_skill_name}", 
            input_data, 
            sample_user_context
        )
        
        # Assert
        assert result["success"] is True
        assert "content" in result
        assert result["processing_time_ms"] < 5000
        assert result["confidence_score"] >= 0.7
    
    @pytest.mark.asyncio
    async def test_skill_with_invalid_input(self, agent):
        """Test skill with invalid input data."""
        # Arrange
        invalid_input = {"invalid": "data"}
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await agent.skills_manager.execute_skill(
                "{main_skill_name}", 
                invalid_input
            )
        
        assert "validation" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_skill_external_service_failure(self, agent, sample_user_context):
        """Test skill behavior when external service fails."""
        # Arrange
        input_data = {"query": "Test query"}
        
        with patch.object(agent.dependencies.gemini_client, 'generate_content') as mock_gemini:
            mock_gemini.side_effect = ConnectionError("Service unavailable")
            
            # Act
            result = await agent.skills_manager.execute_skill(
                "{main_skill_name}", 
                input_data, 
                sample_user_context
            )
            
            # Assert
            assert result["success"] is False
            assert "fallback" in result
            assert result["error_type"] == "ExternalServiceError"
    
    @pytest.mark.asyncio
    async def test_skill_performance_benchmark(self, agent, sample_user_context):
        """Test skill performance meets benchmarks."""
        import time
        
        # Arrange
        input_data = {"query": "Performance test query"}
        
        # Act
        start_time = time.time()
        result = await agent.skills_manager.execute_skill(
            "{main_skill_name}", 
            input_data, 
            sample_user_context
        )
        execution_time = (time.time() - start_time) * 1000
        
        # Assert
        assert execution_time < 500  # 500ms benchmark
        assert result["success"] is True
    
    @pytest.mark.parametrize("program_type,expected_style", [
        ("NGX_PRIME", "strategic"),
        ("NGX_LONGEVITY", "nurturing"),
    ])
    @pytest.mark.asyncio
    async def test_personality_adaptation_by_program(
        self, agent, program_type, expected_style
    ):
        """Test personality adaptation varies by program type."""
        # Arrange
        context = {
            "user_id": "test_user",
            "program_type": program_type
        }
        input_data = {"query": "Test adaptation"}
        
        # Act
        result = await agent.skills_manager.execute_skill(
            "{main_skill_name}", 
            input_data, 
            context
        )
        
        # Assert
        assert result["adaptation_metadata"]["program_type"] == program_type
        # Verify adaptation was applied
        adaptation_applied = result["adaptation_metadata"]["adaptation_applied"]
        assert adaptation_applied is True
```

### **3. INTEGRATION TESTS**

```python
# tests/integration/test_full_agent_flows.py
import pytest
from unittest.mock import patch

class TestFullAgentFlows:
    """End-to-end integration tests."""
    
    @pytest.mark.asyncio
    async def test_complete_user_journey_prime(self, agent, prime_user_profile):
        """Test complete user journey for PRIME user."""
        # Simulate multi-turn conversation
        messages = [
            "I need help with {domain_specific_request}",
            "Can you provide more detailed analysis?", 
            "What are the next steps?"
        ]
        
        conversation_context = {
            "user_id": "prime_user_123",
            "program_type": "NGX_PRIME", 
            "conversation_history": []
        }
        
        responses = []
        for message in messages:
            response = await agent.handle_message(message, conversation_context)
            responses.append(response)
            
            # Update conversation history
            conversation_context["conversation_history"].append({
                "user": message,
                "agent": response["content"]
            })
        
        # Verify conversation flow
        assert all(r["success"] for r in responses)
        assert len(responses) == 3
        
        # Verify PRIME-specific adaptations
        for response in responses:
            metadata = response.get("adaptation_metadata", {})
            assert metadata.get("program_type") == "NGX_PRIME"
    
    @pytest.mark.asyncio
    async def test_error_recovery_flow(self, agent, sample_user_context):
        """Test agent recovery from various error scenarios."""
        # Test external service failure recovery
        with patch.object(agent.dependencies.gemini_client, 'generate_content') as mock:
            mock.side_effect = [
                ConnectionError("Service down"),  # First call fails
                {"content": "Recovered response"}  # Second call succeeds
            ]
            
            response = await agent.handle_message(
                "Test error recovery", 
                sample_user_context
            )
            
            # Should recover gracefully
            assert response["success"] is True
            assert "fallback" not in response
```

### **4. PERFORMANCE TESTS**

```python
# tests/performance/test_load_scenarios.py
import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

class TestPerformanceScenarios:
    """Performance and load testing."""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, agent, sample_user_context):
        """Test agent performance under concurrent load."""
        # Arrange
        num_concurrent = 50
        test_message = "Performance test message"
        
        async def make_request():
            start = time.time()
            response = await agent.handle_message(test_message, sample_user_context)
            duration = (time.time() - start) * 1000
            return response, duration
        
        # Act
        start_time = time.time()
        tasks = [make_request() for _ in range(num_concurrent)]
        results = await asyncio.gather(*tasks)
        total_time = (time.time() - start_time) * 1000
        
        # Assert
        responses, durations = zip(*results)
        
        # All requests should succeed
        assert all(r["success"] for r in responses)
        
        # Performance benchmarks
        avg_duration = sum(durations) / len(durations)
        assert avg_duration < 1000  # Average under 1 second
        assert max(durations) < 5000  # No request over 5 seconds
        assert total_time < 10000  # All requests complete in 10 seconds
    
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, agent, sample_user_context):
        """Test memory usage remains stable under load."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Execute many requests
        for i in range(100):
            await agent.handle_message(f"Test message {i}", sample_user_context)
            
            # Check memory every 10 requests
            if i % 10 == 0:
                current_memory = process.memory_info().rss
                memory_growth = (current_memory - initial_memory) / initial_memory
                
                # Memory should not grow more than 50%
                assert memory_growth < 0.5, f"Memory growth {memory_growth:.2%} exceeds limit"
```

### **5. PROPERTY-BASED TESTING**

```python
# tests/property_based/test_input_properties.py
import pytest
from hypothesis import given, strategies as st
from hypothesis.strategies import text, integers, floats

class TestInputProperties:
    """Property-based testing for input validation."""
    
    @given(st.text(min_size=1, max_size=10000))
    @pytest.mark.asyncio
    async def test_agent_handles_any_text_input(self, agent, sample_user_context, text_input):
        """Agent should handle any valid text input without crashing."""
        try:
            response = await agent.handle_message(text_input, sample_user_context)
            # Should either succeed or fail gracefully
            assert isinstance(response, dict)
            assert "success" in response
        except Exception as e:
            # If it fails, it should be a known exception type
            assert isinstance(e, ({Agent}Error, ValidationError))
    
    @given(st.dictionaries(
        keys=st.text(min_size=1, max_size=50),
        values=st.one_of(st.text(), st.integers(), st.floats(), st.booleans())
    ))
    @pytest.mark.asyncio
    async def test_context_robustness(self, agent, context_dict):
        """Agent should handle various context structures robustly."""
        try:
            response = await agent.handle_message("Test message", context_dict)
            assert isinstance(response, dict)
        except Exception as e:
            assert isinstance(e, ({Agent}Error, ValidationError))
```

## 📊 **COVERAGE Y REPORTING**

### **CONFIGURACIÓN PYTEST**

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=agents/{agent_name}
    --cov-report=html:htmlcov
    --cov-report=term-missing
    --cov-report=xml
    --cov-fail-under=85
    --asyncio-mode=auto
    --tb=short
    -v
markers =
    unit: Unit tests
    integration: Integration tests  
    performance: Performance tests
    security: Security tests
    slow: Slow running tests
```

### **COMANDOS DE TESTING**

```bash
# Testing completo con coverage
pytest tests/agents/{agent_name}/ --cov=agents/{agent_name} --cov-report=html

# Solo unit tests
pytest tests/agents/{agent_name}/unit/ -m unit

# Performance tests
pytest tests/agents/{agent_name}/performance/ -m performance --maxfail=1

# Security tests
pytest tests/agents/{agent_name}/security/ -m security

# Property-based tests (más lento)
pytest tests/agents/{agent_name}/property_based/ -m slow --hypothesis-profile=ci
```

## ✅ **CHECKLIST DE TESTING A+**

### **Obligatorio para Certificación A+:**
- [ ] **85%+ line coverage**
- [ ] **80%+ branch coverage** 
- [ ] **90%+ function coverage**
- [ ] **Tests de todos los skills principales**
- [ ] **Tests de PersonalityAdapter integration**
- [ ] **Tests de error handling completos**
- [ ] **Integration tests end-to-end**
- [ ] **Performance benchmarks validados**
- [ ] **Security tests implementados**
- [ ] **Property-based tests para inputs**
- [ ] **Mock scenarios para external services**
- [ ] **Memory leak tests**
- [ ] **Concurrent load tests**

### **Métricas de Calidad:**
- [ ] **Tiempo promedio de test suite < 60 segundos**
- [ ] **Todos los tests pasan en CI/CD**
- [ ] **No flaky tests (deterministic)**
- [ ] **Coverage reports generados automáticamente**
- [ ] **Performance benchmarks documentados**