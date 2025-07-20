"""
NGX Pulse MCP Adapter

Provides MCP interface for NGX Pulse health and biometrics platform.
This adapter translates MCP requests into NGX Pulse API calls.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import aiohttp
import random

from mcp.schemas import ToolDefinition
from mcp.config import ToolConfig
from core.logging_config import get_logger

logger = get_logger(__name__)


class NGXPulseAdapter:
    """
    MCP Adapter for NGX Pulse
    
    Provides access to:
    - Biometric data reading
    - Health metrics tracking
    - Wearable device integration
    - Trend analysis
    """
    
    def __init__(self, endpoint: str = "http://localhost:8003"):
        self.endpoint = endpoint.rstrip("/")
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def initialize(self):
        """Initialize the adapter"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
    
    def get_tool_definitions(self) -> List[ToolDefinition]:
        """Get all tool definitions provided by NGX Pulse"""
        return [
            ToolDefinition(
                name="ngx_pulse.read_biometrics",
                description="Read current biometric data from wearables and health devices",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID or 'current' for authenticated user"
                        },
                        "metric": {
                            "type": "string",
                            "enum": ["heart_rate", "hrv", "sleep", "steps", "calories", "stress", "recovery", "all"],
                            "description": "Specific metric to retrieve"
                        },
                        "device": {
                            "type": "string",
                            "enum": ["all", "apple_watch", "garmin", "whoop", "oura", "fitbit"],
                            "description": "Filter by device type"
                        },
                        "include_raw": {
                            "type": "boolean",
                            "description": "Include raw sensor data"
                        }
                    },
                    "required": ["user_id", "metric"]
                },
                examples=[
                    {
                        "input": {
                            "user_id": "current",
                            "metric": "hrv",
                            "device": "whoop"
                        },
                        "output": {
                            "hrv": {
                                "current": 65,
                                "average_7d": 62,
                                "trend": "improving",
                                "last_updated": "2025-01-20T08:15:00Z"
                            }
                        }
                    }
                ]
            ),
            
            ToolDefinition(
                name="ngx_pulse.track_workout",
                description="Track and analyze workout performance data",
                input_schema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["start", "stop", "pause", "resume", "analyze"],
                            "description": "Workout tracking action"
                        },
                        "workout_id": {
                            "type": "string",
                            "description": "Workout ID (required for stop, pause, resume, analyze)"
                        },
                        "workout_type": {
                            "type": "string",
                            "enum": ["strength", "cardio", "hiit", "yoga", "recovery", "custom"],
                            "description": "Type of workout (required for start)"
                        },
                        "metrics_to_track": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["heart_rate", "calories", "power", "reps", "weight", "distance", "pace"]
                            },
                            "description": "Metrics to track during workout"
                        }
                    },
                    "required": ["action"]
                }
            ),
            
            ToolDefinition(
                name="ngx_pulse.analyze_trends",
                description="Analyze health and fitness trends over time",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID or 'current'"
                        },
                        "metrics": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["fitness_level", "recovery_rate", "sleep_quality", "stress_level", "body_composition"]
                            },
                            "description": "Metrics to analyze"
                        },
                        "period": {
                            "type": "string",
                            "enum": ["week", "month", "quarter", "year"],
                            "description": "Analysis period"
                        },
                        "compare_to": {
                            "type": "string",
                            "enum": ["previous_period", "baseline", "goals", "peer_group"],
                            "description": "Comparison baseline"
                        }
                    },
                    "required": ["user_id", "metrics", "period"]
                }
            ),
            
            ToolDefinition(
                name="ngx_pulse.sync_wearables",
                description="Sync data from wearable devices and health apps",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID or 'current'"
                        },
                        "devices": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["apple_health", "google_fit", "garmin_connect", "whoop", "oura", "fitbit", "strava"]
                            },
                            "description": "Devices/apps to sync"
                        },
                        "data_types": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["activities", "biometrics", "sleep", "nutrition", "all"]
                            },
                            "description": "Types of data to sync"
                        },
                        "since": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Sync data from this timestamp"
                        }
                    },
                    "required": ["user_id", "devices"]
                }
            ),
            
            ToolDefinition(
                name="ngx_pulse.generate_health_report",
                description="Generate comprehensive health and fitness reports",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID or 'current'"
                        },
                        "report_type": {
                            "type": "string",
                            "enum": ["daily_summary", "weekly_progress", "monthly_analysis", "health_assessment", "performance_review"],
                            "description": "Type of report to generate"
                        },
                        "include_recommendations": {
                            "type": "boolean",
                            "description": "Include AI-powered recommendations"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["json", "pdf", "html"],
                            "description": "Report format"
                        }
                    },
                    "required": ["user_id", "report_type"]
                }
            )
        ]
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if not self.session:
            await self.initialize()
        
        # Route to appropriate handler
        handlers = {
            "ngx_pulse.read_biometrics": self._read_biometrics,
            "ngx_pulse.track_workout": self._track_workout,
            "ngx_pulse.analyze_trends": self._analyze_trends,
            "ngx_pulse.sync_wearables": self._sync_wearables,
            "ngx_pulse.generate_health_report": self._generate_health_report
        }
        
        handler = handlers.get(tool_name)
        if not handler:
            return {"error": f"Unknown tool: {tool_name}"}
        
        try:
            return await handler(arguments)
        except Exception as e:
            logger.error(f"Error executing {tool_name}: {e}")
            return {"error": str(e)}
    
    async def _read_biometrics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Read biometric data"""
        user_id = args.get("user_id", "current")
        metric = args["metric"]
        device = args.get("device", "all")
        
        # Simulated biometric data
        current_time = datetime.utcnow()
        data = {
            "user_id": user_id,
            "timestamp": current_time.isoformat(),
            "device": device
        }
        
        if metric in ["heart_rate", "all"]:
            data["heart_rate"] = {
                "current": random.randint(60, 75),
                "resting": random.randint(50, 60),
                "max_today": random.randint(140, 160),
                "zones": {
                    "recovery": {"min": 50, "max": 100, "minutes_today": 420},
                    "fat_burn": {"min": 100, "max": 140, "minutes_today": 45},
                    "cardio": {"min": 140, "max": 170, "minutes_today": 25},
                    "peak": {"min": 170, "max": 190, "minutes_today": 5}
                }
            }
        
        if metric in ["hrv", "all"]:
            data["hrv"] = {
                "current": random.randint(55, 75),
                "average_7d": random.randint(60, 70),
                "average_30d": random.randint(58, 68),
                "trend": "stable",
                "recovery_score": random.randint(70, 90)
            }
        
        if metric in ["sleep", "all"]:
            data["sleep"] = {
                "last_night": {
                    "total_hours": round(random.uniform(6.5, 8.5), 1),
                    "rem_hours": round(random.uniform(1.5, 2.5), 1),
                    "deep_hours": round(random.uniform(1.0, 2.0), 1),
                    "light_hours": round(random.uniform(3.0, 4.0), 1),
                    "efficiency": random.randint(85, 95),
                    "score": random.randint(75, 95)
                },
                "average_7d": {
                    "total_hours": round(random.uniform(6.8, 7.8), 1),
                    "score": random.randint(80, 90)
                }
            }
        
        if metric in ["steps", "all"]:
            data["steps"] = {
                "today": random.randint(5000, 12000),
                "goal": 10000,
                "average_7d": random.randint(7000, 9000),
                "distance_km": round(random.uniform(4.0, 9.0), 1)
            }
        
        if metric in ["calories", "all"]:
            data["calories"] = {
                "burned_today": random.randint(1800, 2500),
                "active": random.randint(300, 600),
                "resting": random.randint(1500, 1900),
                "consumed": random.randint(1800, 2200),
                "deficit": random.randint(-200, 400)
            }
        
        if metric in ["stress", "all"]:
            data["stress"] = {
                "current_level": random.choice(["low", "moderate", "high"]),
                "score": random.randint(20, 60),
                "recovery_time_hours": round(random.uniform(2.0, 6.0), 1)
            }
        
        if metric in ["recovery", "all"]:
            data["recovery"] = {
                "score": random.randint(60, 95),
                "readiness": random.choice(["ready", "moderate", "rest_recommended"]),
                "muscle_soreness": random.choice(["none", "mild", "moderate"]),
                "hydration": random.choice(["optimal", "adequate", "needs_attention"])
            }
        
        return data
    
    async def _track_workout(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Track workout data"""
        action = args["action"]
        
        if action == "start":
            workout_type = args.get("workout_type", "custom")
            metrics = args.get("metrics_to_track", ["heart_rate", "calories"])
            
            workout_id = f"wkt_{datetime.utcnow().timestamp()}"
            
            return {
                "workout_id": workout_id,
                "status": "tracking",
                "type": workout_type,
                "started_at": datetime.utcnow().isoformat(),
                "tracking_metrics": metrics,
                "initial_readings": {
                    "heart_rate": random.randint(70, 85),
                    "calories": 0
                }
            }
        
        elif action == "analyze":
            workout_id = args.get("workout_id")
            
            return {
                "workout_id": workout_id,
                "analysis": {
                    "duration_minutes": random.randint(30, 60),
                    "calories_burned": random.randint(200, 500),
                    "average_heart_rate": random.randint(120, 140),
                    "peak_heart_rate": random.randint(160, 180),
                    "performance_score": random.randint(75, 95),
                    "recovery_time_hours": round(random.uniform(12.0, 36.0), 1),
                    "improvements": [
                        "Maintained target heart rate zone for 85% of workout",
                        "Improved power output by 5% from last session"
                    ],
                    "recommendations": [
                        "Consider increasing rest between sets",
                        "Hydration levels could be improved"
                    ]
                }
            }
        
        return {"status": f"Action {action} completed"}
    
    async def _analyze_trends(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze health trends"""
        user_id = args.get("user_id", "current")
        metrics = args["metrics"]
        period = args["period"]
        compare_to = args.get("compare_to", "previous_period")
        
        trends = {
            "user_id": user_id,
            "period": period,
            "comparison": compare_to,
            "generated_at": datetime.utcnow().isoformat(),
            "trends": {}
        }
        
        for metric in metrics:
            if metric == "fitness_level":
                trends["trends"]["fitness_level"] = {
                    "current_score": random.randint(70, 90),
                    "change": round(random.uniform(-5, 10), 1),
                    "trend": random.choice(["improving", "stable", "declining"]),
                    "vo2_max": round(random.uniform(40, 55), 1),
                    "strength_index": random.randint(60, 85)
                }
            
            elif metric == "recovery_rate":
                trends["trends"]["recovery_rate"] = {
                    "average_hours": round(random.uniform(18, 30), 1),
                    "improvement": f"{random.randint(-10, 20)}%",
                    "factors": {
                        "sleep_quality": "positive",
                        "nutrition": "neutral",
                        "stress_management": "needs_improvement"
                    }
                }
            
            elif metric == "sleep_quality":
                trends["trends"]["sleep_quality"] = {
                    "average_score": random.randint(75, 90),
                    "consistency": random.randint(70, 95),
                    "problem_areas": ["late_bedtime", "frequent_waking"],
                    "improvements": ["deeper_sleep_increased", "rem_cycles_normalized"]
                }
            
            elif metric == "stress_level":
                trends["trends"]["stress_level"] = {
                    "average": random.choice(["low", "moderate", "high"]),
                    "peak_times": ["weekday_mornings", "sunday_evenings"],
                    "coping_effectiveness": random.randint(60, 85),
                    "recommendations": [
                        "Increase meditation frequency",
                        "Consider breath work before meetings"
                    ]
                }
            
            elif metric == "body_composition":
                trends["trends"]["body_composition"] = {
                    "muscle_mass_kg": round(random.uniform(30, 45), 1),
                    "body_fat_percentage": round(random.uniform(12, 25), 1),
                    "lean_mass_change": f"+{round(random.uniform(0.5, 2.0), 1)}kg",
                    "metabolic_age": random.randint(25, 40)
                }
        
        return trends
    
    async def _sync_wearables(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Sync wearable device data"""
        user_id = args.get("user_id", "current")
        devices = args["devices"]
        data_types = args.get("data_types", ["all"])
        since = args.get("since", (datetime.utcnow() - timedelta(days=1)).isoformat())
        
        sync_result = {
            "user_id": user_id,
            "sync_id": f"sync_{datetime.utcnow().timestamp()}",
            "started_at": datetime.utcnow().isoformat(),
            "devices_synced": {}
        }
        
        for device in devices:
            device_result = {
                "status": "success",
                "last_sync": datetime.utcnow().isoformat(),
                "data_points": {}
            }
            
            if "all" in data_types or "activities" in data_types:
                device_result["data_points"]["activities"] = random.randint(5, 20)
            
            if "all" in data_types or "biometrics" in data_types:
                device_result["data_points"]["biometrics"] = random.randint(100, 500)
            
            if "all" in data_types or "sleep" in data_types:
                device_result["data_points"]["sleep"] = random.randint(7, 30)
            
            if "all" in data_types or "nutrition" in data_types:
                device_result["data_points"]["nutrition"] = random.randint(20, 100)
            
            sync_result["devices_synced"][device] = device_result
        
        sync_result["completed_at"] = datetime.utcnow().isoformat()
        sync_result["total_data_points"] = sum(
            sum(device["data_points"].values()) 
            for device in sync_result["devices_synced"].values()
        )
        
        return sync_result
    
    async def _generate_health_report(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Generate health report"""
        user_id = args.get("user_id", "current")
        report_type = args["report_type"]
        include_recommendations = args.get("include_recommendations", True)
        format_type = args.get("format", "json")
        
        report = {
            "report_id": f"rpt_{datetime.utcnow().timestamp()}",
            "user_id": user_id,
            "type": report_type,
            "generated_at": datetime.utcnow().isoformat(),
            "format": format_type
        }
        
        if report_type == "daily_summary":
            report["summary"] = {
                "date": datetime.utcnow().date().isoformat(),
                "health_score": random.randint(75, 95),
                "activity_minutes": random.randint(30, 90),
                "sleep_quality": random.randint(70, 90),
                "nutrition_adherence": random.randint(80, 95),
                "stress_level": random.choice(["low", "moderate"]),
                "hydration": "adequate"
            }
        
        elif report_type == "weekly_progress":
            report["progress"] = {
                "workouts_completed": random.randint(3, 6),
                "goals_met": random.randint(5, 8),
                "consistency_score": random.randint(80, 95),
                "improvements": [
                    "Increased workout intensity by 10%",
                    "Improved sleep consistency",
                    "Met daily step goal 6/7 days"
                ],
                "areas_for_focus": [
                    "Increase protein intake",
                    "Add one recovery day"
                ]
            }
        
        elif report_type == "health_assessment":
            report["assessment"] = {
                "overall_health": "good",
                "cardiovascular_fitness": "above_average",
                "metabolic_health": "excellent",
                "musculoskeletal": "good",
                "mental_wellness": "moderate",
                "risk_factors": ["sedentary_time", "irregular_sleep"],
                "strengths": ["consistent_exercise", "balanced_nutrition"]
            }
        
        if include_recommendations:
            report["recommendations"] = [
                {
                    "category": "fitness",
                    "priority": "high",
                    "action": "Add 2 strength training sessions per week",
                    "expected_benefit": "Increase lean muscle mass and metabolic rate"
                },
                {
                    "category": "recovery",
                    "priority": "medium",
                    "action": "Implement 10-minute daily stretching routine",
                    "expected_benefit": "Reduce injury risk and improve flexibility"
                },
                {
                    "category": "nutrition",
                    "priority": "medium",
                    "action": "Increase water intake to 3L daily",
                    "expected_benefit": "Improve recovery and cognitive function"
                }
            ]
        
        if format_type != "json":
            report["download_url"] = f"{self.endpoint}/reports/{report['report_id']}/download"
            report["expires_at"] = (datetime.utcnow() + timedelta(hours=48)).isoformat()
        
        return report