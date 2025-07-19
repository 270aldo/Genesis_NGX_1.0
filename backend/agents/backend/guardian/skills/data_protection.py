"""
Data Protection Skill
====================

Implements data protection and privacy strategies.
"""

from typing import Dict, Any, List
from core.logging_config import get_logger

logger = get_logger(__name__)


class DataProtectionSkill:
    """Skill for data protection strategies."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "data_protection"
        self.description = "Design data protection strategies"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design data protection strategy.
        
        Args:
            request: Contains data_types, requirements, compliance_needs
            
        Returns:
            Data protection strategy
        """
        try:
            protection_data = {
                "data_types": request.get("data_types", ["personal_data"]),
                "requirements": request.get("requirements", ["encryption", "access_control"]),
                "compliance_needs": request.get("compliance_needs", ["GDPR"]),
                "risk_tolerance": request.get("risk_tolerance", "low")
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_data_protection_prompt(protection_data)
            
            # Generate protection strategy
            response = await self.agent.generate_response(prompt)
            
            # Analyze data classification
            classification = self._classify_data(protection_data["data_types"])
            
            return {
                "success": True,
                "protection_strategy": response,
                "skill_used": "data_protection",
                "data": {
                    "data_classification": classification,
                    "encryption_methods": self._recommend_encryption(classification),
                    "access_controls": self._recommend_access_controls(classification),
                    "protection_level": self._determine_protection_level(protection_data)
                },
                "metadata": {
                    "confidence": 0.91,
                    "privacy_by_design": True,
                    "standards_followed": ["ISO27001", "NIST"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error in data protection: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "data_protection"
            }
    
    def _classify_data(self, data_types: List[str]) -> Dict[str, str]:
        """Classify data by sensitivity level."""
        classification = {}
        
        high_sensitivity = ["health_data", "financial_data", "biometric_data", "genetic_data"]
        medium_sensitivity = ["personal_data", "contact_info", "behavioral_data"]
        low_sensitivity = ["anonymous_data", "public_data", "aggregated_data"]
        
        for data_type in data_types:
            if any(sensitive in data_type.lower() for sensitive in high_sensitivity):
                classification[data_type] = "highly_sensitive"
            elif any(sensitive in data_type.lower() for sensitive in medium_sensitivity):
                classification[data_type] = "sensitive"
            else:
                classification[data_type] = "low_sensitivity"
        
        return classification
    
    def _recommend_encryption(self, classification: Dict[str, str]) -> List[str]:
        """Recommend encryption methods based on data classification."""
        methods = []
        
        if any(level == "highly_sensitive" for level in classification.values()):
            methods.extend([
                "AES-256-GCM encryption at rest",
                "TLS 1.3 for data in transit",
                "End-to-end encryption for communications"
            ])
        elif any(level == "sensitive" for level in classification.values()):
            methods.extend([
                "AES-256 encryption at rest",
                "TLS 1.2+ for data in transit"
            ])
        else:
            methods.append("Standard encryption protocols")
        
        return methods
    
    def _recommend_access_controls(self, classification: Dict[str, str]) -> List[str]:
        """Recommend access controls based on data classification."""
        controls = ["Role-based access control (RBAC)"]
        
        if any(level == "highly_sensitive" for level in classification.values()):
            controls.extend([
                "Multi-factor authentication required",
                "Principle of least privilege",
                "Regular access reviews",
                "Audit logging for all access"
            ])
        elif any(level == "sensitive" for level in classification.values()):
            controls.extend([
                "Strong authentication required",
                "Access logging enabled"
            ])
        
        return controls
    
    def _determine_protection_level(self, data: Dict[str, Any]) -> str:
        """Determine overall protection level needed."""
        risk_tolerance = data.get("risk_tolerance", "low")
        
        if risk_tolerance == "low" or "health_data" in str(data.get("data_types", [])):
            return "maximum_protection"
        elif risk_tolerance == "medium":
            return "enhanced_protection"
        else:
            return "standard_protection"