"""
API endpoints para análisis visual nutricional usando SAGE.

Este módulo proporciona endpoints para analizar imágenes de:
- Etiquetas nutricionales
- Platos de comida preparada
- Alimentos en general
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
import base64
import json
import logging
from datetime import datetime

from app.schemas.agent import AgentRunRequest, AgentRunResponse
from app.schemas.chat import ChatRequest
from core.auth import get_current_user
from infrastructure.a2a_optimized import A2AServer
from infrastructure.adapters.precision_nutrition_architect_adapter import (
    PrecisionNutritionArchitectAdapter,
)
from agents.precision_nutrition_architect.schemas import (
    AnalyzeNutritionLabelInput,
    AnalyzeNutritionLabelOutput,
    AnalyzePreparedMealInput,
    AnalyzePreparedMealOutput,
    AnalyzeFoodImageInput,
    AnalyzeFoodImageOutput,
)

# Configurar logger
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(
    prefix="/api/nutrition/vision",
    tags=["nutrition-vision"],
    responses={404: {"description": "No encontrado"}},
)

# Inicializar adaptador de SAGE
nutrition_adapter = PrecisionNutritionArchitectAdapter()


@router.post("/analyze-label", response_model=Dict[str, Any])
async def analyze_nutrition_label(
    file: UploadFile = File(..., description="Imagen de la etiqueta nutricional"),
    user_input: Optional[str] = Form(
        None, description="Pregunta específica del usuario"
    ),
    dietary_restrictions: Optional[str] = Form(
        None, description="Restricciones dietéticas (JSON array)"
    ),
    comparison_mode: bool = Form(
        False, description="Modo de comparación con productos similares"
    ),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Analiza una etiqueta nutricional usando OCR y AI.

    Extrae información nutricional completa, analiza ingredientes,
    evalúa la salud del producto y proporciona recomendaciones personalizadas.
    """
    try:
        # Validar que es una imagen
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"El archivo debe ser una imagen. Tipo recibido: {file.content_type}",
            )

        # Leer y codificar la imagen
        image_content = await file.read()
        image_base64 = base64.b64encode(image_content).decode("utf-8")
        image_data = f"data:{file.content_type};base64,{image_base64}"

        # Parsear restricciones dietéticas si se proporcionaron
        dietary_restrictions_list = []
        if dietary_restrictions:
            try:
                dietary_restrictions_list = json.loads(dietary_restrictions)
            except json.JSONDecodeError:
                logger.warning(
                    f"No se pudo parsear dietary_restrictions: {dietary_restrictions}"
                )

        # Preparar input para la skill
        skill_input = AnalyzeNutritionLabelInput(
            image_data=image_data,
            user_input=user_input or "",
            user_profile={
                "user_id": current_user.get("id"),
                "email": current_user.get("email"),
                "goals": current_user.get("goals", []),
            },
            dietary_restrictions=dietary_restrictions_list,
            comparison_mode=comparison_mode,
        )

        # Ejecutar skill usando el adaptador
        logger.info(
            f"Analizando etiqueta nutricional para usuario {current_user.get('id')}"
        )

        # Usar el adaptador para ejecutar la skill específica
        result = await nutrition_adapter.run_skill(
            skill_name="analyze_nutrition_label",
            input_data=skill_input.dict(),
            user_id=current_user.get("id"),
        )

        # Log del resultado
        logger.info(
            f"Análisis de etiqueta completado. Producto: {result.get('product_name', 'N/A')}"
        )

        return {
            "status": "success",
            "data": result,
            "metadata": {
                "file_name": file.filename,
                "file_size": len(image_content),
                "analyzed_at": datetime.utcnow().isoformat(),
            },
        }

    except Exception as e:
        logger.error(f"Error al analizar etiqueta nutricional: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al analizar la etiqueta nutricional: {str(e)}",
        )


