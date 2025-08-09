"""
Tests unitarios para ADKAgent.

Este módulo contiene pruebas completas para la clase base ADKAgent,
asegurando compatibilidad con el Google Agent Development Kit.
"""

from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from adk.toolkit import Toolkit

# Import the actual ADK implementation from the project
from agents.base.adk_agent import ADKAgent
from core.skill import Skill


class MockSkill:
    """Skill mock para testing."""

    def __init__(
        self, name: str = "mock_skill", description: str = "Mock skill for testing"
    ):
        self.name = name
        self.description = description
        self.execution_count = 0
        self.priority = 1
        self.enabled = True
        self.metadata = {}
        self.version = "1.0.0"  # Added version attribute
        self.category = "test"  # Added category attribute
        self.tags = []  # Added tags attribute

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta la skill mock."""
        self.execution_count += 1
        return {
            "status": "success",
            "skill": self.name,
            "params": params,
            "count": self.execution_count,
        }

    def validate(self, params: Dict[str, Any]) -> bool:
        """Valida los parámetros de la skill."""
        return True


@pytest.fixture
def mock_toolkit():
    """Mock del toolkit ADK."""
    toolkit = Mock(spec=Toolkit)
    toolkit.skills = {}
    toolkit.register_skill = Mock()
    toolkit.get_skill = Mock()
    toolkit.list_skills = Mock(return_value=[])
    return toolkit


@pytest.fixture
def adk_agent(mock_toolkit):
    """Fixture que proporciona una instancia de ADKAgent para testing."""
    with patch("agents.base.adk_agent.Toolkit", return_value=mock_toolkit):
        # Create agent with all required parameters
        agent = ADKAgent(
            agent_id="test-agent-001",
            name="Test ADK Agent",
            description="Test agent for ADK functionality",
            model="gemini-1.5-flash",
            instruction="You are a test agent",
            vertex_ai_client=None,  # Mock client
            supabase_client=None,  # Mock client
            state_manager=None,  # Mock manager
            adk_toolkit=mock_toolkit,
            capabilities=["test", "mock"],
            endpoint=None,
            auto_register_skills=False,
            a2a_server_url=None,
            version="1.0.0",
        )
        agent.toolkit = mock_toolkit
        return agent


class TestADKAgent:
    """Tests para ADKAgent."""

    def test_initialization(self, adk_agent):
        """Test de inicialización correcta."""
        assert adk_agent.name == "Test ADK Agent"
        assert adk_agent.description == "Test agent for ADK functionality"
        assert adk_agent.instruction == "You are a test agent"
        assert adk_agent.toolkit is not None

    def test_skill_registration(self, adk_agent, mock_toolkit):
        """Test de registro de skills."""
        skill = MockSkill("test_skill")

        adk_agent.register_skill(skill)

        mock_toolkit.register_skill.assert_called_once_with(skill)

    def test_skill_retrieval(self, adk_agent, mock_toolkit):
        """Test de obtención de skills."""
        skill = MockSkill("test_skill")
        mock_toolkit.get_skill.return_value = skill

        retrieved_skill = adk_agent.get_skill("test_skill")

        assert retrieved_skill == skill
        mock_toolkit.get_skill.assert_called_once_with("test_skill")

    def test_list_skills(self, adk_agent, mock_toolkit):
        """Test de listado de skills."""
        skills = [
            {"name": "skill1", "description": "First skill"},
            {"name": "skill2", "description": "Second skill"},
        ]
        mock_toolkit.list_skills.return_value = skills

        skill_list = adk_agent.list_skills()

        assert len(skill_list) == 2
        assert skill_list[0]["name"] == "skill1"
        assert skill_list[1]["name"] == "skill2"

    async def test_execute_skill(self, adk_agent):
        """Test de ejecución de skill."""
        skill = MockSkill("test_skill")
        adk_agent._skills = {"test_skill": skill}

        result = await adk_agent.execute_skill("test_skill", {"param": "value"})

        assert result["status"] == "success"
        assert result["skill"] == "test_skill"
        assert result["params"]["param"] == "value"
        assert skill.execution_count == 1

    async def test_execute_nonexistent_skill(self, adk_agent):
        """Test de ejecución de skill inexistente."""
        with pytest.raises(ValueError) as exc_info:
            await adk_agent.execute_skill("nonexistent_skill", {})

        assert "Skill 'nonexistent_skill' not found" in str(exc_info.value)

    def test_get_agent_info(self, adk_agent):
        """Test de información del agente."""
        info = adk_agent.get_agent_info()

        assert info["name"] == "Test ADK Agent"
        assert info["description"] == "Test agent for ADK functionality"
        assert "skills" in info
        assert "version" in info
        assert "adk_compatible" in info
        assert info["adk_compatible"] is True

    def test_update_instruction(self, adk_agent):
        """Test de actualización de instrucciones."""
        new_instruction = "You are an updated test agent"

        adk_agent.update_instruction(new_instruction)

        assert adk_agent.instruction == new_instruction

    async def test_skill_chaining(self, adk_agent):
        """Test de encadenamiento de skills."""
        skill1 = MockSkill("skill1")
        skill2 = MockSkill("skill2")

        adk_agent._skills = {"skill1": skill1, "skill2": skill2}

        # Ejecutar skills en cadena
        result1 = await adk_agent.execute_skill("skill1", {"step": 1})
        result2 = await adk_agent.execute_skill(
            "skill2", {"step": 2, "previous": result1}
        )

        assert result1["count"] == 1
        assert result2["count"] == 1
        assert result2["params"]["previous"]["skill"] == "skill1"

    def test_skill_validation(self, adk_agent):
        """Test de validación de skills."""
        # Intentar registrar algo que no es una skill
        invalid_skill = "not a skill"

        with pytest.raises(TypeError):
            adk_agent.register_skill(invalid_skill)

    async def test_error_handling_in_skill(self, adk_agent):
        """Test de manejo de errores en skills."""

        class ErrorSkill(Skill):
            async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
                raise RuntimeError("Skill execution failed")

        error_skill = ErrorSkill()
        adk_agent._skills = {"error_skill": error_skill}

        with pytest.raises(RuntimeError) as exc_info:
            await adk_agent.execute_skill("error_skill", {})

        assert "Skill execution failed" in str(exc_info.value)

    def test_toolkit_integration(self, adk_agent, mock_toolkit):
        """Test de integración con toolkit."""
        # Verificar que el agente puede acceder a funcionalidades del toolkit
        mock_toolkit.get_tool = Mock(return_value="mock_tool")

        # Simular acceso a herramienta del toolkit
        tool = adk_agent.toolkit.get_tool("test_tool")

        assert tool == "mock_tool"
        mock_toolkit.get_tool.assert_called_once_with("test_tool")

    def test_metadata_handling(self, adk_agent):
        """Test de manejo de metadata."""
        metadata = {
            "author": "Test Author",
            "version": "1.0.0",
            "tags": ["test", "adk"],
        }

        adk_agent.set_metadata(metadata)
        retrieved_metadata = adk_agent.get_metadata()

        assert retrieved_metadata["author"] == "Test Author"
        assert retrieved_metadata["version"] == "1.0.0"
        assert "test" in retrieved_metadata["tags"]

    async def test_batch_skill_execution(self, adk_agent):
        """Test de ejecución en lote de skills."""
        skill = MockSkill("batch_skill")
        adk_agent._skills = {"batch_skill": skill}

        # Ejecutar múltiples veces
        params_list = [{"batch": 1}, {"batch": 2}, {"batch": 3}]

        results = []
        for params in params_list:
            result = await adk_agent.execute_skill("batch_skill", params)
            results.append(result)

        assert len(results) == 3
        assert results[0]["count"] == 1
        assert results[1]["count"] == 2
        assert results[2]["count"] == 3

    def test_skill_discovery(self, adk_agent):
        """Test de descubrimiento de skills."""
        # Simular auto-descubrimiento de skills
        discovered_skills = [MockSkill("auto_skill1"), MockSkill("auto_skill2")]

        for skill in discovered_skills:
            adk_agent.register_skill(skill)

        # Verificar que se registraron correctamente
        assert adk_agent.toolkit.register_skill.call_count == 2


@pytest.mark.asyncio
class TestADKAgentAsync:
    """Tests asíncronos para ADKAgent."""

    async def test_concurrent_skill_execution(self, adk_agent):
        """Test de ejecución concurrente de skills."""
        import asyncio

        skill = MockSkill("concurrent_skill")
        adk_agent._skills = {"concurrent_skill": skill}

        # Ejecutar skill concurrentemente
        tasks = [
            adk_agent.execute_skill("concurrent_skill", {"task": i}) for i in range(5)
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 5
        # Verificar que el contador se incrementó correctamente
        assert results[-1]["count"] == 5

    async def test_skill_timeout(self, adk_agent):
        """Test de timeout en ejecución de skills."""
        import asyncio

        class SlowSkill(Skill):
            async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
                await asyncio.sleep(10)
                return {"status": "completed"}

        slow_skill = SlowSkill()
        adk_agent._skills = {"slow_skill": slow_skill}

        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                adk_agent.execute_skill("slow_skill", {}), timeout=0.1
            )
