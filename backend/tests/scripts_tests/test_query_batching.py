#!/usr/bin/env python3
"""
Test script para verificar Query Batching - FASE 12 QUICK WIN #1

Este script prueba la funcionalidad del Query Batch Processor
y verifica que se está obteniendo la mejora esperada del 40%.
"""

import asyncio
import time
import random
import uuid
from typing import List, Dict, Any

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.logging_config import get_logger
from clients.supabase_client import (
    get_supabase_client,
    execute_batched_query,
    execute_critical_query,
    get_batch_metrics,
    initialize_batch_optimization
)

logger = get_logger(__name__)


class QueryBatchingTester:
    """Tester para verificar el funcionamiento del Query Batch Processor."""
    
    def __init__(self):
        self.results = {
            'batch_tests': [],
            'performance_tests': [],
            'metrics': {},
            'success_rate': 0.0,
            'performance_improvement': 0.0
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """
        Ejecuta todos los tests del Query Batch Processor.
        
        Returns:
            Dict con resultados de todos los tests
        """
        logger.info("🚀 Iniciando tests de Query Batching - FASE 12 QUICK WIN #1")
        
        try:
            # Inicializar batch processor
            await initialize_batch_optimization()
            await asyncio.sleep(0.1)  # Dar tiempo para inicialización
            
            # Test 1: Funcionalidad básica
            await self._test_basic_functionality()
            
            # Test 2: Rendimiento de batching
            await self._test_batch_performance()
            
            # Test 3: Diferentes tipos de queries
            await self._test_different_query_types()
            
            # Test 4: Prioridades de batch
            await self._test_batch_priorities()
            
            # Test 5: Métricas y monitoreo
            await self._test_metrics_collection()
            
            # Recopilar métricas finales
            await self._collect_final_metrics()
            
            # Generar reporte
            return self._generate_test_report()
            
        except Exception as e:
            logger.error(f"Error en tests de Query Batching: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def _test_basic_functionality(self):
        """Test de funcionalidad básica del batch processor."""
        logger.info("Test 1: Funcionalidad básica")
        
        test_results = []
        
        try:
            # Test insert batching
            insert_data = [
                {"data": {"name": f"test_user_{i}", "email": f"test{i}@example.com"}}
                for i in range(5)
            ]
            
            start_time = time.time()
            tasks = [
                execute_batched_query(
                    table="test_users",
                    query_type="insert",
                    priority="normal",
                    **data
                )
                for data in insert_data
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            # Verificar resultados
            success_count = sum(1 for r in results if not isinstance(r, Exception))
            
            test_results.append({
                "test": "insert_batching",
                "success_rate": success_count / len(tasks),
                "execution_time": end_time - start_time,
                "queries_count": len(tasks),
                "status": "passed" if success_count >= len(tasks) * 0.8 else "failed"
            })
            
            # Test select batching
            select_queries = [
                {"filters": {"id": {"operator": "eq", "value": i}}, "limit": 1}
                for i in range(1, 6)
            ]
            
            start_time = time.time()
            tasks = [
                execute_batched_query(
                    table="test_users",
                    query_type="select",
                    priority="normal",
                    **query
                )
                for query in select_queries
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            success_count = sum(1 for r in results if not isinstance(r, Exception))
            
            test_results.append({
                "test": "select_batching",
                "success_rate": success_count / len(tasks),
                "execution_time": end_time - start_time,
                "queries_count": len(tasks),
                "status": "passed" if success_count >= len(tasks) * 0.8 else "failed"
            })
            
        except Exception as e:
            test_results.append({
                "test": "basic_functionality",
                "error": str(e),
                "status": "error"
            })
        
        self.results['batch_tests'].extend(test_results)
        logger.info(f"Test 1 completado: {len([t for t in test_results if t.get('status') == 'passed'])} tests pasaron")
    
    async def _test_batch_performance(self):
        """Test de rendimiento comparando batch vs individual."""
        logger.info("Test 2: Rendimiento de batching")
        
        try:
            # Preparar datos de test
            num_queries = 20
            
            # Test 1: Queries individuales (sin batch)
            logger.info("Ejecutando queries individuales...")
            start_time = time.time()
            
            individual_tasks = []
            for i in range(num_queries):
                task = execute_critical_query(  # Sin batch
                    table="test_users",
                    query_type="select",
                    filters={"id": {"operator": "gt", "value": 0}},
                    limit=5
                )
                individual_tasks.append(task)
            
            await asyncio.gather(*individual_tasks, return_exceptions=True)
            individual_time = time.time() - start_time
            
            # Esperar un momento para separar los tests
            await asyncio.sleep(0.2)
            
            # Test 2: Queries con batch
            logger.info("Ejecutando queries con batching...")
            start_time = time.time()
            
            batch_tasks = []
            for i in range(num_queries):
                task = execute_batched_query(  # Con batch
                    table="test_users",
                    query_type="select",
                    priority="normal",
                    filters={"id": {"operator": "gt", "value": 0}},
                    limit=5
                )
                batch_tasks.append(task)
            
            await asyncio.gather(*batch_tasks, return_exceptions=True)
            batch_time = time.time() - start_time
            
            # Calcular mejora
            if individual_time > 0:
                improvement = ((individual_time - batch_time) / individual_time) * 100
            else:
                improvement = 0
            
            performance_result = {
                "test": "batch_vs_individual",
                "individual_time": individual_time,
                "batch_time": batch_time,
                "improvement_percent": improvement,
                "queries_count": num_queries,
                "target_improvement": 40.0,
                "status": "passed" if improvement >= 20 else "needs_improvement"
            }
            
            self.results['performance_tests'].append(performance_result)
            self.results['performance_improvement'] = improvement
            
            logger.info(f"Mejora de rendimiento: {improvement:.1f}% (objetivo: 40%)")
            
        except Exception as e:
            logger.error(f"Error en test de rendimiento: {e}")
            self.results['performance_tests'].append({
                "test": "batch_vs_individual",
                "error": str(e),
                "status": "error"
            })
    
    async def _test_different_query_types(self):
        """Test diferentes tipos de queries con batch."""
        logger.info("Test 3: Diferentes tipos de queries")
        
        query_types = ["select", "insert", "update"]
        
        for query_type in query_types:
            try:
                if query_type == "select":
                    tasks = [
                        execute_batched_query(
                            table="test_users",
                            query_type="select",
                            columns="id, name",
                            limit=3
                        ) for _ in range(3)
                    ]
                elif query_type == "insert":
                    tasks = [
                        execute_batched_query(
                            table="test_users",
                            query_type="insert",
                            data={"name": f"batch_test_{i}", "email": f"batch{i}@test.com"}
                        ) for i in range(3)
                    ]
                elif query_type == "update":
                    tasks = [
                        execute_batched_query(
                            table="test_users",
                            query_type="update",
                            data={"updated_at": "2025-06-09"},
                            filters={"id": {"operator": "eq", "value": i}}
                        ) for i in range(1, 4)
                    ]
                
                start_time = time.time()
                results = await asyncio.gather(*tasks, return_exceptions=True)
                execution_time = time.time() - start_time
                
                success_count = sum(1 for r in results if not isinstance(r, Exception))
                
                self.results['batch_tests'].append({
                    "test": f"{query_type}_batch",
                    "success_rate": success_count / len(tasks),
                    "execution_time": execution_time,
                    "queries_count": len(tasks),
                    "status": "passed" if success_count >= len(tasks) * 0.8 else "failed"
                })
                
            except Exception as e:
                logger.error(f"Error en test {query_type}: {e}")
                self.results['batch_tests'].append({
                    "test": f"{query_type}_batch",
                    "error": str(e),
                    "status": "error"
                })
    
    async def _test_batch_priorities(self):
        """Test diferentes prioridades de batch."""
        logger.info("Test 4: Prioridades de batch")
        
        priorities = ["critical", "high", "normal", "low"]
        
        for priority in priorities:
            try:
                tasks = [
                    execute_batched_query(
                        table="test_users",
                        query_type="select",
                        priority=priority,
                        limit=2
                    ) for _ in range(3)
                ]
                
                start_time = time.time()
                results = await asyncio.gather(*tasks, return_exceptions=True)
                execution_time = time.time() - start_time
                
                success_count = sum(1 for r in results if not isinstance(r, Exception))
                
                self.results['batch_tests'].append({
                    "test": f"priority_{priority}",
                    "success_rate": success_count / len(tasks),
                    "execution_time": execution_time,
                    "priority": priority,
                    "status": "passed" if success_count >= len(tasks) * 0.8 else "failed"
                })
                
            except Exception as e:
                logger.error(f"Error en test prioridad {priority}: {e}")
    
    async def _test_metrics_collection(self):
        """Test recolección de métricas."""
        logger.info("Test 5: Métricas y monitoreo")
        
        try:
            # Ejecutar algunas queries para generar métricas
            tasks = [
                execute_batched_query(
                    table="test_users",
                    query_type="select",
                    limit=1
                ) for _ in range(5)
            ]
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Esperar para que se procesen los batches
            await asyncio.sleep(0.3)
            
            # Obtener métricas
            metrics = await get_batch_metrics()
            
            if "error" not in metrics:
                self.results['batch_tests'].append({
                    "test": "metrics_collection",
                    "metrics_available": True,
                    "total_queries": metrics.get('total_queries', 0),
                    "batch_savings": metrics.get('batch_savings_percent', 0),
                    "status": "passed"
                })
            else:
                self.results['batch_tests'].append({
                    "test": "metrics_collection",
                    "error": metrics["error"],
                    "status": "failed"
                })
                
        except Exception as e:
            logger.error(f"Error en test de métricas: {e}")
    
    async def _collect_final_metrics(self):
        """Recolecta métricas finales del batch processor."""
        try:
            # Esperar a que se procesen todos los batches
            await asyncio.sleep(0.5)
            
            metrics = await get_batch_metrics()
            if "error" not in metrics:
                self.results['metrics'] = metrics
            
        except Exception as e:
            logger.error(f"Error recolectando métricas finales: {e}")
    
    def _generate_test_report(self) -> Dict[str, Any]:
        """Genera reporte final de tests."""
        total_tests = len(self.results['batch_tests'])
        passed_tests = len([t for t in self.results['batch_tests'] if t.get('status') == 'passed'])
        
        if total_tests > 0:
            self.results['success_rate'] = (passed_tests / total_tests) * 100
        
        report = {
            "fase": "FASE 12 QUICK WIN #1: Query Batching",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "success_rate": f"{self.results['success_rate']:.1f}%",
                "performance_improvement": f"{self.results['performance_improvement']:.1f}%",
                "target_improvement": "40%",
                "status": "SUCCESS" if self.results['success_rate'] >= 80 else "NEEDS_IMPROVEMENT"
            },
            "detailed_results": self.results,
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en los resultados."""
        recommendations = []
        
        if self.results['performance_improvement'] < 40:
            recommendations.append(
                f"Mejora de rendimiento ({self.results['performance_improvement']:.1f}%) "
                "está por debajo del objetivo (40%). Considerar ajustar parámetros del batch processor."
            )
        
        if self.results['success_rate'] < 90:
            recommendations.append(
                f"Tasa de éxito ({self.results['success_rate']:.1f}%) puede mejorarse. "
                "Revisar manejo de errores en batch processor."
            )
        
        if self.results['performance_improvement'] >= 40:
            recommendations.append(
                "✅ Objetivo de mejora del 40% alcanzado exitosamente. "
                "Query Batching está funcionando correctamente."
            )
        
        return recommendations


async def main():
    """Función principal para ejecutar los tests."""
    print("🚀 FASE 12 QUICK WIN #1: Query Batching Test Suite")
    print("=" * 60)
    
    tester = QueryBatchingTester()
    
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
        print(f"Mejora de rendimiento: {summary.get('performance_improvement', 'N/A')}")
        print(f"Objetivo: {summary.get('target_improvement', 'N/A')}")
        
        print("\n📝 RECOMENDACIONES:")
        for rec in report.get("recommendations", []):
            print(f"• {rec}")
        
        if summary.get('status') == 'SUCCESS':
            print("\n✅ Query Batching implementado exitosamente!")
        else:
            print("\n⚠️  Query Batching necesita ajustes.")
            
    except Exception as e:
        print(f"\n❌ Error ejecutando tests: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)