@router.post("/analyze-prepared-meal", response_model=Dict[str, Any])
async def analyze_prepared_meal(
    file: UploadFile = File(..., description="Imagen del plato preparado"),
    user_input: Optional[str] = Form(
        None, description="Descripción adicional del plato"
    ),
    meal_type: Optional[str] = Form(
        None, description="Tipo de comida (desayuno, almuerzo, cena, snack)"
    ),
    meal_time: Optional[str] = Form(None, description="Hora de la comida"),
    portion_estimation_mode: bool = Form(
        True, description="Incluir estimación detallada de porciones"
    ),
    nutrition_precision: str = Form(
        "standard", description="Nivel de precisión (basic, standard, detailed)"
    ),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Analiza un plato de comida preparada con estimación avanzada de porciones.

    Identifica componentes, estima porciones usando referencias visuales,
    calcula información nutricional detallada y proporciona análisis de timing.
    """
    try:
        # Validar que es una imagen
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"El archivo debe ser una imagen. Tipo recibido: {file.content_type}",
            )

        # Validar nutrition_precision
        if nutrition_precision not in ["basic", "standard", "detailed"]:
            nutrition_precision = "standard"

        # Leer y codificar la imagen
        image_content = await file.read()
        image_base64 = base64.b64encode(image_content).decode("utf-8")
        image_data = f"data:{file.content_type};base64,{image_base64}"

        # Preparar contexto de la comida
        meal_context = {}
        if meal_type:
            meal_context["meal_type"] = meal_type
        if meal_time:
            meal_context["meal_time"] = meal_time

        # Preparar input para la skill
        skill_input = AnalyzePreparedMealInput(
            image_data=image_data,
            user_input=user_input or "",
            user_profile={
                "user_id": current_user.get("id"),
                "email": current_user.get("email"),
                "goals": current_user.get("goals", []),
                "dietary_preferences": current_user.get("dietary_preferences", []),
            },
            meal_context=meal_context,
            portion_estimation_mode=portion_estimation_mode,
            nutrition_precision=nutrition_precision,
        )

        # Ejecutar skill usando el adaptador
        logger.info(
            f"Analizando plato preparado para usuario {current_user.get('id')} "
            f"con precisión {nutrition_precision}"
        )

        # Usar el adaptador para ejecutar la skill específica
        result = await nutrition_adapter.run_skill(
            skill_name="analyze_prepared_meal",
            input_data=skill_input.dict(),
            user_id=current_user.get("id"),
        )

        # Log del resultado
        logger.info(
            f"Análisis de plato completado. Identificación: {result.get('meal_identification', 'N/A')}, "
            f"Componentes: {result.get('food_components', []).__len__()} identificados"
        )

        return {
            "status": "success",
            "data": result,
            "metadata": {
                "file_name": file.filename,
                "file_size": len(image_content),
                "analyzed_at": datetime.utcnow().isoformat(),
                "analysis_settings": {
                    "portion_estimation": portion_estimation_mode,
                    "precision": nutrition_precision,
                },
            },
        }

    except Exception as e:
        logger.error(f"Error al analizar plato preparado: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al analizar el plato preparado: {str(e)}",
        )


@router.post("/analyze-food-image", response_model=Dict[str, Any])
async def analyze_food_image(
    file: UploadFile = File(..., description="Imagen de alimentos"),
    user_input: Optional[str] = Form(
        None, description="Descripción o pregunta del usuario"
    ),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Analiza una imagen general de alimentos (endpoint mejorado).

    Identifica alimentos, estima valores nutricionales y proporciona
    recomendaciones generales.
    """
    try:
        # Validar que es una imagen
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"El archivo debe ser una imagen. Tipo recibido: {file.content_type}",
            )

        # Leer y codificar la imagen
        image_content = await file.read()
        image_base64 = base64.b64encode(image_content).decode("utf-8")
        image_data = f"data:{file.content_type};base64,{image_base64}"

        # Preparar input para la skill
        skill_input = AnalyzeFoodImageInput(
            image_data=image_data,
            user_input=user_input or "",
            user_profile={
                "user_id": current_user.get("id"),
                "email": current_user.get("email"),
                "goals": current_user.get("goals", []),
            },
            dietary_preferences=current_user.get("dietary_preferences", []),
        )

        # Ejecutar skill usando el adaptador
        logger.info(
            f"Analizando imagen de alimentos para usuario {current_user.get('id')}"
        )

        # Usar el adaptador para ejecutar la skill específica
        result = await nutrition_adapter.run_skill(
            skill_name="analyze_food_image",
            input_data=skill_input.dict(),
            user_id=current_user.get("id"),
        )

        # Log del resultado
        logger.info(
            f"Análisis de alimentos completado. "
            f"Alimentos identificados: {result.get('identified_foods', []).__len__()}"
        )

        return {
            "status": "success",
            "data": result,
            "metadata": {
                "file_name": file.filename,
                "file_size": len(image_content),
                "analyzed_at": datetime.utcnow().isoformat(),
            },
        }

    except Exception as e:
        logger.error(f"Error al analizar imagen de alimentos: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al analizar la imagen de alimentos: {str(e)}",
        )


