"""
NEXUS ENHANCED - Performance Tests for Load Scenarios
====================================================

Tests de performance y carga para validar el comportamiento del sistema
NEXUS Enhanced bajo diferentes condiciones de estrés y volumen.

Arquitectura A+ - Testing Framework
"""

import pytest
import asyncio
import time
import statistics
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List, Tuple
from datetime import datetime
import random
import string

# Imports para performance testing
from ..core.dependencies import NexusDependencies
from ..core.config import NexusConfig, OrchestratorMode, ClientSuccessLevel
from ..skills_manager import NexusSkillsManager


@pytest.mark.asyncio
class TestConcurrencyPerformance:
    """Tests de performance con concurrencia."""

    async def test_concurrent_intent_analysis_load(self, nexus_skills_manager):
        """Test análisis de intención bajo carga concurrente."""
        # Generar 20 consultas simultáneas
        user_inputs = [
            "Plan de entrenamiento para principiante",
            "¿Qué debo comer antes del gym?",
            "Soy nuevo, ¿cómo empiezo?",
            "Tengo problemas con la app",
            "¡Alcancé mi objetivo de peso!",
            "Plan de nutrición personalizado",
            "Ejercicios para ganar músculo",
            "¿Cómo mejorar mi resistencia?",
            "Ayuda con mi rutina de recuperación",
            "Análisis de mis datos biométricos",
            "Motivación para seguir entrenando",
            "Seguimiento de mi progreso",
            "Técnicas de biohacking avanzado",
            "Consultas sobre salud femenina",
            "Integración con mi dispositivo",
            "Problemas de seguridad",
            "Plan de entrenamiento avanzado",
            "Recetas saludables",
            "¿Puedes ayudarme?",
            "Celebrar mi logro de hoy",
        ]

        start_time = time.time()

        # Ejecutar análisis concurrente
        tasks = [
            nexus_skills_manager.analyze_intent_enhanced(user_input, f"user_{i:03d}")
            for i, user_input in enumerate(user_inputs)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        total_time = (end_time - start_time) * 1000  # ms

        # Métricas de performance
        successful_results = [r for r in results if isinstance(r, dict)]
        failure_rate = (len(results) - len(successful_results)) / len(results)
        avg_time_per_request = total_time / len(results)

        # Assertions de performance
        assert total_time < 5000, f"Total time {total_time}ms exceeds 5s threshold"
        assert failure_rate < 0.05, f"Failure rate {failure_rate} exceeds 5% threshold"
        assert (
            avg_time_per_request < 500
        ), f"Average time {avg_time_per_request}ms exceeds 500ms per request"

        # Verificar calidad de respuestas
        for result in successful_results:
            assert "primary_intent" in result
            assert "recommended_mode" in result
            assert "confidence" in result

    async def test_sustained_load_performance(self, nexus_skills_manager):
        """Test performance bajo carga sostenida."""
        # Simular carga sostenida: 10 usuarios por 30 segundos
        duration_seconds = 10  # Reducido para testing
        users_per_second = 2

        start_time = time.time()
        all_tasks = []
        response_times = []

        async def simulate_user_interaction(user_id: str, iteration: int):
            """Simula interacción de usuario individual."""
            interaction_start = time.time()

            user_inputs = [
                "Plan de entrenamiento",
                "Ayuda nutricional",
                "¿Cómo van mis objetivos?",
                "Problemas con la app",
                "¡Logré mi meta!",
            ]

            user_input = random.choice(user_inputs)

            try:
                result = await nexus_skills_manager.analyze_intent_enhanced(
                    user_input, f"{user_id}_iter_{iteration}"
                )

                interaction_time = (time.time() - interaction_start) * 1000
                response_times.append(interaction_time)

                return {
                    "status": "success",
                    "response_time": interaction_time,
                    "result": result,
                }
            except Exception as e:
                interaction_time = (time.time() - interaction_start) * 1000
                return {
                    "status": "error",
                    "response_time": interaction_time,
                    "error": str(e),
                }

        # Generar carga sostenida
        iteration = 0
        while time.time() - start_time < duration_seconds:
            # Crear batch de usuarios
            batch_tasks = [
                simulate_user_interaction(f"load_user_{i}", iteration)
                for i in range(users_per_second)
            ]

            all_tasks.extend(batch_tasks)
            iteration += 1

            # Esperar un segundo antes del siguiente batch
            await asyncio.sleep(1)

        # Ejecutar todas las tareas
        results = await asyncio.gather(*all_tasks, return_exceptions=True)

        # Análisis de performance
        successful_results = [
            r for r in results if isinstance(r, dict) and r.get("status") == "success"
        ]
        total_requests = len(results)
        success_rate = (
            len(successful_results) / total_requests if total_requests > 0 else 0
        )

        # Estadísticas de tiempo de respuesta
        if response_times:
            p50_response_time = statistics.median(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[
                18
            ]  # 95th percentile
            avg_response_time = statistics.mean(response_times)
        else:
            p50_response_time = p95_response_time = avg_response_time = 0

        # Assertions de carga sostenida
        assert success_rate >= 0.95, f"Success rate {success_rate} below 95% threshold"
        assert (
            p50_response_time < 500
        ), f"P50 response time {p50_response_time}ms exceeds 500ms"
        assert (
            p95_response_time < 1000
        ), f"P95 response time {p95_response_time}ms exceeds 1000ms"
        assert (
            total_requests >= duration_seconds * users_per_second * 0.8
        ), "Insufficient load generated"

    async def test_memory_usage_under_load(self, nexus_skills_manager):
        """Test uso de memoria bajo carga."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Ejecutar 100 operaciones para verificar memory leaks
        tasks = []
        for i in range(100):
            user_input = f"Test query {i} with some variable content {random.random()}"
            task = nexus_skills_manager.analyze_intent_enhanced(
                user_input, f"memory_test_user_{i}"
            )
            tasks.append(task)

        # Ejecutar en batches para evitar sobrecargar
        batch_size = 10
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i : i + batch_size]
            await asyncio.gather(*batch, return_exceptions=True)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Assertion de uso de memoria
        assert (
            memory_increase < 50
        ), f"Memory usage increased by {memory_increase}MB, possible memory leak"


@pytest.mark.asyncio
class TestScalabilityLimits:
    """Tests para determinar límites de escalabilidad."""

    async def test_maximum_concurrent_users(self, nexus_skills_manager):
        """Test máximo número de usuarios concurrentes."""
        # Incrementar gradualmente hasta encontrar límite
        concurrent_levels = [5, 10, 20, 30]
        results_by_level = {}

        for level in concurrent_levels:
            tasks = [
                nexus_skills_manager.analyze_intent_enhanced(
                    f"Test query for user {i}", f"concurrent_user_{i}"
                )
                for i in range(level)
            ]

            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            successful_results = [r for r in results if isinstance(r, dict)]
            success_rate = len(successful_results) / len(results)
            total_time = (end_time - start_time) * 1000
            avg_time = total_time / len(results)

            results_by_level[level] = {
                "success_rate": success_rate,
                "total_time": total_time,
                "avg_time": avg_time,
            }

            # Si la tasa de éxito cae dramáticamente, hemos encontrado el límite
            if success_rate < 0.8:
                break

        # Verificar que maneja al menos 10 usuarios concurrentes con 90% success rate
        assert (
            results_by_level[10]["success_rate"] >= 0.9
        ), "Cannot handle 10 concurrent users"

        # Imprimir resultados para análisis
        for level, metrics in results_by_level.items():
            print(
                f"Level {level}: Success={metrics['success_rate']:.2%}, "
                f"Total={metrics['total_time']:.1f}ms, Avg={metrics['avg_time']:.1f}ms"
            )

    async def test_large_input_handling(self, nexus_skills_manager):
        """Test manejo de inputs grandes."""
        # Generar inputs de diferentes tamaños
        input_sizes = [100, 500, 1000, 2000, 4000]  # caracteres

        for size in input_sizes:
            # Generar input de tamaño específico
            large_input = "Necesito ayuda con mi plan de entrenamiento. " * (size // 50)
            large_input = large_input[:size]  # Truncar al tamaño exacto

            start_time = time.time()

            try:
                result = await nexus_skills_manager.analyze_intent_enhanced(
                    large_input, f"large_input_user_{size}"
                )

                processing_time = (time.time() - start_time) * 1000

                # Verificar que se procesó correctamente
                assert isinstance(result, dict)
                assert "primary_intent" in result

                # Tiempo debe crecer linealmente, no exponencialmente
                max_expected_time = size * 0.5  # 0.5ms per character max
                assert (
                    processing_time < max_expected_time
                ), f"Processing time {processing_time}ms too high for input size {size}"

            except Exception as e:
                # Para inputs muy grandes, error controlado es aceptable
                if size > 3000:
                    assert "too large" in str(e).lower() or "limit" in str(e).lower()
                else:
                    raise  # Inputs menores deben procesarse correctamente

    async def test_rapid_sequential_requests(self, nexus_skills_manager):
        """Test requests secuenciales rápidos del mismo usuario."""
        user_id = "rapid_user_001"
        num_requests = 50

        # Generar requests secuenciales rápidos
        start_time = time.time()

        for i in range(num_requests):
            user_input = f"Consulta rápida número {i}"

            result = await nexus_skills_manager.analyze_intent_enhanced(
                user_input, user_id
            )

            # Verificar que cada request se procesa correctamente
            assert isinstance(result, dict)
            assert "primary_intent" in result

        end_time = time.time()
        total_time = (end_time - start_time) * 1000
        avg_time_per_request = total_time / num_requests

        # Assertions para requests secuenciales
        assert (
            avg_time_per_request < 200
        ), f"Average sequential time {avg_time_per_request}ms too high"
        assert total_time < 10000, f"Total sequential time {total_time}ms exceeds 10s"


@pytest.mark.asyncio
class TestResourceManagement:
    """Tests de gestión de recursos."""

    async def test_connection_pool_efficiency(self, nexus_skills_manager):
        """Test eficiencia del connection pooling."""
        # Simular múltiples requests que requieren conexiones externas
        num_requests = 20

        start_time = time.time()

        tasks = [
            nexus_skills_manager.analyze_intent_enhanced(
                f"Query requiring external connection {i}", f"conn_pool_user_{i}"
            )
            for i in range(num_requests)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        total_time = (end_time - start_time) * 1000

        successful_results = [r for r in results if isinstance(r, dict)]
        success_rate = len(successful_results) / len(results)

        # Connection pooling debe permitir alta concurrencia
        assert (
            success_rate >= 0.95
        ), f"Connection pool success rate {success_rate} too low"
        assert total_time < 3000, f"Connection pool total time {total_time}ms too high"

    async def test_cache_performance_impact(self, nexus_skills_manager):
        """Test impacto de caché en performance."""
        user_input = "Plan de entrenamiento para principiante"
        user_id = "cache_test_user"

        # Primera ejecución (sin caché)
        start_time = time.time()
        result1 = await nexus_skills_manager.analyze_intent_enhanced(
            user_input, user_id
        )
        first_time = (time.time() - start_time) * 1000

        # Segunda ejecución (con caché, si está implementado)
        start_time = time.time()
        result2 = await nexus_skills_manager.analyze_intent_enhanced(
            user_input, user_id
        )
        second_time = (time.time() - start_time) * 1000

        # Verificar consistencia de resultados
        assert result1["primary_intent"] == result2["primary_intent"]

        # Si hay caché, la segunda ejecución debe ser más rápida
        # Si no hay caché, ambas deben ser razonablemente rápidas
        cache_speedup = first_time / second_time if second_time > 0 else 1

        print(
            f"Cache performance: First={first_time:.1f}ms, Second={second_time:.1f}ms, "
            f"Speedup={cache_speedup:.1f}x"
        )

        # Ambas ejecuciones deben completarse en tiempo razonable
        assert first_time < 1000, f"First execution {first_time}ms too slow"
        assert second_time < 1000, f"Second execution {second_time}ms too slow"

    async def test_error_handling_performance(self, nexus_skills_manager):
        """Test performance de manejo de errores."""
        # Inputs que pueden causar errores
        error_inducing_inputs = [
            "",  # Input vacío
            "a" * 10000,  # Input muy largo
            "🚀🚀🚀" * 100,  # Emojis repetidos
            "SELECT * FROM users;",  # SQL injection attempt
            "<script>alert('xss')</script>",  # XSS attempt
        ]

        error_handling_times = []

        for i, user_input in enumerate(error_inducing_inputs):
            start_time = time.time()

            try:
                result = await nexus_skills_manager.analyze_intent_enhanced(
                    user_input, f"error_test_user_{i}"
                )
                # Si no lanza error, debe ser resultado válido
                assert isinstance(result, dict)
            except Exception:
                # Error es aceptable para algunos inputs
                pass

            error_time = (time.time() - start_time) * 1000
            error_handling_times.append(error_time)

        # Manejo de errores debe ser rápido
        avg_error_time = statistics.mean(error_handling_times)
        max_error_time = max(error_handling_times)

        assert (
            avg_error_time < 100
        ), f"Average error handling time {avg_error_time}ms too high"
        assert (
            max_error_time < 500
        ), f"Max error handling time {max_error_time}ms too high"


@pytest.mark.asyncio
class TestRealWorldScenarios:
    """Tests de escenarios del mundo real."""

    async def test_peak_hour_simulation(self, nexus_skills_manager):
        """Simula hora pico con patrones realistas de uso."""
        # Patrones típicos de uso en hora pico
        usage_patterns = {
            "morning_workout": {
                "inputs": [
                    "Plan de entrenamiento matutino",
                    "¿Qué desayunar antes del gym?",
                    "Ejercicios de calentamiento",
                ],
                "weight": 0.4,  # 40% de usuarios
            },
            "nutrition_planning": {
                "inputs": [
                    "Plan de comidas para hoy",
                    "¿Cuántas calorías necesito?",
                    "Recetas saludables",
                ],
                "weight": 0.3,  # 30% de usuarios
            },
            "progress_tracking": {
                "inputs": [
                    "¿Cómo van mis objetivos?",
                    "Registrar mi peso de hoy",
                    "Ver mi progreso semanal",
                ],
                "weight": 0.2,  # 20% de usuarios
            },
            "support_help": {
                "inputs": [
                    "Tengo una pregunta",
                    "Problemas técnicos",
                    "¿Cómo hago esto?",
                ],
                "weight": 0.1,  # 10% de usuarios
            },
        }

        # Generar 30 requests distribuidos según patrones
        requests = []
        for pattern_name, pattern_data in usage_patterns.items():
            num_requests = int(30 * pattern_data["weight"])
            for i in range(num_requests):
                user_input = random.choice(pattern_data["inputs"])
                user_id = f"{pattern_name}_user_{i}"
                requests.append((user_input, user_id))

        # Mezclar requests para simular llegada aleatoria
        random.shuffle(requests)

        # Ejecutar simulación de hora pico
        start_time = time.time()

        tasks = [
            nexus_skills_manager.analyze_intent_enhanced(user_input, user_id)
            for user_input, user_id in requests
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        total_time = (end_time - start_time) * 1000

        # Análisis de resultados
        successful_results = [r for r in results if isinstance(r, dict)]
        success_rate = len(successful_results) / len(results)
        avg_time = total_time / len(results)

        # Assertions para hora pico
        assert success_rate >= 0.95, f"Peak hour success rate {success_rate} below 95%"
        assert avg_time < 300, f"Peak hour average time {avg_time}ms too high"
        assert total_time < 5000, f"Peak hour total time {total_time}ms exceeds 5s"

    async def test_mixed_load_simulation(self, nexus_skills_manager):
        """Simula carga mixta con diferentes tipos de usuarios."""
        # Diferentes tipos de usuarios con comportamientos distintos
        user_types = {
            "power_user": {
                "requests_per_session": 10,
                "delay_between_requests": 0.1,  # Requests rápidos
                "complexity": "high",
            },
            "casual_user": {
                "requests_per_session": 3,
                "delay_between_requests": 2.0,  # Requests pausados
                "complexity": "low",
            },
            "new_user": {
                "requests_per_session": 5,
                "delay_between_requests": 1.0,  # Requests moderados
                "complexity": "medium",
            },
        }

        async def simulate_user_session(user_type: str, user_id: str, config: Dict):
            """Simula sesión completa de usuario."""
            session_results = []

            for i in range(config["requests_per_session"]):
                # Generar input basado en complejidad
                if config["complexity"] == "high":
                    user_input = f"Análisis detallado y plan completo para objetivo específico {i}"
                elif config["complexity"] == "low":
                    user_input = f"Ayuda simple {i}"
                else:
                    user_input = f"Consulta moderada sobre fitness {i}"

                try:
                    result = await nexus_skills_manager.analyze_intent_enhanced(
                        user_input, f"{user_id}_req_{i}"
                    )
                    session_results.append({"status": "success", "result": result})
                except Exception as e:
                    session_results.append({"status": "error", "error": str(e)})

                # Delay entre requests según tipo de usuario
                if i < config["requests_per_session"] - 1:  # No delay en última request
                    await asyncio.sleep(config["delay_between_requests"])

            return session_results

        # Crear múltiples sesiones de usuarios simultáneas
        session_tasks = []
        for user_type, config in user_types.items():
            for user_num in range(3):  # 3 usuarios de cada tipo
                user_id = f"{user_type}_{user_num}"
                task = simulate_user_session(user_type, user_id, config)
                session_tasks.append(task)

        # Ejecutar todas las sesiones concurrentemente
        start_time = time.time()
        session_results = await asyncio.gather(*session_tasks, return_exceptions=True)
        end_time = time.time()

        total_time = (end_time - start_time) * 1000

        # Analizar resultados agregados
        total_requests = 0
        successful_requests = 0

        for session_result in session_results:
            if isinstance(session_result, list):
                total_requests += len(session_result)
                successful_requests += sum(
                    1 for r in session_result if r.get("status") == "success"
                )

        overall_success_rate = (
            successful_requests / total_requests if total_requests > 0 else 0
        )

        # Assertions para carga mixta
        assert (
            overall_success_rate >= 0.90
        ), f"Mixed load success rate {overall_success_rate} below 90%"
        assert total_time < 15000, f"Mixed load total time {total_time}ms exceeds 15s"
        assert (
            total_requests >= 60
        ), "Insufficient mixed load generated"  # 9 users * ~6.67 avg requests


# Fixtures para performance testing


@pytest.fixture
def performance_benchmarks():
    """Benchmarks de performance esperados."""
    return {
        "intent_analysis_max_time_ms": 500,
        "response_synthesis_max_time_ms": 1000,
        "concierge_onboarding_max_time_ms": 800,
        "milestone_celebration_max_time_ms": 600,
        "overall_response_max_time_ms": 3000,
        "min_confidence_threshold": 0.7,
        "max_error_rate": 0.01,
        "min_success_rate": 0.95,
        "max_concurrent_users": 20,
        "max_memory_increase_mb": 50,
    }


@pytest.fixture
def load_test_data():
    """Datos para testing de carga."""
    return {
        "user_inputs": [
            "Plan de entrenamiento personalizado",
            "Análisis nutricional completo",
            "¿Cómo puedo mejorar mi recuperación?",
            "Tracking de progreso semanal",
            "Motivación para seguir adelante",
            "Problemas con mi rutina actual",
            "¿Qué ejercicios son mejores para mí?",
            "Plan de alimentación saludable",
            "¿Cómo optimizar mi rendimiento?",
            "Ayuda con objetivos a largo plazo",
        ],
        "stress_inputs": [
            "",  # Input vacío
            "a" * 1000,  # Input muy largo
            "🚀" * 100,  # Caracteres especiales
            "Plan de entrenamiento " * 50,  # Repetitivo
            "MAYÚSCULAS EXTREMAS!!!",  # Formateo agresivo
        ],
        "concurrent_levels": [1, 5, 10, 15, 20, 25, 30],
        "load_duration_seconds": 10,
    }


# Utilidades para performance testing


def generate_random_string(length: int) -> str:
    """Genera string aleatorio para testing."""
    return "".join(random.choices(string.ascii_letters + string.digits + " ", k=length))


def calculate_percentile(data: List[float], percentile: int) -> float:
    """Calcula percentil específico de lista de datos."""
    if not data:
        return 0.0

    sorted_data = sorted(data)
    index = (percentile / 100) * (len(sorted_data) - 1)

    if index == int(index):
        return sorted_data[int(index)]
    else:
        lower = sorted_data[int(index)]
        upper = sorted_data[int(index) + 1]
        return lower + (upper - lower) * (index - int(index))


async def measure_operation_time(operation_coro):
    """Mide tiempo de ejecución de operación asíncrona."""
    start_time = time.time()
    result = await operation_coro
    end_time = time.time()
    execution_time = (end_time - start_time) * 1000  # ms

    return result, execution_time
