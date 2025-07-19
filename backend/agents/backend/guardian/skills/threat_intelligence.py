"""
Threat Intelligence Skill
========================

Analyzes threat intelligence and indicators.
"""

from typing import Dict, Any, List
from core.logging_config import get_logger

logger = get_logger(__name__)


class ThreatIntelligenceSkill:
    """Skill for threat intelligence analysis."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "threat_intelligence"
        self.description = "Analyze threat intelligence"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze threat intelligence.
        
        Args:
            request: Contains indicators, context, threat_type
            
        Returns:
            Threat intelligence analysis
        """
        try:
            threat_data = {
                "indicators": request.get("indicators", []),
                "context": request.get("context", {}),
                "threat_type": request.get("threat_type", "unknown"),
                "source": request.get("source", "internal")
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_threat_intelligence_prompt(threat_data)
            
            # Generate threat analysis
            response = await self.agent.generate_response(prompt)
            
            # Analyze threat actors
            threat_actors = self._identify_threat_actors(threat_data)
            
            # Extract IOCs
            iocs = self._extract_iocs(threat_data["indicators"])
            
            return {
                "success": True,
                "threat_analysis": response,
                "skill_used": "threat_intelligence",
                "data": {
                    "threat_actors": threat_actors,
                    "iocs_identified": len(iocs),
                    "threat_level": self._assess_threat_level(threat_data),
                    "ttps": self._map_ttps(threat_data),
                    "recommended_actions": self._generate_actions(threat_data)
                },
                "metadata": {
                    "confidence": 0.85,
                    "framework": "MITRE_ATT&CK",
                    "intelligence_source": threat_data["source"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error in threat intelligence: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "threat_intelligence"
            }
    
    def _identify_threat_actors(self, threat_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential threat actors."""
        # Simplified threat actor identification
        threat_type = threat_data.get("threat_type", "").lower()
        
        actors = []
        if "apt" in threat_type or "advanced" in threat_type:
            actors.append({
                "type": "APT",
                "sophistication": "high",
                "motivation": "espionage"
            })
        elif "ransomware" in threat_type:
            actors.append({
                "type": "Ransomware Group",
                "sophistication": "medium",
                "motivation": "financial"
            })
        elif "insider" in threat_type:
            actors.append({
                "type": "Insider Threat",
                "sophistication": "varies",
                "motivation": "varies"
            })
        else:
            actors.append({
                "type": "Unknown",
                "sophistication": "unknown",
                "motivation": "unknown"
            })
        
        return actors
    
    def _extract_iocs(self, indicators: List[Any]) -> List[Dict[str, str]]:
        """Extract Indicators of Compromise."""
        iocs = []
        
        for indicator in indicators:
            if isinstance(indicator, str):
                # Simple IOC type detection
                if "@" in indicator and "." in indicator:
                    iocs.append({"type": "email", "value": indicator})
                elif indicator.startswith("http"):
                    iocs.append({"type": "url", "value": indicator})
                elif "." in indicator and indicator.count(".") >= 3:
                    iocs.append({"type": "ip", "value": indicator})
                elif len(indicator) in [32, 40, 64]:  # MD5, SHA1, SHA256
                    iocs.append({"type": "hash", "value": indicator})
                else:
                    iocs.append({"type": "unknown", "value": indicator})
        
        return iocs
    
    def _assess_threat_level(self, threat_data: Dict[str, Any]) -> str:
        """Assess overall threat level."""
        indicators_count = len(threat_data.get("indicators", []))
        threat_type = threat_data.get("threat_type", "").lower()
        
        if indicators_count > 10 or "apt" in threat_type:
            return "critical"
        elif indicators_count > 5 or "ransomware" in threat_type:
            return "high"
        elif indicators_count > 2:
            return "medium"
        else:
            return "low"
    
    def _map_ttps(self, threat_data: Dict[str, Any]) -> List[str]:
        """Map to MITRE ATT&CK TTPs."""
        # Simplified TTP mapping
        ttps = []
        threat_type = threat_data.get("threat_type", "").lower()
        
        if "phishing" in threat_type:
            ttps.append("T1566 - Phishing")
        if "malware" in threat_type:
            ttps.append("T1204 - User Execution")
        if "lateral" in threat_type:
            ttps.append("T1021 - Remote Services")
        if "exfiltration" in threat_type:
            ttps.append("T1041 - Exfiltration Over C2 Channel")
        
        return ttps if ttps else ["Unknown TTPs"]
    
    def _generate_actions(self, threat_data: Dict[str, Any]) -> List[str]:
        """Generate recommended actions."""
        actions = [
            "Update threat intelligence feeds",
            "Block identified IOCs at perimeter"
        ]
        
        threat_level = self._assess_threat_level(threat_data)
        if threat_level in ["critical", "high"]:
            actions.insert(0, "Initiate incident response procedures")
            actions.append("Conduct threat hunting activities")
        
        return actions