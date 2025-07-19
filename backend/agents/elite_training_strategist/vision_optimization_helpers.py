"""
BLAZE Vision Optimization Helpers - Funciones auxiliares para capacidades de visión mejoradas.

🔥 BLAZE Enhanced Vision Support Functions 🔥

Este módulo contiene funciones auxiliares para las capacidades optimizadas
de análisis de visión del Elite Training Strategist (BLAZE).
"""

from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
import numpy as np
import json

from core.logging_config import get_logger

logger = get_logger(__name__)


def analyze_biomechanics(
    joint_angles: Dict[str, float], keypoints: Dict[str, Any], exercise_name: str
) -> Dict[str, Any]:
    """
    🚀 NUEVO: Análisis biomecánico completo basado en ángulos articulares.

    Args:
        joint_angles: Ángulos articulares calculados
        keypoints: Datos de keypoints detectados
        exercise_name: Nombre del ejercicio

    Returns:
        Análisis biomecánico completo con scores y factores de riesgo
    """

    # Parámetros ideales por ejercicio
    ideal_ranges = {
        "sentadilla": {
            "left_knee": (90, 120),
            "right_knee": (90, 120),
            "left_hip": (60, 90),
            "torso_lean": (0, 15),
        },
        "peso_muerto": {
            "left_knee": (160, 180),
            "right_knee": (160, 180),
            "left_hip": (30, 60),
            "torso_lean": (30, 45),
        },
        "press_banca": {"torso_lean": (0, 5)},
    }

    exercise_ideals = ideal_ranges.get(exercise_name.lower(), {})

    efficiency_scores = []
    alignment_scores = []
    risk_factors = []

    # Evaluar cada ángulo contra rangos ideales
    for joint, angle in joint_angles.items():
        if joint in exercise_ideals:
            ideal_min, ideal_max = exercise_ideals[joint]

            # Score de eficiencia (0-100)
            if ideal_min <= angle <= ideal_max:
                efficiency = 100
            else:
                # Penalizar desviación
                deviation = min(abs(angle - ideal_min), abs(angle - ideal_max))
                efficiency = max(0, 100 - (deviation * 2))

            efficiency_scores.append(efficiency)

            # Score de alineación
            alignment_score = 100 - abs(angle - ((ideal_min + ideal_max) / 2)) * 3
            alignment_scores.append(max(0, alignment_score))

            # Factores de riesgo
            if efficiency < 70:
                severity = "high" if efficiency < 50 else "medium"
                risk_factors.append(
                    {
                        "joint": joint,
                        "issue": f"Ángulo fuera del rango óptimo ({angle:.1f}° vs {ideal_min}-{ideal_max}°)",
                        "severity": severity,
                        "recommendation": get_angle_correction_recommendation(
                            joint, angle, ideal_min, ideal_max
                        ),
                    }
                )

    # Calcular scores promedio
    avg_efficiency = np.mean(efficiency_scores) if efficiency_scores else 75.0
    avg_alignment = np.mean(alignment_scores) if alignment_scores else 75.0

    # Score de precisión basado en consistencia
    precision_score = calculate_precision_score(joint_angles, exercise_ideals)

    return {
        "efficiency_score": round(avg_efficiency, 1),
        "alignment_score": round(avg_alignment, 1),
        "precision_score": round(precision_score, 1),
        "risk_factors": risk_factors,
        "joint_analysis": {
            joint: {
                "angle": angle,
                "ideal_range": exercise_ideals.get(joint, "no_data"),
                "status": get_joint_status(joint, angle, exercise_ideals),
            }
            for joint, angle in joint_angles.items()
        },
    }


