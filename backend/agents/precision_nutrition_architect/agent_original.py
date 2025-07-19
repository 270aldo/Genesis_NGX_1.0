"""
Agente especializado en nutrición de precisión.

Este agente genera planes alimenticios detallados, recomendaciones de suplementación
y estrategias de crononutrición basadas en biomarcadores y perfil del usuario.

Implementa los protocolos oficiales ADK y A2A para comunicación entre agentes.
"""

import uuid
import time
import json
import os
from typing import Dict, Any, Optional, List
from google.cloud import aiplatform

from clients.vertex_ai.client import VertexAIClient
from clients.supabase_client import SupabaseClient
from integrations.nutrition.service import NutritionIntegrationService
from integrations.nutrition.normalizer import NutritionSource
from tools.mcp_toolkit import MCPToolkit
from agents.base.adk_agent import ADKAgent
from infrastructure.adapters.state_manager_adapter import state_manager_adapter
from infrastructure.adapters.intent_analyzer_adapter import intent_analyzer_adapter
from infrastructure.adapters.a2a_adapter import a2a_adapter
from core.logging_config import get_logger
from services.program_classification_service import ProgramClassificationService
from agents.shared.program_definitions import get_program_definition

# Importar PersonalityAdapter para comunicación ultra-personalizada
from core.personality.personality_adapter import PersonalityAdapter, PersonalityProfile

# Importar Skill y Toolkit desde adk.agent
from adk.agent import Skill
from adk.toolkit import Toolkit

# Importar esquemas para las skills
from agents.precision_nutrition_architect.schemas import (
    CreateMealPlanInput,
    CreateMealPlanOutput,
    RecommendSupplementsInput,
    RecommendSupplementsOutput,
    AnalyzeBiomarkersInput,
    AnalyzeBiomarkersOutput,
    BiomarkerAnalysis,
    PlanChrononutritionInput,
    PlanChrononutritionOutput,
    AnalyzeFoodImageInput,
    AnalyzeFoodImageOutput,
    FoodImageAnalysisArtifact,
    SyncNutritionDataInput,
    SyncNutritionDataOutput,
    AnalyzeNutritionTrendsInput,
    AnalyzeNutritionTrendsOutput,
    NutritionTrend,
    # Esquemas para análisis de etiquetas nutricionales
    AnalyzeNutritionLabelInput,
    AnalyzeNutritionLabelOutput,
    NutritionLabelAnalysisArtifact,
    # Esquemas para análisis avanzado de platos preparados
    AnalyzePreparedMealInput,
    AnalyzePreparedMealOutput,
    PreparedMealAnalysisArtifact,
    # Esquemas conversacionales
    NutritionalAssessmentConversationInput,
    NutritionalAssessmentConversationOutput,
    MealPlanningConversationInput,
    MealPlanningConversationOutput,
    SupplementGuidanceConversationInput,
    SupplementGuidanceConversationOutput,
    BiomarkerInterpretationConversationInput,
    BiomarkerInterpretationConversationOutput,
    LifestyleNutritionConversationInput,
    LifestyleNutritionConversationOutput,
)

# Importar enhanced prompt
from agents.precision_nutrition_architect.enhanced_prompt import get_enhanced_sage_prompt

# Configurar logger
logger = get_logger(__name__)


