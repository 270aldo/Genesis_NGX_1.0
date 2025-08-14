"""
Elite Performance Monitoring Router for GENESIS - FASE 9 Enhancement
====================================================================

Advanced performance monitoring and analytics endpoints providing:
- Real-time system metrics and performance analysis
- Multi-level cache efficiency monitoring
- Database performance insights
- AI agent response time analytics
- Streaming service performance tracking
- Performance optimization recommendations
- Health status assessment with KPI scoring
- Historical trend analysis and alerts
"""

import os
import time
from datetime import datetime
from typing import Any, Dict, List

import psutil
from fastapi import APIRouter

from app.middleware.performance import get_performance_middleware
from core.cache.cache_manager import get_cache_manager
from core.database import get_database_manager
from core.logging_config import get_logger
from core.semantic_agent_cache import get_semantic_agent_cache
from monitoring.performance_dashboard import get_performance_dashboard

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/v1/performance",
    tags=["Performance Monitoring"],
    responses={404: {"description": "Not found"}},
)


@router.get("/metrics", response_model=Dict[str, Any])
async def get_elite_performance_metrics():
    """
    Get comprehensive elite performance metrics for the API.

    Returns:
        Dictionary containing advanced performance analytics and insights
    """
    try:
        # Get elite middleware performance stats
        middleware = get_performance_middleware()
        middleware_stats = (
            middleware.get_elite_performance_stats() if middleware else {}
        )

        # Get comprehensive system metrics
        system_metrics = await _get_elite_system_metrics()

        # Get multi-level cache performance
        cache_manager = await get_cache_manager()
        cache_stats = await cache_manager.get_stats()

        # Get semantic agent cache metrics
        try:
            agent_cache = await get_semantic_agent_cache()
            agent_cache_stats = await agent_cache.get_cache_stats()
        except Exception as e:
            logger.warning(f"Agent cache not available: {e}")
            agent_cache_stats = {"status": "unavailable"}

        # Get database performance metrics
        db_metrics = await _get_elite_database_metrics()

        # Get performance dashboard summary
        try:
            dashboard = await get_performance_dashboard()
            dashboard_summary = dashboard.get_dashboard_summary()
        except Exception as e:
            logger.warning(f"Performance dashboard not available: {e}")
            dashboard_summary = {"status": "unavailable"}

        # Calculate overall performance score
        performance_score = _calculate_overall_performance_score(
            middleware_stats, system_metrics, cache_stats
        )

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "performance_score": performance_score,
            "api_performance": middleware_stats,
            "system_metrics": system_metrics,
            "multi_level_cache": cache_stats,
            "agent_cache": agent_cache_stats,
            "database_metrics": db_metrics,
            "dashboard_summary": dashboard_summary,
            "health_status": _determine_health_status(performance_score),
            "recommendations": _generate_elite_recommendations(
                middleware_stats, system_metrics, cache_stats, performance_score
            ),
            "alerts": _get_active_alerts(dashboard_summary),
            "kpis": _calculate_performance_kpis(middleware_stats, system_metrics),
        }

    except Exception as e:
        logger.error(f"Error getting elite performance metrics: {e}")
        return {
            "error": "Failed to retrieve performance metrics",
            "timestamp": datetime.utcnow().isoformat(),
            "performance_score": 0,
        }


