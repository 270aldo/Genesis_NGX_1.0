"""
Stress Test Scenarios

Tests GENESIS system performance under extreme conditions including high load,
marathon sessions, resource constraints, and concurrent usage patterns.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, timezone
import json
import random
import string
from concurrent.futures import ThreadPoolExecutor

from app.schemas.chat import ChatRequest, ChatResponse
from core.logging_config import get_logger

logger = get_logger(__name__)


class StressTestScenarios:
    """Test scenarios for system stress and performance limits"""
    
    def __init__(self, orchestrator_client):
        """
        Initialize with orchestrator client for testing
        
        Args:
            orchestrator_client: Client to interact with GENESIS orchestrator
        """
        self.orchestrator = orchestrator_client
        self.results = []
        
    async def run_all_scenarios(self) -> Dict[str, Any]:
        """Run all stress test scenarios"""
        scenarios = [
            self.test_concurrent_users,
            self.test_marathon_session,
            self.test_rapid_fire_messages,
            self.test_large_context_accumulation,
            self.test_memory_pressure,
            self.test_api_rate_limits,
            self.test_database_connection_pool,
            self.test_cache_saturation,
            self.test_websocket_limits,
            self.test_error_recovery,
            self.test_cascade_failures,
            self.test_resource_exhaustion,
            self.test_network_latency,
            self.test_data_consistency_under_load,
            self.test_graceful_degradation
        ]
        
        results = {
            "category": "stress_tests",
            "total_scenarios": len(scenarios),
            "passed": 0,
            "failed": 0,
            "details": []
        }
        
        for scenario in scenarios:
            try:
                result = await scenario()
                if result["passed"]:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                results["details"].append(result)
            except Exception as e:
                logger.error(f"Error in scenario {scenario.__name__}: {e}")
                results["failed"] += 1
                results["details"].append({
                    "scenario": scenario.__name__,
                    "passed": False,
                    "error": str(e)
                })
        
        return results
    
    async def test_concurrent_users(self) -> Dict[str, Any]:
        """Test: Multiple concurrent users (100+)"""
        scenario_name = "concurrent_users"
        
        num_users = 100
        messages_per_user = 5
        
        async def simulate_user(user_id: int):
            """Simulate a single user session"""
            session_results = []
            session_id = f"stress_user_{user_id}_{int(datetime.now(timezone.utc).timestamp())}"
            
            messages = [
                "Hola, necesito un plan de entrenamiento",
                f"Tengo {20 + user_id % 30} años y peso {60 + user_id % 40}kg",
                "Quiero ganar músculo y perder grasa",
                "¿Cuántas calorías debo consumir?",
                "Gracias por la ayuda"
            ]
            
            for msg in messages[:messages_per_user]:
                try:
                    request = ChatRequest(
                        text=msg,
                        user_id=f"stress_test_user_{user_id}",
                        session_id=session_id
                    )
                    
                    start_time = datetime.now(timezone.utc)
                    response = await self.orchestrator.process_message(request)
                    end_time = datetime.now(timezone.utc)
                    
                    session_results.append({
                        "success": True,
                        "response_time": (end_time - start_time).total_seconds(),
                        "message_length": len(response.response)
                    })
                    
                    # Small random delay between messages
                    await asyncio.sleep(random.uniform(0.5, 2.0))
                    
                except Exception as e:
                    session_results.append({
                        "success": False,
                        "error": str(e)
                    })
            
            return session_results
        
        # Run concurrent user simulations
        start_time = datetime.now(timezone.utc)
        
        # Create tasks for all users
        tasks = [simulate_user(i) for i in range(num_users)]
        
        # Execute with controlled concurrency
        all_results = []
        batch_size = 20  # Process users in batches
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            all_results.extend(batch_results)
            
            # Brief pause between batches
            await asyncio.sleep(1)
        
        end_time = datetime.now(timezone.utc)
        
        # Analyze results
        total_requests = 0
        successful_requests = 0
        failed_requests = 0
        response_times = []
        
        for user_results in all_results:
            if isinstance(user_results, Exception):
                failed_requests += messages_per_user
                continue
                
            for result in user_results:
                total_requests += 1
                if result["success"]:
                    successful_requests += 1
                    response_times.append(result["response_time"])
                else:
                    failed_requests += 1
        
        # Calculate metrics
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "scenario": scenario_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "num_users": num_users,
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "max_response_time": max_response_time,
                "total_duration": (end_time - start_time).total_seconds()
            },
            "passed": success_rate >= 95 and avg_response_time < 3.0,
            "issues": []
        }
    
    async def test_marathon_session(self) -> Dict[str, Any]:
        """Test: Single user marathon session (2+ hours)"""
        scenario_name = "marathon_session"
        
        session_id = f"marathon_{int(datetime.now(timezone.utc).timestamp())}"
        user_id = "marathon_test_user"
        
        # Simulate 2-hour conversation with varied topics
        conversation_topics = [
            # First 30 minutes: Initial assessment
            ("Evaluación inicial", [
                "Hola, quiero empezar un programa completo de fitness",
                "Tengo 35 años, peso 85kg y mido 1.80m",
                "Mi objetivo es perder 10kg y ganar músculo",
                "Trabajo en oficina y tengo poco tiempo",
                "Nunca he hecho ejercicio consistentemente"
            ]),
            # 30-60 minutes: Training planning
            ("Plan de entrenamiento", [
                "¿Qué tipo de ejercicios me recomiendas?",
                "¿Cuántos días a la semana debo entrenar?",
                "Explícame la técnica de las sentadillas",
                "¿Qué es mejor, pesas o cardio?",
                "Dame una rutina específica para principiantes"
            ]),
            # 60-90 minutes: Nutrition discussion
            ("Nutrición", [
                "Hablemos de la dieta",
                "¿Cuántas calorías debo consumir?",
                "No me gusta el brócoli, ¿alternativas?",
                "¿Qué opinas de la dieta keto?",
                "Dame un plan de comidas para la semana"
            ]),
            # 90-120 minutes: Advanced topics
            ("Temas avanzados", [
                "Cuéntame sobre suplementos",
                "¿Cómo mejoro mi sueño?",
                "Tengo dolor de espalda, ¿qué hago?",
                "¿Cómo mantengo la motivación?",
                "Quiero preparame para una carrera 5K"
            ])
        ]
        
        results = {
            "scenario": scenario_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_duration": 0,
            "messages_exchanged": 0,
            "context_coherence": True,
            "memory_usage": [],
            "response_quality": [],
            "errors": [],
            "passed": False
        }
        
        start_time = datetime.now(timezone.utc)
        
        try:
            for topic_name, messages in conversation_topics:
                logger.info(f"Marathon session - Topic: {topic_name}")
                
                for message in messages:
                    # Send message
                    request = ChatRequest(
                        text=message,
                        user_id=user_id,
                        session_id=session_id,
                        context={"marathon_test": True, "current_topic": topic_name}
                    )
                    
                    response = await self.orchestrator.process_message(request)
                    results["messages_exchanged"] += 1
                    
                    # Evaluate response quality
                    quality_score = self._evaluate_response_quality(response)
                    results["response_quality"].append(quality_score)
                    
                    # Check for context coherence
                    if not self._check_context_coherence(response, topic_name):
                        results["context_coherence"] = False
                    
                    # Simulate realistic conversation pace
                    await asyncio.sleep(random.uniform(5, 15))
                    
                # Longer pause between topics
                await asyncio.sleep(30)
            
            end_time = datetime.now(timezone.utc)
            results["session_duration"] = (end_time - start_time).total_seconds()
            
            # Calculate final metrics
            avg_quality = sum(results["response_quality"]) / len(results["response_quality"])
            
            results["passed"] = (
                results["context_coherence"] and
                avg_quality >= 0.8 and
                len(results["errors"]) == 0 and
                results["session_duration"] >= 7200  # 2 hours
            )
            
        except Exception as e:
            results["errors"].append(str(e))
            results["passed"] = False
            
        return results
    
    async def test_rapid_fire_messages(self) -> Dict[str, Any]:
        """Test: Rapid fire messages (no delay)"""
        scenario_name = "rapid_fire_messages"
        
        num_messages = 50
        session_id = f"rapid_fire_{int(datetime.now(timezone.utc).timestamp())}"
        
        # Generate diverse rapid messages
        rapid_messages = [
            "¿Cuántas series?",
            "¿Y repeticiones?",
            "¿Descanso?",
            "¿Peso?",
            "¿Alternativas?",
            "¿Por qué?",
            "No entiendo",
            "Explica más",
            "¿Es seguro?",
            "¿Cuándo veo resultados?"
        ] * 5  # 50 messages total
        
        results = {
            "messages_sent": 0,
            "successful_responses": 0,
            "errors": [],
            "response_times": [],
            "rate_limit_hits": 0
        }
        
        start_time = datetime.now(timezone.utc)
        
        # Send messages as fast as possible
        for message in rapid_messages:
            try:
                request = ChatRequest(
                    text=message,
                    user_id="rapid_test_user",
                    session_id=session_id
                )
                
                msg_start = datetime.now(timezone.utc)
                response = await self.orchestrator.process_message(request)
                msg_end = datetime.now(timezone.utc)
                
                results["messages_sent"] += 1
                results["successful_responses"] += 1
                results["response_times"].append((msg_end - msg_start).total_seconds())
                
            except Exception as e:
                error_str = str(e)
                results["errors"].append(error_str)
                if "rate limit" in error_str.lower():
                    results["rate_limit_hits"] += 1
        
        end_time = datetime.now(timezone.utc)
        total_duration = (end_time - start_time).total_seconds()
        
        # Calculate metrics
        messages_per_second = results["messages_sent"] / total_duration
        avg_response_time = sum(results["response_times"]) / len(results["response_times"]) if results["response_times"] else 0
        
        return {
            "scenario": scenario_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "messages_sent": results["messages_sent"],
                "successful_responses": results["successful_responses"],
                "messages_per_second": messages_per_second,
                "avg_response_time": avg_response_time,
                "rate_limit_hits": results["rate_limit_hits"],
                "total_duration": total_duration
            },
            "passed": results["successful_responses"] >= 40 and avg_response_time < 2.0,
            "issues": results["errors"][:5]  # First 5 errors
        }
    
    async def test_large_context_accumulation(self) -> Dict[str, Any]:
        """Test: Large context accumulation over conversation"""
        scenario_name = "large_context_accumulation"
        
        session_id = f"large_context_{int(datetime.now(timezone.utc).timestamp())}"
        
        # Build increasingly complex context
        context_building_messages = [
            # Personal info dump
            "Mi nombre es Juan Carlos Rodríguez González, tengo 42 años, vivo en Madrid, " +
            "trabajo como ingeniero de software en una empresa tecnológica, estoy casado " +
            "con María y tenemos dos hijos de 8 y 12 años.",
            
            # Medical history
            "Mi historial médico incluye: hipertensión diagnosticada hace 5 años, " +
            "colesterol alto, cirugía de rodilla en 2019, alergia al polen y los ácaros, " +
            "intolerancia a la lactosa, y antecedentes familiares de diabetes.",
            
            # Detailed goals
            "Mis objetivos son: perder 15kg en 6 meses, correr una media maratón en octubre, " +
            "mejorar mi postura para el dolor de espalda, aumentar masa muscular en brazos, " +
            "mejorar mi flexibilidad para yoga, y reducir mi tiempo en 5K a menos de 25 minutos.",
            
            # Complex preferences
            "Mis preferencias de entrenamiento: no puedo entrenar lunes y miércoles por trabajo, " +
            "prefiero entrenar en casa o al aire libre, no me gustan las pesas muy pesadas, " +
            "disfruto natación pero solo en verano, odio burpees y jumping jacks, " +
            "y necesito ejercicios silenciosos porque entreno cuando duermen mis hijos.",
            
            # Add 20 more context-heavy messages
            *[f"Información adicional {i}: " + "x" * 200 for i in range(20)]
        ]
        
        results = {
            "scenario": scenario_name,
            "context_size": 0,
            "response_coherence": [],
            "memory_efficiency": True,
            "performance_degradation": []
        }
        
        try:
            for i, message in enumerate(context_building_messages):
                request = ChatRequest(
                    text=message,
                    user_id="context_test_user",
                    session_id=session_id
                )
                
                start_time = datetime.now(timezone.utc)
                response = await self.orchestrator.process_message(request)
                end_time = datetime.now(timezone.utc)
                
                response_time = (end_time - start_time).total_seconds()
                results["performance_degradation"].append(response_time)
                
                # Check if response still coherent with accumulated context
                coherence_score = self._evaluate_context_coherence_score(response, i)
                results["response_coherence"].append(coherence_score)
                
                # Estimate context size
                results["context_size"] += len(message) + len(response.response)
                
                await asyncio.sleep(1)
            
            # Analyze performance degradation
            early_avg = sum(results["performance_degradation"][:5]) / 5
            late_avg = sum(results["performance_degradation"][-5:]) / 5
            degradation_ratio = late_avg / early_avg if early_avg > 0 else float('inf')
            
            avg_coherence = sum(results["response_coherence"]) / len(results["response_coherence"])
            
            results["passed"] = (
                degradation_ratio < 2.0 and  # Less than 2x slowdown
                avg_coherence > 0.7 and
                results["memory_efficiency"]
            )
            
        except Exception as e:
            results["error"] = str(e)
            results["passed"] = False
            
        return results
    
    async def test_memory_pressure(self) -> Dict[str, Any]:
        """Test: System behavior under memory pressure"""
        scenario_name = "memory_pressure"
        
        # Create multiple sessions with large contexts
        num_sessions = 20
        messages_per_session = 10
        
        async def memory_intensive_session(session_num: int):
            """Run a memory-intensive session"""
            session_id = f"memory_test_{session_num}"
            large_message = "A" * 5000  # 5KB message
            
            session_results = []
            
            for i in range(messages_per_session):
                try:
                    request = ChatRequest(
                        text=f"Mensaje {i}: {large_message}",
                        user_id=f"memory_user_{session_num}",
                        session_id=session_id,
                        context={"large_data": "B" * 10000}  # 10KB context
                    )
                    
                    response = await self.orchestrator.process_message(request)
                    session_results.append({"success": True})
                    
                except Exception as e:
                    session_results.append({"success": False, "error": str(e)})
            
            return session_results
        
        # Run sessions concurrently
        tasks = [memory_intensive_session(i) for i in range(num_sessions)]
        all_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        total_attempts = num_sessions * messages_per_session
        successful = sum(
            1 for session in all_results
            if not isinstance(session, Exception)
            for result in session
            if result["success"]
        )
        
        return {
            "scenario": scenario_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "total_sessions": num_sessions,
                "total_attempts": total_attempts,
                "successful_requests": successful,
                "success_rate": (successful / total_attempts * 100) if total_attempts > 0 else 0,
                "estimated_memory_usage": f"{num_sessions * messages_per_session * 15}KB"
            },
            "passed": successful / total_attempts >= 0.9,  # 90% success rate
            "issues": []
        }
    
    async def test_api_rate_limits(self) -> Dict[str, Any]:
        """Test: API rate limiting behavior"""
        scenario_name = "api_rate_limits"
        
        # Test different rate limit scenarios
        test_cases = [
            {"requests": 10, "duration": 1, "name": "burst_10_per_second"},
            {"requests": 60, "duration": 60, "name": "sustained_1_per_second"},
            {"requests": 100, "duration": 10, "name": "heavy_burst"}
        ]
        
        results = {
            "scenario": scenario_name,
            "test_cases": []
        }
        
        for test_case in test_cases:
            case_results = await self._test_rate_limit_case(
                test_case["requests"],
                test_case["duration"],
                test_case["name"]
            )
            results["test_cases"].append(case_results)
        
        # Overall pass if all cases handle rate limits gracefully
        results["passed"] = all(case["handled_gracefully"] for case in results["test_cases"])
        
        return results
    
    async def test_database_connection_pool(self) -> Dict[str, Any]:
        """Test: Database connection pool exhaustion"""
        scenario_name = "database_connection_pool"
        
        # Simulate many concurrent database operations
        num_concurrent = 50
        
        async def db_intensive_operation(op_id: int):
            """Simulate database-intensive operation"""
            try:
                # Multiple requests that likely hit the database
                messages = [
                    "Revisa mi historial completo",
                    "Muestra todas mis métricas",
                    "Analiza mi progreso de 6 meses",
                    "Compara con otros usuarios"
                ]
                
                results = []
                for msg in messages:
                    request = ChatRequest(
                        text=msg,
                        user_id=f"db_test_user_{op_id}",
                        session_id=f"db_test_{op_id}"
                    )
                    
                    start = datetime.now(timezone.utc)
                    response = await self.orchestrator.process_message(request)
                    end = datetime.now(timezone.utc)
                    
                    results.append({
                        "success": True,
                        "duration": (end - start).total_seconds()
                    })
                
                return results
                
            except Exception as e:
                return [{"success": False, "error": str(e)}]
        
        # Run concurrent operations
        tasks = [db_intensive_operation(i) for i in range(num_concurrent)]
        all_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        total_operations = 0
        successful_operations = 0
        connection_errors = 0
        
        for result in all_results:
            if isinstance(result, Exception):
                connection_errors += 1
            else:
                for op in result:
                    total_operations += 1
                    if op["success"]:
                        successful_operations += 1
                    elif "connection" in op.get("error", "").lower():
                        connection_errors += 1
        
        return {
            "scenario": scenario_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "concurrent_operations": num_concurrent,
                "total_operations": total_operations,
                "successful_operations": successful_operations,
                "connection_errors": connection_errors,
                "success_rate": (successful_operations / total_operations * 100) if total_operations > 0 else 0
            },
            "passed": connection_errors == 0 and successful_operations / total_operations >= 0.95,
            "issues": []
        }
    
    async def test_cache_saturation(self) -> Dict[str, Any]:
        """Test: Cache saturation and eviction"""
        scenario_name = "cache_saturation"
        
        # Generate many unique requests to saturate cache
        num_unique_requests = 1000
        
        results = {
            "cache_hits": 0,
            "cache_misses": 0,
            "response_times": [],
            "errors": []
        }
        
        # First pass: populate cache
        for i in range(num_unique_requests):
            try:
                request = ChatRequest(
                    text=f"Pregunta única número {i}: ¿Cuál es el mejor ejercicio para {i}?",
                    user_id=f"cache_test_user_{i % 10}",
                    session_id=f"cache_test_{i % 100}"
                )
                
                start = datetime.now(timezone.utc)
                await self.orchestrator.process_message(request)
                end = datetime.now(timezone.utc)
                
                results["response_times"].append((end - start).total_seconds())
                
            except Exception as e:
                results["errors"].append(str(e))
        
        # Second pass: test cache hits
        for i in range(min(100, num_unique_requests)):
            try:
                request = ChatRequest(
                    text=f"Pregunta única número {i}: ¿Cuál es el mejor ejercicio para {i}?",
                    user_id=f"cache_test_user_{i % 10}",
                    session_id=f"cache_test_{i % 100}"
                )
                
                start = datetime.now(timezone.utc)
                await self.orchestrator.process_message(request)
                end = datetime.now(timezone.utc)
                
                response_time = (end - start).total_seconds()
                
                # Assume cache hit if response is very fast
                if response_time < 0.1:
                    results["cache_hits"] += 1
                else:
                    results["cache_misses"] += 1
                    
            except Exception as e:
                results["errors"].append(str(e))
        
        cache_hit_rate = results["cache_hits"] / (results["cache_hits"] + results["cache_misses"]) if (results["cache_hits"] + results["cache_misses"]) > 0 else 0
        
        return {
            "scenario": scenario_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "unique_requests": num_unique_requests,
                "cache_hits": results["cache_hits"],
                "cache_misses": results["cache_misses"],
                "cache_hit_rate": cache_hit_rate * 100,
                "avg_response_time": sum(results["response_times"]) / len(results["response_times"]) if results["response_times"] else 0
            },
            "passed": len(results["errors"]) == 0 and cache_hit_rate > 0,
            "issues": results["errors"][:5]
        }
    
    async def test_websocket_limits(self) -> Dict[str, Any]:
        """Test: WebSocket connection limits"""
        scenario_name = "websocket_limits"
        
        # Note: This is a simplified test since we're not directly testing WebSocket
        # In a real scenario, this would test actual WebSocket connections
        
        num_connections = 100
        results = {
            "attempted_connections": num_connections,
            "successful_connections": 0,
            "connection_errors": []
        }
        
        # Simulate multiple streaming sessions
        async def simulate_streaming_session(session_id: int):
            try:
                # Simulate a streaming request
                request = ChatRequest(
                    text="Dame un plan de entrenamiento detallado con explicaciones largas",
                    user_id=f"ws_test_user_{session_id}",
                    session_id=f"ws_test_{session_id}",
                    context={"streaming": True}
                )
                
                response = await self.orchestrator.process_message(request)
                return {"success": True, "session_id": session_id}
                
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        # Attempt concurrent connections
        tasks = [simulate_streaming_session(i) for i in range(num_connections)]
        connection_results = await asyncio.gather(*tasks)
        
        for result in connection_results:
            if result["success"]:
                results["successful_connections"] += 1
            else:
                results["connection_errors"].append(result["error"])
        
        success_rate = results["successful_connections"] / results["attempted_connections"] * 100
        
        return {
            "scenario": scenario_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "attempted_connections": results["attempted_connections"],
                "successful_connections": results["successful_connections"],
                "success_rate": success_rate,
                "unique_errors": len(set(results["connection_errors"]))
            },
            "passed": success_rate >= 80,  # Allow some connection limits
            "issues": list(set(results["connection_errors"]))[:5]
        }
    
    async def test_error_recovery(self) -> Dict[str, Any]:
        """Test: System recovery from various errors"""
        scenario_name = "error_recovery"
        
        # Test various error scenarios
        error_scenarios = [
            {"message": "SELECT * FROM users; DROP TABLE users;--", "type": "sql_injection"},
            {"message": "A" * 100000, "type": "oversized_message"},
            {"message": "\x00\x01\x02\x03", "type": "binary_data"},
            {"message": "{'json': 'invalid'}", "type": "malformed_json"},
            {"message": "Repeat this 1000 times: " + "X" * 100, "type": "amplification"}
        ]
        
        results = {
            "scenarios_tested": len(error_scenarios),
            "recovered": 0,
            "failed": 0,
            "recovery_times": []
        }
        
        for scenario in error_scenarios:
            try:
                # Send error-inducing message
                request = ChatRequest(
                    text=scenario["message"],
                    user_id="error_test_user",
                    session_id=f"error_test_{scenario['type']}"
                )
                
                start = datetime.now(timezone.utc)
                
                try:
                    await self.orchestrator.process_message(request)
                except Exception:
                    # Expected to fail, that's ok
                    pass
                
                # Test recovery with normal message
                recovery_request = ChatRequest(
                    text="Hola, necesito ayuda con mi entrenamiento",
                    user_id="error_test_user",
                    session_id=f"error_recovery_{scenario['type']}"
                )
                
                recovery_response = await self.orchestrator.process_message(recovery_request)
                end = datetime.now(timezone.utc)
                
                if recovery_response and recovery_response.response:
                    results["recovered"] += 1
                    results["recovery_times"].append((end - start).total_seconds())
                else:
                    results["failed"] += 1
                    
            except Exception as e:
                results["failed"] += 1
                logger.error(f"Failed to recover from {scenario['type']}: {e}")
        
        avg_recovery_time = sum(results["recovery_times"]) / len(results["recovery_times"]) if results["recovery_times"] else 0
        
        return {
            "scenario": scenario_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "scenarios_tested": results["scenarios_tested"],
                "successful_recoveries": results["recovered"],
                "failed_recoveries": results["failed"],
                "recovery_rate": (results["recovered"] / results["scenarios_tested"] * 100) if results["scenarios_tested"] > 0 else 0,
                "avg_recovery_time": avg_recovery_time
            },
            "passed": results["recovered"] / results["scenarios_tested"] >= 0.8,
            "issues": []
        }
    
    async def test_cascade_failures(self) -> Dict[str, Any]:
        """Test: Cascade failure prevention"""
        scenario_name = "cascade_failures"
        
        # Simulate component failures
        failure_scenarios = [
            {"component": "database", "messages": ["Revisa mi historial", "Muestra mis datos", "Analiza mi progreso"]},
            {"component": "cache", "messages": ["Dame info rápida", "Repite mi última consulta", "Cache test"]},
            {"component": "external_api", "messages": ["Conecta con mi wearable", "Sincroniza datos externos", "API test"]}
        ]
        
        results = {
            "component_failures": [],
            "isolated_failures": 0,
            "cascade_prevented": 0
        }
        
        for scenario in failure_scenarios:
            component_result = {
                "component": scenario["component"],
                "requests_sent": len(scenario["messages"]),
                "successful": 0,
                "failed": 0,
                "other_components_affected": False
            }
            
            # Send messages that would use the "failed" component
            for message in scenario["messages"]:
                try:
                    request = ChatRequest(
                        text=message,
                        user_id="cascade_test_user",
                        session_id=f"cascade_test_{scenario['component']}",
                        context={"simulate_failure": scenario["component"]}
                    )
                    
                    response = await self.orchestrator.process_message(request)
                    
                    if response and response.response:
                        component_result["successful"] += 1
                    else:
                        component_result["failed"] += 1
                        
                except Exception:
                    component_result["failed"] += 1
            
            # Test if other components still work
            test_request = ChatRequest(
                text="Hola, dame un consejo de motivación",
                user_id="cascade_test_user",
                session_id="cascade_test_other"
            )
            
            try:
                other_response = await self.orchestrator.process_message(test_request)
                if other_response and other_response.response:
                    results["cascade_prevented"] += 1
                else:
                    component_result["other_components_affected"] = True
            except Exception:
                component_result["other_components_affected"] = True
            
            results["component_failures"].append(component_result)
            
            if component_result["failed"] > 0 and not component_result["other_components_affected"]:
                results["isolated_failures"] += 1
        
        return {
            "scenario": scenario_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "components_tested": len(failure_scenarios),
                "isolated_failures": results["isolated_failures"],
                "cascades_prevented": results["cascade_prevented"],
                "isolation_rate": (results["isolated_failures"] / len(failure_scenarios) * 100) if len(failure_scenarios) > 0 else 0
            },
            "passed": results["isolated_failures"] == len(failure_scenarios),
            "component_results": results["component_failures"]
        }
    
    async def test_resource_exhaustion(self) -> Dict[str, Any]:
        """Test: Resource exhaustion handling"""
        scenario_name = "resource_exhaustion"
        
        # Test CPU-intensive requests
        cpu_intensive_messages = [
            "Analiza todas las posibles combinaciones de ejercicios para un plan de 6 meses",
            "Calcula las calorías exactas para cada comida de los próximos 365 días",
            "Genera 100 variaciones diferentes de mi rutina de entrenamiento"
        ]
        
        results = {
            "cpu_tests": [],
            "memory_tests": [],
            "handled_gracefully": True
        }
        
        # CPU exhaustion test
        for message in cpu_intensive_messages:
            try:
                start = datetime.now(timezone.utc)
                request = ChatRequest(
                    text=message,
                    user_id="resource_test_user",
                    session_id="resource_cpu_test"
                )
                
                response = await self.orchestrator.process_message(request)
                end = datetime.now(timezone.utc)
                
                duration = (end - start).total_seconds()
                
                results["cpu_tests"].append({
                    "message": message[:50] + "...",
                    "duration": duration,
                    "success": True,
                    "timed_out": duration > 30
                })
                
                if duration > 60:  # Excessive processing time
                    results["handled_gracefully"] = False
                    
            except Exception as e:
                results["cpu_tests"].append({
                    "message": message[:50] + "...",
                    "success": False,
                    "error": str(e)
                })
        
        # Memory exhaustion test (large data processing)
        memory_message = "Procesa esta información: " + "datos " * 10000
        
        try:
            request = ChatRequest(
                text=memory_message,
                user_id="resource_test_user",
                session_id="resource_memory_test"
            )
            
            response = await self.orchestrator.process_message(request)
            
            results["memory_tests"].append({
                "test": "large_data_processing",
                "success": True,
                "handled": len(response.response) < 10000  # Should not echo large data
            })
            
        except Exception as e:
            if "memory" in str(e).lower() or "resource" in str(e).lower():
                results["memory_tests"].append({
                    "test": "large_data_processing",
                    "success": False,
                    "handled": True  # Properly rejected
                })
            else:
                results["handled_gracefully"] = False
        
        return {
            "scenario": scenario_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu_tests": results["cpu_tests"],
            "memory_tests": results["memory_tests"],
            "passed": results["handled_gracefully"],
            "issues": []
        }
    
    async def test_network_latency(self) -> Dict[str, Any]:
        """Test: High network latency simulation"""
        scenario_name = "network_latency"
        
        # Simulate various latency conditions
        latency_scenarios = [
            {"delay": 0.1, "name": "low_latency"},
            {"delay": 1.0, "name": "moderate_latency"},
            {"delay": 5.0, "name": "high_latency"}
        ]
        
        results = {
            "latency_tests": []
        }
        
        for scenario in latency_scenarios:
            test_result = {
                "scenario": scenario["name"],
                "simulated_delay": scenario["delay"],
                "actual_response_times": [],
                "timeouts": 0,
                "successful": 0
            }
            
            for i in range(5):  # 5 requests per latency level
                try:
                    # Add artificial delay
                    await asyncio.sleep(scenario["delay"])
                    
                    request = ChatRequest(
                        text=f"Test mensaje con latencia {i}",
                        user_id="latency_test_user",
                        session_id=f"latency_test_{scenario['name']}"
                    )
                    
                    start = datetime.now(timezone.utc)
                    response = await self.orchestrator.process_message(request)
                    end = datetime.now(timezone.utc)
                    
                    response_time = (end - start).total_seconds()
                    test_result["actual_response_times"].append(response_time)
                    test_result["successful"] += 1
                    
                except asyncio.TimeoutError:
                    test_result["timeouts"] += 1
                except Exception:
                    pass
            
            avg_response_time = sum(test_result["actual_response_times"]) / len(test_result["actual_response_times"]) if test_result["actual_response_times"] else 0
            test_result["avg_response_time"] = avg_response_time
            
            results["latency_tests"].append(test_result)
        
        # Check if system handles latency gracefully
        all_successful = all(test["successful"] >= 4 for test in results["latency_tests"])  # 80% success
        no_excessive_timeouts = all(test["timeouts"] <= 1 for test in results["latency_tests"])
        
        return {
            "scenario": scenario_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "latency_tests": results["latency_tests"],
            "passed": all_successful and no_excessive_timeouts,
            "issues": []
        }
    
    async def test_data_consistency_under_load(self) -> Dict[str, Any]:
        """Test: Data consistency with concurrent updates"""
        scenario_name = "data_consistency_under_load"
        
        user_id = "consistency_test_user"
        
        # Initial setup
        setup_request = ChatRequest(
            text="Mi peso inicial es 80kg",
            user_id=user_id,
            session_id="consistency_setup"
        )
        await self.orchestrator.process_message(setup_request)
        
        # Concurrent updates
        async def update_weight(new_weight: int, session_num: int):
            try:
                request = ChatRequest(
                    text=f"Actualiza mi peso a {new_weight}kg",
                    user_id=user_id,
                    session_id=f"consistency_update_{session_num}"
                )
                
                response = await self.orchestrator.process_message(request)
                return {"success": True, "weight": new_weight}
                
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        # Send 10 concurrent weight updates
        weights = list(range(75, 85))
        tasks = [update_weight(weight, i) for i, weight in enumerate(weights)]
        update_results = await asyncio.gather(*tasks)
        
        # Verify final state
        verify_request = ChatRequest(
            text="¿Cuál es mi peso actual?",
            user_id=user_id,
            session_id="consistency_verify"
        )
        
        verify_response = await self.orchestrator.process_message(verify_request)
        
        # Extract weight from response (simplified)
        import re
        weight_match = re.search(r'(\d+)\s*kg', verify_response.response.lower())
        final_weight = int(weight_match.group(1)) if weight_match else None
        
        # Check if final weight is one of the updates
        valid_final_weight = final_weight in weights if final_weight else False
        
        return {
            "scenario": scenario_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "concurrent_updates": len(weights),
                "successful_updates": sum(1 for r in update_results if r["success"]),
                "final_weight": final_weight,
                "valid_final_state": valid_final_weight
            },
            "passed": valid_final_weight,
            "issues": []
        }
    
    async def test_graceful_degradation(self) -> Dict[str, Any]:
        """Test: Graceful degradation under extreme load"""
        scenario_name = "graceful_degradation"
        
        # Progressively increase load
        load_levels = [
            {"users": 10, "messages": 5, "name": "normal_load"},
            {"users": 50, "messages": 5, "name": "high_load"},
            {"users": 100, "messages": 5, "name": "extreme_load"},
            {"users": 200, "messages": 3, "name": "overload"}
        ]
        
        results = {
            "load_tests": [],
            "degradation_pattern": "unknown"
        }
        
        for level in load_levels:
            level_start = datetime.now(timezone.utc)
            
            # Run load test for this level
            async def user_session(user_num: int):
                session_results = {
                    "successful": 0,
                    "failed": 0,
                    "degraded": 0,
                    "response_times": []
                }
                
                for msg_num in range(level["messages"]):
                    try:
                        request = ChatRequest(
                            text=f"Usuario {user_num} mensaje {msg_num}",
                            user_id=f"load_user_{user_num}",
                            session_id=f"load_session_{level['name']}_{user_num}"
                        )
                        
                        start = datetime.now(timezone.utc)
                        response = await self.orchestrator.process_message(request)
                        end = datetime.now(timezone.utc)
                        
                        response_time = (end - start).total_seconds()
                        session_results["response_times"].append(response_time)
                        
                        # Check for degraded service
                        if "sistema ocupado" in response.response.lower() or "intente más tarde" in response.response.lower():
                            session_results["degraded"] += 1
                        else:
                            session_results["successful"] += 1
                            
                    except Exception:
                        session_results["failed"] += 1
                
                return session_results
            
            # Run concurrent users
            tasks = [user_session(i) for i in range(level["users"])]
            user_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Aggregate results
            total_successful = 0
            total_failed = 0
            total_degraded = 0
            all_response_times = []
            
            for result in user_results:
                if isinstance(result, Exception):
                    total_failed += level["messages"]
                else:
                    total_successful += result["successful"]
                    total_failed += result["failed"]
                    total_degraded += result["degraded"]
                    all_response_times.extend(result["response_times"])
            
            level_end = datetime.now(timezone.utc)
            
            level_result = {
                "load_level": level["name"],
                "users": level["users"],
                "total_requests": level["users"] * level["messages"],
                "successful": total_successful,
                "failed": total_failed,
                "degraded": total_degraded,
                "avg_response_time": sum(all_response_times) / len(all_response_times) if all_response_times else 0,
                "duration": (level_end - level_start).total_seconds()
            }
            
            results["load_tests"].append(level_result)
            
            # Brief pause between load levels
            await asyncio.sleep(5)
        
        # Analyze degradation pattern
        if results["load_tests"][-1]["failed"] > results["load_tests"][-1]["successful"]:
            results["degradation_pattern"] = "catastrophic_failure"
        elif results["load_tests"][-1]["degraded"] > results["load_tests"][-1]["successful"]:
            results["degradation_pattern"] = "graceful_degradation"
        else:
            results["degradation_pattern"] = "resilient"
        
        return {
            "scenario": scenario_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "load_tests": results["load_tests"],
            "degradation_pattern": results["degradation_pattern"],
            "passed": results["degradation_pattern"] in ["graceful_degradation", "resilient"],
            "issues": []
        }
    
    # Helper methods
    
    def _evaluate_response_quality(self, response: ChatResponse) -> float:
        """Evaluate response quality on a scale of 0-1"""
        score = 1.0
        
        # Check response length
        if len(response.response) < 10:
            score -= 0.3
        elif len(response.response) > 2000:
            score -= 0.1
            
        # Check for error indicators
        error_indicators = ["error", "problema", "no puedo", "intente más tarde"]
        for indicator in error_indicators:
            if indicator in response.response.lower():
                score -= 0.2
                
        # Check for helpful content
        helpful_indicators = ["puedes", "recomiendo", "sugiero", "importante"]
        for indicator in helpful_indicators:
            if indicator in response.response.lower():
                score += 0.1
                
        return max(0, min(1, score))
    
    def _check_context_coherence(self, response: ChatResponse, expected_topic: str) -> bool:
        """Check if response maintains context coherence"""
        topic_keywords = {
            "Evaluación inicial": ["edad", "peso", "objetivo", "experiencia"],
            "Plan de entrenamiento": ["ejercicio", "rutina", "series", "repeticiones"],
            "Nutrición": ["calorías", "proteína", "dieta", "comida"],
            "Temas avanzados": ["suplemento", "sueño", "recuperación", "motivación"]
        }
        
        keywords = topic_keywords.get(expected_topic, [])
        response_lower = response.response.lower()
        
        # Check if at least one keyword is present
        return any(keyword in response_lower for keyword in keywords)
    
    def _evaluate_context_coherence_score(self, response: ChatResponse, message_index: int) -> float:
        """Evaluate how well the response maintains context coherence"""
        score = 1.0
        
        # Later messages should reference earlier context
        if message_index > 5:
            context_indicators = ["como mencionaste", "anteriormente", "basándome en", "tu historial"]
            if not any(indicator in response.response.lower() for indicator in context_indicators):
                score -= 0.3
                
        # Check for generic responses (bad for context-heavy conversations)
        generic_phrases = ["en general", "normalmente", "la mayoría de las personas"]
        generic_count = sum(1 for phrase in generic_phrases if phrase in response.response.lower())
        score -= generic_count * 0.1
        
        return max(0, min(1, score))
    
    async def _test_rate_limit_case(self, num_requests: int, duration: int, case_name: str) -> Dict[str, Any]:
        """Test a specific rate limit case"""
        results = {
            "case_name": case_name,
            "requests_sent": 0,
            "requests_accepted": 0,
            "rate_limited": 0,
            "errors": [],
            "handled_gracefully": True
        }
        
        start_time = datetime.now(timezone.utc)
        
        # Calculate request interval
        interval = duration / num_requests if num_requests > 0 else 1
        
        for i in range(num_requests):
            try:
                request = ChatRequest(
                    text=f"Rate limit test {i}",
                    user_id="rate_limit_test_user",
                    session_id=f"rate_limit_{case_name}"
                )
                
                response = await self.orchestrator.process_message(request)
                results["requests_sent"] += 1
                results["requests_accepted"] += 1
                
            except Exception as e:
                error_str = str(e).lower()
                if "rate limit" in error_str or "too many requests" in error_str:
                    results["rate_limited"] += 1
                else:
                    results["errors"].append(str(e))
                    results["handled_gracefully"] = False
            
            # Wait for interval (except for last request)
            if i < num_requests - 1:
                await asyncio.sleep(interval)
        
        end_time = datetime.now(timezone.utc)
        actual_duration = (end_time - start_time).total_seconds()
        
        results["actual_duration"] = actual_duration
        results["actual_rate"] = results["requests_sent"] / actual_duration if actual_duration > 0 else 0
        
        return results