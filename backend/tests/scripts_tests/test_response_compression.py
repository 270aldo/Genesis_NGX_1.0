#!/usr/bin/env python3
"""
Test script para verificar Response Compression - FASE 12 QUICK WIN #2

Este script prueba la funcionalidad del sistema de compresión de respuestas
y verifica que se está obteniendo la mejora esperada del 60% en ancho de banda.
"""

import asyncio
import json
import time
import random
import string
from typing import Dict, Any, List

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.logging_config import get_logger
from core.response_compression import (
    response_compressor,
    CompressionType,
    compress_api_response,
    get_compression_metrics,
    estimate_bandwidth_savings
)

logger = get_logger(__name__)


class CompressionTester:
    """Tester para verificar el funcionamiento del sistema de compresión."""
    
    def __init__(self):
        self.results = {
            'compression_tests': [],
            'algorithm_tests': [],
            'performance_tests': [],
            'bandwidth_savings': [],
            'overall_savings_percent': 0.0
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """
        Ejecuta todos los tests del sistema de compresión.
        
        Returns:
            Dict con resultados de todos los tests
        """
        logger.info("🚀 Iniciando tests de Response Compression - FASE 12 QUICK WIN #2")
        
        try:
            # Test 1: Compresión básica con diferentes tamaños
            await self._test_basic_compression()
            
            # Test 2: Diferentes algoritmos de compresión
            await self._test_different_algorithms()
            
            # Test 3: Rendimiento y velocidad
            await self._test_compression_performance()
            
            # Test 4: Tipos de datos realistas
            await self._test_realistic_data()
            
            # Test 5: Cache de compresión
            await self._test_compression_cache()
            
            # Calcular ahorro total
            self._calculate_overall_savings()
            
            # Generar reporte
            return self._generate_test_report()
            
        except Exception as e:
            logger.error(f"Error en tests de Response Compression: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def _test_basic_compression(self):
        """Test de compresión básica con diferentes tamaños."""
        logger.info("Test 1: Compresión básica")
        
        test_sizes = [
            (100, "muy pequeño"),      # No se comprimirá
            (1024, "pequeño"),         # Límite mínimo
            (10240, "mediano"),        # 10KB
            (102400, "grande"),        # 100KB
            (1048576, "muy grande")    # 1MB
        ]
        
        for size, description in test_sizes:
            try:
                # Generar datos de prueba
                test_data = {
                    "data": "x" * size,
                    "metadata": {
                        "size": size,
                        "description": description
                    }
                }
                
                # Comprimir
                compressed, encoding = await compress_api_response(
                    test_data,
                    "gzip, br, zstd"
                )
                
                # Calcular ahorro
                original_size = len(json.dumps(test_data).encode('utf-8'))
                compressed_size = len(compressed)
                savings = estimate_bandwidth_savings(original_size, compressed_size)
                
                test_result = {
                    "test": f"compression_{description}",
                    "original_size": original_size,
                    "compressed_size": compressed_size,
                    "savings_percent": savings['savings_percent'],
                    "compression_ratio": savings['compression_ratio'],
                    "algorithm": encoding or "none",
                    "status": "passed" if savings['savings_percent'] > 0 or size < 1024 else "failed"
                }
                
                self.results['compression_tests'].append(test_result)
                self.results['bandwidth_savings'].append(savings['savings_percent'])
                
                logger.debug(f"Test {description}: {savings['savings_percent']:.1f}% ahorro")
                
            except Exception as e:
                logger.error(f"Error en test {description}: {e}")
                self.results['compression_tests'].append({
                    "test": f"compression_{description}",
                    "error": str(e),
                    "status": "error"
                })
    
    async def _test_different_algorithms(self):
        """Test de diferentes algoritmos de compresión."""
        logger.info("Test 2: Diferentes algoritmos")
        
        # Datos de prueba (JSON típico de API)
        test_data = {
            "users": [
                {
                    "id": i,
                    "name": f"User {i}",
                    "email": f"user{i}@example.com",
                    "profile": {
                        "bio": "Lorem ipsum dolor sit amet " * 10,
                        "interests": ["fitness", "nutrition", "wellness"]
                    }
                }
                for i in range(50)
            ]
        }
        
        algorithms = [
            (CompressionType.GZIP, "gzip"),
            (CompressionType.BROTLI, "br"),
            (CompressionType.ZSTD, "zstd")
        ]
        
        for algo_type, accept_encoding in algorithms:
            try:
                if not response_compressor._available_algorithms.get(algo_type):
                    logger.info(f"Algoritmo {algo_type.value} no disponible, saltando")
                    continue
                
                start_time = time.time()
                
                # Comprimir con algoritmo específico
                compressed_data, algorithm = response_compressor.compress_response(
                    test_data,
                    accept_encoding,
                    force_algorithm=algo_type
                )
                
                compression_time = time.time() - start_time
                
                # Calcular métricas
                original_size = len(json.dumps(test_data).encode('utf-8'))
                compressed_size = len(compressed_data)
                savings = estimate_bandwidth_savings(original_size, compressed_size)
                
                self.results['algorithm_tests'].append({
                    "algorithm": algo_type.value,
                    "original_size": original_size,
                    "compressed_size": compressed_size,
                    "savings_percent": savings['savings_percent'],
                    "compression_ratio": savings['compression_ratio'],
                    "compression_time_ms": compression_time * 1000,
                    "status": "passed"
                })
                
            except Exception as e:
                logger.error(f"Error testing {algo_type.value}: {e}")
                self.results['algorithm_tests'].append({
                    "algorithm": algo_type.value,
                    "error": str(e),
                    "status": "error"
                })
    
    async def _test_compression_performance(self):
        """Test de rendimiento de compresión."""
        logger.info("Test 3: Rendimiento de compresión")
        
        # Generar datos de diferentes tipos
        test_cases = [
            {
                "name": "JSON repetitivo",
                "data": {"items": [{"id": i, "value": "test"} for i in range(1000)]},
                "expected_savings": 70
            },
            {
                "name": "Texto largo",
                "data": {"content": " ".join(["Lorem ipsum dolor sit amet"] * 500)},
                "expected_savings": 60
            },
            {
                "name": "Datos mixtos",
                "data": {
                    "numbers": list(range(1000)),
                    "strings": [f"string_{i}" for i in range(100)],
                    "nested": [{"a": i, "b": i*2} for i in range(50)]
                },
                "expected_savings": 50
            }
        ]
        
        for test_case in test_cases:
            try:
                # Medir rendimiento
                iterations = 10
                total_time = 0
                total_savings = 0
                
                for _ in range(iterations):
                    start_time = time.time()
                    
                    compressed, encoding = await compress_api_response(
                        test_case['data'],
                        "gzip, br, zstd"
                    )
                    
                    compression_time = time.time() - start_time
                    total_time += compression_time
                    
                    # Calcular ahorro
                    original_size = len(json.dumps(test_case['data']).encode('utf-8'))
                    compressed_size = len(compressed)
                    savings = estimate_bandwidth_savings(original_size, compressed_size)
                    total_savings += savings['savings_percent']
                
                avg_time = (total_time / iterations) * 1000  # en ms
                avg_savings = total_savings / iterations
                
                self.results['performance_tests'].append({
                    "test": test_case['name'],
                    "avg_compression_time_ms": round(avg_time, 2),
                    "avg_savings_percent": round(avg_savings, 2),
                    "expected_savings": test_case['expected_savings'],
                    "performance_score": _calculate_performance_score(avg_time, avg_savings),
                    "status": "passed" if avg_savings >= test_case['expected_savings'] * 0.8 else "needs_improvement"
                })
                
            except Exception as e:
                logger.error(f"Error en test de rendimiento {test_case['name']}: {e}")
    
    async def _test_realistic_data(self):
        """Test con datos realistas de NGX Agents."""
        logger.info("Test 4: Datos realistas de API")
        
        # Simular respuestas típicas de la API
        realistic_responses = [
            {
                "name": "Lista de agentes",
                "data": {
                    "agents": [
                        {
                            "id": f"agent_{i}",
                            "name": f"Agent {i}",
                            "description": "Specialized fitness and nutrition agent " * 5,
                            "capabilities": ["fitness", "nutrition", "wellness"],
                            "status": "active"
                        }
                        for i in range(11)
                    ],
                    "metadata": {"total": 11, "page": 1}
                }
            },
            {
                "name": "Plan de entrenamiento",
                "data": {
                    "workout_plan": {
                        "week": 1,
                        "days": [
                            {
                                "day": day,
                                "exercises": [
                                    {
                                        "name": f"Exercise {j}",
                                        "sets": 3,
                                        "reps": 12,
                                        "rest": 60,
                                        "notes": "Focus on form and control " * 3
                                    }
                                    for j in range(5)
                                ]
                            }
                            for day in range(1, 8)
                        ]
                    }
                }
            },
            {
                "name": "Métricas de usuario",
                "data": {
                    "user_metrics": {
                        "daily": [{"date": f"2025-06-{i:02d}", "calories": 2000 + i*50, "steps": 8000 + i*500} for i in range(1, 31)],
                        "weekly_summary": {"avg_calories": 2500, "avg_steps": 10000},
                        "recommendations": ["Increase protein intake", "Add more cardio", "Focus on recovery"]
                    }
                }
            }
        ]
        
        for response in realistic_responses:
            try:
                compressed, encoding = await compress_api_response(
                    response['data'],
                    "gzip, br, zstd"
                )
                
                original_size = len(json.dumps(response['data']).encode('utf-8'))
                compressed_size = len(compressed)
                savings = estimate_bandwidth_savings(original_size, compressed_size)
                
                self.results['compression_tests'].append({
                    "test": f"realistic_{response['name']}",
                    "original_size": original_size,
                    "compressed_size": compressed_size,
                    "savings_percent": savings['savings_percent'],
                    "algorithm": encoding or "none",
                    "status": "passed" if savings['savings_percent'] >= 40 else "needs_improvement"
                })
                
                self.results['bandwidth_savings'].append(savings['savings_percent'])
                
            except Exception as e:
                logger.error(f"Error con datos realistas {response['name']}: {e}")
    
    async def _test_compression_cache(self):
        """Test del cache de compresión."""
        logger.info("Test 5: Cache de compresión")
        
        # Limpiar cache primero
        response_compressor.clear_cache()
        
        test_data = {"test": "cache_data", "content": "x" * 5000}
        
        # Primera compresión (cache miss)
        start_time = time.time()
        compressed1, _ = await compress_api_response(test_data, "gzip")
        first_time = time.time() - start_time
        
        # Segunda compresión (debería ser cache hit)
        start_time = time.time()
        compressed2, _ = await compress_api_response(test_data, "gzip")
        second_time = time.time() - start_time
        
        # Verificar que el cache funcionó
        cache_speedup = (first_time - second_time) / first_time * 100 if first_time > 0 else 0
        
        metrics_after = get_compression_metrics()
        
        self.results['compression_tests'].append({
            "test": "cache_performance",
            "first_compression_ms": first_time * 1000,
            "cached_compression_ms": second_time * 1000,
            "cache_speedup_percent": cache_speedup,
            "cache_hit_rate": metrics_after.get('cache_hit_rate', 0),
            "status": "passed" if cache_speedup > 50 else "needs_improvement"
        })
    
    def _calculate_overall_savings(self):
        """Calcula el ahorro promedio total."""
        if self.results['bandwidth_savings']:
            self.results['overall_savings_percent'] = sum(self.results['bandwidth_savings']) / len(self.results['bandwidth_savings'])
        else:
            self.results['overall_savings_percent'] = 0
    
    def _generate_test_report(self) -> Dict[str, Any]:
        """Genera reporte final de tests."""
        # Contar tests exitosos
        all_tests = (
            self.results['compression_tests'] + 
            self.results['algorithm_tests'] + 
            self.results['performance_tests']
        )
        
        total_tests = len(all_tests)
        passed_tests = len([t for t in all_tests if t.get('status') == 'passed'])
        
        # Obtener métricas finales
        final_metrics = get_compression_metrics()
        
        report = {
            "fase": "FASE 12 QUICK WIN #2: Response Compression",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "success_rate": f"{(passed_tests / total_tests * 100) if total_tests > 0 else 0:.1f}%",
                "bandwidth_saved": f"{self.results['overall_savings_percent']:.1f}%",
                "target_improvement": "60%",
                "status": "SUCCESS" if self.results['overall_savings_percent'] >= 50 else "NEEDS_IMPROVEMENT"
            },
            "algorithm_comparison": self._compare_algorithms(),
            "performance_summary": self._summarize_performance(),
            "detailed_results": self.results,
            "system_metrics": final_metrics,
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _compare_algorithms(self) -> Dict[str, Any]:
        """Compara el rendimiento de diferentes algoritmos."""
        if not self.results['algorithm_tests']:
            return {}
        
        comparison = {}
        for test in self.results['algorithm_tests']:
            if test.get('status') == 'passed':
                algo = test['algorithm']
                comparison[algo] = {
                    "compression_ratio": test.get('compression_ratio', 0),
                    "savings_percent": test.get('savings_percent', 0),
                    "speed_ms": test.get('compression_time_ms', 0)
                }
        
        return comparison
    
    def _summarize_performance(self) -> Dict[str, Any]:
        """Resume el rendimiento general."""
        if not self.results['performance_tests']:
            return {}
        
        avg_times = [t['avg_compression_time_ms'] for t in self.results['performance_tests'] if 'avg_compression_time_ms' in t]
        avg_savings = [t['avg_savings_percent'] for t in self.results['performance_tests'] if 'avg_savings_percent' in t]
        
        return {
            "average_compression_time_ms": sum(avg_times) / len(avg_times) if avg_times else 0,
            "average_savings_percent": sum(avg_savings) / len(avg_savings) if avg_savings else 0,
            "performance_rating": _calculate_overall_rating(avg_times, avg_savings)
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en los resultados."""
        recommendations = []
        
        if self.results['overall_savings_percent'] < 60:
            recommendations.append(
                f"Ahorro de ancho de banda ({self.results['overall_savings_percent']:.1f}%) "
                "está por debajo del objetivo (60%). Considerar habilitar algoritmos más agresivos."
            )
        else:
            recommendations.append(
                "✅ Objetivo de ahorro del 60% en ancho de banda alcanzado exitosamente."
            )
        
        # Verificar algoritmos
        algo_tests = [t for t in self.results['algorithm_tests'] if t.get('status') == 'passed']
        if len(algo_tests) < 2:
            recommendations.append(
                "Considerar instalar librerías adicionales (brotli, zstandard) para mejor compresión."
            )
        
        # Verificar cache
        cache_test = next((t for t in self.results['compression_tests'] if t.get('test') == 'cache_performance'), None)
        if cache_test and cache_test.get('cache_speedup_percent', 0) < 50:
            recommendations.append(
                "El cache de compresión puede optimizarse para mejor rendimiento."
            )
        
        return recommendations


def _calculate_performance_score(time_ms: float, savings_percent: float) -> str:
    """Calcula score de rendimiento."""
    if time_ms < 5 and savings_percent > 60:
        return "Excelente"
    elif time_ms < 10 and savings_percent > 50:
        return "Muy Bueno"
    elif time_ms < 20 and savings_percent > 40:
        return "Bueno"
    else:
        return "Necesita Mejora"


def _calculate_overall_rating(times: List[float], savings: List[float]) -> str:
    """Calcula calificación general."""
    if not times or not savings:
        return "No disponible"
    
    avg_time = sum(times) / len(times)
    avg_savings = sum(savings) / len(savings)
    
    if avg_time < 10 and avg_savings > 60:
        return "A+ (Excelente)"
    elif avg_time < 20 and avg_savings > 50:
        return "A (Muy Bueno)"
    elif avg_time < 30 and avg_savings > 40:
        return "B (Bueno)"
    else:
        return "C (Necesita Mejora)"


async def main():
    """Función principal para ejecutar los tests."""
    print("🚀 FASE 12 QUICK WIN #2: Response Compression Test Suite")
    print("=" * 60)
    
    tester = CompressionTester()
    
    try:
        report = await tester.run_all_tests()
        
        # Mostrar reporte
        print("\n📊 REPORTE DE RESULTADOS:")
        print("=" * 60)
        
        summary = report.get("summary", {})
        print(f"Fase: {report.get('fase', 'N/A')}")
        print(f"Estado: {summary.get('status', 'N/A')}")
        print(f"Tests pasados: {summary.get('passed_tests', 0)}/{summary.get('total_tests', 0)}")
        print(f"Tasa de éxito: {summary.get('success_rate', 'N/A')}")
        print(f"Ancho de banda ahorrado: {summary.get('bandwidth_saved', 'N/A')}")
        print(f"Objetivo: {summary.get('target_improvement', 'N/A')}")
        
        # Comparación de algoritmos
        print("\n🔧 COMPARACIÓN DE ALGORITMOS:")
        for algo, stats in report.get("algorithm_comparison", {}).items():
            print(f"  {algo}: {stats['savings_percent']:.1f}% ahorro, {stats['speed_ms']:.1f}ms")
        
        print("\n📝 RECOMENDACIONES:")
        for rec in report.get("recommendations", []):
            print(f"• {rec}")
        
        if summary.get('status') == 'SUCCESS':
            print("\n✅ Response Compression implementado exitosamente!")
        else:
            print("\n⚠️  Response Compression necesita ajustes.")
            
    except Exception as e:
        print(f"\n❌ Error ejecutando tests: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)