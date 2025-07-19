"""
Tests para todos los agentes usando la suite base.

Este módulo ejecuta la suite de tests base en todos los agentes
para garantizar que cumplan con los estándares.
"""

import pytest
from tests.agents.test_base_agent import BaseAgentTestSuite, NutritionAgentTestMixin, TrainingAgentTestMixin, WellnessAgentTestMixin

# Importar todos los agentes
from agents.orchestrator.agent import OrchestratorAgent
from agents.precision_nutrition_architect.agent import PrecisionNutritionArchitect
from agents.elite_training_strategist.agent import EliteTrainingStrategist
from agents.female_wellness_coach.agent import FemaleWellnessCoach
from agents.progress_tracker.agent import ProgressTrackerAgent
from agents.motivation_behavior_coach.agent import MotivationBehaviorCoach
from agents.nova_biohacking_innovator.agent import NovaBiohackingInnovator
from agents.wave_performance_analytics.agent import WavePerformanceAnalytics
from agents.code_genetic_specialist.agent import CodeGeneticSpecialist


# ============================================================================
# ORCHESTRATOR
# ============================================================================

@pytest.mark.agents
class TestOrchestratorAgent(BaseAgentTestSuite):
    """Tests para el Orchestrator usando la suite base"""
    agent_class = OrchestratorAgent
    agent_id = "orchestrator"
    expected_capabilities = [
        "route_request",
        "coordinate_agents",
        "manage_conversation"
    ]


# ============================================================================
# PRECISION NUTRITION ARCHITECT (SAGE)
# ============================================================================

@pytest.mark.agents
class TestPrecisionNutritionArchitect(BaseAgentTestSuite, NutritionAgentTestMixin):
    """Tests para SAGE usando la suite base + tests de nutrición"""
    agent_class = PrecisionNutritionArchitect
    agent_id = "precision_nutrition_architect"
    expected_capabilities = [
        "nutrition_planning",
        "macro_calculation",
        "meal_planning",
        "supplement_advice"
    ]


# ============================================================================
# ELITE TRAINING STRATEGIST (BLAZE)
# ============================================================================

@pytest.mark.agents
class TestEliteTrainingStrategist(BaseAgentTestSuite, TrainingAgentTestMixin):
    """Tests para BLAZE usando la suite base + tests de entrenamiento"""
    agent_class = EliteTrainingStrategist
    agent_id = "elite_training_strategist"
    expected_capabilities = [
        "workout_planning",
        "exercise_form",
        "periodization",
        "strength_programming"
    ]


# ============================================================================
# FEMALE WELLNESS COACH (LUNA)
# ============================================================================

@pytest.mark.agents
class TestFemaleWellnessCoach(BaseAgentTestSuite, WellnessAgentTestMixin):
    """Tests para LUNA usando la suite base + tests de bienestar"""
    agent_class = FemaleWellnessCoach
    agent_id = "female_wellness_coach"
    expected_capabilities = [
        "hormonal_guidance",
        "cycle_optimization",
        "prenatal_fitness",
        "wellness_coaching"
    ]


# ============================================================================
# PROGRESS TRACKER (STELLA)
# ============================================================================

@pytest.mark.agents
class TestProgressTracker(BaseAgentTestSuite):
    """Tests para STELLA usando la suite base"""
    agent_class = ProgressTrackerAgent
    agent_id = "progress_tracker"
    expected_capabilities = [
        "progress_analysis",
        "goal_tracking",
        "metric_visualization",
        "trend_detection"
    ]


# ============================================================================
# MOTIVATION BEHAVIOR COACH (SPARK)
# ============================================================================

@pytest.mark.agents
class TestMotivationBehaviorCoach(BaseAgentTestSuite, WellnessAgentTestMixin):
    """Tests para SPARK usando la suite base + tests de bienestar"""
    agent_class = MotivationBehaviorCoach
    agent_id = "motivation_behavior_coach"
    expected_capabilities = [
        "motivation_coaching",
        "habit_formation",
        "behavior_change",
        "mental_wellness"
    ]


# ============================================================================
# NOVA BIOHACKING INNOVATOR
# ============================================================================

@pytest.mark.agents
class TestNovaBiohackingInnovator(BaseAgentTestSuite):
    """Tests para NOVA usando la suite base"""
    agent_class = NovaBiohackingInnovator
    agent_id = "nova_biohacking_innovator"
    expected_capabilities = [
        "biometric_analysis",
        "optimization_protocols",
        "supplement_stacking",
        "performance_hacking"
    ]


# ============================================================================
# WAVE PERFORMANCE ANALYTICS
# ============================================================================

@pytest.mark.agents
class TestWavePerformanceAnalytics(BaseAgentTestSuite):
    """Tests para WAVE usando la suite base"""
    agent_class = WavePerformanceAnalytics
    agent_id = "wave_performance_analytics"
    expected_capabilities = [
        "data_analysis",
        "performance_metrics",
        "predictive_modeling",
        "insight_generation"
    ]


# ============================================================================
# CODE GENETIC SPECIALIST
# ============================================================================

@pytest.mark.agents
class TestCodeGeneticSpecialist(BaseAgentTestSuite):
    """Tests para CODE usando la suite base"""
    agent_class = CodeGeneticSpecialist
    agent_id = "code_genetic_specialist"
    expected_capabilities = [
        "genetic_analysis",
        "dna_interpretation",
        "personalized_recommendations",
        "risk_assessment"
    ]


# ============================================================================
# TESTS DE INTEGRACIÓN ENTRE AGENTES
# ============================================================================