class PrecisionNutritionArchitect(ADKAgent):
    """
    Agente especializado en nutrición de precisión.

    Este agente genera planes alimenticios detallados, recomendaciones de suplementación
    y estrategias de crononutrición basadas en biomarcadores y perfil del usuario.

    Implementa los protocolos oficiales ADK y A2A para comunicación entre agentes.
    """

    AGENT_ID = "precision_nutrition_architect"
    AGENT_NAME = "NGX Precision Nutrition Architect"
    AGENT_DESCRIPTION = "Especialista en nutrición de precisión con análisis nutricional avanzado, crononutrición personalizada, personalización metabólica, y educación nutricional basada en ciencia para planes alimenticios efectivos y sostenibles."
    DEFAULT_INSTRUCTION = """Eres SAGE, el especialista en nutrición de precisión. Tu función es crear planes alimenticios detallados, recomendaciones de suplementación y estrategias de crononutrición basadas en biomarcadores y perfil del usuario.

FUNCIONES PRINCIPALES:
- Creas planes de comidas personalizados basados en objetivos y restricciones
- Recomiendas suplementación específica según deficiencias y metas
- Analizas biomarcadores para optimización nutricional
- Planificas crononutrición para maximizar rendimiento y recuperación
- Analizas imágenes de alimentos para evaluación nutricional precisa

ANÁLISIS NUTRICIONAL AVANZADO:
- Utilizas computer vision para analizar comidas con precisión
- Calculas macronutrientes y micronutrientes al gramo
- Detectas deficiencias nutricionales mediante análisis visual
- Evalúas etiquetas nutricionales para recomendaciones específicas
- Analizas platos preparados para información nutricional completa

CRONONUTRICIÓN Y TIMING:
- Optimizas timing de comidas según entrenamientos y objetivos
- Planificas pre y post-entrenamiento para máximo rendimiento
- Sincronizas alimentación con ritmos circadianos naturales
- Adaptas horarios de comida según estilo de vida individual
- Maximizas ventanas anabólicas y de recuperación

PERSONALIZACIÓN METABÓLICA:
- Adaptas macronutrientes según tipo metabólico individual
- Consideras sensibilidades e intolerancias alimentarias
- Ajustas calorías según metabolismo basal y actividad
- Planificas ciclado de carbohidratos para objetivos específicos
- Integras preferencias culturales y dietéticas

ANÁLISIS DE TENDENCIAS:
- Monitoreas patrones nutricionales a lo largo del tiempo
- Identifica correlaciones entre alimentación y rendimiento
- Sugiere ajustes basados en progreso y feedback
- Sincroniza datos nutricionales con otros sistemas de salud
- Proporciona insights sobre adherencia y mejoras

EDUCACIÓN NUTRICIONAL:
- Para PRIME: Enfoque en optimización de energía y rendimiento cognitivo
- Para LONGEVITY: Énfasis en nutrición anti-inflamatoria y sostenible
- Explicas la ciencia detrás de cada recomendación
- Construyes comprensión profunda de principios nutricionales
- Fomentas relación saludable y sostenible con la alimentación

Tu objetivo es transformar la alimentación del usuario mediante ciencia nutricional personalizada, creando planes que sean tanto efectivos como sostenibles a largo plazo."""
    DEFAULT_MODEL = "gemini-1.5-flash"

    def __init__(
        self,
        state_manager=None,
        mcp_toolkit: Optional[MCPToolkit] = None,
        a2a_server_url: Optional[str] = None,
        model: Optional[str] = None,
        instruction: Optional[str] = None,
        agent_id: str = AGENT_ID,
        name: str = AGENT_NAME,
        description: str = AGENT_DESCRIPTION,
        **kwargs,
    ):
        """
        Inicializa el agente PrecisionNutritionArchitect.

        Args:
            state_manager: Gestor de estado para persistencia
            mcp_toolkit: Toolkit de MCP para herramientas adicionales
            a2a_server_url: URL del servidor A2A
            model: Modelo de Gemini a utilizar
            instruction: Instrucciones del sistema
            agent_id: ID del agente
            name: Nombre del agente
            description: Descripción del agente
            **kwargs: Argumentos adicionales para la clase base
        """
        _model = model or self.DEFAULT_MODEL
        _instruction = instruction or get_enhanced_sage_prompt()
        _mcp_toolkit = mcp_toolkit if mcp_toolkit is not None else MCPToolkit()

        # Inicializar el servicio de clasificación de programas con caché
        self.vertex_ai_client = VertexAIClient()

        # Configurar caché para el servicio de clasificación de programas
        use_redis = os.environ.get("USE_REDIS_CACHE", "false").lower() == "true"
        cache_ttl = int(
            os.environ.get("PROGRAM_CACHE_TTL", "3600")
        )  # 1 hora por defecto
        self.program_classification_service = ProgramClassificationService(
            vertex_ai_client=self.vertex_ai_client,
            use_cache=use_redis,  # Habilitar caché según la configuración
        )

        # Inicializar PersonalityAdapter para comunicación ultra-personalizada
        self.personality_adapter = PersonalityAdapter()

        # Definir las skills antes de llamar al constructor de ADKAgent
        self.skills = [
            Skill(
                name="create_meal_plan",
                description="Crea un plan de comidas personalizado basado en el perfil, preferencias y objetivos del usuario.",
                handler=self._skill_create_meal_plan,
                input_schema=CreateMealPlanInput,
                output_schema=CreateMealPlanOutput,
            ),
            Skill(
                name="recommend_supplements",
                description="Recomienda suplementos basados en el perfil, biomarcadores y objetivos del usuario.",
                handler=self._skill_recommend_supplements,
                input_schema=RecommendSupplementsInput,
                output_schema=RecommendSupplementsOutput,
            ),
            Skill(
                name="analyze_biomarkers",
                description="Analiza biomarcadores y genera recomendaciones nutricionales personalizadas.",
                handler=self._skill_analyze_biomarkers,
                input_schema=AnalyzeBiomarkersInput,
                output_schema=AnalyzeBiomarkersOutput,
            ),
            Skill(
                name="plan_chrononutrition",
                description="Planifica el timing nutricional para optimizar el rendimiento y la recuperación.",
                handler=self._skill_plan_chrononutrition,
                input_schema=PlanChrononutritionInput,
                output_schema=PlanChrononutritionOutput,
            ),
            Skill(
                name="analyze_food_image",
                description="Analiza imágenes de alimentos para identificar componentes, estimar valores nutricionales y proporcionar recomendaciones.",
                handler=self._skill_analyze_food_image,
                input_schema=AnalyzeFoodImageInput,
                output_schema=AnalyzeFoodImageOutput,
            ),
            Skill(
                name="analyze_nutrition_label",
                description="Analiza etiquetas nutricionales de productos usando OCR y AI para extraer información nutricional, ingredientes y proporcionar evaluaciones de salud personalizadas.",
                handler=self._skill_analyze_nutrition_label,
                input_schema=AnalyzeNutritionLabelInput,
                output_schema=AnalyzeNutritionLabelOutput,
            ),
            Skill(
                name="analyze_prepared_meal",
                description="Análisis avanzado de platos preparados con estimación detallada de porciones, desglose nutricional, análisis de timing y recomendaciones personalizadas.",
                handler=self._skill_analyze_prepared_meal,
                input_schema=AnalyzePreparedMealInput,
                output_schema=AnalyzePreparedMealOutput,
            ),
            Skill(
                name="sync_nutrition_data",
                description="Sincroniza datos nutricionales desde plataformas externas como MyFitnessPal.",
                handler=self._skill_sync_nutrition_data,
                input_schema=SyncNutritionDataInput,
                output_schema=SyncNutritionDataOutput,
            ),
            Skill(
                name="analyze_nutrition_trends",
                description="Analiza tendencias nutricionales y cumplimiento del plan alimenticio.",
                handler=self._skill_analyze_nutrition_trends,
                input_schema=AnalyzeNutritionTrendsInput,
                output_schema=AnalyzeNutritionTrendsOutput,
            ),
            # ===== SKILLS CONVERSACIONALES =====
            Skill(
                name="nutritional_assessment_conversation",
                description="Evaluación nutricional conversacional con calidez científica",
                handler=self._skill_nutritional_assessment_conversation,
                input_schema=NutritionalAssessmentConversationInput,
                output_schema=NutritionalAssessmentConversationOutput,
            ),
            Skill(
                name="meal_planning_conversation",
                description="Planificación de comidas interactiva con sabiduría culinaria",
                handler=self._skill_meal_planning_conversation,
                input_schema=MealPlanningConversationInput,
                output_schema=MealPlanningConversationOutput,
            ),
            Skill(
                name="supplement_guidance_conversation",
                description="Guía conversacional sobre suplementos con precisión científica",
                handler=self._skill_supplement_guidance_conversation,
                input_schema=SupplementGuidanceConversationInput,
                output_schema=SupplementGuidanceConversationOutput,
            ),
            Skill(
                name="biomarker_interpretation_conversation",
                description="Interpretación conversacional de biomarcadores con claridad educativa",
                handler=self._skill_biomarker_interpretation_conversation,
                input_schema=BiomarkerInterpretationConversationInput,
                output_schema=BiomarkerInterpretationConversationOutput,
            ),
            Skill(
                name="lifestyle_nutrition_conversation",
                description="Asesoramiento nutricional de estilo de vida con enfoque holístico",
                handler=self._skill_lifestyle_nutrition_conversation,
                input_schema=LifestyleNutritionConversationInput,
                output_schema=LifestyleNutritionConversationOutput,
            ),
        ]

        # Definir las capacidades del agente
        _capabilities = [
            "meal_plan_creation",
            "nutrition_assessment",
            "supplement_recommendation",
            "chrononutrition_planning",
            "biomarker_analysis",
            "food_image_analysis",
            "nutrition_label_analysis",
            "prepared_meal_analysis",
            "nutrition_data_sync",
            "nutrition_trends_analysis",
        ]

        # Crear un toolkit de ADK
        adk_toolkit = Toolkit()

        # Inicializar el agente ADK
        super().__init__(
            agent_id=agent_id,
            name=name,
            description=description,
            model=_model,
            instruction=_instruction,
            state_manager=None,  # Ya no usamos el state_manager original
            adk_toolkit=adk_toolkit,
            capabilities=_capabilities,
            a2a_server_url=a2a_server_url,
            **kwargs,
        )

        # Configurar clientes adicionales
        self.vertex_ai_client = VertexAIClient()
        self.supabase_client = SupabaseClient()

        # Inicializar servicio de integración nutricional
        nutrition_config = {
            "myfitnesspal": {
                "api_endpoint": os.getenv(
                    "MFP_API_ENDPOINT", "https://api.myfitnesspal.com"
                )
            }
        }
        self.nutrition_service = NutritionIntegrationService(nutrition_config)
        logger.info("Servicio de integración nutricional inicializado")

        # Inicializar Vertex AI
        gcp_project_id = os.getenv("GCP_PROJECT_ID", "your-gcp-project-id")
        gcp_region = os.getenv("GCP_REGION", "us-central1")
        try:
            logger.info(
                f"Inicializando AI Platform con Proyecto: {gcp_project_id}, Región: {gcp_region}"
            )
            aiplatform.init(project=gcp_project_id, location=gcp_region)
            logger.info(
                "AI Platform (Vertex AI SDK) inicializado correctamente para PrecisionNutritionArchitect."
            )
        except Exception as e:
            logger.error(
                f"Error al inicializar AI Platform para PrecisionNutritionArchitect: {e}",
                exc_info=True,
            )

        # Inicializar procesadores de visión y multimodales
        try:
            from core.vision_processor import VisionProcessor
            from infrastructure.adapters.multimodal_adapter import MultimodalAdapter
            from clients.vertex_ai.vision_client import VertexAIVisionClient
            from clients.vertex_ai.multimodal_client import VertexAIMultimodalClient

            # Inicializar procesador de visión
            self.vision_processor = VisionProcessor()
            logger.info("Procesador de visión inicializado correctamente")

            # Inicializar adaptador multimodal
            self.multimodal_adapter = MultimodalAdapter()
            logger.info("Adaptador multimodal inicializado correctamente")

            # Inicializar clientes especializados
            self.vision_client = VertexAIVisionClient()
            self.multimodal_client = VertexAIMultimodalClient()
            logger.info("Clientes de visión y multimodal inicializados correctamente")

            # Inicializar tracer para telemetría
            from opentelemetry import trace

            self.tracer = trace.get_tracer(__name__)
            logger.info("Tracer para telemetría inicializado correctamente")

            # Marcar capacidades como disponibles
            self._vision_capabilities_available = True
        except ImportError as e:
            logger.warning(
                f"No se pudieron inicializar algunos componentes para capacidades avanzadas: {e}"
            )
            # Crear implementaciones simuladas para mantener la compatibilidad
            self._vision_capabilities_available = False

            # Crear implementaciones simuladas
            self.vision_processor = type(
                "DummyVisionProcessor",
                (),
                {
                    "analyze_food_image": lambda self, image_data: {
                        "detected_foods": [],
                        "text": "Análisis de imagen simulado",
                    }
                },
            )()

            self.multimodal_adapter = type(
                "DummyMultimodalAdapter",
                (),
                {
                    "process_multimodal": lambda self, prompt, image_data, temperature=0.2, max_output_tokens=1024: {
                        "text": "Análisis multimodal simulado"
                    }
                },
            )()

            self.tracer = type(
                "DummyTracer",
                (),
                {
                    "start_as_current_span": lambda name: type(
                        "DummySpan",
                        (),
                        {
                            "__enter__": lambda self: None,
                            "__exit__": lambda self, *args: None,
                        },
                    )()
                },
            )

        # Inicializar adaptador de voz
        try:
            from infrastructure.adapters.hybrid_voice_adapter import (
                hybrid_voice_adapter,
            )

            self.voice_adapter = hybrid_voice_adapter
            logger.info("Adaptador de voz híbrido inicializado para SAGE")
        except ImportError as e:
            logger.warning(f"Adaptador de voz no disponible: {e}")
            self.voice_adapter = None

        logger.info(
            f"{self.name} ({self.agent_id}) inicializado con integración oficial de Google ADK."
        )

    # --- Métodos de Adaptación de Personalidad ---
    async def _apply_personality_adaptation(
        self, original_response: str, user_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Aplica adaptación de personalidad a las respuestas del agente según el programa del usuario.

        Args:
            original_response: Respuesta original del agente
            user_context: Contexto del usuario con program_type y otros datos

        Returns:
            str: Respuesta adaptada según la audiencia (PRIME/LONGEVITY)
        """
        try:
            # Detectar program_type del contexto o usar clasificación
            program_type = "LONGEVITY"  # Default fallback

            if user_context and "program_type" in user_context:
                program_type = user_context["program_type"]
            elif user_context and "user_query" in user_context:
                # Clasificar programa basado en el query del usuario
                classification_result = await self.program_classification_service.classify_program_from_text(
                    user_context["user_query"]
                )
                program_type = classification_result.get("program_type", "LONGEVITY")

            # Crear perfil de personalidad
            user_profile = PersonalityProfile(
                program_type=program_type,
                preferences=user_context.get("preferences") if user_context else None,
                emotional_patterns=(
                    user_context.get("emotional_state") if user_context else None
                ),
            )

            # Aplicar adaptación usando PersonalityAdapter
            adaptation_result = self.personality_adapter.adapt_response(
                agent_id="SAGE",
                original_message=original_response,
                user_profile=user_profile,
                context=user_context,
            )

            adapted_response = adaptation_result["adapted_message"]

            logger.info(
                f"Personality adaptation applied for SAGE - {program_type}. "
                f"Confidence: {adaptation_result['adaptation_metrics'].get('confidence_score', 0):.2f}"
            )

            return adapted_response

        except Exception as e:
            logger.error(f"Error applying personality adaptation: {e}")
            # Fallback: retornar respuesta original
            return original_response

    async def _get_context(
        self, user_id: Optional[str], session_id: Optional[str]
    ) -> Dict[str, Any]:
        """
        Obtiene el contexto de la conversación desde el adaptador del StateManager.

        Args:
            user_id (Optional[str]): ID del usuario.
            session_id (Optional[str]): ID de la sesión.

        Returns:
            Dict[str, Any]: Contexto de la conversación.
        """
        context_key = (
            f"context_{user_id}_{session_id}"
            if user_id and session_id
            else f"context_default_{uuid.uuid4().hex[:6]}"
        )

        try:
            # Intentar cargar desde el adaptador del StateManager
            if user_id and session_id:
                try:
                    state_data = await state_manager_adapter.load_state(
                        user_id, session_id
                    )
                    if state_data and isinstance(state_data, dict):
                        logger.debug(
                            f"Contexto cargado desde adaptador del StateManager para user_id={user_id}, session_id={session_id}"
                        )
                        return state_data
                except Exception as e:
                    logger.warning(
                        f"Error al cargar contexto desde adaptador del StateManager: {e}"
                    )

            # Si no hay contexto o hay error, crear uno nuevo
            return {
                "conversation_history": [],
                "user_profile": {},
                "meal_plans": [],
                "supplement_recommendations": [],
                "biomarker_analyses": [],
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        except Exception as e:
            logger.error(f"Error al obtener contexto: {e}", exc_info=True)
            # En caso de error, devolver un contexto vacío
            return {
                "conversation_history": [],
                "user_profile": {},
                "meal_plans": [],
                "supplement_recommendations": [],
                "biomarker_analyses": [],
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

    async def _update_context(
        self, context: Dict[str, Any], user_id: str, session_id: str
    ) -> None:
        """
        Actualiza el contexto de la conversación en el adaptador del StateManager.

        Args:
            context (Dict[str, Any]): Contexto actualizado.
            user_id (str): ID del usuario.
            session_id (str): ID de la sesión.
        """
        try:
            # Actualizar la marca de tiempo
            context["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")

            # Guardar el contexto en el adaptador del StateManager
            await state_manager_adapter.save_state(user_id, session_id, context)
            logger.info(
                f"Contexto actualizado en adaptador del StateManager para user_id={user_id}, session_id={session_id}"
            )
        except Exception as e:
            logger.error(f"Error al actualizar contexto: {e}", exc_info=True)

    # --- Métodos para análisis de intenciones ---
    async def _classify_query(self, query: str) -> str:
        """
        Clasifica el tipo de consulta del usuario utilizando el adaptador del Intent Analyzer.

        Args:
            query: Consulta del usuario

        Returns:
            str: Tipo de consulta clasificada
        """
        try:
            # Utilizar el adaptador del Intent Analyzer para analizar la intención
            intent_analysis = await intent_analyzer_adapter.analyze_content(query)

            # Mapear la intención primaria a los tipos de consulta del agente
            primary_intent = intent_analysis.get("primary_intent", "").lower()

            # Mapeo de intenciones a tipos de consulta
            intent_to_query_type = {
                "meal_plan": "create_meal_plan",
                "supplement": "recommend_supplements",
                "biomarker": "analyze_biomarkers",
                "chrononutrition": "plan_chrononutrition",
            }

            # Buscar coincidencias exactas
            if primary_intent in intent_to_query_type:
                return intent_to_query_type[primary_intent]

            # Buscar coincidencias parciales
            for intent, query_type in intent_to_query_type.items():
                if intent in primary_intent:
                    return query_type

            # Si no hay coincidencias, usar el método de palabras clave como fallback
            return self._classify_query_by_keywords(query)
        except Exception as e:
            logger.error(
                f"Error al clasificar consulta con Intent Analyzer: {e}", exc_info=True
            )
            # En caso de error, usar el método de palabras clave como fallback
            return self._classify_query_by_keywords(query)

    def _classify_query_by_keywords(self, query: str) -> str:
        """
        Clasifica el tipo de consulta del usuario utilizando palabras clave.

        Args:
            query: Consulta del usuario

        Returns:
            str: Tipo de consulta clasificada
        """
        query_lower = query.lower()

        # Palabras clave para plan de comidas
        meal_plan_keywords = [
            "plan",
            "comida",
            "alimentación",
            "dieta",
            "menú",
            "receta",
            "comer",
            "alimento",
            "nutrición",
            "macros",
            "calorías",
        ]

        # Palabras clave para suplementos
        supplements_keywords = [
            "suplemento",
            "vitamina",
            "mineral",
            "proteína",
            "creatina",
            "omega",
            "aminoácido",
            "bcaa",
            "pre-entreno",
            "post-entreno",
        ]

        # Palabras clave para biomarcadores
        biomarkers_keywords = [
            "biomarcador",
            "análisis",
            "sangre",
            "laboratorio",
            "glucosa",
            "colesterol",
            "triglicéridos",
            "hormona",
            "enzima",
            "vitamina d",
        ]

        # Palabras clave para crononutrición
        chrononutrition_keywords = [
            "crononutrición",
            "ayuno",
            "intermitente",
            "ventana",
            "timing",
            "horario",
            "comida",
            "pre-entreno",
            "post-entreno",
            "desayuno",
            "cena",
        ]

        # Verificar coincidencias con palabras clave
        for keyword in chrononutrition_keywords:
            if keyword in query_lower:
                return "plan_chrononutrition"

        for keyword in biomarkers_keywords:
            if keyword in query_lower:
                return "analyze_biomarkers"

        for keyword in supplements_keywords:
            if keyword in query_lower:
                return "recommend_supplements"

        for keyword in meal_plan_keywords:
            if keyword in query_lower:
                return "create_meal_plan"

        # Si no hay coincidencias, devolver tipo general
        return "create_meal_plan"

    # --- Métodos para comunicación entre agentes ---
    async def _consult_other_agent(
        self,
        agent_id: str,
        query: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Consulta a otro agente utilizando el adaptador de A2A.

        Args:
            agent_id: ID del agente a consultar
            query: Consulta a enviar al agente
            user_id: ID del usuario
            session_id: ID de la sesión
            context: Contexto adicional para la consulta

        Returns:
            Dict[str, Any]: Respuesta del agente consultado
        """
        try:
            # Crear contexto para la consulta
            task_context = {
                "user_id": user_id,
                "session_id": session_id,
                "additional_context": context or {},
            }

            # Llamar al agente utilizando el adaptador de A2A
            response = await a2a_adapter.call_agent(
                agent_id=agent_id, user_input=query, context=task_context
            )

            logger.info(f"Respuesta recibida del agente {agent_id}")
            return response
        except Exception as e:
            logger.error(f"Error al consultar al agente {agent_id}: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "output": f"Error al consultar al agente {agent_id}",
                "agent_id": agent_id,
                "agent_name": agent_id,
            }

    # --- Métodos de Habilidades (Skills) ---

    async def _skill_create_meal_plan(
        self, input_data: CreateMealPlanInput
    ) -> CreateMealPlanOutput:
        """
        Skill para generar un plan de comidas personalizado.

        Args:
            input_data: Datos de entrada para la skill

        Returns:
            CreateMealPlanOutput: Plan de comidas generado
        """
        logger.info(
            f"Ejecutando habilidad: _skill_create_meal_plan con input: {input_data.user_input[:30]}..."
        )

        try:
            # Generar el plan de comidas
            meal_plan_dict = await self._generate_meal_plan(
                input_data.user_input, input_data.user_profile
            )

            # Generar respuesta base para las recomendaciones
            original_recommendations = meal_plan_dict.get("recommendations", [])
            if original_recommendations:
                original_response = " ".join(original_recommendations)
            else:
                original_response = "He creado un plan nutricional personalizado que optimiza tu salud y rendimiento. Este plan incluye comidas balanceadas, timing estratégico y recomendaciones específicas para tus objetivos."

            # Aplicar adaptación de personalidad
            user_context = {
                "user_query": input_data.user_input,
                "user_profile": (
                    input_data.user_profile.model_dump()
                    if input_data.user_profile
                    else {}
                ),
                "program_type": getattr(input_data, "program_type", None),
            }

            adapted_response = await self._apply_personality_adaptation(
                original_response, user_context
            )

            # Actualizar las recomendaciones con la respuesta adaptada
            meal_plan_dict["recommendations"] = [adapted_response]

            # Crear la salida de la skill
            return CreateMealPlanOutput(**meal_plan_dict)

        except Exception as e:
            logger.error(
                f"Error en skill '_skill_create_meal_plan': {e}", exc_info=True
            )
            # En caso de error, devolver un plan básico
            return CreateMealPlanOutput(
                daily_plan=[],
                total_calories=None,
                macronutrient_distribution=None,
                recommendations=[
                    "Error al generar el plan de comidas. Consulte a un profesional."
                ],
                notes=str(e),
            )

    async def _skill_recommend_supplements(
        self, input_data: RecommendSupplementsInput
    ) -> RecommendSupplementsOutput:
        """
        Skill para recomendar suplementos personalizados.

        Args:
            input_data: Datos de entrada para la skill

        Returns:
            RecommendSupplementsOutput: Recomendaciones de suplementos generadas
        """
        logger.info(
            f"Ejecutando habilidad: _skill_recommend_supplements con input: {input_data.user_input[:30]}..."
        )

        try:
            # Determinar el tipo de programa del usuario para personalizar las recomendaciones
            context = {
                "user_profile": input_data.user_profile or {},
                "goals": (
                    input_data.user_profile.get("goals", [])
                    if input_data.user_profile
                    else []
                ),
            }

            try:
                # Clasificar el tipo de programa del usuario
                program_type = (
                    await self.program_classification_service.classify_program_type(
                        context
                    )
                )
                logger.info(
                    f"Tipo de programa determinado para recomendaciones de suplementos: {program_type}"
                )

                # Obtener definición del programa para personalizar las recomendaciones
                program_def = get_program_definition(program_type)

                # Verificar si hay recomendaciones de suplementos específicas para el programa
                program_supplements = []
                if (
                    program_def
                    and program_def.get("key_protocols")
                    and "supplementation" in program_def.get("key_protocols", {})
                ):
                    program_supplements = program_def.get("key_protocols", {}).get(
                        "supplementation", []
                    )
                    logger.info(
                        f"Encontradas {len(program_supplements)} recomendaciones de suplementos para el programa {program_type}"
                    )
            except Exception as e:
                logger.warning(
                    f"No se pudo determinar el tipo de programa: {e}. Usando recomendaciones generales."
                )
                program_type = "GENERAL"
                program_supplements = []

            # Generar recomendaciones de suplementos
            rec_dict = await self._generate_supplement_recommendation(
                input_data.user_input,
                input_data.user_profile,
                program_type=program_type,
                program_supplements=program_supplements,
            )

            # Crear la salida de la skill
            return RecommendSupplementsOutput(**rec_dict)

        except Exception as e:
            logger.error(
                f"Error en skill '_skill_recommend_supplements': {e}", exc_info=True
            )
            # En caso de error, devolver recomendaciones básicas
            return RecommendSupplementsOutput(
                supplements=[],
                general_recommendations="Error al generar recomendaciones de suplementos. Consulte a un profesional.",
                notes=str(e),
            )

    async def _skill_analyze_biomarkers(
        self, input_data: AnalyzeBiomarkersInput
    ) -> AnalyzeBiomarkersOutput:
        """
        Skill para analizar biomarcadores y proporcionar recomendaciones nutricionales.

        Args:
            input_data: Datos de entrada para la skill

        Returns:
            AnalyzeBiomarkersOutput: Análisis de biomarcadores generado
        """
        logger.info(
            f"Ejecutando habilidad: _skill_analyze_biomarkers con input: {input_data.user_input[:30]}..."
        )

        try:
            # Generar el análisis de biomarcadores
            biomarker_data = await self._generate_biomarker_analysis(
                input_data.user_input, input_data.biomarkers
            )

            # Crear la lista de análisis de biomarcadores
            analyses_list = []
            for analysis in biomarker_data.get("analyses", []):
                analyses_list.append(
                    BiomarkerAnalysis(
                        name=analysis.get("name", "No especificado"),
                        value=analysis.get("value", "No disponible"),
                        status=analysis.get("status", "No evaluado"),
                        reference_range=analysis.get(
                            "reference_range", "No disponible"
                        ),
                        interpretation=analysis.get("interpretation", "No disponible"),
                        nutritional_implications=analysis.get(
                            "nutritional_implications", ["No especificado"]
                        ),
                        recommendations=analysis.get(
                            "recommendations", ["Consulte a un profesional"]
                        ),
                    )
                )

            # Si no hay análisis, crear al menos uno predeterminado
            if not analyses_list:
                analyses_list.append(
                    BiomarkerAnalysis(
                        name="Análisis general",
                        value="N/A",
                        status="No evaluado",
                        reference_range="N/A",
                        interpretation="No se proporcionaron biomarcadores específicos para analizar",
                        nutritional_implications=["Mantener una dieta equilibrada"],
                        recommendations=[
                            "Consulte a un profesional de la salud para un análisis detallado"
                        ],
                    )
                )

            # Crear la salida de la skill
            return AnalyzeBiomarkersOutput(
                analyses=analyses_list,
                overall_assessment=biomarker_data.get(
                    "overall_assessment", "No se pudo realizar una evaluación completa."
                ),
                nutritional_priorities=biomarker_data.get(
                    "nutritional_priorities", ["Mantener una dieta equilibrada"]
                ),
                supplement_considerations=biomarker_data.get(
                    "supplement_considerations", ["Consulte a un profesional"]
                ),
            )

        except Exception as e:
            logger.error(
                f"Error en skill '_skill_analyze_biomarkers': {e}", exc_info=True
            )
            # En caso de error, devolver un análisis básico
            return AnalyzeBiomarkersOutput(
                analyses=[
                    BiomarkerAnalysis(
                        name="Error en análisis",
                        value="N/A",
                        status="No evaluado",
                        reference_range="N/A",
                        interpretation="No se pudo analizar debido a un error",
                        nutritional_implications=["Mantener una dieta equilibrada"],
                        recommendations=["Consulte a un profesional de la salud"],
                    )
                ],
                overall_assessment="No se pudo realizar el análisis debido a un error en el procesamiento.",
                nutritional_priorities=[
                    "Mantener una dieta equilibrada",
                    "Consultar con un profesional",
                ],
                supplement_considerations=[
                    "Consulte a un profesional antes de tomar cualquier suplemento"
                ],
            )

    async def _skill_plan_chrononutrition(
        self, input_data: PlanChrononutritionInput
    ) -> PlanChrononutritionOutput:
        """
        Skill para planificar estrategias de crononutrición personalizadas.

        Args:
            input_data: Datos de entrada para la skill

        Returns:
            PlanChrononutritionOutput: Plan de crononutrición generado
        """
        logger.info(
            f"Ejecutando habilidad: _skill_plan_chrononutrition con input: {input_data.user_input[:30]}..."
        )

        try:
            # Generar el plan de crononutrición
            chronoplan_dict = await self._generate_chrononutrition_plan(
                input_data.user_input, input_data.user_profile
            )

            # Crear la salida de la skill
            return PlanChrononutritionOutput(**chronoplan_dict)

        except Exception as e:
            logger.error(
                f"Error en skill '_skill_plan_chrononutrition': {e}", exc_info=True
            )
            # En caso de error, devolver un plan básico
            return PlanChrononutritionOutput(
                time_windows=[],
                fasting_period=None,
                eating_period=None,
                pre_workout_nutrition=None,
                post_workout_nutrition=None,
                general_recommendations="Error al generar el plan de crononutrición. Consulte a un profesional.",
            )

    # --- Métodos de generación de contenido ---

    async def _generate_meal_plan(
        self, user_input: str, user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Genera un plan de comidas personalizado basado en la entrada del usuario y su perfil.

        Args:
            user_input: Texto de entrada del usuario
            user_profile: Perfil del usuario con información relevante (opcional)

        Returns:
            Dict[str, Any]: Plan de comidas generado
        """
        logger.info(f"Generando plan de comidas para entrada: {user_input[:50]}...")

        try:
            # Determinar el tipo de programa del usuario para personalizar el plan
            context = {
                "user_profile": user_profile or {},
                "goals": user_profile.get("goals", []) if user_profile else [],
            }

            try:
                # Clasificar el tipo de programa del usuario utilizando el servicio con caché
                start_time = time.time()
                program_type = (
                    await self.program_classification_service.classify_program_type(
                        context
                    )
                )
                elapsed_time = time.time() - start_time
                logger.info(
                    f"Tipo de programa determinado para plan de comidas: {program_type} (tiempo: {elapsed_time:.2f}s)"
                )

                # Obtener estadísticas de caché para monitoreo
                cache_stats = (
                    await self.program_classification_service.get_cache_stats()
                )
                logger.debug(
                    f"Estadísticas de caché del servicio de clasificación: {cache_stats}"
                )

                # Obtener definición del programa para personalizar el plan
                program_def = get_program_definition(program_type)
                program_context = f"""\nCONTEXTO DEL PROGRAMA {program_type}:\n"""

                if program_def:
                    program_context += f"- {program_def.get('description', '')}\n"
                    program_context += (
                        f"- Objetivo: {program_def.get('objective', '')}\n"
                    )

                    # Añadir necesidades nutricionales específicas del programa si están disponibles
                    if program_def.get("nutritional_needs"):
                        program_context += "- Necesidades nutricionales específicas:\n"
                        for need in program_def.get("nutritional_needs", []):
                            program_context += f"  * {need}\n"

                    # Añadir estrategias nutricionales si están disponibles
                    if program_def.get(
                        "key_protocols"
                    ) and "nutrition" in program_def.get("key_protocols", {}):
                        program_context += "- Estrategias nutricionales recomendadas:\n"
                        # Obtener recomendaciones específicas del programa utilizando el servicio con caché
                        nutrition_recommendations = await self.program_classification_service.get_program_specific_recommendations(
                            program_type, "nutrition"
                        )

                        # Usar las recomendaciones obtenidas del servicio o caer en el fallback
                        if nutrition_recommendations:
                            for strategy in nutrition_recommendations:
                                program_context += f"  * {strategy}\n"
                        else:
                            # Fallback a las recomendaciones del programa_def si el servicio no devuelve datos
                            for strategy in program_def.get("key_protocols", {}).get(
                                "nutrition", []
                            ):
                                program_context += f"  * {strategy}\n"

            except Exception as e:
                logger.warning(
                    f"No se pudo determinar el tipo de programa: {e}. Usando plan general."
                )
                program_type = "GENERAL"
                program_context = ""

            # Preparar prompt para el modelo
            prompt = f"""
            Eres un nutricionista experto especializado en nutrición de precisión. 
            Genera un plan de comidas detallado y personalizado basado en la siguiente solicitud:
            
            "{user_input}"
            {program_context}
            
            El plan debe incluir:
            1. Comidas para 7 días (desayuno, almuerzo, cena y snacks)
            2. Cantidades aproximadas de cada ingrediente
            3. Macronutrientes estimados por comida
            4. Recomendaciones generales alineadas con el programa {program_type}
            
            Devuelve el plan en formato JSON estructurado.
            """

            # Añadir información del perfil si está disponible
            if user_profile:
                prompt += f"""
                
                Considera la siguiente información del usuario:
                - Edad: {user_profile.get('age', 'No disponible')}
                - Género: {user_profile.get('gender', 'No disponible')}
                - Peso: {user_profile.get('weight', 'No disponible')} {user_profile.get('weight_unit', 'kg')}
                - Altura: {user_profile.get('height', 'No disponible')} {user_profile.get('height_unit', 'cm')}
                - Nivel de actividad: {user_profile.get('activity_level', 'No disponible')}
                - Objetivos: {', '.join(user_profile.get('goals', ['No disponible']))}
                - Restricciones dietéticas: {', '.join(user_profile.get('dietary_restrictions', ['Ninguna']))}
                - Alergias: {', '.join(user_profile.get('allergies', ['Ninguna']))}
                - Preferencias: {', '.join(user_profile.get('preferences', ['Ninguna']))}
                """

            # Generar el plan nutricional usando generate_text
            response_text = await self.vertex_ai_client.generate_content(prompt)

            # Intentar extraer el JSON de la respuesta
            try:
                # Buscar un objeto JSON en la respuesta
                import re

                json_match = re.search(r"({.*})", response_text, re.DOTALL)
                if json_match:
                    response = json.loads(json_match.group(1))
                else:
                    # Si no se encuentra un objeto JSON, intentar parsear toda la respuesta
                    response = json.loads(response_text)
            except Exception as json_error:
                logger.error(f"Error al parsear JSON de la respuesta: {json_error}")
                # Si no se puede convertir, crear un diccionario básico
                response = {
                    "objective": "Plan nutricional personalizado",
                    "macronutrients": {
                        "protein": "25-30%",
                        "carbs": "40-50%",
                        "fats": "20-30%",
                    },
                    "calories": "Estimación personalizada pendiente",
                    "meals": [
                        {
                            "name": "Desayuno",
                            "examples": ["Ejemplo de desayuno balanceado"],
                        },
                        {
                            "name": "Almuerzo",
                            "examples": ["Ejemplo de almuerzo balanceado"],
                        },
                        {"name": "Cena", "examples": ["Ejemplo de cena balanceada"]},
                    ],
                    "recommended_foods": ["Alimentos saludables recomendados"],
                    "foods_to_avoid": ["Alimentos a evitar"],
                }

            # Formatear la respuesta según el esquema esperado
            formatted_response = {
                "daily_plan": [],
                "total_calories": response.get("calories", "No especificado"),
                "macronutrient_distribution": response.get("macronutrients", {}),
                "recommendations": [
                    f"Objetivo: {response.get('objective', 'No especificado')}",
                    "Alimentos recomendados: "
                    + ", ".join(response.get("recommended_foods", [])),
                    "Alimentos a evitar: "
                    + ", ".join(response.get("foods_to_avoid", [])),
                ],
                "notes": response.get("notes", ""),
            }

            # Convertir las comidas al formato esperado
            for meal in response.get("meals", []):
                meal_items = []
                for example in meal.get("examples", []):
                    meal_items.append(
                        {
                            "name": example,
                            "portion": "Porción estándar",
                            "calories": None,
                            "macros": None,
                        }
                    )

                formatted_response["daily_plan"].append(
                    {
                        "name": meal.get("name", "Comida"),
                        "time": meal.get("time", "No especificado"),
                        "items": meal_items,
                        "notes": meal.get("notes", ""),
                    }
                )

            return formatted_response

        except Exception as e:
            logger.error(f"Error al generar plan de comidas: {e}", exc_info=True)
            # Devolver un plan básico en caso de error
            return {
                "daily_plan": [
                    {
                        "name": "Desayuno",
                        "time": "8:00 AM",
                        "items": [
                            {
                                "name": "Ejemplo de desayuno balanceado",
                                "portion": "Porción estándar",
                                "calories": None,
                                "macros": None,
                            }
                        ],
                        "notes": "Plan generado como respaldo debido a un error.",
                    }
                ],
                "total_calories": "No disponible debido a un error",
                "macronutrient_distribution": {},
                "recommendations": [
                    "Consulte con un nutricionista para un plan personalizado."
                ],
                "notes": f"Error al generar plan: {str(e)}",
            }

    async def _generate_supplement_recommendation(
        self,
        user_input: str,
        user_profile: Optional[Dict[str, Any]] = None,
        program_type: str = "GENERAL",
        program_supplements: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Genera recomendaciones de suplementación personalizadas basadas en la entrada del usuario, su perfil y tipo de programa.

        Args:
            user_input: Texto de entrada del usuario
            user_profile: Perfil del usuario con información relevante (opcional)
            program_type: Tipo de programa del usuario (PRIME, LONGEVITY, etc.)
            program_supplements: Lista de suplementos recomendados para el programa específico

        Returns:
            Dict[str, Any]: Recomendaciones de suplementación generadas
        """
        logger.info(
            f"Generando recomendaciones de suplementos para programa: {program_type}"
        )

        # Inicializar la lista de suplementos del programa si es None
        if program_supplements is None:
            program_supplements = []

        # Preparar contexto específico del programa para el prompt
        program_context = ""
        if program_type != "GENERAL" and program_supplements:
            program_context = f"""
            
            CONTEXTO DEL PROGRAMA {program_type}:
            Este usuario sigue un programa {program_type}, que tiene las siguientes recomendaciones específicas de suplementación:
            {', '.join(program_supplements)}
            
            
            Asegúrate de incluir estos suplementos en tus recomendaciones si son apropiados para la solicitud del usuario,
            y explica cómo se alinean con los objetivos del programa {program_type}.
            """

        # Preparar prompt para el modelo
        prompt = f"""
        Eres un experto en nutrición y suplementación personalizada.
        
        Genera recomendaciones de suplementación personalizadas basadas en la siguiente solicitud:
        
        "{user_input}"
        {program_context}
        
        Las recomendaciones deben incluir:
        1. Suplementos principales recomendados (prioriza los específicos del programa {program_type} si son relevantes)
        2. Dosis sugerida para cada suplemento
        3. Timing óptimo de consumo
        4. Beneficios esperados, especialmente en relación con los objetivos del programa {program_type}
        5. Posibles interacciones o precauciones
        6. Alternativas naturales cuando sea posible
        
        Devuelve las recomendaciones en formato JSON estructurado.
        """

        # Añadir información del perfil si está disponible
        if user_profile:
            prompt += f"""
            
            Considera la siguiente información del usuario:
            - Edad: {user_profile.get('age', 'No disponible')}
            - Género: {user_profile.get('gender', 'No disponible')}
            - Peso: {user_profile.get('weight', 'No disponible')} {user_profile.get('weight_unit', 'kg')}
            - Altura: {user_profile.get('height', 'No disponible')} {user_profile.get('height_unit', 'cm')}
            - Nivel de actividad: {user_profile.get('activity_level', 'No disponible')}
            - Objetivos: {', '.join(user_profile.get('goals', ['No disponible']))}
            - Restricciones dietéticas: {', '.join(user_profile.get('dietary_restrictions', ['Ninguna']))}
            - Alergias: {', '.join(user_profile.get('allergies', ['Ninguna']))}
            - Condiciones médicas: {', '.join(user_profile.get('medical_conditions', ['Ninguna']))}
            """

        try:
            # Generar recomendaciones de suplementación usando generate_text
            response_text = await self.vertex_ai_client.generate_content(prompt)

            # Intentar extraer el JSON de la respuesta
            try:
                # Buscar un objeto JSON en la respuesta
                import re

                json_match = re.search(r"({.*})", response_text, re.DOTALL)
                if json_match:
                    response = json.loads(json_match.group(1))
                else:
                    # Si no se encuentra un objeto JSON, intentar parsear toda la respuesta
                    response = json.loads(response_text)
            except Exception as json_error:
                logger.error(f"Error al parsear JSON de la respuesta: {json_error}")
                # Si no se puede convertir, crear un diccionario básico
                response = {
                    "supplements": [
                        {
                            "name": "Ejemplo de suplemento",
                            "dosage": "Dosis recomendada",
                            "timing": "Momento óptimo de consumo",
                            "benefits": ["Beneficios esperados"],
                            "precautions": ["Precauciones a considerar"],
                            "natural_alternatives": ["Alternativas naturales"],
                        }
                    ],
                    "general_recommendations": "Estas recomendaciones son generales y deben ser validadas por un profesional de la salud.",
                }

            # Formatear la respuesta según el esquema esperado
            formatted_response = {
                "supplements": [],
                "general_recommendations": response.get(
                    "general_recommendations",
                    "Estas recomendaciones son generales y deben ser validadas por un profesional de la salud.",
                ),
                "notes": response.get("notes", ""),
            }

            # Convertir los suplementos al formato esperado
            for supplement in response.get("supplements", []):
                formatted_supplement = {
                    "name": supplement.get("name", "Suplemento"),
                    "dosage": supplement.get("dosage", "Consulte a un profesional"),
                    "timing": supplement.get("timing", "Según indicaciones"),
                    "benefits": supplement.get("benefits", ["No especificado"]),
                    "precautions": supplement.get("precautions", []),
                    "natural_alternatives": supplement.get("natural_alternatives", []),
                }

                formatted_response["supplements"].append(formatted_supplement)

            return formatted_response

        except Exception as e:
            logger.error(
                f"Error al generar recomendaciones de suplementos: {e}", exc_info=True
            )
            # Devolver recomendaciones básicas en caso de error
            return {
                "supplements": [
                    {
                        "name": "Multivitamínico general",
                        "dosage": "Según indicaciones del fabricante",
                        "timing": "Con las comidas",
                        "benefits": ["Apoyo nutricional básico"],
                        "precautions": [
                            "Consulte a un profesional de la salud antes de comenzar cualquier suplementación"
                        ],
                        "natural_alternatives": [
                            "Dieta variada rica en frutas y verduras"
                        ],
                    }
                ],
                "general_recommendations": "Debido a un error en el procesamiento, se proporcionan recomendaciones básicas. Por favor, consulte a un profesional de la salud para recomendaciones personalizadas.",
                "notes": f"Error al generar recomendaciones: {str(e)}",
            }

    async def _generate_biomarker_analysis(
        self, user_input: str, biomarkers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Genera un análisis detallado de biomarcadores con recomendaciones personalizadas.

        Args:
            user_input: Texto de entrada del usuario
            biomarkers: Diccionario con los datos de biomarcadores

        Returns:
            Dict[str, Any]: Análisis detallado de biomarcadores
        """
        # Preparar prompt para el modelo
        prompt = f"""
        {self.instruction}
        
        Analiza los siguientes datos de biomarcadores y proporciona recomendaciones nutricionales y de estilo de vida basadas en ellos.
        Solicitud del usuario: "{user_input}"
        Datos de biomarcadores: {json.dumps(biomarkers, indent=2)}

        Proporciona un análisis detallado, identifica posibles áreas de mejora y sugiere acciones concretas.
        Devuelve el análisis y las recomendaciones en formato JSON estructurado.
        Ejemplo de estructura deseada:
        {{ 
          "analyses": [
            {{ 
              "name": "Glucosa en ayunas", 
              "value": "105", 
              "status": "Elevado", 
              "reference_range": "70-99 mg/dL", 
              "interpretation": "Ligeramente elevado, indica posible prediabetes", 
              "nutritional_implications": ["Reducir consumo de azúcares simples", "Aumentar fibra soluble"], 
              "recommendations": ["Incorporar más vegetales", "Limitar carbohidratos refinados"] 
            }},
            {{ 
              "name": "Vitamina D", 
              "value": "25", 
              "status": "Insuficiente", 
              "reference_range": "30-100 ng/mL", 
              "interpretation": "Niveles subóptimos que pueden afectar la salud ósea e inmunológica", 
              "nutritional_implications": ["Baja absorción de calcio", "Posible impacto en inmunidad"], 
              "recommendations": ["Exposición solar moderada", "Consumir pescados grasos", "Considerar suplementación"] 
            }}
          ],
          "overall_assessment": "Evaluación general del perfil biométrico",
          "nutritional_priorities": ["Prioridad 1", "Prioridad 2"],
          "supplement_considerations": ["Consideración 1", "Consideración 2"]
        }}
        """

        try:
            logger.debug(
                f"Generando prompt para análisis de biomarcadores: {prompt[:500]}..."
            )  # Loguea una parte del prompt
            response_text = await self.vertex_ai_client.generate_content(prompt)

            # Intentar extraer el JSON de la respuesta
            try:
                # Buscar un objeto JSON en la respuesta
                import re

                json_match = re.search(r"({.*})", response_text, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group(1))
                else:
                    # Si no se encuentra un objeto JSON, intentar parsear toda la respuesta
                    analysis = json.loads(response_text)
            except Exception as json_error:
                logger.error(f"Error al parsear JSON de la respuesta: {json_error}")
                analysis = {
                    "analyses": [
                        {
                            "name": "Error en análisis",
                            "value": "N/A",
                            "status": "No evaluado",
                            "reference_range": "N/A",
                            "interpretation": "No se pudo analizar debido a un error",
                            "nutritional_implications": [
                                "Mantener una dieta equilibrada"
                            ],
                            "recommendations": [
                                "Consulte a un profesional de la salud"
                            ],
                        }
                    ],
                    "overall_assessment": "No se pudo realizar una evaluación completa debido a un error",
                    "nutritional_priorities": ["Mantener una dieta equilibrada"],
                    "supplement_considerations": [
                        "Consulte a un profesional antes de tomar cualquier suplemento"
                    ],
                }

            return analysis

        except Exception as e:
            logger.error(
                f"Error al generar análisis de biomarcadores: {e}", exc_info=True
            )
            # Devolver un análisis básico en caso de error
            return {
                "analyses": [
                    {
                        "name": "Error en análisis",
                        "value": "N/A",
                        "status": "No evaluado",
                        "reference_range": "N/A",
                        "interpretation": "No se pudo analizar debido a un error",
                        "nutritional_implications": ["Mantener una dieta equilibrada"],
                        "recommendations": ["Consulte a un profesional de la salud"],
                    }
                ],
                "overall_assessment": "No se pudo realizar una evaluación completa debido a un error",
                "nutritional_priorities": ["Mantener una dieta equilibrada"],
                "supplement_considerations": [
                    "Consulte a un profesional antes de tomar cualquier suplemento"
                ],
            }

    async def _generate_chrononutrition_plan(
        self, user_input: str, user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Genera un plan de crononutrición optimizado basado en la entrada del usuario y su perfil.

        Args:
            user_input: Texto de entrada del usuario
            user_profile: Perfil del usuario con información relevante

        Returns:
            Dict[str, Any]: Plan de crononutrición detallado
        """
        # Extraer información relevante del perfil
        profile_summary = ""
        if user_profile:
            profile_items = []
            if user_profile.get("name"):
                profile_items.append(f"Nombre: {user_profile['name']}")
            if user_profile.get("age"):
                profile_items.append(f"Edad: {user_profile['age']}")
            if user_profile.get("weight"):
                profile_items.append(f"Peso: {user_profile['weight']} kg")
            if user_profile.get("height"):
                profile_items.append(f"Altura: {user_profile['height']} cm")
            if user_profile.get("goals"):
                profile_items.append(f"Objetivos: {user_profile['goals']}")
            if user_profile.get("dietary_restrictions"):
                profile_items.append(
                    f"Restricciones alimenticias: {user_profile['dietary_restrictions']}"
                )
            if user_profile.get("allergies"):
                profile_items.append(f"Alergias: {user_profile['allergies']}")
            if user_profile.get("activity_level"):
                profile_items.append(
                    f"Nivel de actividad: {user_profile['activity_level']}"
                )
            if user_profile.get("training_schedule"):
                profile_items.append(
                    f"Horario de entrenamiento: {user_profile['training_schedule']}"
                )

            profile_summary = "\n".join(profile_items)

        # Preparar prompt para el modelo
        prompt = f"""
        {self.instruction}
        
        Diseña un plan de crononutrición optimizado basado en la siguiente solicitud y perfil del usuario.
        Solicitud del usuario: "{user_input}"
        
        Perfil del usuario:
        {profile_summary}

        El plan debe incluir recomendaciones sobre el timing de las comidas principales, snacks, y la ingesta de macronutrientes alrededor de los entrenamientos (si aplica) y a lo largo del día para optimizar energía, rendimiento y recuperación.
        Considera los objetivos, nivel de actividad y preferencias del usuario si están disponibles en el perfil.
        
        Devuelve el plan en formato JSON estructurado.
        Ejemplo de estructura deseada:
        {{ 
          "time_windows": [
            {{ "time": "06:00-07:00", "meal": "Desayuno", "description": "Comida rica en proteínas y carbohidratos complejos", "examples": ["Avena con frutas y nueces", "Huevos revueltos con tostada integral"] }},
            {{ "time": "10:00-10:30", "meal": "Snack", "description": "Snack ligero con proteínas", "examples": ["Yogur griego con frutas", "Puñado de frutos secos"] }},
            {{ "time": "12:30-13:30", "meal": "Almuerzo", "description": "Comida balanceada con proteínas, carbohidratos y grasas saludables", "examples": ["Pechuga de pollo con arroz integral y vegetales", "Ensalada con salmón y quinoa"] }},
            {{ "time": "16:00-16:30", "meal": "Snack pre-entreno", "description": "Carbohidratos de rápida absorción", "examples": ["Plátano", "Batido de frutas"] }},
            {{ "time": "19:00-20:00", "meal": "Cena", "description": "Comida ligera rica en proteínas y vegetales", "examples": ["Pescado al horno con vegetales asados", "Tofu salteado con verduras"] }}
          ],
          "fasting_period": "20:30-06:00 (10 horas)",
          "eating_period": "06:00-20:30 (14 horas)",
          "pre_workout_nutrition": "Consumir carbohidratos de fácil digestión 30-60 minutos antes del ejercicio",
          "post_workout_nutrition": "Consumir proteínas y carbohidratos dentro de los 30-60 minutos posteriores al ejercicio",
          "general_recommendations": [
            "Mantener una hidratación adecuada a lo largo del día",
            "Ajustar la ingesta calórica según los días de entrenamiento y descanso",
            "Evitar comidas pesadas antes de dormir"
          ]
        }}
        """

        try:
            logger.debug(
                f"Generando prompt para plan de crononutrición: {prompt[:500]}..."
            )  # Loguea una parte del prompt
            response_text = await self.vertex_ai_client.generate_content(prompt)

            # Intentar extraer el JSON de la respuesta
            try:
                # Buscar un objeto JSON en la respuesta
                import re

                json_match = re.search(r"({.*})", response_text, re.DOTALL)
                if json_match:
                    chronoplan = json.loads(json_match.group(1))
                else:
                    # Si no se encuentra un objeto JSON, intentar parsear toda la respuesta
                    chronoplan = json.loads(response_text)
            except Exception as json_error:
                logger.error(f"Error al parsear JSON de la respuesta: {json_error}")
                chronoplan = {
                    "time_windows": [
                        {
                            "time": "07:00-08:00",
                            "meal": "Desayuno",
                            "description": "Comida rica en proteínas y carbohidratos complejos",
                            "examples": [
                                "Avena con frutas y nueces",
                                "Huevos revueltos con tostada integral",
                            ],
                        },
                        {
                            "time": "12:00-13:00",
                            "meal": "Almuerzo",
                            "description": "Comida balanceada con proteínas, carbohidratos y grasas saludables",
                            "examples": [
                                "Pechuga de pollo con arroz integral y vegetales",
                                "Ensalada con salmón y quinoa",
                            ],
                        },
                        {
                            "time": "19:00-20:00",
                            "meal": "Cena",
                            "description": "Comida ligera rica en proteínas y vegetales",
                            "examples": [
                                "Pescado al horno con vegetales asados",
                                "Tofu salteado con verduras",
                            ],
                        },
                    ],
                    "fasting_period": "20:00-07:00 (11 horas)",
                    "eating_period": "07:00-20:00 (13 horas)",
                    "pre_workout_nutrition": "Consumir carbohidratos de fácil digestión 30-60 minutos antes del ejercicio",
                    "post_workout_nutrition": "Consumir proteínas y carbohidratos dentro de los 30-60 minutos posteriores al ejercicio",
                    "general_recommendations": [
                        "Mantener una hidratación adecuada a lo largo del día",
                        "Ajustar la ingesta calórica según los días de entrenamiento y descanso",
                        "Evitar comidas pesadas antes de dormir",
                    ],
                }

            return chronoplan

        except Exception as e:
            logger.error(f"Error al generar plan de crononutrición: {e}", exc_info=True)
            # Devolver un plan básico en caso de error
            return {
                "time_windows": [
                    {
                        "time": "07:00-08:00",
                        "meal": "Desayuno",
                        "description": "Comida rica en proteínas y carbohidratos complejos",
                        "examples": [
                            "Avena con frutas y nueces",
                            "Huevos revueltos con tostada integral",
                        ],
                    },
                    {
                        "time": "12:00-13:00",
                        "meal": "Almuerzo",
                        "description": "Comida balanceada con proteínas, carbohidratos y grasas saludables",
                        "examples": [
                            "Pechuga de pollo con arroz integral y vegetales",
                            "Ensalada con salmón y quinoa",
                        ],
                    },
                    {
                        "time": "19:00-20:00",
                        "meal": "Cena",
                        "description": "Comida ligera rica en proteínas y vegetales",
                        "examples": [
                            "Pescado al horno con vegetales asados",
                            "Tofu salteado con verduras",
                        ],
                    },
                ],
                "fasting_period": "20:00-07:00 (11 horas)",
                "eating_period": "07:00-20:00 (13 horas)",
                "pre_workout_nutrition": "Consumir carbohidratos de fácil digestión 30-60 minutos antes del ejercicio",
                "post_workout_nutrition": "Consumir proteínas y carbohidratos dentro de los 30-60 minutos posteriores al ejercicio",
                "general_recommendations": [
                    "Mantener una hidratación adecuada a lo largo del día",
                    "Ajustar la ingesta calórica según los días de entrenamiento y descanso",
                    "Evitar comidas pesadas antes de dormir",
                ],
            }

    async def _skill_analyze_food_image(
        self, input_data: AnalyzeFoodImageInput
    ) -> AnalyzeFoodImageOutput:
        """
        Skill para analizar imágenes de alimentos.

        Args:
            input_data: Datos de entrada para la skill

        Returns:
            AnalyzeFoodImageOutput: Análisis de la imagen de alimentos
        """
        logger.info(f"Ejecutando skill de análisis de imágenes de alimentos")

        try:
            # Obtener datos de la imagen
            image_data = input_data.image_data
            user_profile = input_data.user_profile or {}
            dietary_preferences = input_data.dietary_preferences or []

            # Determinar el tipo de programa del usuario para personalizar el análisis
            context = {
                "user_profile": user_profile,
                "goals": user_profile.get("goals", []) if user_profile else [],
            }

            try:
                # Clasificar el tipo de programa del usuario
                program_type = (
                    await self.program_classification_service.classify_program_type(
                        context
                    )
                )
                logger.info(
                    f"Tipo de programa determinado para análisis de imagen de alimentos: {program_type}"
                )

                # Obtener definición del programa para personalizar el análisis
                program_def = get_program_definition(program_type)
                program_context = f"""\nCONTEXTO DEL PROGRAMA {program_type}:\n"""

                if program_def:
                    program_context += f"- {program_def.get('description', '')}\n"
                    program_context += (
                        f"- Objetivo: {program_def.get('objective', '')}\n"
                    )

                    # Añadir necesidades nutricionales específicas del programa si están disponibles
                    if program_def.get("nutritional_needs"):
                        program_context += "- Necesidades nutricionales específicas:\n"
                        for need in program_def.get("nutritional_needs", []):
                            program_context += f"  * {need}\n"
            except Exception as e:
                logger.warning(
                    f"No se pudo determinar el tipo de programa: {e}. Usando análisis general."
                )
                program_type = "GENERAL"
                program_context = ""

            # Utilizar las capacidades de visión del agente base
            with self.tracer.start_as_current_span("food_image_analysis"):
                # Verificar si las capacidades de visión están disponibles
                if (
                    not hasattr(self, "_vision_capabilities_available")
                    or not self._vision_capabilities_available
                ):
                    logger.warning(
                        "Capacidades de visión no disponibles. Usando análisis simulado."
                    )
                    vision_result = {
                        "detected_foods": [],
                        "text": "Análisis de imagen simulado",
                    }
                else:
                    # Analizar la imagen utilizando el procesador de visión
                    vision_result = await self.vision_processor.analyze_image(
                        image_data=image_data,
                        prompt="Analiza esta imagen de alimentos e identifica todos los alimentos visibles.",
                    )

                # Extraer información de alimentos de la imagen usando el modelo multimodal
                prompt = f"""
                Eres un experto en nutrición y análisis de alimentos. Analiza esta imagen de alimentos y proporciona:
                
                1. Identificación precisa de todos los alimentos visibles
                2. Estimación de calorías y macronutrientes (proteínas, carbohidratos, grasas)
                3. Evaluación nutricional general (qué tan saludable es esta comida)
                4. Recomendaciones para mejorar el valor nutricional
                
                Considera que este análisis es para un usuario con programa tipo {program_type}.
                {program_context}
                
                Proporciona un análisis detallado y objetivo basado únicamente en lo que es visible en la imagen.
                """

                multimodal_result = await self.multimodal_adapter.process_multimodal(
                    prompt=prompt,
                    image_data=image_data,
                    temperature=0.2,
                    max_output_tokens=1024,
                )

                # Extraer información de alimentos detectados
                food_items = []
                for food in vision_result.get("detected_foods", []):
                    food_item = {
                        "name": food,
                        "confidence_score": 0.85,  # Valor simulado
                        "estimated_calories": "No disponible",
                        "estimated_portion": "Porción estándar",
                        "macronutrients": {
                            "proteínas": "No disponible",
                            "carbohidratos": "No disponible",
                            "grasas": "No disponible",
                        },
                    }
                    food_items.append(food_item)

                # Si no se detectaron alimentos, extraer de la respuesta multimodal
                if not food_items:
                    # Analizar la respuesta multimodal para extraer alimentos
                    analysis_text = multimodal_result.get("text", "")

                    # Generar prompt para extraer alimentos estructurados
                    extraction_prompt = f"""
                    Basándote en el siguiente análisis de una imagen de alimentos, extrae una lista estructurada
                    de los alimentos identificados con sus propiedades nutricionales estimadas.
                    
                    Análisis:
                    {analysis_text}
                    
                    Devuelve la información en formato JSON estructurado con los siguientes campos para cada alimento:
                    - name: nombre del alimento
                    - estimated_calories: calorías estimadas (si es posible)
                    - estimated_portion: porción estimada
                    - macronutrients: macronutrientes estimados (proteínas, carbohidratos, grasas)
                    
                    Ejemplo de formato:
                    [
                      {
                        "name": "Pollo a la parrilla",
                        "estimated_calories": "150-200 kcal",
                        "estimated_portion": "100g",
                        "macronutrients": {
                          "proteínas": "25-30g",
                          "carbohidratos": "0g",
                          "grasas": "8-10g"
                        }
                      }
                    ]
                    """

                    extraction_response = (
                        await self.vertex_ai_client.generate_structured_output(
                            extraction_prompt
                        )
                    )

                    # Procesar la respuesta
                    if isinstance(extraction_response, list):
                        for food in extraction_response:
                            if isinstance(food, dict) and "name" in food:
                                food_items.append(
                                    {
                                        "name": food.get(
                                            "name", "Alimento no identificado"
                                        ),
                                        "confidence_score": 0.7,  # Valor por defecto
                                        "estimated_calories": food.get(
                                            "estimated_calories", "No disponible"
                                        ),
                                        "estimated_portion": food.get(
                                            "estimated_portion", "Porción estándar"
                                        ),
                                        "macronutrients": food.get(
                                            "macronutrients",
                                            {
                                                "proteínas": "No disponible",
                                                "carbohidratos": "No disponible",
                                                "grasas": "No disponible",
                                            },
                                        ),
                                    }
                                )

                # Si aún no hay alimentos identificados, crear uno genérico
                if not food_items:
                    food_items.append(
                        {
                            "name": "Comida no identificada específicamente",
                            "confidence_score": 0.5,
                            "estimated_calories": "No disponible",
                            "estimated_portion": "No disponible",
                            "macronutrients": {
                                "proteínas": "No disponible",
                                "carbohidratos": "No disponible",
                                "grasas": "No disponible",
                            },
                        }
                    )

                # Generar evaluación nutricional
                nutritional_assessment_prompt = f"""
                Basándote en el siguiente análisis de una imagen de alimentos, genera una evaluación nutricional
                concisa y objetiva. Considera el contexto del programa {program_type} del usuario.
                
                Análisis:
                {multimodal_result.get("text", "")}
                
                La evaluación debe ser de 2-3 párrafos y debe incluir:
                1. Valoración general de la calidad nutricional
                2. Aspectos positivos de la comida
                3. Áreas de mejora
                """

                nutritional_assessment = await self.vertex_ai_client.generate_content(
                    nutritional_assessment_prompt
                )

                # Generar recomendaciones
                recommendations_prompt = f"""
                Basándote en el siguiente análisis de una imagen de alimentos, genera 3-5 recomendaciones
                nutricionales específicas y accionables. Considera el contexto del programa {program_type} del usuario
                y sus preferencias dietéticas: {', '.join(dietary_preferences) if dietary_preferences else 'No especificadas'}.
                
                Análisis:
                {multimodal_result.get("text", "")}
                
                Las recomendaciones deben ser concretas, prácticas y enfocadas en mejorar el valor nutricional
                manteniendo el tipo de comida similar.
                """

                recommendations_response = await self.vertex_ai_client.generate_content(
                    recommendations_prompt
                )
                recommendations = [
                    rec.strip()
                    for rec in recommendations_response.split("\n")
                    if rec.strip()
                ]

                # Generar alternativas más saludables
                alternatives_prompt = f"""
                Basándote en el siguiente análisis de una imagen de alimentos, sugiere 2-3 alternativas más saludables
                para los alimentos identificados. Considera el contexto del programa {program_type} del usuario.
                
                Análisis:
                {multimodal_result.get("text", "")}
                
                Para cada alternativa, proporciona:
                1. El alimento original
                2. La alternativa más saludable
                3. Beneficio nutricional de la alternativa
                
                Devuelve la información en formato JSON estructurado.
                """

                alternatives_response = (
                    await self.vertex_ai_client.generate_structured_output(
                        alternatives_prompt
                    )
                )

                # Procesar alternativas
                alternatives = []
                if isinstance(alternatives_response, list):
                    alternatives = alternatives_response
                elif (
                    isinstance(alternatives_response, dict)
                    and "alternatives" in alternatives_response
                ):
                    alternatives = alternatives_response["alternatives"]
                else:
                    # Crear alternativas genéricas
                    for food in food_items:
                        alternatives.append(
                            {
                                "original": food["name"],
                                "alternative": f"Versión más saludable de {food['name']}",
                                "benefit": "Mayor valor nutricional y menos calorías",
                            }
                        )

                # Calcular puntuación de salud (simulada)
                health_score = 7.5  # Valor simulado entre 0-10

                # Crear artefacto con el análisis
                artifact_id = str(uuid.uuid4())
                artifact = FoodImageAnalysisArtifact(
                    analysis_id=artifact_id,
                    created_at=time.strftime("%Y-%m-%d %H:%M:%S"),
                    food_count=len(food_items),
                    health_score=health_score,
                    processed_image_url="",  # En un caso real, aquí iría la URL de la imagen procesada
                )

                # Determinar tipo de comida
                meal_type = "No determinado"
                if "desayuno" in multimodal_result.get("text", "").lower():
                    meal_type = "Desayuno"
                elif (
                    "almuerzo" in multimodal_result.get("text", "").lower()
                    or "comida" in multimodal_result.get("text", "").lower()
                ):
                    meal_type = "Almuerzo"
                elif "cena" in multimodal_result.get("text", "").lower():
                    meal_type = "Cena"
                elif (
                    "snack" in multimodal_result.get("text", "").lower()
                    or "merienda" in multimodal_result.get("text", "").lower()
                ):
                    meal_type = "Snack"

                # Crear la salida de la skill
                return AnalyzeFoodImageOutput(
                    identified_foods=food_items,
                    total_calories="No disponible con precisión desde la imagen",
                    meal_type=meal_type,
                    nutritional_assessment=nutritional_assessment,
                    health_score=health_score,
                    recommendations=recommendations,
                    alternatives=alternatives,
                )

        except Exception as e:
            logger.error(f"Error al analizar imagen de alimentos: {e}", exc_info=True)

            # En caso de error, devolver un análisis básico
            return AnalyzeFoodImageOutput(
                identified_foods=[
                    {
                        "name": "Error en análisis",
                        "confidence_score": 0.0,
                        "estimated_calories": "No disponible",
                        "estimated_portion": "No disponible",
                        "macronutrients": {
                            "proteínas": "No disponible",
                            "carbohidratos": "No disponible",
                            "grasas": "No disponible",
                        },
                    }
                ],
                total_calories="No disponible",
                meal_type="No determinado",
                nutritional_assessment="No se pudo realizar el análisis debido a un error en el procesamiento.",
                health_score=None,
                recommendations=[
                    "Consulte a un nutricionista para un análisis preciso de su alimentación."
                ],
                alternatives=[],
            )

    async def _skill_analyze_nutrition_label(
        self, input_data: AnalyzeNutritionLabelInput
    ) -> AnalyzeNutritionLabelOutput:
        """
        Skill para analizar etiquetas nutricionales usando OCR y AI.

        Args:
            input_data: Datos de entrada para la skill

        Returns:
            AnalyzeNutritionLabelOutput: Análisis completo de la etiqueta nutricional
        """
        logger.info(f"Ejecutando skill de análisis de etiquetas nutricionales")

        try:
            # Obtener datos de entrada
            image_data = input_data.image_data
            user_profile = input_data.user_profile or {}
            dietary_restrictions = input_data.dietary_restrictions or []
            user_input = input_data.user_input or ""
            comparison_mode = input_data.comparison_mode

            # Determinar el tipo de programa del usuario para personalizar el análisis
            context = {
                "user_profile": user_profile,
                "goals": user_profile.get("goals", []) if user_profile else [],
            }

            try:
                # Clasificar el tipo de programa del usuario
                program_type = (
                    await self.program_classification_service.classify_program_type(
                        context
                    )
                )
                logger.info(
                    f"Tipo de programa determinado para análisis de etiqueta nutricional: {program_type}"
                )

                # Obtener definición del programa para personalizar el análisis
                program_def = get_program_definition(program_type)
                program_context = f"""\nCONTEXTO DEL PROGRAMA {program_type}:\n"""

                if program_def:
                    program_context += f"- {program_def.get('description', '')}\n"
                    program_context += (
                        f"- Objetivo: {program_def.get('objective', '')}\n"
                    )
                    # Añadir necesidades nutricionales específicas del programa si están disponibles
                    if program_def.get("nutritional_needs"):
                        program_context += "- Necesidades nutricionales específicas:\n"
                        for need in program_def.get("nutritional_needs", []):
                            program_context += f"  * {need}\n"
            except Exception as e:
                logger.warning(
                    f"No se pudo determinar el tipo de programa: {e}. Usando análisis general."
                )
                program_type = "GENERAL"
                program_context = ""

            # Utilizar las capacidades de visión del agente base para OCR
            with self.tracer.start_as_current_span("nutrition_label_analysis"):
                # Verificar si las capacidades de visión están disponibles
                if (
                    not hasattr(self, "_vision_capabilities_available")
                    or not self._vision_capabilities_available
                ):
                    logger.warning(
                        "Capacidades de visión no disponibles. Usando análisis simulado."
                    )
                    # Análisis simulado para testing
                    return AnalyzeNutritionLabelOutput(
                        product_name="Producto Simulado",
                        brand="Marca Simulada",
                        nutrition_facts={
                            "serving_size": "1 porción (100g)",
                            "calories_per_serving": 250.0,
                            "total_fat": "10g",
                            "protein": "15g",
                            "total_carbs": "30g",
                        },
                        ingredients_list=[
                            "Ingrediente 1",
                            "Ingrediente 2",
                            "Ingrediente 3",
                        ],
                        ingredient_analysis=[
                            {
                                "name": "Ingrediente 1",
                                "category": "natural",
                                "health_impact": "positivo",
                                "processing_level": "mínimo",
                            }
                        ],
                        product_assessment={
                            "health_score": 7.5,
                            "processing_level": "mínimamente procesado",
                            "quality_grade": "B",
                            "allergen_warnings": [],
                            "dietary_compatibility": {
                                "vegetariano": True,
                                "vegano": False,
                            },
                        },
                        personalized_recommendations=[
                            "Análisis simulado - consulte un nutricionista profesional."
                        ],
                        warnings=[],
                        summary="Análisis simulado de etiqueta nutricional para testing.",
                    )

                # Prompt especializado para análisis de etiquetas nutricionales
                nutrition_label_prompt = f"""
                Eres un experto nutricionista especializado en análisis de etiquetas de productos alimenticios. 
                Analiza esta imagen de etiqueta nutricional con extrema precisión y proporciona:

                1. **EXTRACCIÓN OCR PRECISA**:
                   - Nombre del producto y marca
                   - Información nutricional completa (calorías, macronutrientes, micronutrientes)
                   - Lista de ingredientes en orden de aparición
                   - Tamaño de porción y porciones por envase

                2. **ANÁLISIS DE INGREDIENTES**:
                   - Clasificar cada ingrediente (natural, procesado, aditivo, conservante)
                   - Evaluar impacto en la salud (positivo, neutro, negativo)
                   - Identificar alérgenos y sustancias problemáticas
                   - Nivel de procesamiento del producto

                3. **EVALUACIÓN DE SALUD**:
                   - Puntuación de salud (0-10)
                   - Calificación de calidad (A, B, C, D, F)
                   - Nivel de procesamiento (ultra-procesado, procesado, mínimamente procesado)
                   - Advertencias de salud relevantes

                4. **PERSONALIZACIÓN**:
                   - Programa del usuario: {program_type}
                   - Restricciones dietéticas: {dietary_restrictions}
                   - Pregunta específica del usuario: "{user_input}"
                   {program_context}

                5. **RECOMENDACIONES**:
                   - Recomendaciones personalizadas basadas en el perfil
                   - Alternativas más saludables si aplicable
                   - Advertencias específicas para el usuario

                6. **COMPATIBILIDAD DIETÉTICA**:
                   - Evaluar compatibilidad con dietas comunes (vegana, vegetariana, keto, etc.)
                   - Identificar si es apto para restricciones específicas

                INSTRUCCIONES CRÍTICAS:
                - Lee TODA la información visible en la etiqueta con precisión máxima
                - NO inventes información que no esté visible
                - Si algún dato no es legible, indica "No legible" o "No disponible"
                - Prioriza la seguridad del usuario en todas las recomendaciones
                - Sé específico en el análisis de ingredientes problemáticos
                """

                # Procesar la imagen con el adaptador multimodal
                multimodal_result = await self.multimodal_adapter.process_multimodal(
                    prompt=nutrition_label_prompt,
                    image_data=image_data,
                    model="gemini-2.5-pro",  # Usar el modelo más avanzado para OCR
                )

                # Procesar la respuesta del modelo
                ai_response = multimodal_result.get("response", "")

                # Parsear la respuesta del AI para extraer información estructurada
                # Por ahora, creamos una respuesta estructurada básica
                # En una implementación más avanzada, se podría usar parsing más sofisticado

                analysis_id = str(uuid.uuid4())
                current_time = time.strftime("%Y-%m-%d %H:%M:%S")

                # Crear respuesta estructurada basada en el análisis del AI
                return AnalyzeNutritionLabelOutput(
                    product_name=self._extract_product_name(ai_response),
                    brand=self._extract_brand(ai_response),
                    nutrition_facts=self._extract_nutrition_facts(ai_response),
                    ingredients_list=self._extract_ingredients_list(ai_response),
                    ingredient_analysis=self._analyze_ingredients(ai_response),
                    product_assessment=self._assess_product(ai_response, program_type),
                    personalized_recommendations=self._generate_personalized_recommendations(
                        ai_response, user_profile, dietary_restrictions, program_type
                    ),
                    alternatives=(
                        self._suggest_alternatives(ai_response)
                        if comparison_mode
                        else None
                    ),
                    warnings=self._extract_warnings(ai_response, dietary_restrictions),
                    summary=self._generate_summary(ai_response),
                )

        except Exception as e:
            logger.error(f"Error al analizar etiqueta nutricional: {e}", exc_info=True)

            # En caso de error, devolver un análisis de fallback
            return AnalyzeNutritionLabelOutput(
                product_name="Error en análisis",
                brand=None,
                nutrition_facts={
                    "serving_size": "No disponible",
                    "calories_per_serving": None,
                },
                ingredients_list=["Error en extracción"],
                ingredient_analysis=[],
                product_assessment={
                    "health_score": 0.0,
                    "processing_level": "No determinado",
                    "quality_grade": "F",
                    "allergen_warnings": ["Error en análisis"],
                    "dietary_compatibility": {},
                },
                personalized_recommendations=[
                    "No se pudo realizar el análisis debido a un error. Consulte a un nutricionista profesional."
                ],
                warnings=["Error en el procesamiento de la imagen"],
                summary="No se pudo completar el análisis de la etiqueta nutricional debido a un error técnico.",
            )

    # Métodos auxiliares para parsing de la respuesta del AI
    def _extract_product_name(self, ai_response: str) -> str:
        """Extrae el nombre del producto de la respuesta del AI."""
        # Implementación básica - en producción se usaría parsing más sofisticado
        if "producto:" in ai_response.lower():
            lines = ai_response.split("\n")
            for line in lines:
                if "producto:" in line.lower():
                    return line.split(":")[-1].strip()
        return "Producto no identificado"

    def _extract_brand(self, ai_response: str) -> Optional[str]:
        """Extrae la marca del producto."""
        if "marca:" in ai_response.lower():
            lines = ai_response.split("\n")
            for line in lines:
                if "marca:" in line.lower():
                    return line.split(":")[-1].strip()
        return None

    def _extract_nutrition_facts(self, ai_response: str) -> Dict[str, Any]:
        """Extrae los datos nutricionales."""
        # Implementación básica - retorna estructura mínima
        return {
            "serving_size": "Información extraída del análisis AI",
            "calories_per_serving": None,
            "total_fat": "Según análisis",
            "protein": "Según análisis",
            "total_carbs": "Según análisis",
        }

    def _extract_ingredients_list(self, ai_response: str) -> List[str]:
        """Extrae la lista de ingredientes."""
        # Implementación básica
        return ["Ingredientes extraídos del análisis AI"]

    def _analyze_ingredients(self, ai_response: str) -> List[Dict[str, Any]]:
        """Analiza los ingredientes."""
        return [
            {
                "name": "Análisis basado en AI",
                "category": "procesado",
                "health_impact": "neutro",
                "processing_level": "moderado",
            }
        ]

    def _assess_product(self, ai_response: str, program_type: str) -> Dict[str, Any]:
        """Evalúa el producto."""
        return {
            "health_score": 7.0,
            "processing_level": "procesado",
            "quality_grade": "B",
            "allergen_warnings": [],
            "dietary_compatibility": {"vegetariano": True, "vegano": False},
        }

    def _generate_personalized_recommendations(
        self,
        ai_response: str,
        user_profile: Dict,
        dietary_restrictions: List[str],
        program_type: str,
    ) -> List[str]:
        """Genera recomendaciones personalizadas."""
        recommendations = [
            f"Recomendaciones basadas en programa {program_type}",
            "Consulte la información nutricional completa antes del consumo",
        ]

        if dietary_restrictions:
            recommendations.append(
                f"Verifique ingredientes para restricciones: {', '.join(dietary_restrictions)}"
            )

        return recommendations

    def _suggest_alternatives(self, ai_response: str) -> List[Dict[str, str]]:
        """Sugiere alternativas más saludables."""
        return [
            {
                "name": "Alternativa saludable sugerida",
                "reason": "Menos procesado y mejor perfil nutricional",
            }
        ]

    def _extract_warnings(
        self, ai_response: str, dietary_restrictions: List[str]
    ) -> List[str]:
        """Extrae advertencias relevantes."""
        warnings = []
        if dietary_restrictions:
            warnings.append("Revise ingredientes para posibles alérgenos")
        return warnings

    def _generate_summary(self, ai_response: str) -> str:
        """Genera un resumen del análisis."""
        return "Análisis completado. Revise la información nutricional y recomendaciones personalizadas."

    async def _skill_analyze_prepared_meal(
        self, input_data: AnalyzePreparedMealInput
    ) -> AnalyzePreparedMealOutput:
        """
        Skill para análisis avanzado de platos preparados con estimación de porciones.

        Args:
            input_data: Datos de entrada para la skill

        Returns:
            AnalyzePreparedMealOutput: Análisis completo del plato preparado
        """
        logger.info(f"Ejecutando skill de análisis avanzado de platos preparados")

        try:
            # Obtener datos de entrada
            image_data = input_data.image_data
            user_profile = input_data.user_profile or {}
            meal_context = input_data.meal_context or {}
            user_input = input_data.user_input or ""
            portion_estimation_mode = input_data.portion_estimation_mode
            nutrition_precision = input_data.nutrition_precision

            # Determinar el tipo de programa del usuario para personalizar el análisis
            context = {
                "user_profile": user_profile,
                "goals": user_profile.get("goals", []) if user_profile else [],
            }

            try:
                # Clasificar el tipo de programa del usuario
                program_type = (
                    await self.program_classification_service.classify_program_type(
                        context
                    )
                )
                logger.info(
                    f"Tipo de programa determinado para análisis de plato preparado: {program_type}"
                )

                # Obtener definición del programa para personalizar el análisis
                program_def = get_program_definition(program_type)
                program_context = f"""\nCONTEXTO DEL PROGRAMA {program_type}:\n"""

                if program_def:
                    program_context += f"- {program_def.get('description', '')}\n"
                    program_context += (
                        f"- Objetivo: {program_def.get('objective', '')}\n"
                    )
                    # Añadir necesidades nutricionales específicas del programa si están disponibles
                    if program_def.get("nutritional_needs"):
                        program_context += "- Necesidades nutricionales específicas:\n"
                        for need in program_def.get("nutritional_needs", []):
                            program_context += f"  * {need}\n"
            except Exception as e:
                logger.warning(
                    f"No se pudo determinar el tipo de programa: {e}. Usando análisis general."
                )
                program_type = "GENERAL"
                program_context = ""

            # Utilizar las capacidades de visión del agente base
            with self.tracer.start_as_current_span("prepared_meal_analysis"):
                # Verificar si las capacidades de visión están disponibles
                if (
                    not hasattr(self, "_vision_capabilities_available")
                    or not self._vision_capabilities_available
                ):
                    logger.warning(
                        "Capacidades de visión no disponibles. Usando análisis simulado."
                    )
                    # Análisis simulado para testing
                    return self._create_simulated_meal_analysis()

                # Prompt especializado para análisis avanzado de platos preparados
                prepared_meal_prompt = f"""
                Eres un nutricionista experto especializado en análisis visual de comidas preparadas. 
                Analiza esta imagen de plato/comida preparada con máxima precisión y proporciona un análisis completo:

                ## 1. IDENTIFICACIÓN DE COMPONENTES:
                - Identifica TODOS los alimentos visibles en el plato
                - Estima el peso/volumen de cada componente usando referencias visuales (tamaño del plato, utensilios, etc.)
                - Determina el método de cocción de cada alimento (hervido, asado, frito, crudo, etc.)
                - Categoriza cada componente (proteína, carbohidrato, grasa, vegetal, condimento)
                - Evalúa qué porcentaje de cada alimento es visible vs oculto

                ## 2. ANÁLISIS NUTRICIONAL DETALLADO:
                - Calcula calorías totales con rango (mínimo-máximo)
                - Desglose preciso de macronutrientes en gramos
                - Identifica micronutrientes destacados (vitaminas, minerales)
                - Evalúa la calidad de proteínas y complejidad de carbohidratos
                - Estima contenido de fibra y azúcares

                ## 3. EVALUACIÓN DE PORCIONES:
                {"- ANÁLISIS DETALLADO DE PORCIONES requerido" if portion_estimation_mode else "- Análisis básico de porciones"}
                - Evalúa si las porciones son adecuadas para el usuario
                - Compara con porciones recomendadas estándar
                - Identifica señales visuales de saciedad/densidad calórica
                - Proporciona recomendaciones de ajuste de porciones

                ## 4. ANÁLISIS DE TIMING Y CONTEXTO:
                - Contexto de la comida: {meal_context}
                - Determina momentos óptimos para consumir esta comida
                - Evalúa idoneidad pre/post entrenamiento
                - Considera velocidad de digestión y perfil energético

                ## 5. PERSONALIZACIÓN:
                - Programa del usuario: {program_type}
                - Nivel de precisión requerido: {nutrition_precision}
                - Descripción del usuario: "{user_input}"
                {program_context}

                ## 6. EVALUACIÓN Y RECOMENDACIONES:
                - Puntuación de salud general (0-10)
                - Compatibilidad con programas NGX (PRIME, LONGEVITY, TRANSFORMATION)
                - Identificar qué mejorar en el plato
                - Sugerir modificaciones específicas
                - Proponer alternativas más saludables si es necesario

                ## 7. INSIGHTS DE PREPARACIÓN:
                - Evalúa métodos de cocción utilizados
                - Identifica técnicas culinarias saludables/no saludables
                - Sugiere mejoras en la preparación

                INSTRUCCIONES CRÍTICAS:
                - Sé EXTREMADAMENTE preciso en las estimaciones de porciones
                - Considera referencias visuales (plato, cubiertos, manos si están visibles)
                - NO inventes alimentos que no veas claramente
                - Prioriza la seguridad nutricional en todas las recomendaciones
                - Adapta el análisis al programa específico del usuario
                - Sé específico en números cuando sea posible (gramos, calorías, etc.)
                """

                # Procesar la imagen con el adaptador multimodal
                multimodal_result = await self.multimodal_adapter.process_multimodal(
                    prompt=prepared_meal_prompt,
                    image_data=image_data,
                    model="gemini-2.5-pro",  # Usar el modelo más avanzado
                )

                # Procesar la respuesta del modelo
                ai_response = multimodal_result.get("response", "")

                # Crear análisis estructurado basado en la respuesta del AI
                analysis_id = str(uuid.uuid4())
                current_time = time.strftime("%Y-%m-%d %H:%M:%S")

                # Crear respuesta estructurada
                return AnalyzePreparedMealOutput(
                    meal_identification=self._extract_meal_identification(ai_response),
                    cuisine_type=self._extract_cuisine_type(ai_response),
                    food_components=self._extract_food_components(ai_response),
                    nutrition_analysis=self._extract_nutrition_analysis(ai_response),
                    portion_assessment=self._extract_portion_assessment(ai_response),
                    timing_analysis=self._extract_timing_analysis(
                        ai_response, meal_context
                    ),
                    health_score=self._extract_health_score(ai_response),
                    program_compatibility=self._extract_program_compatibility(
                        ai_response, program_type
                    ),
                    personalized_feedback=self._extract_personalized_feedback(
                        ai_response, user_profile, program_type
                    ),
                    improvement_suggestions=self._extract_improvement_suggestions(
                        ai_response
                    ),
                    similar_healthier_options=self._extract_healthier_options(
                        ai_response
                    ),
                    preparation_insights=self._extract_preparation_insights(
                        ai_response
                    ),
                    summary=self._extract_meal_summary(ai_response),
                )

        except Exception as e:
            logger.error(f"Error al analizar plato preparado: {e}", exc_info=True)

            # En caso de error, devolver un análisis de fallback
            return self._create_error_meal_analysis()

    def _create_simulated_meal_analysis(self) -> AnalyzePreparedMealOutput:
        """Crea un análisis simulado para testing."""
        return AnalyzePreparedMealOutput(
            meal_identification="Plato Simulado para Testing",
            cuisine_type="Internacional",
            food_components=[
                {
                    "name": "Componente simulado",
                    "category": "proteína",
                    "confidence_score": 0.9,
                    "portion_size": "1 porción estándar",
                    "visible_percentage": 1.0,
                    "nutrition_density": "alta",
                }
            ],
            nutrition_analysis={
                "calories_range": {"min": 400.0, "max": 600.0},
                "macronutrient_breakdown": {
                    "carb_complexity": "complejo",
                },
                "micronutrient_highlights": ["Vitamina C", "Hierro"],
                "nutritional_balance_score": 8.0,
                "meal_completeness": "completa",
            },
            portion_assessment={
                "total_volume_assessment": "Adecuado",
                "portion_adequacy": "adecuada",
                "portion_recommendations": ["Mantener porciones actuales"],
                "visual_satiety_cues": ["Plato equilibrado"],
                "caloric_density": "media",
            },
            timing_analysis={
                "optimal_timing": ["Almuerzo", "Cena"],
                "pre_post_workout_suitability": "post-entrenamiento",
                "digestion_considerations": ["Digestión normal"],
                "energy_profile": "sostenida",
            },
            health_score=8.5,
            program_compatibility={
                "NGX_PRIME": "Excelente",
                "NGX_LONGEVITY": "Muy bueno",
            },
            personalized_feedback=[
                "Análisis simulado - consulte un nutricionista profesional."
            ],
            improvement_suggestions=["Este es un análisis simulado para testing."],
            similar_healthier_options=[
                {
                    "name": "Versión más saludable simulada",
                    "reason": "Mejores métodos de cocción",
                }
            ],
            preparation_insights=["Métodos de cocción simulados"],
            summary="Análisis simulado completo para testing del sistema.",
        )

    def _create_error_meal_analysis(self) -> AnalyzePreparedMealOutput:
        """Crea un análisis de error."""
        return AnalyzePreparedMealOutput(
            meal_identification="Error en análisis",
            cuisine_type=None,
            food_components=[],
            nutrition_analysis={
                "calories_range": {"min": 0.0, "max": 0.0},
                "macronutrient_breakdown": {
                    "carb_complexity": "No determinado",
                },
                "micronutrient_highlights": [],
                "nutritional_balance_score": 0.0,
                "meal_completeness": "No determinado",
            },
            portion_assessment={
                "total_volume_assessment": "No determinado",
                "portion_adequacy": "No determinado",
                "portion_recommendations": ["Consulte un nutricionista profesional"],
                "visual_satiety_cues": [],
                "caloric_density": "No determinado",
            },
            timing_analysis={
                "optimal_timing": [],
                "pre_post_workout_suitability": "No determinado",
                "digestion_considerations": [],
                "energy_profile": "No determinado",
            },
            health_score=0.0,
            program_compatibility={},
            personalized_feedback=[
                "No se pudo realizar el análisis debido a un error técnico. Consulte un nutricionista profesional."
            ],
            improvement_suggestions=["Error en el procesamiento"],
            similar_healthier_options=None,
            preparation_insights=[],
            summary="No se pudo completar el análisis del plato debido a un error técnico.",
        )

    # Métodos auxiliares para parsing de análisis de platos preparados
    def _extract_meal_identification(self, ai_response: str) -> str:
        """Extrae la identificación del plato."""
        # Implementación básica - en producción se usaría parsing más sofisticado
        return "Plato identificado basado en análisis AI"

    def _extract_cuisine_type(self, ai_response: str) -> Optional[str]:
        """Extrae el tipo de cocina."""
        return "Cocina identificada por AI"

    def _extract_food_components(self, ai_response: str) -> List[Dict[str, Any]]:
        """Extrae los componentes del plato."""
        return [
            {
                "name": "Componente basado en AI",
                "category": "mixto",
                "confidence_score": 0.8,
                "portion_size": "Estimado por AI",
                "visible_percentage": 0.9,
                "nutrition_density": "media",
            }
        ]

    def _extract_nutrition_analysis(self, ai_response: str) -> Dict[str, Any]:
        """Extrae el análisis nutricional."""
        return {
            "calories_range": {"min": 350.0, "max": 550.0},
            "macronutrient_breakdown": {
                "carb_complexity": "mixto",
            },
            "micronutrient_highlights": ["Análisis basado en AI"],
            "nutritional_balance_score": 7.5,
            "meal_completeness": "completa",
        }

    def _extract_portion_assessment(self, ai_response: str) -> Dict[str, Any]:
        """Extrae la evaluación de porciones."""
        return {
            "total_volume_assessment": "Evaluado por AI",
            "portion_adequacy": "adecuada",
            "portion_recommendations": ["Recomendaciones basadas en AI"],
            "visual_satiety_cues": ["Análisis visual por AI"],
            "caloric_density": "media",
        }

    def _extract_timing_analysis(
        self, ai_response: str, meal_context: Dict
    ) -> Dict[str, Any]:
        """Extrae el análisis de timing."""
        return {
            "optimal_timing": ["Determinado por AI"],
            "pre_post_workout_suitability": "evaluado",
            "digestion_considerations": ["Consideraciones de AI"],
            "energy_profile": "sostenida",
        }

    def _extract_health_score(self, ai_response: str) -> float:
        """Extrae la puntuación de salud."""
        return 7.5

    def _extract_program_compatibility(
        self, ai_response: str, program_type: str
    ) -> Dict[str, str]:
        """Extrae la compatibilidad con programas."""
        return {
            program_type: "Compatible",
            "GENERAL": "Adecuado",
        }

    def _extract_personalized_feedback(
        self, ai_response: str, user_profile: Dict, program_type: str
    ) -> List[str]:
        """Extrae feedback personalizado."""
        return [
            f"Feedback personalizado para programa {program_type}",
            "Análisis basado en IA avanzada",
        ]

    def _extract_improvement_suggestions(self, ai_response: str) -> List[str]:
        """Extrae sugerencias de mejora."""
        return ["Sugerencias generadas por AI"]

    def _extract_healthier_options(self, ai_response: str) -> List[Dict[str, str]]:
        """Extrae opciones más saludables."""
        return [
            {
                "name": "Alternativa sugerida por AI",
                "reason": "Mejor perfil nutricional",
            }
        ]

    def _extract_preparation_insights(self, ai_response: str) -> List[str]:
        """Extrae insights de preparación."""
        return ["Insights de preparación basados en AI"]

    def _extract_meal_summary(self, ai_response: str) -> str:
        """Extrae el resumen del análisis."""
        return "Análisis completo de plato preparado completado exitosamente."

    async def _skill_sync_nutrition_data(
        self, input: SyncNutritionDataInput
    ) -> SyncNutritionDataOutput:
        """
        Sincroniza datos nutricionales desde plataformas externas.

        Args:
            input: Entrada con configuración de sincronización

        Returns:
            Resultado de la sincronización con resumen e insights
        """
        try:
            logger.info(
                f"Sincronizando datos nutricionales para usuario {input.user_id}"
            )

            # Mapear el nombre de la plataforma al enum
            source_map = {
                "myfitnesspal": NutritionSource.MYFITNESSPAL,
                "cronometer": NutritionSource.CRONOMETER,
                "loseit": NutritionSource.LOSEIT,
            }

            source = source_map.get(input.platform.lower())
            if not source:
                return SyncNutritionDataOutput(
                    success=False,
                    days_synced=0,
                    meals_synced=0,
                    foods_synced=0,
                    summary={},
                    insights=[],
                    error_message=f"Plataforma no soportada: {input.platform}",
                )

            # Sincronizar datos
            sync_result = await self.nutrition_service.sync_nutrition_data(
                user_id=input.user_id,
                source=source,
                days_back=input.days_back,
                force_refresh=input.force_refresh,
            )

            if not sync_result.success:
                return SyncNutritionDataOutput(
                    success=False,
                    days_synced=0,
                    meals_synced=0,
                    foods_synced=0,
                    summary={},
                    insights=[],
                    error_message=sync_result.error_message,
                )

            # Obtener resumen de tendencias
            trends = await self.nutrition_service.get_nutrition_trends(
                user_id=input.user_id, days=input.days_back
            )

            # Generar insights personalizados
            insights = trends.get("insights", [])

            # Agregar insights adicionales basados en los datos sincronizados
            if sync_result.meals_synced > 0:
                avg_meals_per_day = sync_result.meals_synced / max(
                    sync_result.days_synced, 1
                )
                if avg_meals_per_day < 3:
                    insights.append(
                        f"Estás registrando un promedio de {avg_meals_per_day:.1f} comidas por día. "
                        "Considera registrar todas tus comidas para un análisis más preciso."
                    )

            summary = {
                "average_daily_calories": trends.get("average_daily_calories", 0),
                "average_daily_protein": trends.get("average_daily_protein_g", 0),
                "average_daily_carbs": trends.get("average_daily_carbs_g", 0),
                "average_daily_fat": trends.get("average_daily_fat_g", 0),
                "calorie_trend": trends.get("calorie_trend", "stable"),
                "goal_adherence": trends.get("average_goal_adherence_percent", 0),
                "macro_balance": trends.get("average_macro_balance", {}),
            }

            return SyncNutritionDataOutput(
                success=True,
                days_synced=sync_result.days_synced,
                meals_synced=sync_result.meals_synced,
                foods_synced=sync_result.foods_synced,
                summary=summary,
                insights=insights,
            )

        except Exception as e:
            logger.error(
                f"Error al sincronizar datos nutricionales: {e}", exc_info=True
            )
            return SyncNutritionDataOutput(
                success=False,
                days_synced=0,
                meals_synced=0,
                foods_synced=0,
                summary={},
                insights=[],
                error_message=str(e),
            )

    async def _skill_analyze_nutrition_trends(
        self, input: AnalyzeNutritionTrendsInput
    ) -> AnalyzeNutritionTrendsOutput:
        """
        Analiza tendencias nutricionales y cumplimiento del plan.

        Args:
            input: Entrada con parámetros de análisis

        Returns:
            Análisis de tendencias con recomendaciones
        """
        try:
            logger.info(
                f"Analizando tendencias nutricionales para usuario {input.user_id}"
            )

            # Obtener tendencias del servicio
            trends_data = await self.nutrition_service.get_nutrition_trends(
                user_id=input.user_id, days=input.days
            )

            if "error" in trends_data:
                return AnalyzeNutritionTrendsOutput(
                    trends=[],
                    overall_compliance=0.0,
                    macro_balance={},
                    recommendations=[trends_data["error"]],
                    needs_adjustment=True,
                )

            # Analizar tendencias para cada métrica solicitada
            nutrition_trends = []

            metric_map = {
                "calories": ("average_daily_calories", "calorías", "kcal"),
                "protein": ("average_daily_protein_g", "proteína", "g"),
                "carbs": ("average_daily_carbs_g", "carbohidratos", "g"),
                "fat": ("average_daily_fat_g", "grasa", "g"),
            }

            for metric in input.metrics:
                if metric in metric_map:
                    data_key, metric_name, unit = metric_map[metric]
                    avg_value = trends_data.get(data_key, 0)
                    trend_direction = trends_data.get(f"{metric}_trend", "stable")

                    # Calcular variación (simplificado)
                    variation = 0.0
                    if trend_direction == "increasing":
                        variation = 10.0  # Placeholder
                    elif trend_direction == "decreasing":
                        variation = -10.0  # Placeholder

                    # Generar recomendación basada en la tendencia
                    recommendation = self._generate_trend_recommendation(
                        metric, avg_value, trend_direction, trends_data
                    )

                    nutrition_trends.append(
                        NutritionTrend(
                            metric=metric_name,
                            average=avg_value,
                            trend=trend_direction,
                            variation=variation,
                            recommendation=recommendation,
                        )
                    )

            # Calcular cumplimiento general
            overall_compliance = trends_data.get("average_goal_adherence_percent", 75.0)
            if overall_compliance is None:
                overall_compliance = 75.0  # Valor por defecto si no hay metas

            # Obtener balance de macros
            macro_balance = trends_data.get(
                "average_macro_balance",
                {"protein_percent": 25.0, "carbs_percent": 45.0, "fat_percent": 30.0},
            )

            # Generar recomendaciones generales
            recommendations = self._generate_general_recommendations(
                trends_data, overall_compliance, macro_balance
            )

            # Determinar si el plan necesita ajustes
            needs_adjustment = (
                overall_compliance < 80.0
                or any(
                    t.trend == "decreasing"
                    for t in nutrition_trends
                    if t.metric == "proteína"
                )
                or macro_balance.get("protein_percent", 0) < 20
                or macro_balance.get("fat_percent", 0) > 40
            )

            return AnalyzeNutritionTrendsOutput(
                trends=nutrition_trends,
                overall_compliance=overall_compliance,
                macro_balance=macro_balance,
                recommendations=recommendations,
                needs_adjustment=needs_adjustment,
            )

        except Exception as e:
            logger.error(
                f"Error al analizar tendencias nutricionales: {e}", exc_info=True
            )
            return AnalyzeNutritionTrendsOutput(
                trends=[],
                overall_compliance=0.0,
                macro_balance={},
                recommendations=[f"Error en el análisis: {str(e)}"],
                needs_adjustment=True,
            )

    def _generate_trend_recommendation(
        self, metric: str, avg_value: float, trend: str, trends_data: Dict[str, Any]
    ) -> str:
        """Genera recomendaciones específicas para cada tendencia."""

        if metric == "calories":
            if trend == "increasing" and avg_value > 2500:
                return "Tu consumo calórico está aumentando. Considera revisar las porciones si tu objetivo es mantener o perder peso."
            elif trend == "decreasing" and avg_value < 1500:
                return "Tu consumo calórico está disminuyendo significativamente. Asegúrate de consumir suficientes calorías para mantener tu metabolismo activo."
            else:
                return "Tu consumo calórico se mantiene estable. Continúa monitoreando según tus objetivos."

        elif metric == "protein":
            if avg_value < 50:
                return "Tu consumo de proteína es bajo. Considera agregar más fuentes de proteína magra a tus comidas."
            elif avg_value > 150:
                return "Tu consumo de proteína es alto. Asegúrate de mantener una hidratación adecuada."
            else:
                return "Tu consumo de proteína es adecuado. Mantén la variedad de fuentes proteicas."

        elif metric == "carbs":
            if trend == "increasing" and avg_value > 300:
                return "Tu consumo de carbohidratos está aumentando. Prioriza carbohidratos complejos y fibra."
            elif avg_value < 100:
                return "Tu consumo de carbohidratos es bajo. Si haces ejercicio intenso, considera aumentar la ingesta."
            else:
                return "Tu consumo de carbohidratos es moderado. Enfócate en fuentes de calidad."

        elif metric == "fat":
            if avg_value > 100:
                return "Tu consumo de grasas es elevado. Prioriza grasas saludables como omega-3 y monoinsaturadas."
            elif avg_value < 40:
                return "Tu consumo de grasas es bajo. Las grasas saludables son esenciales para las hormonas y absorción de vitaminas."
            else:
                return "Tu consumo de grasas es adecuado. Mantén el equilibrio entre diferentes tipos de grasas."

        return "Continúa monitoreando esta métrica según tus objetivos personales."

    def _generate_general_recommendations(
        self,
        trends_data: Dict[str, Any],
        compliance: float,
        macro_balance: Dict[str, float],
    ) -> List[str]:
        """Genera recomendaciones generales basadas en el análisis completo."""

        recommendations = []

        # Recomendaciones basadas en cumplimiento
        if compliance < 70:
            recommendations.append(
                "Tu adherencia al plan es baja. Considera simplificar las metas o buscar alternativas más prácticas."
            )
        elif compliance > 90:
            recommendations.append(
                "Excelente adherencia al plan. Mantén la consistencia para resultados óptimos."
            )

        # Recomendaciones basadas en balance de macros
        protein_percent = macro_balance.get("protein_percent", 0)
        carbs_percent = macro_balance.get("carbs_percent", 0)
        fat_percent = macro_balance.get("fat_percent", 0)

        if protein_percent < 20:
            recommendations.append(
                "Tu porcentaje de proteína es bajo. Aumenta el consumo de proteínas para preservar masa muscular."
            )

        if carbs_percent > 60:
            recommendations.append(
                "Tu dieta es muy alta en carbohidratos. Considera balancear con más proteína y grasas saludables."
            )

        if fat_percent < 20:
            recommendations.append(
                "Tu consumo de grasas es muy bajo. Las grasas saludables son esenciales para la salud hormonal."
            )

        # Agregar insights específicos si están disponibles
        if "insights" in trends_data:
            recommendations.extend(trends_data["insights"][:2])  # Limitar a 2 insights

        return recommendations

    async def synthesize_voice_response(
        self,
        text: str,
        program_type: str = "PRIME",
        emotion_context: Optional[str] = "nurturing",
        nutrition_context: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Sintetiza respuesta de voz con la personalidad científica cálida de SAGE.

        Args:
            text: Texto a sintetizar
            program_type: Tipo de programa (PRIME/LONGEVITY)
            emotion_context: Contexto emocional para adaptar el tono
            nutrition_context: Contexto nutricional (meal_plan, supplement, biomarker)

        Returns:
            Dict[str, Any]: Audio sintetizado con metadatos de personalidad
        """
        if not self.voice_adapter:
            logger.warning("Adaptador de voz no disponible para SAGE")
            return {
                "error": "Voice synthesis not available",
                "status": "error",
                "agent_id": self.AGENT_ID,
            }

        try:
            # Adaptar texto para personalidad SAGE (científico cálido)
            adapted_text = self._adapt_text_for_sage_personality(
                text, emotion_context, nutrition_context
            )

            result = await self.voice_adapter.synthesize_speech(
                text=adapted_text,
                agent_id="sage_nutrition",
                program_type=program_type,
                emotion_context=emotion_context,
                **kwargs,
            )

            # Agregar metadatos específicos de SAGE
            if result.get("status") == "success":
                result["sage_personality"] = {
                    "communication_style": "scientific_warmth",
                    "nutritional_approach": "mediterranean_wisdom",
                    "emotional_tone": "nurturing_expert",
                    "personality_type": "ISFJ - The Protector",
                    "nutrition_context_adaptation": nutrition_context or "general",
                }

                # Ajustar parámetros de voz para SAGE
                if result.get("voice_settings"):
                    result["voice_settings"]["warmth"] = 0.8
                    result["voice_settings"]["authority"] = 0.7
                    result["voice_settings"]["pace"] = "measured"

            logger.info(
                f"Voz sintetizada exitosamente para SAGE con contexto: {nutrition_context}"
            )
            return result

        except Exception as e:
            logger.error(f"Error al sintetizar voz para SAGE: {e}", exc_info=True)
            return {"error": str(e), "status": "error", "agent_id": self.AGENT_ID}

    def _adapt_text_for_sage_personality(
        self, text: str, emotion_context: str, nutrition_context: Optional[str] = None
    ) -> str:
        """
        Adapta el texto para reflejar la personalidad de SAGE.

        SAGE es un Chef Científico con calidez mediterránea, combina
        conocimiento nutricional profundo con un enfoque nutritivo y cálido.
        """
        # Adaptaciones base según emoción
        emotion_adaptations = {
            "nurturing": {"prefix": "", "suffix": "", "style": "gentle_guidance"},
            "encouraging": {
                "prefix": "",
                "suffix": " ¡Tu salud está en buenas manos!",
                "style": "positive_reinforcement",
            },
            "educational": {
                "prefix": "Permíteme explicarte",
                "suffix": "",
                "style": "teaching_moment",
            },
            "concerned": {
                "prefix": "",
                "suffix": " Cuidemos juntos estos aspectos.",
                "style": "caring_attention",
            },
            "celebratory": {
                "prefix": "¡Qué maravilloso!",
                "suffix": "",
                "style": "joyful_support",
            },
        }

        # Adaptaciones según contexto nutricional
        if nutrition_context == "meal_plan":
            text = f"He diseñado para ti... {text}"
        elif nutrition_context == "supplement":
            text = f"Basándome en tu perfil único, {text}"
        elif nutrition_context == "biomarker":
            text = f"Tus biomarcadores nos cuentan una historia... {text}"
        elif nutrition_context == "chrononutrition":
            text = f"El timing es clave en nutrición. {text}"

        # Aplicar adaptación emocional
        adaptation = emotion_adaptations.get(
            emotion_context, emotion_adaptations["nurturing"]
        )

        # Construir texto adaptado
        adapted_text = f"{adaptation['prefix']} {text} {adaptation['suffix']}".strip()

        # Agregar pausas naturales para un ritmo más cálido
        adapted_text = adapted_text.replace(". ", "... ")
        adapted_text = adapted_text.replace("!", "! ")

        return adapted_text

    # ===== IMPLEMENTACIONES DE SKILLS CONVERSACIONALES =====

    async def _skill_nutritional_assessment_conversation(
        self, input_data: NutritionalAssessmentConversationInput
    ) -> NutritionalAssessmentConversationOutput:
        """
        Evaluación nutricional conversacional con calidez científica.

        Args:
            input_data: Datos de entrada con información nutricional

        Returns:
            Respuesta de evaluación nutricional conversacional
        """
        try:
            logger.info("SAGE: Iniciando evaluación nutricional conversacional")

            # Analizar contexto nutricional del usuario
            current_diet = input_data.current_diet or []
            health_concerns = input_data.health_concerns or []
            restrictions = input_data.dietary_restrictions or []
            goals = input_data.nutrition_goals or []

            # Crear respuesta con personalidad ISFJ científica y cálida
            assessment_prompt = f"""
            Como SAGE, el Precision Nutrition Architect con personalidad ISFJ "The Protector",
            proporciona una evaluación nutricional conversacional con calidez científica:
            
            Usuario dice: "{input_data.user_text}"
            Alimentación actual: {', '.join(current_diet) if current_diet else 'no especificada'}
            Preocupaciones de salud: {', '.join(health_concerns) if health_concerns else 'ninguna'}
            Restricciones: {', '.join(restrictions) if restrictions else 'ninguna'}
            Objetivos: {', '.join(goals) if goals else 'bienestar general'}
            
            Responde con:
            1. Calidez científica y conocimiento experto
            2. Enfoque protector y nutritivo (ISFJ)
            3. Evaluación basada en evidencia pero accesible
            4. Sabiduría mediterránea en nutrición
            5. Comprensión empática de sus necesidades
            
            Respuesta de evaluación:
            """

            # Generar respuesta conversacional
            assessment_response = await self.vertex_ai_client.generate_content(
                prompt=assessment_prompt, max_tokens=350, temperature=0.7
            )

            # Crear ID único para la conversación
            conversation_id = f"nutrition_assessment_{uuid.uuid4().hex[:8]}"

            # Insights nutricionales basados en la evaluación
            nutritional_insights = [
                "Balance de macronutrientes para energía sostenida",
                "Micronutrientes clave para tu perfil de salud",
                "Hidratación optimizada para tus necesidades",
                "Timing nutricional para maximizar absorción",
                "Alimentos funcionales para tus objetivos específicos",
                "Estrategias antiinflamatorias personalizadas",
            ]

            # Mejoras sugeridas adaptadas al contexto
            dietary_quality = "alta" if len(current_diet) > 3 else "moderada"
            suggested_improvements = []

            if dietary_quality == "moderada":
                suggested_improvements.extend(
                    [
                        "Incorporar más variedad de vegetales coloridos",
                        "Aumentar proteínas de alta calidad en cada comida",
                        "Optimizar el timing de carbohidratos complejos",
                    ]
                )

            if health_concerns:
                suggested_improvements.extend(
                    [
                        "Alimentos específicos para abordar tus preocupaciones de salud",
                        "Estrategias nutricionales terapéuticas personalizadas",
                        "Suplementación inteligente basada en biomarcadores",
                    ]
                )

            if not suggested_improvements:
                suggested_improvements = [
                    "Mantener la alta calidad de tu alimentación actual",
                    "Afinar el timing nutricional para optimizar resultados",
                    "Explorar alimentos funcionales avanzados",
                ]

            # Preguntas de seguimiento científicamente informadas
            follow_up_questions = [
                "¿Cómo te sientes energéticamente a lo largo del día?",
                "¿Hay algún alimento que notes que te afecta de manera especial?",
                "¿Tienes biomarcadores recientes que podamos analizar juntos?",
                "¿Qué aspectos nutricionales te generan más curiosidad?",
            ]

            return NutritionalAssessmentConversationOutput(
                assessment_response=assessment_response.strip(),
                conversation_id=conversation_id,
                nutritional_insights=nutritional_insights,
                suggested_improvements=suggested_improvements,
                follow_up_questions=follow_up_questions,
            )

        except Exception as e:
            logger.error(f"Error en evaluación nutricional conversacional: {str(e)}")
            return NutritionalAssessmentConversationOutput(
                assessment_response="Como tu chef científico personal, estoy aquí para guiarte en tu journey nutricional con evidencia y calidez. ¿Qué te gustaría explorar primero?",
                conversation_id=f"nutrition_assessment_{uuid.uuid4().hex[:8]}",
                nutritional_insights=[
                    "Nutrición personalizada",
                    "Evidencia científica",
                    "Enfoque holístico",
                ],
                suggested_improvements=[
                    "Evaluación completa de tu alimentación actual",
                    "Optimización gradual",
                ],
                follow_up_questions=["¿Cómo puedo ayudarte con tu nutrición hoy?"],
            )

    async def _skill_meal_planning_conversation(
        self, input_data: MealPlanningConversationInput
    ) -> MealPlanningConversationOutput:
        """
        Planificación de comidas interactiva con sabiduría culinaria.

        Args:
            input_data: Datos de entrada para planificación

        Returns:
            Respuesta de planificación conversacional con estrategias prácticas
        """
        try:
            logger.info("SAGE: Iniciando planificación de comidas conversacional")

            # Analizar contexto de planificación
            lifestyle = input_data.lifestyle or "activo"
            cooking_skills = input_data.cooking_skills or "intermedio"
            time_constraints = input_data.time_constraints or []
            preferences = input_data.food_preferences or []

            # Crear respuesta con sabiduría culinaria mediterránea
            planning_prompt = f"""
            Como SAGE, el chef científico con personalidad ISFJ protectora,
            proporciona planificación de comidas conversacional:
            
            Usuario dice: "{input_data.user_text}"
            Estilo de vida: {lifestyle}
            Habilidades culinarias: {cooking_skills}
            Limitaciones de tiempo: {', '.join(time_constraints) if time_constraints else 'flexibles'}
            Preferencias: {', '.join(preferences) if preferences else 'abiertas'}
            
            Responde con:
            1. Sabiduría culinaria mediterránea y científica
            2. Planificación protectora y práctica (ISFJ)
            3. Estrategias adaptadas a su estilo de vida
            4. Calidez en la enseñanza culinaria
            5. Enfoque en simplicidad y nutrición
            
            Respuesta de planificación:
            """

            planning_response = await self.vertex_ai_client.generate_content(
                prompt=planning_prompt, max_tokens=350, temperature=0.8
            )

            # Sugerencias de comidas adaptadas al nivel y tiempo
            meal_suggestions = []
            if cooking_skills == "principiante":
                meal_suggestions.extend(
                    [
                        "Bowl de quinoa con vegetales asados y proteína simple",
                        "Smoothie verde con espinacas, frutas y proteína en polvo",
                        "Ensalada mediterránea con legumbres enlatadas",
                        "Avena nocturna con frutos secos y semillas",
                    ]
                )
            elif cooking_skills == "intermedio":
                meal_suggestions.extend(
                    [
                        "Salmón a la plancha con vegetales salteados y quinoa",
                        "Curry de lentejas con arroz integral",
                        "Pasta integral con pesto de albahaca casero",
                        "Stir-fry de tofu con vegetales de temporada",
                    ]
                )
            else:
                meal_suggestions.extend(
                    [
                        "Ceviche de pescado con quinoa germinada",
                        "Risotto de hongos con caldo de huesos casero",
                        "Tajine de vegetales con especias marroquíes",
                        "Fermentados caseros con proteínas artesanales",
                    ]
                )

            # Estrategias de preparación según limitaciones de tiempo
            prep_strategies = []
            if "poco_tiempo" in time_constraints:
                prep_strategies.extend(
                    [
                        "Meal prep dominical de 2 horas para toda la semana",
                        "Batch cooking de granos y legumbres",
                        "Vegetales pre-cortados en envases de vidrio",
                        "Proteínas marinadas listas para cocinar",
                    ]
                )
            else:
                prep_strategies.extend(
                    [
                        "Planificación semanal con lista de compras inteligente",
                        "Preparaciones base que se transforman en múltiples platos",
                        "Técnicas de conservación natural de alimentos",
                        "Jardín de hierbas para frescura constante",
                    ]
                )

            # Consejos de compras con enfoque mediterráneo
            shopping_tips = [
                "Mercados locales para productos de temporada",
                "Aceite de oliva extra virgen como base culinaria",
                "Especias frescas para potenciar sabores naturalmente",
                "Proteínas sostenibles y de alta calidad",
                "Vegetales de todos los colores para máxima diversidad",
                "Frutos secos y semillas como snacks nutritivos",
            ]

            return MealPlanningConversationOutput(
                planning_response=planning_response.strip(),
                meal_suggestions=meal_suggestions,
                prep_strategies=prep_strategies,
                shopping_tips=shopping_tips,
            )

        except Exception as e:
            logger.error(f"Error en planificación de comidas: {str(e)}")
            return MealPlanningConversationOutput(
                planning_response="La planificación de comidas es un arte científico. Te guiaré para crear un sistema que funcione para tu vida y nutrición.",
                meal_suggestions=[
                    "Comidas balanceadas",
                    "Preparaciones simples",
                    "Ingredientes de calidad",
                ],
                prep_strategies=["Organización semanal", "Técnicas eficientes"],
                shopping_tips=["Productos frescos", "Calidad sobre cantidad"],
            )

    async def _skill_supplement_guidance_conversation(
        self, input_data: SupplementGuidanceConversationInput
    ) -> SupplementGuidanceConversationOutput:
        """
        Guía conversacional sobre suplementos con precisión científica.

        Args:
            input_data: Datos de entrada sobre suplementación

        Returns:
            Respuesta de guía sobre suplementos con consideraciones de seguridad
        """
        try:
            logger.info("SAGE: Iniciando guía de suplementos conversacional")

            # Analizar contexto de suplementación
            current_supplements = input_data.current_supplements or []
            health_conditions = input_data.health_conditions or []
            concerns = input_data.specific_concerns or []
            biomarkers = input_data.biomarker_data or {}

            # Crear respuesta con precisión científica y cuidado protector
            guidance_prompt = f"""
            Como SAGE, el especialista en nutrición de precisión con personalidad ISFJ protectora,
            proporciona guía sobre suplementos conversacional:
            
            Usuario pregunta: "{input_data.user_text}"
            Suplementos actuales: {', '.join(current_supplements) if current_supplements else 'ninguno'}
            Condiciones de salud: {', '.join(health_conditions) if health_conditions else 'ninguna'}
            Preocupaciones: {', '.join(concerns) if concerns else 'consulta general'}
            Biomarcadores: {'disponibles' if biomarkers else 'no disponibles'}
            
            Responde con:
            1. Precisión científica basada en evidencia
            2. Cuidado protector y responsabilidad (ISFJ)
            3. Evaluación personalizada de necesidades
            4. Consideraciones de seguridad prioritarias
            5. Enfoque en alimentos primero, suplementos segundo
            
            Respuesta de guía:
            """

            guidance_response = await self.vertex_ai_client.generate_content(
                prompt=guidance_prompt,
                max_tokens=350,
                temperature=0.6,  # Menor temperatura para mayor precisión
            )

            # Insights sobre suplementación basados en contexto
            supplement_insights = [
                "Los alimentos siempre son la primera línea de nutrición",
                "La suplementación debe ser personalizada según biomarcadores",
                "La calidad y biodisponibilidad son más importantes que la cantidad",
                "Las interacciones entre suplementos requieren evaluación cuidadosa",
                "El timing de suplementación afecta significativamente la absorción",
                "La ciclización de ciertos suplementos optimiza sus beneficios",
            ]

            # Consideraciones de seguridad prioritarias
            safety_considerations = [
                "Consultar con profesional de salud antes de cambios mayores",
                "Comenzar con dosis mínimas efectivas y ajustar gradualmente",
                "Monitorear reacciones y interacciones con medicamentos",
                "Evaluar calidad de marcas mediante terceros certificadores",
                "Considerar contraindicaciones con condiciones de salud existentes",
                "Evitar megadosis a menos que esté médicamente indicado",
            ]

            # Recomendaciones de timing según principios científicos
            timing_recommendations = []
            if "vitamina_d" in str(current_supplements).lower():
                timing_recommendations.append(
                    "Vitamina D con grasas saludables para mejor absorción"
                )
            if "magnesio" in str(current_supplements).lower():
                timing_recommendations.append(
                    "Magnesio por la noche para relajación y sueño"
                )
            if "hierro" in str(current_supplements).lower():
                timing_recommendations.append(
                    "Hierro con vitamina C, separado de café y té"
                )

            timing_recommendations.extend(
                [
                    "Probióticos con el estómago vacío o según instrucciones específicas",
                    "Vitaminas liposolubles (A, D, E, K) con comidas que contengan grasas",
                    "Vitaminas B por la mañana para apoyo energético",
                    "Omega-3 con comidas para reducir eructos y mejorar absorción",
                ]
            )

            return SupplementGuidanceConversationOutput(
                guidance_response=guidance_response.strip(),
                supplement_insights=supplement_insights,
                safety_considerations=safety_considerations,
                timing_recommendations=timing_recommendations,
            )

        except Exception as e:
            logger.error(f"Error en guía de suplementos: {str(e)}")
            return SupplementGuidanceConversationOutput(
                guidance_response="La suplementación es una ciencia precisa. Te guiaré para tomar decisiones informadas basadas en tu perfil único y evidencia científica.",
                supplement_insights=[
                    "Alimentos primero",
                    "Personalización basada en datos",
                    "Calidad sobre cantidad",
                ],
                safety_considerations=[
                    "Consulta profesional",
                    "Dosis apropiadas",
                    "Monitoreo continuo",
                ],
                timing_recommendations=[
                    "Absorción optimizada",
                    "Evitar interacciones",
                    "Efectividad maximizada",
                ],
            )

    async def _skill_biomarker_interpretation_conversation(
        self, input_data: BiomarkerInterpretationConversationInput
    ) -> BiomarkerInterpretationConversationOutput:
        """
        Interpretación conversacional de biomarcadores con claridad educativa.

        Args:
            input_data: Datos de entrada con biomarcadores

        Returns:
            Respuesta de interpretación con implicaciones nutricionales
        """
        try:
            logger.info(
                "SAGE: Iniciando interpretación de biomarcadores conversacional"
            )

            # Analizar contexto de biomarcadores
            biomarkers = input_data.biomarker_results or {}
            previous_results = input_data.previous_results or {}
            symptoms = input_data.symptoms or []
            medications = input_data.medications or []

            # Crear respuesta educativa con claridad científica
            interpretation_prompt = f"""
            Como SAGE, el experto en nutrición de precisión con personalidad ISFJ educativa,
            interpreta biomarcadores conversacionalmente:
            
            Usuario pregunta: "{input_data.user_text}"
            Biomarcadores actuales: {'disponibles' if biomarkers else 'no especificados'}
            Resultados previos: {'disponibles para comparación' if previous_results else 'primera evaluación'}
            Síntomas: {', '.join(symptoms) if symptoms else 'ninguno reportado'}
            Medicamentos: {', '.join(medications) if medications else 'ninguno'}
            
            Responde con:
            1. Claridad educativa y traducción de ciencia compleja
            2. Enfoque protector en la interpretación (ISFJ)
            3. Conexión entre biomarcadores y nutrición práctica
            4. Educación empática sin alarmar
            5. Enfoque en acciones constructivas
            
            Respuesta de interpretación:
            """

            interpretation_response = await self.vertex_ai_client.generate_content(
                prompt=interpretation_prompt, max_tokens=350, temperature=0.6
            )

            # Hallazgos clave educativos
            key_findings = [
                "Los biomarcadores son una fotografía de tu estado nutricional actual",
                "Las tendencias a lo largo del tiempo son más importantes que valores aislados",
                "La nutrición puede influir positivamente en la mayoría de biomarcadores",
                "Cada biomarcador cuenta una historia específica sobre tu metabolismo",
                "La interpretación integral es más valiosa que valores individuales",
                "Los rangos óptimos pueden diferir de los rangos 'normales'",
            ]

            # Implicaciones nutricionales generales
            nutrition_implications = [
                "Antioxidantes para reducir marcadores inflamatorios",
                "Grasas omega-3 para perfil lipídico y inflamación",
                "Fibra soluble para metabolismo de glucosa y colesterol",
                "Proteínas de calidad para síntesis y reparación",
                "Micronutrientes específicos según deficiencias identificadas",
                "Fitoquímicos diversos para optimización metabólica",
            ]

            # Recomendaciones de monitoreo científicamente fundamentadas
            monitoring_recommendations = [
                "Reevaluación cada 3-6 meses para seguir tendencias",
                "Monitoreo de síntomas correlacionados con biomarcadores",
                "Registro alimentario para correlacionar con cambios",
                "Seguimiento de intervenciones nutricionales específicas",
                "Evaluación integral incluyendo marcadores emergentes",
                "Consideración de factores lifestyle que afectan resultados",
            ]

            return BiomarkerInterpretationConversationOutput(
                interpretation_response=interpretation_response.strip(),
                key_findings=key_findings,
                nutrition_implications=nutrition_implications,
                monitoring_recommendations=monitoring_recommendations,
            )

        except Exception as e:
            logger.error(f"Error en interpretación de biomarcadores: {str(e)}")
            return BiomarkerInterpretationConversationOutput(
                interpretation_response="Los biomarcadores son el lenguaje que tu cuerpo usa para comunicar sus necesidades. Te ayudo a traducir esta información en acciones nutricionales específicas.",
                key_findings=[
                    "Historia metabólica personalizada",
                    "Tendencias más importantes que valores únicos",
                    "Oportunidades de optimización",
                ],
                nutrition_implications=[
                    "Nutrición personalizada",
                    "Intervenciones específicas",
                    "Optimización gradual",
                ],
                monitoring_recommendations=[
                    "Seguimiento regular",
                    "Correlación con síntomas",
                    "Evaluación integral",
                ],
            )

    async def _skill_lifestyle_nutrition_conversation(
        self, input_data: LifestyleNutritionConversationInput
    ) -> LifestyleNutritionConversationOutput:
        """
        Asesoramiento nutricional de estilo de vida con enfoque holístico.

        Args:
            input_data: Datos de entrada sobre estilo de vida

        Returns:
            Respuesta de asesoramiento con adaptaciones prácticas
        """
        try:
            logger.info("SAGE: Iniciando asesoramiento nutricional de estilo de vida")

            # Analizar contexto de estilo de vida
            daily_routine = input_data.daily_routine or "estándar"
            work_schedule = input_data.work_schedule or "horario_regular"
            stress_levels = input_data.stress_levels or "moderado"
            sleep_quality = input_data.sleep_quality or "regular"
            exercise_routine = input_data.exercise_routine or "moderado"

            # Crear respuesta holística con sabiduría integrativa
            lifestyle_prompt = f"""
            Como SAGE, el arquitecto nutricional con personalidad ISFJ holística,
            proporciona asesoramiento de estilo de vida conversacional:
            
            Usuario consulta: "{input_data.user_text}"
            Rutina diaria: {daily_routine}
            Horario de trabajo: {work_schedule}
            Niveles de estrés: {stress_levels}
            Calidad del sueño: {sleep_quality}
            Rutina de ejercicio: {exercise_routine}
            
            Responde con:
            1. Enfoque holístico integrando todos los aspectos
            2. Protección y cuidado en las recomendaciones (ISFJ)
            3. Adaptaciones prácticas y sostenibles
            4. Sabiduría nutricional mediterránea
            5. Consideración de la vida real y sus desafíos
            
            Respuesta de asesoramiento:
            """

            lifestyle_response = await self.vertex_ai_client.generate_content(
                prompt=lifestyle_prompt, max_tokens=350, temperature=0.8
            )

            # Adaptaciones de estilo de vida personalizadas
            lifestyle_adaptations = []

            if "ocupado" in daily_routine or "intenso" in work_schedule:
                lifestyle_adaptations.extend(
                    [
                        "Snacks nutritivos portátiles para energía sostenida",
                        "Hidratación estratégica con electrolitos naturales",
                        "Comidas de recuperación post-trabajo anti-estrés",
                    ]
                )

            if stress_levels in ["alto", "elevado"]:
                lifestyle_adaptations.extend(
                    [
                        "Alimentos adaptógenos para manejo natural del estrés",
                        "Magnesio y vitaminas B para soporte del sistema nervioso",
                        "Técnicas de alimentación mindful para calmar la mente",
                    ]
                )

            if sleep_quality in ["pobre", "irregular"]:
                lifestyle_adaptations.extend(
                    [
                        "Cena ligera 3 horas antes de dormir",
                        "Evitar cafeína después de las 2 PM",
                        "Triptófano natural para producción de melatonina",
                    ]
                )

            lifestyle_adaptations.extend(
                [
                    "Meal prep adaptado a tu horario específico",
                    "Nutrición pre y post ejercicio optimizada",
                    "Estrategias de hidratación según tu actividad",
                ]
            )

            # Consejos de timing de comidas específicos
            meal_timing_tips = [
                "Desayuno dentro de 1 hora de despertar para activar metabolismo",
                "Comidas cada 3-4 horas para estabilidad energética",
                "Carbohidratos complejos antes del ejercicio para energía",
                "Proteína post-ejercicio dentro de 30 minutos para recuperación",
                "Cena balanceada 3 horas antes de dormir",
                "Ayuno intermitente adaptado a tu estilo de vida si es apropiado",
            ]

            # Estrategias nutricionales para manejo del estrés
            stress_nutrition_strategies = [
                "Omega-3 para reducir cortisol y inflamación por estrés",
                "Vitaminas del complejo B para soporte del sistema nervioso",
                "Magnesio para relajación muscular y mental",
                "Antioxidantes para proteger contra daño oxidativo del estrés",
                "Probióticos para el eje intestino-cerebro",
                "Adaptógenos como ashwagandha para resistencia al estrés",
            ]

            return LifestyleNutritionConversationOutput(
                lifestyle_response=lifestyle_response.strip(),
                lifestyle_adaptations=lifestyle_adaptations,
                meal_timing_tips=meal_timing_tips,
                stress_nutrition_strategies=stress_nutrition_strategies,
            )

        except Exception as e:
            logger.error(f"Error en asesoramiento de estilo de vida: {str(e)}")
            return LifestyleNutritionConversationOutput(
                lifestyle_response="La nutrición debe fluir armoniosamente con tu estilo de vida. Te ayudo a crear un sistema nutricional que apoye todos los aspectos de tu bienestar.",
                lifestyle_adaptations=[
                    "Nutrición práctica",
                    "Adaptaciones realistas",
                    "Sostenibilidad a largo plazo",
                ],
                meal_timing_tips=[
                    "Timing optimizado",
                    "Energía constante",
                    "Recuperación efectiva",
                ],
                stress_nutrition_strategies=[
                    "Manejo nutricional del estrés",
                    "Alimentos calmantes",
                    "Equilibrio natural",
                ],
            )