def get_angle_correction_recommendation(
    joint: str, current_angle: float, ideal_min: float, ideal_max: float
) -> str:
    """Genera recomendación específica para corrección de ángulo."""

    corrections = {
        "left_knee": {
            "too_small": "Aumenta la profundidad de la sentadilla gradualmente",
            "too_large": "Controla el descenso, no bajes tanto",
        },
        "right_knee": {
            "too_small": "Aumenta la profundidad de la sentadilla gradualmente",
            "too_large": "Controla el descenso, no bajes tanto",
        },
        "left_hip": {
            "too_small": "Inclínate más hacia adelante manteniendo la espalda recta",
            "too_large": "Mantén el torso más erecto",
        },
        "torso_lean": {
            "too_small": "Perfecto, mantén esa posición",
            "too_large": "Mantén el pecho más arriba y la espalda más erguida",
        },
    }

    joint_corrections = corrections.get(joint, {})

    if current_angle < ideal_min:
        return joint_corrections.get("too_small", f"Aumenta el ángulo de {joint}")
    elif current_angle > ideal_max:
        return joint_corrections.get("too_large", f"Reduce el ángulo de {joint}")
    else:
        return "Ángulo óptimo, mantén esta posición"


def get_joint_status(
    joint: str, angle: float, exercise_ideals: Dict[str, Tuple[float, float]]
) -> str:
    """Determina el estado de un ángulo articular."""

    if joint not in exercise_ideals:
        return "no_reference"

    ideal_min, ideal_max = exercise_ideals[joint]

    if ideal_min <= angle <= ideal_max:
        return "optimal"
    elif abs(angle - ideal_min) <= 10 or abs(angle - ideal_max) <= 10:
        return "acceptable"
    else:
        return "needs_correction"


def calculate_precision_score(
    joint_angles: Dict[str, float], exercise_ideals: Dict[str, Tuple[float, float]]
) -> float:
    """Calcula score de precisión técnica basado en consistencia."""

    if not joint_angles or not exercise_ideals:
        return 75.0

    precision_scores = []

    # Evaluar consistencia bilateral (izquierda vs derecha)
    bilateral_pairs = [("left_knee", "right_knee"), ("left_hip", "right_hip")]

    for left_joint, right_joint in bilateral_pairs:
        if left_joint in joint_angles and right_joint in joint_angles:
            left_angle = joint_angles[left_joint]
            right_angle = joint_angles[right_joint]

            # Diferencia entre lados (debería ser mínima)
            bilateral_diff = abs(left_angle - right_angle)

            # Score: 100 = perfecta simetría, 0 = muy asimétrico
            bilateral_score = max(0, 100 - (bilateral_diff * 5))
            precision_scores.append(bilateral_score)

    # Evaluar adherencia a rangos ideales
    for joint, angle in joint_angles.items():
        if joint in exercise_ideals:
            ideal_min, ideal_max = exercise_ideals[joint]
            ideal_center = (ideal_min + ideal_max) / 2

            # Distancia del centro ideal
            distance_from_ideal = abs(angle - ideal_center)
            ideal_range = ideal_max - ideal_min

            # Score basado en proximidad al centro ideal
            adherence_score = max(0, 100 - (distance_from_ideal / ideal_range * 100))
            precision_scores.append(adherence_score)

    return np.mean(precision_scores) if precision_scores else 75.0


def assess_movement_quality(
    joint_angles: Dict[str, float], symmetry_score: float
) -> Dict[str, Any]:
    """Evalúa la calidad general del movimiento."""

    # Factores de calidad de movimiento
    quality_factors = {
        "symmetry": symmetry_score,
        "joint_coordination": calculate_joint_coordination(joint_angles),
        "range_adequacy": assess_range_adequacy(joint_angles),
        "stability": assess_stability_indicators(joint_angles),
    }

    # Score general de calidad
    overall_quality = np.mean(list(quality_factors.values()))

    # Categorización de calidad
    if overall_quality >= 90:
        quality_rating = "excellent"
        feedback = "Técnica excepcional, mantén este nivel"
    elif overall_quality >= 80:
        quality_rating = "good"
        feedback = "Buena técnica, pequeños ajustes para perfeccionar"
    elif overall_quality >= 70:
        quality_rating = "fair"
        feedback = "Técnica aceptable, varios aspectos por mejorar"
    else:
        quality_rating = "needs_work"
        feedback = "Técnica requiere trabajo significativo"

    return {
        "overall_score": round(overall_quality, 1),
        "rating": quality_rating,
        "feedback": feedback,
        "quality_factors": quality_factors,
        "primary_strengths": identify_movement_strengths(quality_factors),
        "improvement_priorities": identify_movement_priorities(quality_factors),
    }


