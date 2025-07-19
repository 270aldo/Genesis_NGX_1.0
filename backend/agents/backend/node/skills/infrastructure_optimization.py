"""
Infrastructure Optimization Skill
================================

Optimizes infrastructure and cloud resources.
"""

from typing import Dict, Any, List
from core.logging_config import get_logger

logger = get_logger(__name__)


class InfrastructureOptimizationSkill:
    """Skill for infrastructure optimization."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "infrastructure_optimization"
        self.description = "Optimize infrastructure and cloud resources"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize infrastructure setup.
        
        Args:
            request: Contains current_setup, pain_points, goals
            
        Returns:
            Infrastructure optimization plan
        """
        try:
            infra_data = {
                "current_setup": request.get("current_setup", {}),
                "pain_points": request.get("pain_points", ["performance"]),
                "goals": request.get("goals", ["cost_reduction", "scalability"]),
                "budget": request.get("budget", "moderate"),
                "cloud_provider": request.get("cloud_provider", "multi_cloud")
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_infrastructure_optimization_prompt(infra_data)
            
            # Generate optimization plan
            response = await self.agent.generate_response(prompt)
            
            # Analyze current infrastructure
            analysis = self._analyze_infrastructure(infra_data)
            
            return {
                "success": True,
                "optimization_plan": response,
                "skill_used": "infrastructure_optimization",
                "data": {
                    "current_analysis": analysis,
                    "optimization_strategies": self._generate_strategies(infra_data),
                    "cost_savings_estimate": self._estimate_savings(analysis),
                    "implementation_phases": self._create_phases(infra_data)
                },
                "metadata": {
                    "confidence": 0.87,
                    "optimization_potential": analysis["optimization_potential"],
                    "risk_level": "low"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in infrastructure optimization: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "infrastructure_optimization"
            }
    
    def _analyze_infrastructure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current infrastructure setup."""
        current = data.get("current_setup", {})
        pain_points = data.get("pain_points", [])
        
        analysis = {
            "resource_utilization": self._calculate_utilization(current),
            "bottlenecks": self._identify_bottlenecks(pain_points),
            "optimization_potential": "high" if len(pain_points) > 3 else "medium",
            "cloud_maturity": self._assess_cloud_maturity(current)
        }
        
        return analysis
    
    def _calculate_utilization(self, setup: Dict[str, Any]) -> Dict[str, str]:
        """Calculate resource utilization."""
        # Simplified calculation
        if not setup:
            return {"cpu": "unknown", "memory": "unknown", "storage": "unknown"}
        
        return {
            "cpu": "75%",
            "memory": "60%",
            "storage": "45%",
            "network": "30%"
        }
    
    def _identify_bottlenecks(self, pain_points: List[str]) -> List[Dict[str, str]]:
        """Identify infrastructure bottlenecks."""
        bottlenecks = []
        
        pain_map = {
            "performance": {"area": "compute", "severity": "high"},
            "scalability": {"area": "architecture", "severity": "medium"},
            "cost": {"area": "resource_allocation", "severity": "medium"},
            "reliability": {"area": "redundancy", "severity": "high"},
            "latency": {"area": "network", "severity": "high"}
        }
        
        for pain in pain_points:
            if pain.lower() in pain_map:
                bottlenecks.append(pain_map[pain.lower()])
        
        return bottlenecks
    
    def _generate_strategies(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimization strategies."""
        strategies = []
        goals = data.get("goals", [])
        
        if "cost_reduction" in goals:
            strategies.append({
                "name": "Right-sizing",
                "description": "Optimize instance types and sizes",
                "impact": "20-30% cost reduction",
                "effort": "low"
            })
            strategies.append({
                "name": "Reserved Instances",
                "description": "Commit to long-term usage for discounts",
                "impact": "40-60% cost reduction",
                "effort": "low"
            })
        
        if "scalability" in goals:
            strategies.append({
                "name": "Auto-scaling",
                "description": "Implement dynamic scaling policies",
                "impact": "Improved elasticity",
                "effort": "medium"
            })
            strategies.append({
                "name": "Containerization",
                "description": "Move to container-based architecture",
                "impact": "Better resource utilization",
                "effort": "high"
            })
        
        if "performance" in str(goals):
            strategies.append({
                "name": "Caching Layer",
                "description": "Implement Redis/Memcached",
                "impact": "50-80% latency reduction",
                "effort": "medium"
            })
        
        return strategies
    
    def _estimate_savings(self, analysis: Dict[str, Any]) -> Dict[str, str]:
        """Estimate potential cost savings."""
        potential = analysis.get("optimization_potential", "medium")
        
        if potential == "high":
            return {
                "monthly": "$5,000 - $10,000",
                "annual": "$60,000 - $120,000",
                "percentage": "30-40%"
            }
        elif potential == "medium":
            return {
                "monthly": "$2,000 - $5,000",
                "annual": "$24,000 - $60,000",
                "percentage": "15-25%"
            }
        else:
            return {
                "monthly": "$500 - $2,000",
                "annual": "$6,000 - $24,000",
                "percentage": "5-15%"
            }
    
    def _create_phases(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create implementation phases."""
        return [
            {
                "phase": 1,
                "name": "Assessment & Planning",
                "duration": "2 weeks",
                "activities": [
                    "Infrastructure audit",
                    "Cost analysis",
                    "Risk assessment"
                ]
            },
            {
                "phase": 2,
                "name": "Quick Wins",
                "duration": "4 weeks",
                "activities": [
                    "Right-sizing instances",
                    "Remove unused resources",
                    "Enable basic monitoring"
                ]
            },
            {
                "phase": 3,
                "name": "Architecture Optimization",
                "duration": "8-12 weeks",
                "activities": [
                    "Implement auto-scaling",
                    "Optimize data storage",
                    "Improve network topology"
                ]
            },
            {
                "phase": 4,
                "name": "Advanced Optimization",
                "duration": "Ongoing",
                "activities": [
                    "Implement IaC",
                    "Advanced monitoring",
                    "Continuous optimization"
                ]
            }
        ]
    
    def _assess_cloud_maturity(self, setup: Dict[str, Any]) -> str:
        """Assess cloud maturity level."""
        if not setup:
            return "initial"
        
        # Simplified assessment
        if "kubernetes" in str(setup).lower():
            return "advanced"
        elif "auto_scaling" in str(setup).lower():
            return "intermediate"
        else:
            return "basic"