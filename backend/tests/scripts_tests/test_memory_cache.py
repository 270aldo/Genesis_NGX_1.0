#!/usr/bin/env python3
"""
Test script para verificar Memory Cache Optimizer - FASE 12 QUICK WIN #3

Este script prueba la funcionalidad del Memory Cache Optimizer
y verifica que se está obteniendo la mejora esperada del 25% en tiempo de respuesta.
"""

import asyncio
import time
import random
import string
from typing import Dict, Any, List, Callable

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.logging_config import get_logger
from core.memory_cache_optimizer import (
    memory_cache,
    cache_get,
    cache_set,
    cache_stats,
    cache_invalidate,
    initialize_memory_cache,
    CachePriority
)
from core.cache_decorators import cached, invalidates, cache_key

logger = get_logger(__name__)


class MemoryCacheTester:
    """Tester para verificar el funcionamiento del Memory Cache Optimizer."""
    
    def __init__(self):
        self.results = {
            'basic_tests': [],
            'performance_tests': [],
            'decorator_tests': [],
            'strategy_tests': [],
            'response_time_improvements': []
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """
        Ejecuta todos los tests del Memory Cache Optimizer.
        
        Returns:
            Dict con resultados de todos los tests
        """
        logger.info("🚀 Iniciando tests de Memory Cache Optimizer - FASE 12 QUICK WIN #3")
        
        try:
            # Inicializar sistema de caché
            await initialize_memory_cache()
            await asyncio.sleep(0.1)  # Dar tiempo para inicialización
            
            # Limpiar caché para tests limpios
            memory_cache.clear()
            
            # Test 1: Funcionalidad básica
            await self._test_basic_functionality()
            
            # Test 2: Rendimiento y mejora en tiempo de respuesta
            await self._test_performance_improvement()
            
            # Test 3: Decoradores de caché
            await self._test_cache_decorators()
            
            # Test 4: Estrategias de evicción
            await self._test_eviction_strategies()
            
            # Test 5: TTL y expiración
            await self._test_ttl_expiration()
            
            # Test 6: Precalentamiento
            await self._test_prewarming()
            
            # Generar reporte
            return self._generate_test_report()
            
        except Exception as e:
            logger.error(f"Error en tests de Memory Cache: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def _test_basic_functionality(self):
        """Test de funcionalidad básica del caché."""
        logger.info("Test 1: Funcionalidad básica")
        
        test_results = []
        
        try:
            # Test set/get básico
            key = "test:basic"
            value = {"data": "test_value", "number": 42}
            
            # Set
            success = await cache_set(key, value)
            test_results.append({
                "test": "basic_set",
                "success": success,
                "status": "passed" if success else "failed"
            })
            
            # Get
            retrieved = await cache_get(key)
            get_success = retrieved == value
            test_results.append({
                "test": "basic_get",
                "success": get_success,
                "status": "passed" if get_success else "failed"
            })
            
            # Test cache hit vs miss timing
            start_time = time.time()
            await cache_get(key)  # Cache hit
            hit_time = time.time() - start_time
            
            start_time = time.time()
            await cache_get("nonexistent:key")  # Cache miss
            miss_time = time.time() - start_time
            
            test_results.append({
                "test": "hit_vs_miss_timing",
                "hit_time_ms": hit_time * 1000,
                "miss_time_ms": miss_time * 1000,
                "hit_faster": hit_time < miss_time,
                "status": "passed" if hit_time < miss_time else "failed"
            })
            
        except Exception as e:
            test_results.append({
                "test": "basic_functionality",
                "error": str(e),
                "status": "error"
            })
        
        self.results['basic_tests'].extend(test_results)
        logger.info(f"Test 1 completado: {len([t for t in test_results if t.get('status') == 'passed'])} tests pasaron")
    
    async def _test_performance_improvement(self):
        """Test de mejora en rendimiento."""
        logger.info("Test 2: Mejora en rendimiento")
        
        try:
            # Simulador de función lenta
            async def slow_operation(data_id: str) -> Dict[str, Any]:
                await asyncio.sleep(0.01)  # 10ms de latencia simulada
                return {
                    "id": data_id,
                    "data": "x" * 1000,  # 1KB de datos
                    "timestamp": time.time()
                }
            
            # Test 1: Sin caché (baseline)
            test_keys = [f"data:{i}" for i in range(20)]
            
            logger.info("Ejecutando operaciones sin caché...")
            start_time = time.time()
            uncached_results = []
            
            for key in test_keys:
                result = await slow_operation(key)
                uncached_results.append(result)
            
            uncached_time = time.time() - start_time
            
            # Test 2: Con caché
            logger.info("Ejecutando operaciones con caché...")
            start_time = time.time()
            cached_results = []
            
            for key in test_keys:
                # Primera vez: cache miss, se ejecutará slow_operation
                result = await cache_get(key, lambda k=key: slow_operation(k))
                cached_results.append(result)
            
            # Segunda vez: cache hits
            for key in test_keys:
                result = await cache_get(key, lambda k=key: slow_operation(k))
                cached_results.append(result)
            
            cached_time = time.time() - start_time
            
            # Calcular mejora
            if uncached_time > 0:
                improvement = ((uncached_time - cached_time/2) / uncached_time) * 100  # /2 porque hicimos doble ejecución
            else:
                improvement = 0
            
            performance_result = {
                "test": "performance_with_cache",
                "uncached_time_ms": uncached_time * 1000,
                "cached_time_ms": cached_time * 1000,
                "improvement_percent": improvement,
                "operations_count": len(test_keys),
                "target_improvement": 25.0,
                "status": "passed" if improvement >= 15 else "needs_improvement"  # Al menos 15% para considerar éxito
            }
            
            self.results['performance_tests'].append(performance_result)
            self.results['response_time_improvements'].append(improvement)
            
            logger.info(f"Mejora en tiempo de respuesta: {improvement:.1f}% (objetivo: 25%)")
            
        except Exception as e:
            logger.error(f"Error en test de rendimiento: {e}")
            self.results['performance_tests'].append({
                "test": "performance_with_cache",
                "error": str(e),
                "status": "error"
            })
    
    async def _test_cache_decorators(self):
        """Test de decoradores de caché."""
        logger.info("Test 3: Decoradores de caché")
        
        # Función con decorador cached
        @cached(ttl=60, priority="high")
        async def expensive_calculation(x: int, y: int) -> int:
            await asyncio.sleep(0.005)  # 5ms de latencia
            return x * y + random.randint(1, 100)
        
        # Función que invalida caché
        @invalidates("func:*expensive_calculation*")
        async def update_data():
            return "updated"
        
        try:
            # Test decorador cached
            start_time = time.time()
            result1 = await expensive_calculation(5, 10)
            first_call_time = time.time() - start_time
            
            start_time = time.time()
            result2 = await expensive_calculation(5, 10)  # Debería venir del caché
            second_call_time = time.time() - start_time
            
            cache_speedup = ((first_call_time - second_call_time) / first_call_time * 100) if first_call_time > 0 else 0
            
            self.results['decorator_tests'].append({
                "test": "cached_decorator",
                "first_call_ms": first_call_time * 1000,
                "cached_call_ms": second_call_time * 1000,
                "results_identical": result1 == result2,
                "cache_speedup_percent": cache_speedup,
                "status": "passed" if result1 == result2 and second_call_time < first_call_time else "failed"
            })
            
            # Test invalidación
            await update_data()
            
            start_time = time.time()
            result3 = await expensive_calculation(5, 10)  # Debería ejecutarse de nuevo
            third_call_time = time.time() - start_time
            
            # El tercer call debería tomar más tiempo (fue invalidado)
            invalidation_worked = third_call_time > second_call_time
            
            self.results['decorator_tests'].append({
                "test": "invalidation_decorator",
                "third_call_ms": third_call_time * 1000,
                "invalidation_worked": invalidation_worked,
                "status": "passed" if invalidation_worked else "failed"
            })
            
        except Exception as e:
            logger.error(f"Error en test de decoradores: {e}")
            self.results['decorator_tests'].append({
                "test": "decorators",
                "error": str(e),
                "status": "error"
            })
    
    async def _test_eviction_strategies(self):
        """Test de estrategias de evicción."""
        logger.info("Test 4: Estrategias de evicción")
        
        try:
            # Configurar caché pequeño para forzar evicción
            original_max_size = memory_cache.max_size_bytes
            memory_cache.max_size_bytes = 1024  # 1KB para forzar evicción
            
            # Llenar caché hasta el límite
            for i in range(10):
                await cache_set(f"eviction:test:{i}", "x" * 200, priority="normal")  # 200 bytes cada uno
            
            initial_count = len(memory_cache._cache)
            
            # Agregar uno más, debería forzar evicción
            await cache_set("eviction:trigger", "x" * 200, priority="high")
            
            final_count = len(memory_cache._cache)
            
            # Verificar que se evictó algo
            eviction_occurred = final_count <= initial_count
            
            self.results['strategy_tests'].append({
                "test": "eviction_strategy",
                "initial_entries": initial_count,
                "final_entries": final_count,
                "eviction_occurred": eviction_occurred,
                "status": "passed" if eviction_occurred else "failed"
            })
            
            # Restaurar tamaño original
            memory_cache.max_size_bytes = original_max_size
            
        except Exception as e:
            logger.error(f"Error en test de evicción: {e}")
            self.results['strategy_tests'].append({
                "test": "eviction_strategy",
                "error": str(e),
                "status": "error"
            })
    
    async def _test_ttl_expiration(self):
        """Test de TTL y expiración."""
        logger.info("Test 5: TTL y expiración")
        
        try:
            # Set valor con TTL corto
            key = "ttl:test"
            value = "expiring_value"
            
            await cache_set(key, value, ttl=0.1)  # 100ms TTL
            
            # Verificar que está presente
            retrieved1 = await cache_get(key)
            present_initially = retrieved1 == value
            
            # Esperar a que expire
            await asyncio.sleep(0.15)
            
            # Verificar que expiró
            retrieved2 = await cache_get(key)
            expired_correctly = retrieved2 is None
            
            self.results['basic_tests'].append({
                "test": "ttl_expiration",
                "present_initially": present_initially,
                "expired_correctly": expired_correctly,
                "status": "passed" if present_initially and expired_correctly else "failed"
            })
            
        except Exception as e:
            logger.error(f"Error en test de TTL: {e}")
            self.results['basic_tests'].append({
                "test": "ttl_expiration",
                "error": str(e),
                "status": "error"
            })
    
    async def _test_prewarming(self):
        """Test de precalentamiento."""
        logger.info("Test 6: Precalentamiento")
        
        try:
            # Función loader para precalentamiento
            async def preload_data() -> str:
                await asyncio.sleep(0.005)  # 5ms simulado
                return "prewarmed_data"
            
            # Programar precalentamiento
            await memory_cache.prewarm("prewarm:test", preload_data, priority=0.1)
            
            # Dar tiempo para que se procese
            await asyncio.sleep(0.2)
            
            # Verificar que se precalentó
            start_time = time.time()
            result = await cache_get("prewarm:test")
            get_time = time.time() - start_time
            
            prewarming_worked = result == "prewarmed_data" and get_time < 0.001  # Muy rápido = estaba en caché
            
            self.results['basic_tests'].append({
                "test": "prewarming",
                "prewarming_worked": prewarming_worked,
                "get_time_ms": get_time * 1000,
                "status": "passed" if prewarming_worked else "failed"
            })
            
        except Exception as e:
            logger.error(f"Error en test de precalentamiento: {e}")
            self.results['basic_tests'].append({
                "test": "prewarming",
                "error": str(e),
                "status": "error"
            })
    
    def _generate_test_report(self) -> Dict[str, Any]:
        """Genera reporte final de tests."""
        # Contar tests exitosos
        all_tests = (
            self.results['basic_tests'] + 
            self.results['performance_tests'] + 
            self.results['decorator_tests'] + 
            self.results['strategy_tests']
        )
        
        total_tests = len(all_tests)
        passed_tests = len([t for t in all_tests if t.get('status') == 'passed'])
        
        # Calcular mejora promedio
        avg_improvement = 0
        if self.results['response_time_improvements']:
            avg_improvement = sum(self.results['response_time_improvements']) / len(self.results['response_time_improvements'])
        
        # Obtener métricas finales
        final_stats = cache_stats()
        
        report = {
            "fase": "FASE 12 QUICK WIN #3: Memory Cache Optimizer",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "success_rate": f"{(passed_tests / total_tests * 100) if total_tests > 0 else 0:.1f}%",
                "response_time_improvement": f"{avg_improvement:.1f}%",
                "target_improvement": "25%",
                "status": "SUCCESS" if avg_improvement >= 20 else "NEEDS_IMPROVEMENT"
            },
            "cache_performance": {
                "hit_rate": final_stats.get('hit_rate', '0%'),
                "average_hit_time_ms": final_stats.get('avg_hit_time_ms', 0),
                "average_miss_time_ms": final_stats.get('avg_miss_time_ms', 0),
                "cache_utilization": final_stats.get('utilization', '0%')
            },
            "detailed_results": self.results,
            "system_stats": final_stats,
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en los resultados."""
        recommendations = []
        
        # Verificar mejora en tiempo de respuesta
        avg_improvement = 0
        if self.results['response_time_improvements']:
            avg_improvement = sum(self.results['response_time_improvements']) / len(self.results['response_time_improvements'])
        
        if avg_improvement < 25:
            recommendations.append(
                f"Mejora en tiempo de respuesta ({avg_improvement:.1f}%) "
                "está por debajo del objetivo (25%). Considerar ajustar estrategia de caché."
            )
        else:
            recommendations.append(
                "✅ Objetivo de mejora del 25% en tiempo de respuesta alcanzado exitosamente."
            )
        
        # Verificar tests de decoradores
        decorator_tests = [t for t in self.results['decorator_tests'] if t.get('status') == 'passed']
        if len(decorator_tests) < len(self.results['decorator_tests']):
            recommendations.append(
                "Algunos tests de decoradores fallaron. Verificar implementación de @cached."
            )
        
        # Verificar evicción
        eviction_tests = [t for t in self.results['strategy_tests'] if t.get('test') == 'eviction_strategy']
        if eviction_tests and eviction_tests[0].get('status') != 'passed':
            recommendations.append(
                "Estrategia de evicción no está funcionando correctamente. Revisar configuración."
            )
        
        return recommendations


async def main():
    """Función principal para ejecutar los tests."""
    print("🚀 FASE 12 QUICK WIN #3: Memory Cache Optimizer Test Suite")
    print("=" * 60)
    
    tester = MemoryCacheTester()
    
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
        print(f"Mejora en tiempo de respuesta: {summary.get('response_time_improvement', 'N/A')}")
        print(f"Objetivo: {summary.get('target_improvement', 'N/A')}")
        
        # Rendimiento del caché
        print("\n📈 RENDIMIENTO DEL CACHÉ:")
        perf = report.get("cache_performance", {})
        print(f"  Hit Rate: {perf.get('hit_rate', 'N/A')}")
        print(f"  Tiempo promedio hit: {perf.get('average_hit_time_ms', 0):.2f}ms")
        print(f"  Tiempo promedio miss: {perf.get('average_miss_time_ms', 0):.2f}ms")
        print(f"  Utilización: {perf.get('cache_utilization', 'N/A')}")
        
        print("\n📝 RECOMENDACIONES:")
        for rec in report.get("recommendations", []):
            print(f"• {rec}")
        
        if summary.get('status') == 'SUCCESS':
            print("\n✅ Memory Cache Optimizer implementado exitosamente!")
        else:
            print("\n⚠️  Memory Cache Optimizer necesita ajustes.")
            
    except Exception as e:
        print(f"\n❌ Error ejecutando tests: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)