def calculate_joint_coordination(joint_angles: Dict[str, float]) -> float:
    """Calcula score de coordinación articular."""

    # Verificar relaciones típicas entre articulaciones
    coordination_score = 75.0  # Base neutral

    # Coordinación rodilla-cadera en sentadilla
    if "left_knee" in joint_angles and "left_hip" in joint_angles:
        knee_angle = joint_angles["left_knee"]
        hip_angle = joint_angles["left_hip"]

        # Relación típica: cuando rodilla flexiona más, cadera también
        expected_ratio = 1.3  # Rodilla típicamente más flexionada que cadera
        actual_ratio = knee_angle / hip_angle if hip_angle > 0 else 1.0

        ratio_deviation = abs(actual_ratio - expected_ratio)
        coordination_score = max(50, 100 - (ratio_deviation * 30))

    return coordination_score


def assess_range_adequacy(joint_angles: Dict[str, float]) -> float:
    """Evalúa si los rangos de movimiento son adecuados."""

    adequacy_scores = []

    # Rangos mínimos para funcionalidad
    minimum_ranges = {
        "left_knee": 90,  # Mínimo para sentadilla funcional
        "right_knee": 90,
        "left_hip": 60,  # Mínimo para flexión de cadera
        "torso_lean": 0,  # Torso no debería inclinarse excesivamente
    }

    for joint, angle in joint_angles.items():
        if joint in minimum_ranges:
            min_required = minimum_ranges[joint]

            if joint == "torso_lean":
                # Para torso, menor ángulo es mejor
                adequacy = max(0, 100 - angle * 2) if angle <= 30 else 40
            else:
                # Para otros joints, ángulo debe ser al menos el mínimo
                if angle >= min_required:
                    adequacy = 100
                else:
                    deficit = min_required - angle
                    adequacy = max(0, 100 - (deficit * 2))

            adequacy_scores.append(adequacy)

    return np.mean(adequacy_scores) if adequacy_scores else 75.0


def assess_stability_indicators(joint_angles: Dict[str, float]) -> float:
    """Evalúa indicadores de estabilidad en la posición."""

    stability_score = 75.0  # Base neutral

    # Indicadores de inestabilidad
    instability_penalties = 0

    # Asimetría excesiva en rodillas
    if "left_knee" in joint_angles and "right_knee" in joint_angles:
        knee_asymmetry = abs(joint_angles["left_knee"] - joint_angles["right_knee"])
        if knee_asymmetry > 10:  # Más de 10 grados de diferencia es preocupante
            instability_penalties += knee_asymmetry * 2

    # Inclinación excesiva del torso
    if "torso_lean" in joint_angles:
        excessive_lean = max(
            0, joint_angles["torso_lean"] - 20
        )  # Más de 20° es excesivo
        instability_penalties += excessive_lean * 3

    # Aplicar penalizaciones
    stability_score = max(20, stability_score - instability_penalties)

    return stability_score


def identify_movement_strengths(quality_factors: Dict[str, float]) -> List[str]:
    """Identifica fortalezas en el movimiento."""

    strengths = []

    for factor, score in quality_factors.items():
        if score >= 85:
            strength_descriptions = {
                "symmetry": "Excelente simetría corporal",
                "joint_coordination": "Coordinación articular muy buena",
                "range_adequacy": "Rangos de movimiento adecuados",
                "stability": "Muy buena estabilidad postural",
            }

            if factor in strength_descriptions:
                strengths.append(strength_descriptions[factor])

    return strengths