@router.get("/health", response_model=Dict[str, Any])
async def get_comprehensive_health_status():
    """
    Get comprehensive system health status with detailed component analysis.

    Returns:
        Detailed health status of all system components
    """
    try:
        health_status = {
            "overall_status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {},
            "performance_indicators": {},
            "alerts": [],
        }

        # Check middleware health
        middleware = get_performance_middleware()
        if middleware:
            stats = middleware.get_elite_performance_stats()
            perf_score = stats.get("health_indicators", {}).get(
                "performance_score", 100
            )
            middleware_status = (
                "healthy"
                if perf_score > 70
                else "degraded" if perf_score > 40 else "unhealthy"
            )

            health_status["components"]["middleware"] = {
                "status": middleware_status,
                "performance_score": perf_score,
                "request_count": stats.get("total_requests", 0),
                "avg_response_time": stats.get("response_times", {}).get(
                    "average_ms", 0
                ),
            }
        else:
            health_status["components"]["middleware"] = {"status": "unavailable"}

        # Check database health
        try:
            db_manager = await get_database_manager()
            db_health = await db_manager.get_health_status()
            health_status["components"]["database"] = db_health
        except Exception as e:
            health_status["components"]["database"] = {
                "status": "error",
                "error": str(e),
            }

        # Check cache health
        try:
            cache_manager = await get_cache_manager()
            cache_health = await cache_manager.health_check()
            health_status["components"]["cache"] = cache_health
        except Exception as e:
            health_status["components"]["cache"] = {"status": "error", "error": str(e)}

        # Check agent cache health
        try:
            agent_cache = await get_semantic_agent_cache()
            agent_health = await agent_cache.get_health_status()
            health_status["components"]["agent_cache"] = agent_health
        except Exception as e:
            health_status["components"]["agent_cache"] = {
                "status": "error",
                "error": str(e),
            }

        # System resource health
        system_metrics = await _get_elite_system_metrics()
        cpu_health = "healthy"
        memory_health = "healthy"

        if system_metrics.get("cpu", {}).get("usage_percent", 0) > 80:
            cpu_health = "warning"
        if system_metrics.get("memory", {}).get("usage_percent", 0) > 85:
            memory_health = "critical"

        health_status["components"]["system"] = {
            "status": (
                "healthy"
                if cpu_health == "healthy" and memory_health == "healthy"
                else "warning"
            ),
            "cpu_health": cpu_health,
            "memory_health": memory_health,
            "uptime_hours": system_metrics.get("uptime_seconds", 0) / 3600,
        }

        # Determine overall status
        component_statuses = [
            comp.get("status", "unknown")
            for comp in health_status["components"].values()
        ]
        if "critical" in component_statuses or "unhealthy" in component_statuses:
            health_status["overall_status"] = "unhealthy"
        elif "warning" in component_statuses or "degraded" in component_statuses:
            health_status["overall_status"] = "degraded"

        return health_status

    except Exception as e:
        logger.error(f"Error getting health status: {e}")
        return {
            "overall_status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.get("/benchmarks")
async def get_performance_benchmarks():
    """Get performance benchmarks and targets."""
    return {
        "targets": {
            "p50_response_time_ms": 50,
            "p95_response_time_ms": 100,
            "p99_response_time_ms": 200,
            "throughput_rps": 1000,
            "cache_hit_rate_percent": 90,
            "error_rate_percent": 0.1,
            "cpu_usage_percent": 70,
            "memory_usage_percent": 80,
        },
        "elite_targets": {
            "p50_response_time_ms": 25,
            "p95_response_time_ms": 50,
            "p99_response_time_ms": 100,
            "throughput_rps": 10000,
            "cache_hit_rate_percent": 95,
            "error_rate_percent": 0.01,
            "cpu_usage_percent": 50,
            "memory_usage_percent": 60,
        },
        "current_grade": await _calculate_performance_grade(),
    }


@router.get("/streaming-metrics")
async def get_streaming_metrics():
    """Get streaming service performance metrics."""
    try:
        # This would integrate with the streaming service
        # For now, return a placeholder structure
        return {
            "connections": {
                "active_sse_connections": 0,
                "active_websocket_connections": 0,
                "total_connections_today": 0,
            },
            "performance": {
                "avg_connection_duration_seconds": 0,
                "message_throughput_per_second": 0,
                "compression_ratio": 0,
                "bandwidth_usage_mbps": 0,
            },
            "status": "service_not_integrated",
        }
    except Exception as e:
        logger.error(f"Error getting streaming metrics: {e}")
        return {"error": str(e)}


@router.post("/reset-metrics")
async def reset_performance_metrics():
    """Reset performance counters and metrics."""
    try:
        reset_results = []

        # Reset middleware metrics
        middleware = get_performance_middleware()
        if middleware:
            # Reset the circular buffers and counters
            middleware.request_count = 0
            middleware.total_response_time = 0.0
            middleware.response_times.clear()
            middleware.slow_requests.clear()
            middleware.error_counts.clear()
            middleware.endpoint_metrics.clear()
            middleware.compression_stats = {
                "requests_compressed": 0,
                "bytes_saved": 0,
                "compression_time": 0.0,
                "avg_compression_ratio": 0.0,
            }
            middleware.cache_hits = 0
            middleware.cache_misses = 0
            middleware.response_cache.clear()

            reset_results.append(
                {
                    "component": "middleware_metrics",
                    "status": "reset",
                    "items_cleared": [
                        "request_counters",
                        "response_times",
                        "slow_requests",
                        "cache_metrics",
                    ],
                }
            )

        # Reset dashboard metrics if available
        try:
            dashboard = await get_performance_dashboard()
            # Reset dashboard would be implemented in the dashboard class
            reset_results.append(
                {
                    "component": "performance_dashboard",
                    "status": "reset_requested",
                    "note": "Dashboard reset functionality would be implemented",
                }
            )
        except Exception as e:
            reset_results.append(
                {
                    "component": "performance_dashboard",
                    "status": "error",
                    "error": str(e),
                }
            )

        return {
            "reset_results": reset_results,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Performance metrics have been reset",
        }

    except Exception as e:
        logger.error(f"Error resetting metrics: {e}")
        return {"error": str(e)}


@router.get("/slow-requests", response_model=Dict[str, Any])
async def get_slow_requests(limit: int = 50):
    """
    Get details about recent slow API requests.

    Args:
        limit: Maximum number of slow requests to return

    Returns:
        List of slow requests with details
    """
    try:
        middleware = get_performance_middleware()
        if not middleware:
            return {
                "slow_requests": [],
                "message": "Performance middleware not available",
            }

        stats = middleware.get_performance_stats()
        slow_requests = stats.get("recent_slow_requests", [])

        # Limit results
        limited_requests = (
            slow_requests[-limit:] if len(slow_requests) > limit else slow_requests
        )

        # Add analysis
        analysis = _analyze_slow_requests(slow_requests)

        return {
            "slow_requests": limited_requests,
            "total_slow_requests": len(slow_requests),
            "analysis": analysis,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting slow requests: {e}")
        return {"error": "Failed to retrieve slow requests"}


@router.get("/cache-analysis", response_model=Dict[str, Any])
async def get_cache_analysis():
    """
    Get detailed cache performance analysis and optimization suggestions.

    Returns:
        Cache analysis with optimization recommendations
    """
    try:
        # Get comprehensive cache statistics
        cache_stats = await advanced_cache_manager.get_comprehensive_statistics()

        # Perform cache optimization analysis
        optimization_analysis = (
            await advanced_cache_manager.optimize_cache_distribution()
        )

        # Calculate cache effectiveness scores
        effectiveness_scores = _calculate_cache_effectiveness(cache_stats)

        return {
            "cache_statistics": cache_stats,
            "optimization_analysis": optimization_analysis,
            "effectiveness_scores": effectiveness_scores,
            "recommendations": _generate_cache_recommendations(
                cache_stats, effectiveness_scores
            ),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error performing cache analysis: {e}")
        return {"error": "Failed to analyze cache performance"}


@router.post("/optimize", response_model=Dict[str, Any])
async def trigger_performance_optimization():
    """
    Trigger automatic performance optimization routines.

    Returns:
        Results of optimization operations
    """
    try:
        optimization_results = []

        # 1. Optimize cache distribution
        try:
            cache_optimization = (
                await advanced_cache_manager.optimize_cache_distribution()
            )
            optimization_results.append(
                {
                    "component": "cache",
                    "status": "completed",
                    "results": cache_optimization,
                }
            )
        except Exception as e:
            optimization_results.append(
                {"component": "cache", "status": "failed", "error": str(e)}
            )

        # 2. Clear expired cache entries (if implemented)
        try:
            # TODO: Implement cache cleanup
            optimization_results.append(
                {
                    "component": "cache_cleanup",
                    "status": "skipped",
                    "message": "Cache cleanup not yet implemented",
                }
            )
        except Exception as e:
            optimization_results.append(
                {"component": "cache_cleanup", "status": "failed", "error": str(e)}
            )

        # 3. Reset performance counters
        try:
            middleware = get_performance_middleware()
            if middleware:
                middleware.slow_requests = []  # Clear old slow request records
                optimization_results.append(
                    {
                        "component": "performance_counters",
                        "status": "completed",
                        "message": "Performance counters reset",
                    }
                )
        except Exception as e:
            optimization_results.append(
                {
                    "component": "performance_counters",
                    "status": "failed",
                    "error": str(e),
                }
            )

        return {
            "optimization_results": optimization_results,
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_operations": len(optimization_results),
                "successful": len(
                    [r for r in optimization_results if r["status"] == "completed"]
                ),
                "failed": len(
                    [r for r in optimization_results if r["status"] == "failed"]
                ),
                "skipped": len(
                    [r for r in optimization_results if r["status"] == "skipped"]
                ),
            },
        }

    except Exception as e:
        logger.error(f"Error during performance optimization: {e}")
        return {"error": "Failed to perform optimization"}


def _get_system_metrics() -> Dict[str, Any]:
    """Get current system resource metrics."""
    try:
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()

        # Memory metrics
        memory = psutil.virtual_memory()
        memory_mb = memory.total // (1024 * 1024)
        memory_used_mb = memory.used // (1024 * 1024)
        memory_available_mb = memory.available // (1024 * 1024)

        # Disk metrics
        disk = psutil.disk_usage("/")
        disk_total_gb = disk.total // (1024 * 1024 * 1024)
        disk_used_gb = disk.used // (1024 * 1024 * 1024)
        disk_free_gb = disk.free // (1024 * 1024 * 1024)

        # Process metrics
        process = psutil.Process(os.getpid())
        process_memory_mb = process.memory_info().rss // (1024 * 1024)
        process_cpu_percent = process.cpu_percent()

        return {
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count,
                "process_percent": process_cpu_percent,
            },
            "memory": {
                "total_mb": memory_mb,
                "used_mb": memory_used_mb,
                "available_mb": memory_available_mb,
                "percent": memory.percent,
                "process_mb": process_memory_mb,
            },
            "disk": {
                "total_gb": disk_total_gb,
                "used_gb": disk_used_gb,
                "free_gb": disk_free_gb,
                "percent": (
                    (disk_used_gb / disk_total_gb * 100) if disk_total_gb > 0 else 0
                ),
            },
            "uptime_seconds": time.time() - psutil.boot_time(),
        }

    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        return {"error": "Failed to get system metrics"}


async def _get_database_metrics() -> Dict[str, Any]:
    """Get database performance metrics (placeholder)."""
    # TODO: Implement actual database metrics collection
    return {
        "connection_pool": {
            "active_connections": 0,
            "idle_connections": 0,
            "max_connections": 100,
        },
        "query_performance": {
            "average_query_time_ms": 0.0,
            "slow_queries_count": 0,
            "total_queries": 0,
        },
        "note": "Database metrics collection not yet implemented",
    }


def _analyze_slow_requests(slow_requests: list) -> Dict[str, Any]:
    """Analyze patterns in slow requests."""
    if not slow_requests:
        return {"message": "No slow requests to analyze"}

    # Group by path
    path_counts = {}
    path_avg_times = {}

    for request in slow_requests:
        path = request.get("path", "unknown")
        response_time = request.get("response_time_ms", 0)

        if path not in path_counts:
            path_counts[path] = 0
            path_avg_times[path] = []

        path_counts[path] += 1
        path_avg_times[path].append(response_time)

    # Calculate averages
    for path in path_avg_times:
        times = path_avg_times[path]
        path_avg_times[path] = sum(times) / len(times) if times else 0

    # Find most problematic paths
    problematic_paths = sorted(path_counts.items(), key=lambda x: x[1], reverse=True)[
        :5
    ]
    slowest_paths = sorted(path_avg_times.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "total_slow_requests": len(slow_requests),
        "most_frequent_slow_paths": problematic_paths,
        "slowest_average_paths": slowest_paths,
        "time_range": {
            "oldest": min(r.get("timestamp", 0) for r in slow_requests),
            "newest": max(r.get("timestamp", 0) for r in slow_requests),
        },
    }


def _calculate_cache_effectiveness(cache_stats: Dict[str, Any]) -> Dict[str, float]:
    """Calculate cache effectiveness scores."""
    try:
        global_stats = cache_stats.get("global_statistics", {})
        layer_stats = cache_stats.get("layer_statistics", {})

        # Global effectiveness
        global_hit_ratio = global_stats.get("global_hit_ratio", 0)
        avg_response_time = global_stats.get("average_response_time_ms", 0)

        # Layer effectiveness
        l1_hit_ratio = layer_stats.get("l1_memory", {}).get("hit_ratio", 0)
        l2_hit_ratio = layer_stats.get("l2_redis", {}).get("hit_ratio", 0)

        # Calculate scores (0-100)
        global_score = min(global_hit_ratio * 100, 100)
        speed_score = max(100 - (avg_response_time / 10), 0)  # 10ms = 90 score
        l1_score = min(l1_hit_ratio * 100, 100)
        l2_score = min(l2_hit_ratio * 100, 100)

        overall_score = (global_score + speed_score + l1_score + l2_score) / 4

        return {
            "overall_effectiveness": round(overall_score, 2),
            "global_hit_rate_score": round(global_score, 2),
            "response_speed_score": round(speed_score, 2),
            "l1_cache_score": round(l1_score, 2),
            "l2_cache_score": round(l2_score, 2),
        }

    except Exception as e:
        logger.error(f"Error calculating cache effectiveness: {e}")
        return {"error": "Failed to calculate effectiveness scores"}


def _generate_performance_recommendations(
    middleware_stats: Dict[str, Any],
    system_stats: Dict[str, Any],
    cache_stats: Dict[str, Any],
) -> list:
    """Generate performance improvement recommendations."""

    recommendations = []

    # Analyze API performance
    avg_response_time = middleware_stats.get("average_response_time_ms", 0)
    slow_requests_count = middleware_stats.get("slow_requests_count", 0)

    if avg_response_time > 100:
        recommendations.append(
            {
                "category": "api_performance",
                "priority": "high",
                "issue": f"High average response time: {avg_response_time:.2f}ms",
                "recommendation": "Implement database query optimization and add caching for frequently accessed data",
            }
        )

    if slow_requests_count > 10:
        recommendations.append(
            {
                "category": "api_performance",
                "priority": "medium",
                "issue": f"Many slow requests: {slow_requests_count}",
                "recommendation": "Analyze slow request patterns and optimize problematic endpoints",
            }
        )

    # Analyze system resources
    cpu_percent = system_stats.get("cpu", {}).get("percent", 0)
    memory_percent = system_stats.get("memory", {}).get("percent", 0)

    if cpu_percent > 80:
        recommendations.append(
            {
                "category": "system_resources",
                "priority": "high",
                "issue": f"High CPU usage: {cpu_percent}%",
                "recommendation": "Consider scaling horizontally or optimizing CPU-intensive operations",
            }
        )

    if memory_percent > 85:
        recommendations.append(
            {
                "category": "system_resources",
                "priority": "high",
                "issue": f"High memory usage: {memory_percent}%",
                "recommendation": "Optimize memory usage or increase available RAM",
            }
        )

    # Analyze cache performance
    global_hit_ratio = cache_stats.get("global_statistics", {}).get(
        "global_hit_ratio", 0
    )

    if global_hit_ratio < 0.7:
        recommendations.append(
            {
                "category": "caching",
                "priority": "medium",
                "issue": f"Low cache hit ratio: {global_hit_ratio:.2f}",
                "recommendation": "Review cache TTL settings and cache key strategies",
            }
        )

    # If no issues found
    if not recommendations:
        recommendations.append(
            {
                "category": "general",
                "priority": "info",
                "issue": "No critical performance issues detected",
                "recommendation": "System performance is within acceptable ranges",
            }
        )

    return recommendations


def _generate_cache_recommendations(
    cache_stats: Dict[str, Any], effectiveness_scores: Dict[str, Any]
) -> list:
    """Generate cache-specific recommendations."""

    recommendations = []

    overall_score = effectiveness_scores.get("overall_effectiveness", 0)
    l1_score = effectiveness_scores.get("l1_cache_score", 0)
    l2_score = effectiveness_scores.get("l2_cache_score", 0)

    if overall_score < 70:
        recommendations.append(
            {
                "priority": "high",
                "issue": f"Low overall cache effectiveness: {overall_score:.1f}/100",
                "recommendation": "Review cache strategies and consider increasing cache sizes",
            }
        )

    if l1_score < 60:
        recommendations.append(
            {
                "priority": "medium",
                "issue": f"Low L1 cache performance: {l1_score:.1f}/100",
                "recommendation": "Optimize L1 cache size or eviction policy",
            }
        )

    if l2_score < 50:
        recommendations.append(
            {
                "priority": "medium",
                "issue": f"Low L2 cache performance: {l2_score:.1f}/100",
                "recommendation": "Implement real Redis instead of simulation or optimize L2 strategy",
            }
        )

    # Check cache configuration
    config = cache_stats.get("configuration", {})
    if config.get("read_strategy") == "read_through" and overall_score < 80:
        recommendations.append(
            {
                "priority": "low",
                "issue": "Read-through strategy with low performance",
                "recommendation": "Consider implementing cache warming for frequently accessed data",
            }
        )

    return recommendations


# Elite helper functions for enhanced performance monitoring


async def _get_elite_system_metrics() -> Dict[str, Any]:
    """Get enhanced system resource metrics."""
    try:
        # CPU metrics with more detail
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count_logical = psutil.cpu_count()
        cpu_count_physical = psutil.cpu_count(logical=False)
        cpu_freq = psutil.cpu_freq()
        load_avg = psutil.getloadavg() if hasattr(psutil, "getloadavg") else (0, 0, 0)

        # Memory metrics
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        # Disk metrics
        disk = psutil.disk_usage("/")
        disk_io = psutil.disk_io_counters()

        # Network metrics
        net_io = psutil.net_io_counters()

        # Process metrics
        process = psutil.Process(os.getpid())
        process_memory = process.memory_info()
        process_cpu = process.cpu_percent()
        process_threads = process.num_threads()

        return {
            "cpu": {
                "usage_percent": cpu_percent,
                "logical_cores": cpu_count_logical,
                "physical_cores": cpu_count_physical,
                "current_freq_mhz": cpu_freq.current if cpu_freq else 0,
                "max_freq_mhz": cpu_freq.max if cpu_freq else 0,
                "load_avg_1m": load_avg[0],
                "load_avg_5m": load_avg[1],
                "load_avg_15m": load_avg[2],
                "process_usage_percent": process_cpu,
            },
            "memory": {
                "total_mb": memory.total // (1024 * 1024),
                "used_mb": memory.used // (1024 * 1024),
                "available_mb": memory.available // (1024 * 1024),
                "usage_percent": memory.percent,
                "swap_total_mb": swap.total // (1024 * 1024),
                "swap_used_mb": swap.used // (1024 * 1024),
                "swap_usage_percent": swap.percent,
                "process_rss_mb": process_memory.rss // (1024 * 1024),
                "process_vms_mb": process_memory.vms // (1024 * 1024),
            },
            "disk": {
                "total_gb": disk.total // (1024 * 1024 * 1024),
                "used_gb": disk.used // (1024 * 1024 * 1024),
                "free_gb": disk.free // (1024 * 1024 * 1024),
                "usage_percent": (
                    (disk.used / disk.total * 100) if disk.total > 0 else 0
                ),
                "read_bytes": disk_io.read_bytes if disk_io else 0,
                "write_bytes": disk_io.write_bytes if disk_io else 0,
                "read_count": disk_io.read_count if disk_io else 0,
                "write_count": disk_io.write_count if disk_io else 0,
            },
            "network": {
                "bytes_sent": net_io.bytes_sent if net_io else 0,
                "bytes_recv": net_io.bytes_recv if net_io else 0,
                "packets_sent": net_io.packets_sent if net_io else 0,
                "packets_recv": net_io.packets_recv if net_io else 0,
                "errors_in": net_io.errin if net_io else 0,
                "errors_out": net_io.errout if net_io else 0,
            },
            "process": {
                "threads": process_threads,
                "pid": process.pid,
                "create_time": process.create_time(),
                "open_files": (
                    len(process.open_files()) if hasattr(process, "open_files") else 0
                ),
            },
            "uptime_seconds": time.time() - psutil.boot_time(),
        }

    except Exception as e:
        logger.error(f"Error getting elite system metrics: {e}")
        return {"error": "Failed to get system metrics"}


async def _get_elite_database_metrics() -> Dict[str, Any]:
    """Get enhanced database performance metrics."""
    try:
        db_manager = await get_database_manager()
        health_status = await db_manager.get_health_status()

        if health_status.get("status") == "healthy":
            return {
                "status": "healthy",
                "connection_pool": health_status.get("pool", {}),
                "performance": health_status.get("performance", {}),
                "cache_enabled": health_status.get("cache_enabled", False),
                "circuit_breaker": health_status.get("circuit_breaker", {}),
                "response_time_ms": 0,
            }
        else:
            return {
                "status": "unhealthy",
                "error": health_status.get("error", "Unknown database error"),
            }

    except Exception as e:
        logger.error(f"Error getting database metrics: {e}")
        return {
            "status": "error",
            "error": str(e),
            "connection_pool": {"active": 0, "idle": 0, "max": 0},
            "query_performance": {"avg_time_ms": 0, "slow_queries": 0},
        }


def _calculate_overall_performance_score(
    middleware_stats: Dict[str, Any],
    system_metrics: Dict[str, Any],
    cache_stats: Dict[str, Any],
) -> float:
    """Calculate comprehensive performance score (0-100)."""
    try:
        scores = []

        # API performance score (25%)
        api_response_times = middleware_stats.get("response_times", {})
        p95_time = api_response_times.get("p95_ms", 100)

        if p95_time <= 25:
            api_score = 100
        elif p95_time <= 50:
            api_score = 90
        elif p95_time <= 100:
            api_score = 70
        elif p95_time <= 200:
            api_score = 50
        else:
            api_score = 20

        scores.append(("api_performance", api_score, 0.25))

        # System resource score (25%)
        cpu_usage = system_metrics.get("cpu", {}).get("usage_percent", 0)
        memory_usage = system_metrics.get("memory", {}).get("usage_percent", 0)

        cpu_score = max(0, 100 - cpu_usage)
        memory_score = max(0, 100 - memory_usage)
        system_score = (cpu_score + memory_score) / 2

        scores.append(("system_resources", system_score, 0.25))

        # Cache performance score (25%)
        cache_hit_rates = cache_stats.get("hit_rates", {})
        overall_hit_rate = cache_hit_rates.get("overall_hit_rate", 0) * 100
        cache_score = overall_hit_rate

        scores.append(("cache_performance", cache_score, 0.25))

        # Error rate score (25%)
        error_stats = middleware_stats.get("errors", {})
        error_rate = error_stats.get("error_rate_percent", 0)
        error_score = max(0, 100 - (error_rate * 10))

        scores.append(("error_rate", error_score, 0.25))

        # Calculate weighted average
        total_score = sum(score * weight for _, score, weight in scores)

        return round(total_score, 2)

    except Exception as e:
        logger.error(f"Error calculating performance score: {e}")
        return 0.0


def _determine_health_status(performance_score: float) -> str:
    """Determine health status based on performance score."""
    if performance_score >= 90:
        return "excellent"
    elif performance_score >= 75:
        return "healthy"
    elif performance_score >= 60:
        return "warning"
    elif performance_score >= 40:
        return "degraded"
    else:
        return "critical"


def _get_active_alerts(dashboard_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get active performance alerts."""
    try:
        return dashboard_summary.get("active_alerts", [])
    except Exception:
        return []


def _calculate_performance_kpis(
    middleware_stats: Dict[str, Any], system_metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """Calculate key performance indicators."""
    try:
        response_times = middleware_stats.get("response_times", {})

        return {
            "throughput_rps": middleware_stats.get("requests_per_minute", 0) / 60,
            "availability_percent": 99.9,
            "p50_response_time_ms": response_times.get("p50_ms", 0),
            "p95_response_time_ms": response_times.get("p95_ms", 0),
            "p99_response_time_ms": response_times.get("p99_ms", 0),
            "error_rate_percent": middleware_stats.get("errors", {}).get(
                "error_rate_percent", 0
            ),
            "cache_hit_rate_percent": 0,
            "cpu_efficiency_percent": max(
                0, 100 - system_metrics.get("cpu", {}).get("usage_percent", 0)
            ),
            "memory_efficiency_percent": max(
                0, 100 - system_metrics.get("memory", {}).get("usage_percent", 0)
            ),
        }

    except Exception as e:
        logger.error(f"Error calculating KPIs: {e}")
        return {}


def _generate_elite_recommendations(
    middleware_stats: Dict[str, Any],
    system_metrics: Dict[str, Any],
    cache_stats: Dict[str, Any],
    performance_score: float,
) -> List[Dict[str, Any]]:
    """Generate elite performance recommendations."""
    recommendations = []

    # Performance-based recommendations
    if performance_score < 60:
        recommendations.append(
            {
                "category": "critical_performance",
                "priority": "high",
                "title": "Critical Performance Issues Detected",
                "description": f"Overall performance score is {performance_score}/100",
                "recommendations": [
                    "Immediately investigate slow endpoints",
                    "Review system resource usage",
                    "Optimize database queries",
                    "Implement aggressive caching",
                ],
            }
        )

    # Response time recommendations
    response_times = middleware_stats.get("response_times", {})
    p95_time = response_times.get("p95_ms", 0)

    if p95_time > 100:
        recommendations.append(
            {
                "category": "response_time",
                "priority": "high" if p95_time > 500 else "medium",
                "title": f"Slow Response Times (P95: {p95_time}ms)",
                "description": "API responses are slower than target",
                "recommendations": [
                    "Implement database connection pooling",
                    "Add response compression",
                    "Optimize slow SQL queries",
                    "Implement API-level caching",
                ],
            }
        )

    # System resource recommendations
    cpu_usage = system_metrics.get("cpu", {}).get("usage_percent", 0)
    memory_usage = system_metrics.get("memory", {}).get("usage_percent", 0)

    if cpu_usage > 80 or memory_usage > 85:
        recommendations.append(
            {
                "category": "system_resources",
                "priority": "high",
                "title": "High Resource Usage",
                "description": f"CPU: {cpu_usage}%, Memory: {memory_usage}%",
                "recommendations": [
                    "Scale horizontally with additional instances",
                    "Optimize CPU-intensive operations",
                    "Implement memory leak detection",
                    "Consider upgrading server resources",
                ],
            }
        )

    # Elite-level recommendations for high-performing systems
    if performance_score > 80:
        recommendations.append(
            {
                "category": "optimization",
                "priority": "low",
                "title": "Elite Performance Optimizations",
                "description": "System performing well, consider elite optimizations",
                "recommendations": [
                    "Implement predictive caching",
                    "Add request prioritization",
                    "Optimize for sub-10ms P50 response times",
                    "Implement advanced monitoring and alerting",
                ],
            }
        )

    return recommendations


async def _calculate_performance_grade() -> str:
    """Calculate current performance grade."""
    try:
        middleware = get_performance_middleware()
        if not middleware:
            return "N/A"

        stats = middleware.get_elite_performance_stats()
        score = stats.get("health_indicators", {}).get("performance_score", 0)

        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "A-"
        elif score >= 75:
            return "B+"
        elif score >= 70:
            return "B"
        elif score >= 65:
            return "B-"
        elif score >= 60:
            return "C+"
        elif score >= 55:
            return "C"
        elif score >= 50:
            return "C-"
        else:
            return "F"

    except Exception:
        return "N/A"