@router.get("/capabilities", response_model=Dict[str, Any])
async def get_vision_capabilities(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Obtiene las capacidades de análisis visual nutricional disponibles.
    """
    return {
        "status": "success",
        "capabilities": {
            "nutrition_label_analysis": {
                "description": "Análisis de etiquetas nutricionales con OCR",
                "features": [
                    "Extracción de información nutricional completa",
                    "Análisis de ingredientes",
                    "Evaluación de salud del producto",
                    "Detección de alérgenos",
                    "Recomendaciones personalizadas",
                    "Comparación con productos similares",
                ],
                "supported_formats": ["jpg", "jpeg", "png", "webp"],
            },
            "prepared_meal_analysis": {
                "description": "Análisis avanzado de platos preparados",
                "features": [
                    "Identificación de componentes individuales",
                    "Estimación de porciones con referencias visuales",
                    "Cálculo nutricional detallado",
                    "Análisis de timing óptimo",
                    "Evaluación de métodos de cocción",
                    "Recomendaciones de mejora",
                ],
                "precision_levels": ["basic", "standard", "detailed"],
            },
            "general_food_analysis": {
                "description": "Análisis general de imágenes de alimentos",
                "features": [
                    "Identificación de alimentos",
                    "Estimación calórica",
                    "Macronutrientes básicos",
                    "Evaluación nutricional",
                    "Recomendaciones generales",
                ],
            },
        },
        "limits": {
            "max_file_size_mb": 10,
            "supported_formats": ["image/jpeg", "image/png", "image/webp"],
            "rate_limit": "100 análisis por día",
        },
    }


@router.post("/batch-analyze", response_model=Dict[str, Any])
async def batch_analyze_images(
    files: List[UploadFile] = File(..., description="Lista de imágenes para analizar"),
    analysis_type: str = Form(..., description="Tipo de análisis: label, meal, o food"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Analiza múltiples imágenes en batch.

    Útil para analizar varias etiquetas o platos de una vez.
    Máximo 5 imágenes por request.
    """
    try:
        # Validar número de archivos
        if len(files) > 5:
            raise HTTPException(
                status_code=400,
                detail="Máximo 5 imágenes por solicitud batch",
            )

        # Validar tipo de análisis
        if analysis_type not in ["label", "meal", "food"]:
            raise HTTPException(
                status_code=400,
                detail="Tipo de análisis debe ser: label, meal, o food",
            )

        results = []
        errors = []

        # Procesar cada imagen
        for idx, file in enumerate(files):
            try:
                # Validar que es una imagen
                if not file.content_type.startswith("image/"):
                    errors.append(
                        {
                            "file": file.filename,
                            "error": f"No es una imagen: {file.content_type}",
                        }
                    )
                    continue

                # Leer y codificar la imagen
                image_content = await file.read()
                image_base64 = base64.b64encode(image_content).decode("utf-8")
                image_data = f"data:{file.content_type};base64,{image_base64}"

                # Ejecutar análisis según tipo
                if analysis_type == "label":
                    skill_name = "analyze_nutrition_label"
                    skill_input = AnalyzeNutritionLabelInput(
                        image_data=image_data,
                        user_profile={
                            "user_id": current_user.get("id"),
                        },
                    )
                elif analysis_type == "meal":
                    skill_name = "analyze_prepared_meal"
                    skill_input = AnalyzePreparedMealInput(
                        image_data=image_data,
                        user_profile={
                            "user_id": current_user.get("id"),
                        },
                    )
                else:  # food
                    skill_name = "analyze_food_image"
                    skill_input = AnalyzeFoodImageInput(
                        image_data=image_data,
                        user_profile={
                            "user_id": current_user.get("id"),
                        },
                    )

                # Ejecutar análisis
                result = await nutrition_adapter.run_skill(
                    skill_name=skill_name,
                    input_data=skill_input.dict(),
                    user_id=current_user.get("id"),
                )

                results.append(
                    {
                        "file": file.filename,
                        "index": idx,
                        "result": result,
                    }
                )

            except Exception as e:
                logger.error(f"Error procesando {file.filename}: {e}")
                errors.append(
                    {
                        "file": file.filename,
                        "error": str(e),
                    }
                )

        return {
            "status": "success",
            "analysis_type": analysis_type,
            "total_files": len(files),
            "successful": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors,
            "metadata": {
                "analyzed_at": datetime.utcnow().isoformat(),
            },
        }

    except Exception as e:
        logger.error(f"Error en análisis batch: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar análisis batch: {str(e)}",
        )