def identify_movement_priorities(
    quality_factors: Dict[str, float],
) -> List[Dict[str, str]]:
    """Identifica prioridades de mejora en el movimiento."""

    priorities = []

    # Ordenar factores por score (menor primero = mayor prioridad)
    sorted_factors = sorted(quality_factors.items(), key=lambda x: x[1])

    priority_descriptions = {
        "symmetry": {
            "issue": "Asimetría corporal",
            "action": "Trabajar en ejercicios unilaterales y corrección de desequilibrios",
        },
        "joint_coordination": {
            "issue": "Coordinación articular deficiente",
            "action": "Practicar el patrón de movimiento a velocidad lenta",
        },
        "range_adequacy": {
            "issue": "Rangos de movimiento limitados",
            "action": "Incorporar trabajo de movilidad específica",
        },
        "stability": {
            "issue": "Inestabilidad postural",
            "action": "Fortalecer core y practicar ejercicios de equilibrio",
        },
    }

    # Tomar los 2-3 factores con menor score
    for factor, score in sorted_factors[:3]:
        if score < 80 and factor in priority_descriptions:
            priority = priority_descriptions[factor].copy()
            priority["score"] = score
            priority["urgency"] = "high" if score < 60 else "medium"
            priorities.append(priority)

    return priorities


def identify_optimization_opportunities(
    joint_angles: Dict[str, float], symmetry_score: float, exercise_name: str
) -> List[Dict[str, Any]]:
    """Identifica oportunidades específicas de optimización."""

    opportunities = []

    # 1. Optimización de profundidad (para sentadillas)
    if exercise_name.lower() == "sentadilla":
        if "left_knee" in joint_angles:
            knee_angle = joint_angles["left_knee"]
            if knee_angle > 120:  # Sentadilla superficial
                opportunities.append(
                    {
                        "type": "depth_optimization",
                        "current_state": f"Profundidad limitada (ángulo rodilla: {knee_angle:.1f}°)",
                        "target": "Trabajar hacia 90-100° para máximo beneficio",
                        "method": "Movilidad de tobillo y cadera, sentadillas asistidas",
                        "impact": "high",
                        "timeline": "4-6 semanas",
                    }
                )

    # 2. Optimización de simetría
    if symmetry_score < 85:
        opportunities.append(
            {
                "type": "symmetry_optimization",
                "current_state": f"Asimetría detectada (score: {symmetry_score:.1f}%)",
                "target": "Lograr >90% de simetría",
                "method": "Ejercicios unilaterales, trabajo correctivo",
                "impact": "medium",
                "timeline": "6-8 semanas",
            }
        )

    # 3. Optimización de estabilidad
    if "torso_lean" in joint_angles and joint_angles["torso_lean"] > 15:
        opportunities.append(
            {
                "type": "stability_optimization",
                "current_state": f"Inclinación excesiva del torso ({joint_angles['torso_lean']:.1f}°)",
                "target": "Reducir a <10° para mayor eficiencia",
                "method": "Fortalecimiento de core, mejora de movilidad torácica",
                "impact": "high",
                "timeline": "3-5 semanas",
            }
        )

    # 4. Optimización bilateral
    bilateral_opportunities = check_bilateral_optimization(joint_angles)
    opportunities.extend(bilateral_opportunities)

    return opportunities


def check_bilateral_optimization(
    joint_angles: Dict[str, float],
) -> List[Dict[str, Any]]:
    """Verifica oportunidades de optimización bilateral."""

    opportunities = []

    bilateral_pairs = [("left_knee", "right_knee"), ("left_hip", "right_hip")]

    for left_joint, right_joint in bilateral_pairs:
        if left_joint in joint_angles and right_joint in joint_angles:
            left_angle = joint_angles[left_joint]
            right_angle = joint_angles[right_joint]

            difference = abs(left_angle - right_angle)

            if difference > 8:  # Diferencia significativa
                weaker_side = "izquierdo" if left_angle < right_angle else "derecho"
                stronger_side = "derecho" if weaker_side == "izquierdo" else "izquierdo"

                opportunities.append(
                    {
                        "type": "bilateral_optimization",
                        "current_state": f"Diferencia bilateral en {left_joint.replace('left_', '')} ({difference:.1f}°)",
                        "target": "Reducir diferencia a <5°",
                        "method": f"Trabajo unilateral enfocado en lado {weaker_side}",
                        "impact": "medium",
                        "timeline": "4-6 semanas",
                        "specific_focus": weaker_side,
                    }
                )

    return opportunities


