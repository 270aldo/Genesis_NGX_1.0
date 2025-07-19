"""
Agent Visibility Management System

Manages which agents are visible and accessible based on user context,
query content, and demographic factors. Implements adaptive presentation
logic for specialized agents like LUNA.
"""

import re
from typing import Dict, List, Optional, Any
from enum import Enum
from core.logging_config import get_logger

logger = get_logger(__name__)


class VisibilityLevel(Enum):
    """Agent visibility levels."""

    ALWAYS_VISIBLE = "always_visible"  # Core agents always shown
    CONTEXTUALLY_VISIBLE = "contextually_visible"  # Shown based on context
    ON_DEMAND = "on_demand"  # Shown only when specifically requested
    BACKEND_ONLY = "backend_only"  # Never shown to users


class AgentVisibilityManager:
    """
    Manages agent visibility based on user context and query analysis.

    Implements adaptive presentation logic that shows the most relevant
    agents while keeping specialized agents accessible when needed.
    """

    def __init__(self):
        """Initialize the visibility manager."""
        self.agent_visibility_config = self._initialize_visibility_config()
        self.female_health_keywords = self._initialize_female_health_keywords()
        self.family_context_keywords = self._initialize_family_context_keywords()

    def _initialize_visibility_config(self) -> Dict[str, Dict[str, Any]]:
        """Initialize agent visibility configuration."""
        return {
            # Core visible agents (post-consolidation)
            "nexus": {
                "visibility_level": VisibilityLevel.ALWAYS_VISIBLE,
                "name": "NEXUS - Master Orchestrator & Concierge",
                "description": "Strategic coordination with client success support",
                "priority": 1,
            },
            "blaze": {
                "visibility_level": VisibilityLevel.ALWAYS_VISIBLE,
                "name": "BLAZE - Elite Training Strategist",
                "description": "Personalized training programs and performance optimization",
                "priority": 2,
            },
            "sage": {
                "visibility_level": VisibilityLevel.ALWAYS_VISIBLE,
                "name": "SAGE - Precision Nutrition Architect",
                "description": "AI-enhanced nutrition planning and meal optimization",
                "priority": 3,
            },
            "wave": {
                "visibility_level": VisibilityLevel.ALWAYS_VISIBLE,
                "name": "WAVE - Recovery & Performance Analytics",
                "description": "Data-driven recovery optimization and injury prevention",
                "priority": 4,
            },
            "spark": {
                "visibility_level": VisibilityLevel.ALWAYS_VISIBLE,
                "name": "SPARK - Motivation Behavior Coach",
                "description": "Behavioral change and motivational support",
                "priority": 5,
            },
            "stella": {
                "visibility_level": VisibilityLevel.ALWAYS_VISIBLE,
                "name": "STELLA - Progress Tracker",
                "description": "Achievement celebration and progress analytics",
                "priority": 6,
            },
            "nova": {
                "visibility_level": VisibilityLevel.ALWAYS_VISIBLE,
                "name": "NOVA - Biohacking Innovator",
                "description": "Cutting-edge wellness optimization techniques",
                "priority": 7,
            },
            "code": {
                "visibility_level": VisibilityLevel.ALWAYS_VISIBLE,
                "name": "CODE - Genetic Performance Specialist",
                "description": "Genetic analysis and personalized optimization",
                "priority": 8,
            },
            # LUNA - Adaptive visibility specialist
            "luna": {
                "visibility_level": VisibilityLevel.CONTEXTUALLY_VISIBLE,
                "name": "LUNA - Female Wellness Specialist",
                "description": "Specialized care for women's health across all life stages",
                "priority": 9,
                "adaptive_presentation": True,
                "visibility_contexts": {
                    "primary_specialist": "For female users - prominently featured",
                    "activated_specialist": "When female health topics detected",
                    "recommended_specialist": "When user asks about female family/partners",
                    "available_specialist": "Listed as available but not prominently featured",
                },
            },
            # Backend agents - invisible to users
            "node": {
                "visibility_level": VisibilityLevel.BACKEND_ONLY,
                "name": "NODE - Systems Integration",
                "description": "Infrastructure and API management",
                "accessible_via": "system_calls_only",
            },
            "guardian": {
                "visibility_level": VisibilityLevel.BACKEND_ONLY,
                "name": "GUARDIAN - Security Compliance",
                "description": "Data protection and security monitoring",
                "accessible_via": "security_events_only",
            },
        }

    def _initialize_female_health_keywords(self) -> List[str]:
        """Initialize keywords that trigger LUNA visibility."""
        return [
            # Spanish keywords
            "menstruación",
            "menstrual",
            "ciclo",
            "regla",
            "período",
            "ovulación",
            "embarazo",
            "embarazada",
            "maternidad",
            "lactancia",
            "amamantar",
            "menopausia",
            "perimenopausia",
            "climaterio",
            "sofocos",
            "bochornos",
            "hormonas",
            "hormonal",
            "estrógeno",
            "progesterona",
            "testosterona",
            "parto",
            "cesárea",
            "postparto",
            "recuperación posparto",
            "fertilidad",
            "concepción",
            "planificación familiar",
            "salud femenina",
            "ginecología",
            "ginecológico",
            "huesos",
            "osteoporosis",
            "calcio",
            "síndrome premenstrual",
            "spm",
            "endometriosis",
            "fibromas",
            "anticonceptivos",
            "píldora",
            "diu",
            # English keywords
            "menstruation",
            "menstrual",
            "cycle",
            "period",
            "ovulation",
            "pregnancy",
            "pregnant",
            "maternity",
            "breastfeeding",
            "nursing",
            "menopause",
            "perimenopause",
            "hot flashes",
            "night sweats",
            "hormones",
            "hormonal",
            "estrogen",
            "progesterone",
            "testosterone",
            "birth",
            "delivery",
            "postpartum",
            "postnatal",
            "fertility",
            "conception",
            "family planning",
            "women's health",
            "female health",
            "gynecology",
            "gynecological",
            "bone health",
            "osteoporosis",
            "calcium",
            "pms",
            "premenstrual",
            "endometriosis",
            "fibroids",
            "birth control",
            "contraceptive",
            "iud",
            "pcos",
            "polycystic",
            "thyroid",
            # Life stage keywords
            "adolescence",
            "puberty",
            "teenager",
            "young woman",
            "reproductive age",
            "childbearing",
            "midlife",
            "postmenopausal",
            "elderly women",
            "aging",
        ]

    def _initialize_family_context_keywords(self) -> List[str]:
        """Initialize keywords that suggest asking about female family/partners."""
        return [
            # Spanish
            "esposa",
            "mujer",
            "pareja",
            "novia",
            "hija",
            "mamá",
            "madre",
            "hermana",
            "abuela",
            "suegra",
            "cuñada",
            "sobrina",
            "ella",
            "su ciclo",
            "sus hormonas",
            "su embarazo",
            # English
            "wife",
            "partner",
            "girlfriend",
            "daughter",
            "mom",
            "mother",
            "sister",
            "grandmother",
            "mother-in-law",
            "sister-in-law",
            "niece",
            "she",
            "her cycle",
            "her hormones",
            "her pregnancy",
            "women in my family",
            "female relatives",
        ]

    def determine_luna_visibility(self, user_context: Dict[str, Any]) -> str:
        """
        Determine LUNA's visibility level based on user context.

        Args:
            user_context: Dictionary containing user info and query context

        Returns:
            str: One of the visibility contexts from luna configuration
        """
        try:
            # Extract relevant context
            user_profile = user_context.get("user_profile", {})
            query_text = user_context.get("message", "").lower()
            biological_sex = user_profile.get("biological_sex", "").lower()

            # Primary specialist for female users
            if biological_sex == "female":
                logger.info("LUNA visibility: primary_specialist (user is female)")
                return "primary_specialist"

            # Activated specialist when female health keywords detected
            if self._contains_female_health_keywords(query_text):
                logger.info(
                    "LUNA visibility: activated_specialist (female health keywords detected)"
                )
                return "activated_specialist"

            # Recommended specialist for family/partner context
            if self._contains_family_context_keywords(query_text):
                logger.info(
                    "LUNA visibility: recommended_specialist (family context detected)"
                )
                return "recommended_specialist"

            # Available specialist (default)
            logger.info("LUNA visibility: available_specialist (default)")
            return "available_specialist"

        except Exception as e:
            logger.error(f"Error determining LUNA visibility: {e}", exc_info=True)
            return "available_specialist"  # Safe default

    def _contains_female_health_keywords(self, text: str) -> bool:
        """Check if text contains female health keywords."""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.female_health_keywords)

    def _contains_family_context_keywords(self, text: str) -> bool:
        """Check if text contains family/partner context keywords."""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.family_context_keywords)

    def get_visible_agents(self, user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get list of agents that should be visible to the user.

        Args:
            user_context: User context including profile and query information

        Returns:
            List of agent dictionaries with visibility information
        """
        visible_agents = []

        for agent_id, config in self.agent_visibility_config.items():
            visibility_level = config["visibility_level"]

            # Skip backend agents
            if visibility_level == VisibilityLevel.BACKEND_ONLY:
                continue

            # Always include always visible agents
            if visibility_level == VisibilityLevel.ALWAYS_VISIBLE:
                visible_agents.append(
                    {
                        "agent_id": agent_id,
                        "name": config["name"],
                        "description": config["description"],
                        "priority": config["priority"],
                        "visibility_reason": "core_agent",
                    }
                )

            # Handle contextually visible agents (LUNA)
            elif visibility_level == VisibilityLevel.CONTEXTUALLY_VISIBLE:
                if agent_id == "luna":
                    luna_context = self.determine_luna_visibility(user_context)
                    visibility_config = config["visibility_contexts"][luna_context]

                    visible_agents.append(
                        {
                            "agent_id": agent_id,
                            "name": config["name"],
                            "description": config["description"],
                            "priority": config["priority"],
                            "visibility_reason": luna_context,
                            "visibility_config": visibility_config,
                            "adaptive_presentation": True,
                        }
                    )

        # Sort by priority
        visible_agents.sort(key=lambda x: x["priority"])

        return visible_agents

    def get_agent_presentation_config(
        self, agent_id: str, user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get presentation configuration for a specific agent.

        Args:
            agent_id: ID of the agent
            user_context: User context for adaptive presentation

        Returns:
            Dictionary with presentation configuration
        """
        if agent_id not in self.agent_visibility_config:
            return {"error": "Agent not found"}

        config = self.agent_visibility_config[agent_id].copy()

        # Special handling for LUNA's adaptive presentation
        if agent_id == "luna" and config.get("adaptive_presentation"):
            luna_context = self.determine_luna_visibility(user_context)
            config["current_context"] = luna_context
            config["presentation_style"] = self._get_luna_presentation_style(
                luna_context
            )

        return config

    def _get_luna_presentation_style(self, luna_context: str) -> Dict[str, Any]:
        """Get presentation style for LUNA based on context."""
        styles = {
            "primary_specialist": {
                "prominence": "high",
                "positioning": "top_section",
                "messaging": "Your dedicated women's health specialist",
                "icon_style": "featured",
                "call_to_action": "Explore women's wellness",
            },
            "activated_specialist": {
                "prominence": "high",
                "positioning": "relevant_section",
                "messaging": "Specialized expertise for your women's health question",
                "icon_style": "highlighted",
                "call_to_action": "Get specialized guidance",
            },
            "recommended_specialist": {
                "prominence": "medium",
                "positioning": "recommended_section",
                "messaging": "Expert in women's health for your family",
                "icon_style": "suggested",
                "call_to_action": "Learn about women's wellness",
            },
            "available_specialist": {
                "prominence": "low",
                "positioning": "available_section",
                "messaging": "Women's health specialist available",
                "icon_style": "standard",
                "call_to_action": "View all specialists",
            },
        }

        return styles.get(luna_context, styles["available_specialist"])

    def should_show_luna_notification(
        self, user_context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Determine if LUNA introduction notification should be shown.

        Args:
            user_context: User context

        Returns:
            Notification configuration if applicable, None otherwise
        """
        luna_context = self.determine_luna_visibility(user_context)

        if luna_context in ["activated_specialist", "recommended_specialist"]:
            return {
                "type": "luna_introduction",
                "context": luna_context,
                "message": self._get_luna_notification_message(luna_context),
                "show_duration": 5000,  # 5 seconds
                "dismissible": True,
            }

        return None

    def _get_luna_notification_message(self, context: str) -> str:
        """Get notification message for LUNA introduction."""
        messages = {
            "activated_specialist": "💫 LUNA, our women's health specialist, has expertise in this area and can provide specialized guidance.",
            "recommended_specialist": "🌙 LUNA specializes in women's health and can provide insights for the women in your life.",
        }

        return messages.get(context, "")


# Global visibility manager instance
visibility_manager = AgentVisibilityManager()