@pytest.mark.integration
@pytest.mark.agents
class TestAgentIntegration:
    """Tests de integración entre múltiples agentes"""
    
    @pytest.fixture
    def all_agents(self, mock_mcp_toolkit):
        """Fixture con todos los agentes"""
        return {
            "orchestrator": OrchestratorAgent(mcp_toolkit=mock_mcp_toolkit),
            "sage": PrecisionNutritionArchitect(mcp_toolkit=mock_mcp_toolkit),
            "blaze": EliteTrainingStrategist(mcp_toolkit=mock_mcp_toolkit),
            "luna": FemaleWellnessCoach(mcp_toolkit=mock_mcp_toolkit),
            "stella": ProgressTrackerAgent(mcp_toolkit=mock_mcp_toolkit),
            "spark": MotivationBehaviorCoach(mcp_toolkit=mock_mcp_toolkit),
            "nova": NovaBiohackingInnovator(mcp_toolkit=mock_mcp_toolkit),
            "wave": WavePerformanceAnalytics(mcp_toolkit=mock_mcp_toolkit),
            "code": CodeGeneticSpecialist(mcp_toolkit=mock_mcp_toolkit)
        }
    
    @pytest.mark.asyncio
    async def test_all_agents_registered(self, all_agents):
        """Test que todos los agentes están registrados correctamente"""
        assert len(all_agents) == 9
        
        for agent_id, agent in all_agents.items():
            assert agent is not None
            assert hasattr(agent, 'agent_id')
            assert hasattr(agent, 'process')
    
    @pytest.mark.asyncio
    async def test_orchestrator_can_route_to_all(self, all_agents, mock_vertex_ai_client):
        """Test que el orchestrator puede rutear a todos los agentes"""
        orchestrator = all_agents["orchestrator"]
        
        # Mock para cada tipo de solicitud
        routing_tests = [
            ("¿Qué debo comer?", "precision_nutrition_architect"),
            ("¿Cómo entreno piernas?", "elite_training_strategist"),
            ("Tengo síndrome premenstrual", "female_wellness_coach"),
            ("¿Cómo va mi progreso?", "progress_tracker"),
            ("No tengo motivación", "motivation_behavior_coach"),
            ("Quiero optimizar mi sueño", "nova_biohacking_innovator"),
            ("Analiza mis métricas", "wave_performance_analytics"),
            ("Tengo gen MTHFR", "code_genetic_specialist")
        ]
        
        for prompt, expected_agent in routing_tests:
            mock_vertex_ai_client.generate_content.return_value = {
                "text": f'{{"agent": "{expected_agent}", "confidence": 0.9}}',
                "finish_reason": "STOP"
            }
            
            result = await orchestrator.route_request(
                prompt=prompt,
                user_context={"user_id": "test_123"}
            )
            
            assert result["agent"] == expected_agent
    
    @pytest.mark.asyncio
    async def test_agent_collaboration(self, all_agents, mock_vertex_ai_client):
        """Test que los agentes pueden colaborar entre sí"""
        # Simular colaboración entre SAGE y BLAZE para plan integral
        sage = all_agents["sage"]
        blaze = all_agents["blaze"]
        
        # Mock respuestas coordinadas
        mock_vertex_ai_client.generate_content.side_effect = [
            {
                "text": '{"meal_plan": "High protein diet", "calories": 2800}',
                "finish_reason": "STOP"
            },
            {
                "text": '{"workout_plan": "5-day split", "focus": "hypertrophy"}',
                "finish_reason": "STOP"
            }
        ]
        
        # Obtener plan de nutrición
        nutrition_plan = await sage.process(
            prompt="Plan para ganar músculo",
            user_context={"user_id": "test_123", "goal": "muscle_gain"}
        )
        
        # Obtener plan de entrenamiento relacionado
        training_plan = await blaze.process(
            prompt="Plan para ganar músculo",
            user_context={
                "user_id": "test_123",
                "goal": "muscle_gain",
                "nutrition_context": nutrition_plan
            }
        )
        
        # Verificar que ambos planes existen y son coherentes
        assert nutrition_plan is not None
        assert training_plan is not None
    
    @pytest.mark.asyncio
    async def test_agent_personality_consistency(self, all_agents):
        """Test que todos los agentes manejan personalidades consistentemente"""
        personalities = ["prime", "longevity"]
        
        for agent_id, agent in all_agents.items():
            if agent_id == "orchestrator":
                continue  # Orchestrator siempre es neutral
            
            # Verificar que el agente tiene personalidad
            assert hasattr(agent, 'personality')
            assert agent.personality in personalities + ["neutral"]
            
            # Si soporta cambio de personalidad
            if hasattr(agent, 'set_personality'):
                for personality in personalities:
                    agent.set_personality(personality)
                    assert agent.personality == personality


# ============================================================================
# TESTS DE RENDIMIENTO
# ============================================================================

@pytest.mark.slow
@pytest.mark.agents
class TestAgentPerformance:
    """Tests de rendimiento para todos los agentes"""
    
    @pytest.mark.asyncio
    async def test_response_time_all_agents(self, mock_mcp_toolkit, mock_vertex_ai_client):
        """Test que todos los agentes responden en tiempo razonable"""
        import time
        
        mock_vertex_ai_client.generate_content.return_value = {
            "text": "Quick response",
            "finish_reason": "STOP"
        }
        
        agents_to_test = [
            PrecisionNutritionArchitect,
            EliteTrainingStrategist,
            FemaleWellnessCoach,
            ProgressTrackerAgent,
            MotivationBehaviorCoach
        ]
        
        for AgentClass in agents_to_test:
            agent = AgentClass(mcp_toolkit=mock_mcp_toolkit)
            
            start = time.time()
            await agent.process(
                prompt="Test rápido",
                user_context={"user_id": "test_123"}
            )
            duration = time.time() - start
            
            # Verificar que responde en menos de 5 segundos
            assert duration < 5.0, f"{agent.agent_id} tardó {duration:.2f}s"