def update_performance_metrics(metrics: Dict[str, Any], processing_time: float) -> None:
    """Actualiza métricas de rendimiento del sistema de visión."""

    # Actualizar tiempo promedio de procesamiento
    total_analyses = metrics["total_analyses"]
    if total_analyses > 0:
        current_avg = metrics["average_processing_time"]
        new_avg = (
            (current_avg * (total_analyses - 1)) + processing_time
        ) / total_analyses
        metrics["average_processing_time"] = new_avg
    else:
        metrics["average_processing_time"] = processing_time

    # Calcular eficiencia de cache
    if metrics["total_analyses"] > 0:
        cache_efficiency = (metrics["cache_hits"] / metrics["total_analyses"]) * 100
        metrics["cache_efficiency_percent"] = cache_efficiency

    # Log de métricas cada 10 análisis
    if total_analyses % 10 == 0:
        logger.info(
            f"📊 Métricas BLAZE Vision - Análisis: {total_analyses}, "
            f"Cache: {metrics['cache_hits']}/{total_analyses} ({metrics.get('cache_efficiency_percent', 0):.1f}%), "
            f"Tiempo promedio: {metrics['average_processing_time']:.2f}s"
        )


def analyze_focus_areas_enhanced(
    image: Union[str, bytes],
    exercise_name: str,
    focus_areas: List[str],
    base_analysis: Dict[str, Any],
    keypoints_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Análisis mejorado de áreas específicas de enfoque con keypoints."""

    focused_results = {}

    for area in focus_areas:
        area_analysis = {
            "area_name": area,
            "keypoint_analysis": extract_area_keypoints(area, keypoints_data),
            "quantitative_assessment": assess_area_quantitatively(area, keypoints_data),
            "specific_recommendations": generate_area_specific_recommendations(
                area, keypoints_data
            ),
            "risk_assessment": assess_area_risk_enhanced(area, keypoints_data),
            "improvement_timeline": estimate_area_improvement_time(
                area, keypoints_data
            ),
        }

        focused_results[area] = area_analysis

    return focused_results


def extract_area_keypoints(area: str, keypoints_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extrae keypoints relevantes para un área específica."""

    area_keypoint_mapping = {
        "rodillas": [
            "left_knee",
            "right_knee",
            "left_hip",
            "right_hip",
            "left_ankle",
            "right_ankle",
        ],
        "espalda": ["left_shoulder", "right_shoulder", "left_hip", "right_hip"],
        "hombros": ["left_shoulder", "right_shoulder", "left_elbow", "right_elbow"],
        "cadera": ["left_hip", "right_hip", "left_knee", "right_knee"],
        "tobillos": ["left_ankle", "right_ankle", "left_knee", "right_knee"],
    }

    relevant_keypoints = area_keypoint_mapping.get(area.lower(), [])
    landmarks = {lm["name"]: lm for lm in keypoints_data["pose_landmarks"]}

    area_keypoints = {}
    for keypoint_name in relevant_keypoints:
        if keypoint_name in landmarks:
            area_keypoints[keypoint_name] = landmarks[keypoint_name]

    return area_keypoints


def assess_area_quantitatively(
    area: str, keypoints_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Evaluación cuantitativa específica por área."""

    assessment = {"score": 75, "metrics": {}, "status": "normal"}

    if area.lower() == "rodillas":
        # Análisis específico de rodillas
        landmarks = {
            lm["name"]: (lm["x"], lm["y"]) for lm in keypoints_data["pose_landmarks"]
        }

        if all(k in landmarks for k in ["left_knee", "right_knee"]):
            left_knee = landmarks["left_knee"]
            right_knee = landmarks["right_knee"]

            # Evaluar alineación horizontal
            height_diff = abs(left_knee[1] - right_knee[1])
            alignment_score = max(0, 100 - (height_diff * 1000))  # Escalado

            assessment.update(
                {
                    "score": alignment_score,
                    "metrics": {
                        "bilateral_alignment": alignment_score,
                        "height_difference": height_diff,
                        "tracking_quality": assess_knee_tracking(landmarks),
                    },
                    "status": "good" if alignment_score > 80 else "needs_attention",
                }
            )

    elif area.lower() == "espalda":
        # Análisis específico de espalda
        landmarks = {
            lm["name"]: (lm["x"], lm["y"]) for lm in keypoints_data["pose_landmarks"]
        }

        if all(
            k in landmarks
            for k in ["left_shoulder", "right_shoulder", "left_hip", "right_hip"]
        ):
            spinal_alignment = calculate_spinal_alignment(landmarks)

            assessment.update(
                {
                    "score": spinal_alignment["score"],
                    "metrics": {
                        "spinal_alignment": spinal_alignment["score"],
                        "shoulder_level": spinal_alignment["shoulder_symmetry"],
                        "torso_lean": spinal_alignment["torso_angle"],
                    },
                    "status": (
                        "good" if spinal_alignment["score"] > 80 else "needs_attention"
                    ),
                }
            )

    return assessment


def assess_knee_tracking(landmarks: Dict[str, Tuple[float, float]]) -> float:
    """Evalúa la calidad del tracking de rodillas."""

    if not all(
        k in landmarks for k in ["left_knee", "left_ankle", "right_knee", "right_ankle"]
    ):
        return 75.0

    # Verificar que rodillas están alineadas con tobillos
    left_knee_x = landmarks["left_knee"][0]
    left_ankle_x = landmarks["left_ankle"][0]
    right_knee_x = landmarks["right_knee"][0]
    right_ankle_x = landmarks["right_ankle"][0]

    left_tracking = abs(left_knee_x - left_ankle_x)
    right_tracking = abs(right_knee_x - right_ankle_x)

    avg_tracking_error = (left_tracking + right_tracking) / 2
    tracking_score = max(0, 100 - (avg_tracking_error * 200))  # Escalado

    return tracking_score


def calculate_spinal_alignment(
    landmarks: Dict[str, Tuple[float, float]],
) -> Dict[str, float]:
    """Calcula métricas de alineación espinal."""

    left_shoulder = landmarks["left_shoulder"]
    right_shoulder = landmarks["right_shoulder"]
    left_hip = landmarks["left_hip"]
    right_hip = landmarks["right_hip"]

    # Simetría de hombros
    shoulder_height_diff = abs(left_shoulder[1] - right_shoulder[1])
    shoulder_symmetry = max(0, 100 - (shoulder_height_diff * 500))

    # Ángulo del torso
    shoulder_center = (
        (left_shoulder[0] + right_shoulder[0]) / 2,
        (left_shoulder[1] + right_shoulder[1]) / 2,
    )
    hip_center = ((left_hip[0] + right_hip[0]) / 2, (left_hip[1] + right_hip[1]) / 2)

    torso_angle = abs(
        np.arctan2(
            shoulder_center[0] - hip_center[0], hip_center[1] - shoulder_center[1]
        )
        * 180
        / np.pi
    )

    # Score general de alineación
    alignment_score = (shoulder_symmetry + max(0, 100 - torso_angle * 3)) / 2

    return {
        "score": alignment_score,
        "shoulder_symmetry": shoulder_symmetry,
        "torso_angle": torso_angle,
    }


def generate_area_specific_recommendations(
    area: str, keypoints_data: Dict[str, Any]
) -> List[str]:
    """Genera recomendaciones específicas por área."""

    recommendations = []

    area_recommendations = {
        "rodillas": [
            "Mantén las rodillas alineadas con la punta de los pies",
            "Activa los glúteos para evitar que las rodillas se desvíen hacia adentro",
            "Controla el descenso para evitar valgo de rodilla",
        ],
        "espalda": [
            "Mantén el pecho arriba y los hombros hacia atrás",
            "Activa el core para proteger la columna",
            "Evita redondear la espalda baja",
        ],
        "hombros": [
            "Retrae las escápulas antes de iniciar el movimiento",
            "Mantén los hombros alejados de las orejas",
            "Estabiliza la articulación glenohumeral",
        ],
        "cadera": [
            "Inicia el movimiento empujando la cadera hacia atrás",
            "Mantén la flexibilidad en la articulación de la cadera",
            "Activa los glúteos durante todo el movimiento",
        ],
    }

    base_recommendations = area_recommendations.get(
        area.lower(), ["Mantén control y atención en esta área"]
    )

    # Añadir recomendaciones específicas basadas en análisis
    area_assessment = assess_area_quantitatively(area, keypoints_data)

    if area_assessment["score"] < 70:
        recommendations.extend(
            [
                f"Practica ejercicios específicos para {area.lower()}",
                f"Considera reducir la intensidad para enfocarte en la técnica de {area.lower()}",
            ]
        )

    recommendations.extend(base_recommendations)

    return recommendations[:4]  # Limitar a 4 recomendaciones principales


def assess_area_risk_enhanced(
    area: str, keypoints_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Evaluación mejorada de riesgo por área específica."""

    risk_assessment = {
        "risk_level": "low",
        "risk_score": 25,  # 0-100, donde 100 = muy alto riesgo
        "specific_concerns": [],
        "immediate_actions": [],
    }

    area_assessment = assess_area_quantitatively(area, keypoints_data)

    # Evaluar riesgo basado en score cuantitativo
    if area_assessment["score"] < 50:
        risk_assessment.update(
            {
                "risk_level": "high",
                "risk_score": 80,
                "specific_concerns": [f"Técnica deficiente en {area}"],
                "immediate_actions": ["Detener ejercicio", "Trabajar en correcciones"],
            }
        )
    elif area_assessment["score"] < 70:
        risk_assessment.update(
            {
                "risk_level": "medium",
                "risk_score": 50,
                "specific_concerns": [f"Técnica subóptima en {area}"],
                "immediate_actions": ["Reducir intensidad", "Enfocarse en técnica"],
            }
        )

    # Riesgos específicos por área
    if (
        area.lower() == "rodillas"
        and area_assessment.get("metrics", {}).get("tracking_quality", 100) < 60
    ):
        risk_assessment["specific_concerns"].append(
            "Tracking deficiente de rodillas - riesgo de lesión LCA"
        )
        risk_assessment["risk_score"] = max(risk_assessment["risk_score"], 70)

    elif (
        area.lower() == "espalda"
        and area_assessment.get("metrics", {}).get("torso_lean", 0) > 20
    ):
        risk_assessment["specific_concerns"].append(
            "Inclinación excesiva - riesgo de lesión lumbar"
        )
        risk_assessment["risk_score"] = max(risk_assessment["risk_score"], 65)

    return risk_assessment


def estimate_area_improvement_time(area: str, keypoints_data: Dict[str, Any]) -> str:
    """Estima tiempo de mejora para un área específica."""

    area_assessment = assess_area_quantitatively(area, keypoints_data)
    score = area_assessment["score"]

    if score >= 80:
        return "1-2 semanas para perfeccionar"
    elif score >= 60:
        return "3-4 semanas para mejora significativa"
    elif score >= 40:
        return "6-8 semanas con trabajo dedicado"
    else:
        return "8-12 semanas con entrenamiento específico intensivo"
