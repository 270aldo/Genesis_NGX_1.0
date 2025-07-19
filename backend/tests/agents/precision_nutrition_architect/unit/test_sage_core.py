"""
Tests unitarios para Precision Nutrition Architect (SAGE).

Este módulo contiene tests exhaustivos para el agente de nutrición,
incluyendo planes de alimentación, cálculos y recomendaciones.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date
import json

from agents.precision_nutrition_architect.agent import PrecisionNutritionArchitect
from app.schemas.chat import AgentResponse
from core.exceptions import AgentError, ValidationError


class TestSageCore:
    """Tests principales de SAGE"""
    
    @pytest.fixture
    def sage(self, mock_vertex_ai_client, mock_mcp_toolkit, mock_logger):
        """Fixture de SAGE con dependencias mockeadas"""
        with patch('agents.precision_nutrition_architect.agent.get_logger', return_value=mock_logger):
            with patch('agents.precision_nutrition_architect.agent.VertexAIClient', return_value=mock_vertex_ai_client):
                agent = PrecisionNutritionArchitect(mcp_toolkit=mock_mcp_toolkit)
                return agent
    
    @pytest.mark.asyncio
    async def test_initialization(self, sage):
        """Test de inicialización correcta de SAGE"""
        assert sage.agent_id == "precision_nutrition_architect"
        assert sage.name == "SAGE - Precision Nutrition Architect"
        assert sage.personality in ["prime", "longevity"]
        assert sage.model == "gemini-1.5-flash-002"
        assert sage.temperature == 0.7
    
    @pytest.mark.asyncio
    async def test_calculate_macros(self, sage, mock_vertex_ai_client):
        """Test de cálculo de macronutrientes"""
        user_context = {
            "user_id": "123",
            "age": 30,
            "weight": 75,  # kg
            "height": 175,  # cm
            "gender": "male",
            "activity_level": "moderate",
            "goal": "muscle_gain"
        }
        
        mock_vertex_ai_client.generate_content.return_value = {
            "text": json.dumps({
                "calories": 2800,
                "macros": {
                    "protein": 150,
                    "carbs": 350,
                    "fats": 93
                },
                "reasoning": "Calculado para ganancia muscular con actividad moderada"
            }),
            "finish_reason": "STOP"
        }
        
        result = await sage.calculate_macros(user_context)
        
        assert result["calories"] == 2800
        assert result["macros"]["protein"] == 150
        assert result["macros"]["carbs"] == 350
        assert result["macros"]["fats"] == 93
        assert "reasoning" in result
    
    @pytest.mark.asyncio
    async def test_generate_meal_plan(self, sage, mock_vertex_ai_client):
        """Test de generación de plan de comidas"""
        user_context = {
            "user_id": "123",
            "calories_target": 2500,
            "dietary_restrictions": ["vegetarian"],
            "preferences": ["mexican_food", "pasta"],
            "meals_per_day": 5
        }
        
        mock_vertex_ai_client.generate_content.return_value = {
            "text": json.dumps({
                "meal_plan": {
                    "breakfast": {
                        "name": "Avena con frutas",
                        "calories": 400,
                        "protein": 15,
                        "carbs": 65,
                        "fats": 10
                    },
                    "snack_1": {
                        "name": "Batido de proteína",
                        "calories": 250,
                        "protein": 25,
                        "carbs": 20,
                        "fats": 5
                    },
                    "lunch": {
                        "name": "Pasta integral con verduras",
                        "calories": 600,
                        "protein": 20,
                        "carbs": 90,
                        "fats": 15
                    },
                    "snack_2": {
                        "name": "Nueces mixtas",
                        "calories": 300,
                        "protein": 10,
                        "carbs": 15,
                        "fats": 25
                    },
                    "dinner": {
                        "name": "Tacos de frijoles",
                        "calories": 550,
                        "protein": 25,
                        "carbs": 70,
                        "fats": 20
                    }
                },
                "total_nutrition": {
                    "calories": 2100,
                    "protein": 95,
                    "carbs": 260,
                    "fats": 75
                }
            }),
            "finish_reason": "STOP"
        }
        
        result = await sage.generate_meal_plan(user_context)
        
        assert "meal_plan" in result
        assert len(result["meal_plan"]) == 5
        assert result["total_nutrition"]["calories"] == 2100
        assert all(meal in result["meal_plan"] for meal in ["breakfast", "lunch", "dinner"])
    
    @pytest.mark.asyncio
    async def test_analyze_food_image(self, sage, mock_vertex_ai_client, mock_mcp_toolkit):
        """Test de análisis de imagen de comida"""
        mock_mcp_toolkit.execute_tool.return_value = {
            "success": True,
            "result": {
                "foods_detected": ["rice", "chicken", "vegetables"],
                "confidence": 0.92
            }
        }
        
        mock_vertex_ai_client.generate_content.return_value = {
            "text": json.dumps({
                "nutrition_estimate": {
                    "calories": 450,
                    "protein": 35,
                    "carbs": 45,
                    "fats": 12
                },
                "foods_identified": ["arroz integral", "pechuga de pollo", "brócoli"],
                "portion_sizes": {
                    "rice": "1 cup",
                    "chicken": "150g",
                    "vegetables": "1.5 cups"
                }
            }),
            "finish_reason": "STOP"
        }
        
        result = await sage.analyze_food_image("base64_image_data")
        
        assert result["nutrition_estimate"]["calories"] == 450
        assert "arroz integral" in result["foods_identified"]
        assert result["portion_sizes"]["chicken"] == "150g"
    
    @pytest.mark.asyncio
    async def test_supplement_recommendations(self, sage, mock_vertex_ai_client):
        """Test de recomendaciones de suplementos"""
        user_context = {
            "user_id": "123",
            "goals": ["muscle_gain", "recovery"],
            "diet_type": "omnivore",
            "training_intensity": "high",
            "budget": "medium"
        }
        
        mock_vertex_ai_client.generate_content.return_value = {
            "text": json.dumps({
                "supplements": [
                    {
                        "name": "Creatina Monohidratada",
                        "dosage": "5g diarios",
                        "timing": "Post-entrenamiento",
                        "benefits": ["Fuerza", "Masa muscular"],
                        "priority": "high"
                    },
                    {
                        "name": "Proteína Whey",
                        "dosage": "25-30g por porción",
                        "timing": "Post-entrenamiento y entre comidas",
                        "benefits": ["Recuperación", "Síntesis proteica"],
                        "priority": "high"
                    },
                    {
                        "name": "Omega 3",
                        "dosage": "2-3g EPA/DHA diarios",
                        "timing": "Con comidas",
                        "benefits": ["Antiinflamatorio", "Salud cardiovascular"],
                        "priority": "medium"
                    }
                ],
                "total_monthly_cost": "$75-100",
                "warnings": ["Consultar con médico antes de iniciar"]
            }),
            "finish_reason": "STOP"
        }
        
        result = await sage.recommend_supplements(user_context)
        
        assert len(result["supplements"]) == 3
        assert result["supplements"][0]["name"] == "Creatina Monohidratada"
        assert "total_monthly_cost" in result
        assert "warnings" in result
    
    @pytest.mark.asyncio
    async def test_hydration_calculator(self, sage, mock_vertex_ai_client):
        """Test de cálculo de hidratación"""
        user_context = {
            "weight": 80,  # kg
            "activity_minutes": 90,
            "climate": "hot",
            "caffeine_intake": 2,  # cups
            "alcohol_intake": 0
        }
        
        mock_vertex_ai_client.generate_content.return_value = {
            "text": json.dumps({
                "water_recommendation": {
                    "baseline": 2800,  # ml
                    "exercise_addition": 900,  # ml
                    "climate_adjustment": 500,  # ml
                    "total_daily": 4200,  # ml
                    "per_hour_during_exercise": 750  # ml
                },
                "hydration_schedule": [
                    {"time": "Al despertar", "amount": "500ml"},
                    {"time": "Antes del desayuno", "amount": "250ml"},
                    {"time": "Media mañana", "amount": "500ml"},
                    {"time": "Antes del almuerzo", "amount": "250ml"},
                    {"time": "Durante entrenamiento", "amount": "1000ml"},
                    {"time": "Post-entrenamiento", "amount": "500ml"},
                    {"time": "Tarde", "amount": "500ml"},
                    {"time": "Cena", "amount": "250ml"},
                    {"time": "Antes de dormir", "amount": "450ml"}
                ]
            }),
            "finish_reason": "STOP"
        }
        
        result = await sage.calculate_hydration(user_context)
        
        assert result["water_recommendation"]["total_daily"] == 4200
        assert len(result["hydration_schedule"]) == 9
        assert result["water_recommendation"]["per_hour_during_exercise"] == 750
    
    @pytest.mark.asyncio
    async def test_dietary_restriction_handling(self, sage, mock_vertex_ai_client):
        """Test de manejo de restricciones dietéticas"""
        restrictions = ["vegan", "gluten_free", "nut_allergy"]
        
        mock_vertex_ai_client.generate_content.return_value = {
            "text": json.dumps({
                "safe_foods": ["quinoa", "tofu", "vegetables", "fruits", "legumes"],
                "avoid_foods": ["wheat", "barley", "rye", "all nuts", "animal products"],
                "substitutions": {
                    "milk": "soy milk or oat milk",
                    "cheese": "nutritional yeast or vegan cheese",
                    "bread": "gluten-free bread",
                    "protein_powder": "pea or rice protein"
                },
                "meal_ideas": [
                    "Buddha bowl con quinoa y tofu",
                    "Smoothie de frutas con proteína de guisante",
                    "Curry de lentejas con arroz"
                ]
            }),
            "finish_reason": "STOP"
        }
        
        result = await sage.handle_dietary_restrictions(restrictions)
        
        assert "quinoa" in result["safe_foods"]
        assert "wheat" in result["avoid_foods"]
        assert result["substitutions"]["milk"] == "soy milk or oat milk"
        assert len(result["meal_ideas"]) >= 3
    
    @pytest.mark.asyncio
    async def test_emergency_nutrition_protocol(self, sage, mock_vertex_ai_client):
        """Test de protocolo de emergencia nutricional"""
        # Simular detección de problema grave
        user_input = "No he comido en 3 días y me siento muy débil"
        
        mock_vertex_ai_client.generate_content.return_value = {
            "text": json.dumps({
                "emergency_detected": True,
                "severity": "high",
                "immediate_actions": [
                    "Buscar atención médica inmediata",
                    "Si es posible, consumir líquidos con electrolitos",
                    "Evitar comidas pesadas inicialmente"
                ],
                "warning": "Esta es una situación médica seria que requiere atención profesional"
            }),
            "finish_reason": "STOP"
        }
        
        result = await sage.process(
            prompt=user_input,
            user_context={"user_id": "123"}
        )
        
        assert result.get("emergency_detected") is True
        assert result["severity"] == "high"
        assert "atención médica" in result["immediate_actions"][0]
    
    @pytest.mark.asyncio
    async def test_meal_timing_optimization(self, sage, mock_vertex_ai_client):
        """Test de optimización de horarios de comida"""
        user_context = {
            "wake_time": "06:00",
            "sleep_time": "22:00",
            "workout_time": "17:00",
            "work_schedule": "09:00-18:00",
            "meals_per_day": 5
        }
        
        mock_vertex_ai_client.generate_content.return_value = {
            "text": json.dumps({
                "meal_schedule": {
                    "06:30": {"meal": "Desayuno", "calories": 400, "focus": "Energía"},
                    "10:00": {"meal": "Snack AM", "calories": 200, "focus": "Sostenimiento"},
                    "13:00": {"meal": "Almuerzo", "calories": 600, "focus": "Recuperación"},
                    "16:00": {"meal": "Pre-entreno", "calories": 250, "focus": "Energía rápida"},
                    "19:00": {"meal": "Post-entreno/Cena", "calories": 550, "focus": "Recuperación"}
                },
                "optimization_notes": [
                    "Pre-entreno 1 hora antes del ejercicio",
                    "Post-entreno dentro de 2 horas",
                    "Última comida 3 horas antes de dormir"
                ]
            }),
            "finish_reason": "STOP"
        }
        
        result = await sage.optimize_meal_timing(user_context)
        
        assert len(result["meal_schedule"]) == 5
        assert "16:00" in result["meal_schedule"]  # Pre-workout
        assert result["meal_schedule"]["16:00"]["focus"] == "Energía rápida"
        assert len(result["optimization_notes"]) >= 3


class TestSageValidation:
    """Tests de validación de SAGE"""
    
    @pytest.fixture
    def sage(self, mock_vertex_ai_client, mock_mcp_toolkit):
        """SAGE para tests de validación"""
        return PrecisionNutritionArchitect(mcp_toolkit=mock_mcp_toolkit)
    
    @pytest.mark.asyncio
    async def test_validate_calorie_range(self, sage):
        """Test de validación de rango de calorías"""
        # Calorías muy bajas
        with pytest.raises(ValidationError) as exc_info:
            await sage.validate_calorie_target(800)
        assert "too low" in str(exc_info.value).lower()
        
        # Calorías muy altas
        with pytest.raises(ValidationError) as exc_info:
            await sage.validate_calorie_target(8000)
        assert "too high" in str(exc_info.value).lower()
        
        # Calorías válidas
        result = await sage.validate_calorie_target(2500)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_macro_ratios(self, sage):
        """Test de validación de ratios de macronutrientes"""
        # Ratios que no suman 100%
        invalid_macros = {"protein": 30, "carbs": 40, "fats": 20}  # Solo 90%
        with pytest.raises(ValidationError) as exc_info:
            await sage.validate_macro_ratios(invalid_macros)
        assert "must sum to 100" in str(exc_info.value).lower()
        
        # Ratios válidos
        valid_macros = {"protein": 30, "carbs": 45, "fats": 25}
        result = await sage.validate_macro_ratios(valid_macros)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_user_data_completeness(self, sage):
        """Test de validación de datos completos del usuario"""
        # Datos incompletos
        incomplete_context = {
            "user_id": "123",
            "age": 25
            # Falta weight, height, gender, etc.
        }
        
        with pytest.raises(ValidationError) as exc_info:
            await sage.validate_user_data_for_macros(incomplete_context)
        assert "missing required" in str(exc_info.value).lower()
        
        # Datos completos
        complete_context = {
            "user_id": "123",
            "age": 25,
            "weight": 70,
            "height": 170,
            "gender": "male",
            "activity_level": "moderate",
            "goal": "maintenance"
        }
        
        result = await sage.validate_user_data_for_macros(complete_context)
        assert result is True


class TestSageIntegration:
    """Tests de integración de SAGE con otros componentes"""
    
    @pytest.fixture
    def sage(self, mock_vertex_ai_client, mock_mcp_toolkit, mock_cache_manager):
        """SAGE con componentes integrados"""
        with patch('agents.precision_nutrition_architect.agent.advanced_cache_manager', mock_cache_manager):
            return PrecisionNutritionArchitect(mcp_toolkit=mock_mcp_toolkit)
    
    @pytest.mark.asyncio
    async def test_cache_meal_plans(self, sage, mock_cache_manager, mock_vertex_ai_client):
        """Test de cacheo de planes de comida"""
        user_id = "123"
        cache_key = f"meal_plan:{user_id}:2024-01-15"
        
        # Primera llamada - cache miss
        mock_cache_manager.get.return_value = None
        mock_vertex_ai_client.generate_content.return_value = {
            "text": json.dumps({"meal_plan": "test_plan"}),
            "finish_reason": "STOP"
        }
        
        result = await sage.get_cached_meal_plan(user_id, date.today())
        
        # Verificar que se guardó en caché
        mock_cache_manager.set.assert_called_once()
        assert mock_cache_manager.set.call_args[0][0] == cache_key
        
        # Segunda llamada - cache hit
        mock_cache_manager.get.return_value = {"meal_plan": "cached_plan"}
        result = await sage.get_cached_meal_plan(user_id, date.today())
        
        assert result["meal_plan"] == "cached_plan"
    
    @pytest.mark.asyncio
    async def test_mcp_tool_integration(self, sage, mock_mcp_toolkit):
        """Test de integración con herramientas MCP"""
        # Simular cálculo de calorías con herramienta
        mock_mcp_toolkit.execute_tool.return_value = {
            "success": True,
            "result": {"calories": 2500, "formula": "Harris-Benedict"}
        }
        
        result = await sage.calculate_calories_with_tool(
            weight=75,
            height=175,
            age=30,
            gender="male",
            activity="moderate"
        )
        
        mock_mcp_toolkit.execute_tool.assert_called_with(
            "calculate_calories",
            weight=75,
            height=175,
            age=30,
            gender="male",
            activity="moderate"
        )
        
        assert result["calories"] == 2500
        assert result["formula"] == "Harris-Benedict"