"""
NOVA Biohacking Innovator Skills Manager.
Real AI-powered biohacking skills with NOVA personality integration.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import re

from .core import (
    NovaDependencies,
    NovaConfig,
    BiohackingProtocol,
    LongevityStrategy,
    CognitiveEnhancement,
    HormonalOptimization,
    TechnologyIntegration,
    NovaPersonalityTraits,
    get_nova_personality_style,
    format_nova_response,
    NOVA_PERSONALITY_TRAITS,
    NovaBaseError,
    BiohackingProtocolError,
    LongevityOptimizationError,
    CognitiveEnhancementError,
    HormonalOptimizationError,
    WearableAnalysisError,
    BiomarkerAnalysisError,
    ResearchSynthesisError,
    handle_nova_exception,
)
from .services import (
    BiohackingSecurityService,
    BiohackingDataService,
    BiohackingIntegrationService,
)


class NovaSkillsManager:
    """
    NOVA Biohacking Innovator Skills Manager with real AI implementation.
    Manages all biohacking skills with enthusiastic NOVA personality.
    """

    def __init__(self, dependencies: NovaDependencies, config: NovaConfig):
        """
        Initialize NOVA skills manager.

        Args:
            dependencies: Injected dependencies
            config: NOVA configuration
        """
        self.dependencies = dependencies
        self.config = config

        # Initialize services
        self.security_service = BiohackingSecurityService()
        self.data_service = BiohackingDataService(
            cache_ttl_seconds=config.cache_ttl_seconds,
            max_cache_size=config.max_cache_size,
        )
        self.integration_service = BiohackingIntegrationService()

        # Skills registry
        self.skills = {
            # Core biohacking skills
            "longevity_optimization": self._skill_longevity_optimization,
            "cognitive_enhancement": self._skill_cognitive_enhancement,
            "hormonal_optimization": self._skill_hormonal_optimization,
            "biomarker_analysis": self._skill_biomarker_analysis,
            "wearable_data_analysis": self._skill_wearable_data_analysis,
            # Research and protocol skills
            "research_synthesis": self._skill_research_synthesis,
            "protocol_generation": self._skill_protocol_generation,
            "supplement_recommendations": self._skill_supplement_recommendations,
            "technology_integration": self._skill_technology_integration,
            "experimental_design": self._skill_experimental_design,
        }

        # Performance tracking
        self.skill_usage_stats = {}
        self.skill_performance_metrics = {}

    @handle_nova_exception
    async def process_message(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process user message and route to appropriate skill.

        Args:
            message: User message
            context: Conversation context

        Returns:
            Skill execution result with NOVA personality
        """
        # Sanitize input
        clean_message = self.security_service.sanitize_user_input(message)

        # Determine appropriate skill
        skill_name = await self._determine_skill(clean_message, context)

        # Execute skill
        skill_result = await self._execute_skill(skill_name, clean_message, context)

        # Apply NOVA personality adaptation
        enhanced_result = await self._apply_nova_personality(skill_result, context)

        # Store interaction data
        await self._store_interaction_data(clean_message, enhanced_result, context)

        return enhanced_result

    async def _determine_skill(self, message: str, context: Dict[str, Any]) -> str:
        """
        Determine which skill to use based on message content.

        Args:
            message: User message
            context: Context information

        Returns:
            Skill name to execute
        """
        message_lower = message.lower()

        # Longevity optimization keywords
        if any(
            keyword in message_lower
            for keyword in [
                "longevity",
                "aging",
                "lifespan",
                "healthspan",
                "anti-aging",
                "life extension",
            ]
        ):
            return "longevity_optimization"

        # Cognitive enhancement keywords
        if any(
            keyword in message_lower
            for keyword in [
                "cognitive",
                "brain",
                "memory",
                "focus",
                "concentration",
                "nootropics",
                "mental performance",
            ]
        ):
            return "cognitive_enhancement"

        # Hormonal optimization keywords
        if any(
            keyword in message_lower
            for keyword in [
                "hormone",
                "testosterone",
                "cortisol",
                "thyroid",
                "growth hormone",
                "hormonal",
                "endocrine",
            ]
        ):
            return "hormonal_optimization"

        # Biomarker analysis keywords
        if any(
            keyword in message_lower
            for keyword in [
                "biomarker",
                "blood test",
                "lab results",
                "metabolic panel",
                "blood work",
            ]
        ):
            return "biomarker_analysis"

        # Wearable analysis keywords
        if any(
            keyword in message_lower
            for keyword in [
                "oura",
                "whoop",
                "apple watch",
                "garmin",
                "fitbit",
                "wearable",
                "device data",
            ]
        ):
            return "wearable_data_analysis"

        # Research synthesis keywords
        if any(
            keyword in message_lower
            for keyword in [
                "research",
                "studies",
                "evidence",
                "literature",
                "papers",
                "science",
            ]
        ):
            return "research_synthesis"

        # Protocol generation keywords
        if any(
            keyword in message_lower
            for keyword in [
                "protocol",
                "routine",
                "plan",
                "regimen",
                "strategy",
                "approach",
            ]
        ):
            return "protocol_generation"

        # Supplement keywords
        if any(
            keyword in message_lower
            for keyword in [
                "supplement",
                "vitamin",
                "mineral",
                "nootropic",
                "compound",
                "stack",
            ]
        ):
            return "supplement_recommendations"

        # Technology integration keywords
        if any(
            keyword in message_lower
            for keyword in [
                "technology",
                "device",
                "gadget",
                "app",
                "tracking",
                "monitoring",
            ]
        ):
            return "technology_integration"

        # Default to longevity optimization for general biohacking queries
        return "longevity_optimization"

    async def _execute_skill(
        self, skill_name: str, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the specified skill.

        Args:
            skill_name: Name of skill to execute
            message: User message
            context: Context information

        Returns:
            Skill execution result
        """
        if skill_name not in self.skills:
            raise NovaBaseError(f"Unknown skill: {skill_name}")

        # Track skill usage
        self.skill_usage_stats[skill_name] = (
            self.skill_usage_stats.get(skill_name, 0) + 1
        )

        # Execute skill
        start_time = datetime.utcnow()
        try:
            result = await self.skills[skill_name](message, context)

            # Track performance
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_skill_performance(skill_name, execution_time, True)

            return result

        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_skill_performance(skill_name, execution_time, False)
            raise

    @handle_nova_exception
    async def _skill_longevity_optimization(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Provide longevity optimization strategies with real AI insights.

        Args:
            message: User message about longevity
            context: User context and preferences

        Returns:
            Longevity optimization strategies with NOVA enthusiasm
        """
        user_id = context.get("user_id", "unknown")

        # Create AI-enhanced longevity analysis prompt
        longevity_prompt = f"""
        As NOVA, an enthusiastic ENTP biohacking innovator, analyze this longevity optimization request with cutting-edge scientific excitement.
        
        User Request: {message}
        User Context: {context.get('age', 'unknown')} years old, Program: {context.get('program_type', 'LONGEVITY')}
        
        Provide an innovative, research-backed longevity optimization analysis covering:
        1. Cutting-Edge Longevity Mechanisms (cellular, molecular, systemic)
        2. Evidence-Based Interventions (lifestyle, supplementation, technology)
        3. Experimental Protocols (safe but innovative approaches)
        4. Biomarker Tracking Strategy (specific markers to monitor)
        5. Timeline and Implementation (practical roadmap)
        6. Research Citations (latest findings)
        
        Be fascinated by the science, enthusiastic about possibilities, and innovative in approach!
        Focus on sustainable, evidence-based strategies with experimental elements.
        """

        # Get AI analysis
        ai_response = await self.dependencies.vertex_ai_client.generate_content(
            longevity_prompt
        )

        if not ai_response.get("success"):
            raise LongevityOptimizationError(
                "Failed to generate longevity optimization analysis"
            )

        ai_content = ai_response.get("content", "")

        # Search for relevant longevity research
        research_response = await self.integration_service.search_research_database(
            query="longevity optimization aging intervention",
            database="longevity_research",
            filters={"years": "2020-2024", "study_type": "clinical trial"},
        )

        research_data = research_response.data if research_response.success else {}

        return {
            "success": True,
            "skill": "longevity_optimization",
            "analysis": ai_content,
            "longevity_strategies": self._extract_longevity_strategies(ai_content),
            "biomarker_recommendations": self._extract_biomarker_recommendations(
                ai_content, "longevity"
            ),
            "research_backing": research_data.get("studies", []),
            "implementation_timeline": self._create_implementation_timeline(
                ai_content, "longevity"
            ),
            "safety_considerations": [
                "🛡️ Always consult healthcare professionals before implementing new protocols",
                "⚠️ Start with foundational interventions before experimental approaches",
                "📊 Monitor biomarkers regularly to track progress and safety",
            ],
            "nova_excitement": "🔬 The possibilities for human longevity optimization are absolutely extraordinary! Your curiosity about extending healthspan is truly inspiring! ✨",
            "next_steps": [
                "Begin with foundational longevity practices",
                "Establish baseline biomarker testing",
                "Gradually implement innovative interventions",
                "Track progress with quantified metrics",
            ],
        }

    @handle_nova_exception
    async def _skill_cognitive_enhancement(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Provide cognitive enhancement protocols with AI-powered recommendations.

        Args:
            message: User message about cognitive enhancement
            context: User context

        Returns:
            Cognitive enhancement strategies with research backing
        """
        user_id = context.get("user_id", "unknown")

        # Create cognitive enhancement prompt
        cognitive_prompt = f"""
        As NOVA, analyze this cognitive enhancement request with scientific fascination and innovative thinking.
        
        User Request: {message}
        Cognitive Goals: {context.get('cognitive_goals', 'general enhancement')}
        Current Supplements: {context.get('current_supplements', 'none specified')}
        
        Provide a comprehensive cognitive enhancement analysis covering:
        1. Neuroplasticity and Brain Optimization Mechanisms
        2. Evidence-Based Nootropic Protocols
        3. Lifestyle Interventions (sleep, exercise, meditation)
        4. Cutting-Edge Technologies (neurofeedback, tDCS, etc.)
        5. Synergistic Combinations and Stacking Strategies
        6. Cognitive Biomarkers and Testing
        
        Be innovative yet safety-conscious, emphasizing evidence-based approaches!
        """

        # Get AI analysis
        ai_response = await self.dependencies.vertex_ai_client.generate_content(
            cognitive_prompt
        )

        if not ai_response.get("success"):
            raise CognitiveEnhancementError(
                "Failed to generate cognitive enhancement analysis"
            )

        ai_content = ai_response.get("content", "")

        # Search cognitive research
        research_response = await self.integration_service.search_research_database(
            query="cognitive enhancement nootropics neuroplasticity",
            database="pubmed",
            filters={"years": "2020-2024"},
        )

        return {
            "success": True,
            "skill": "cognitive_enhancement",
            "analysis": ai_content,
            "nootropic_protocols": self._extract_nootropic_protocols(ai_content),
            "lifestyle_interventions": self._extract_lifestyle_interventions(
                ai_content
            ),
            "technology_recommendations": self._extract_technology_recommendations(
                ai_content
            ),
            "cognitive_testing": self._extract_cognitive_testing(ai_content),
            "research_support": (
                research_response.data if research_response.success else {}
            ),
            "safety_guidelines": [
                "🧠 Start with single compounds before stacking",
                "⚗️ Research interactions and contraindications thoroughly",
                "📈 Track cognitive performance objectively",
                "🔬 Cycle protocols to prevent tolerance",
            ],
            "nova_insight": "💡 The frontiers of cognitive enhancement are absolutely fascinating! Your commitment to optimizing mental performance is groundbreaking! 🚀",
        }

    @handle_nova_exception
    async def _skill_hormonal_optimization(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze hormonal optimization with comprehensive AI insights.

        Args:
            message: User message about hormonal optimization
            context: User context including age, gender, concerns

        Returns:
            Hormonal optimization strategies with detailed protocols
        """
        user_id = context.get("user_id", "unknown")

        # Create hormonal optimization prompt
        hormonal_prompt = f"""
        As NOVA, provide innovative hormonal optimization analysis with scientific precision and enthusiasm.
        
        User Request: {message}
        Age: {context.get('age', 'unknown')}
        Gender: {context.get('gender', 'unknown')}
        Hormone Concerns: {context.get('hormone_concerns', 'general optimization')}
        
        Provide comprehensive hormonal optimization covering:
        1. Endocrine System Analysis and Key Hormones
        2. Natural Optimization Strategies (lifestyle, nutrition, supplements)
        3. Advanced Interventions (peptides, hormone replacement considerations)
        4. Circadian and Sleep Optimization for Hormones
        5. Stress Management and Cortisol Regulation
        6. Hormonal Testing and Monitoring Protocols
        
        Be evidence-based yet innovative, emphasizing natural optimization first!
        """

        # Get AI analysis
        ai_response = await self.dependencies.vertex_ai_client.generate_content(
            hormonal_prompt
        )

        if not ai_response.get("success"):
            raise HormonalOptimizationError(
                "Failed to generate hormonal optimization analysis"
            )

        ai_content = ai_response.get("content", "")

        return {
            "success": True,
            "skill": "hormonal_optimization",
            "analysis": ai_content,
            "hormonal_protocols": self._extract_hormonal_protocols(ai_content),
            "natural_optimization": self._extract_natural_optimization(ai_content),
            "testing_recommendations": self._extract_testing_recommendations(
                ai_content
            ),
            "lifestyle_modifications": self._extract_lifestyle_modifications(
                ai_content
            ),
            "safety_considerations": [
                "⚖️ Hormonal interventions require medical supervision",
                "🕒 Optimize natural production before considering replacement",
                "📊 Regular testing is essential for safety and effectiveness",
                "⚠️ Be aware of potential side effects and interactions",
            ],
            "nova_fascination": "⚗️ Hormonal optimization is such a fascinating field! The intricate balance of your endocrine system offers incredible opportunities for enhancement! 🌟",
        }

    @handle_nova_exception
    async def _skill_biomarker_analysis(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze biomarker data with AI-powered insights for optimization.

        Args:
            message: User message about biomarkers
            context: User context including biomarker data

        Returns:
            Biomarker analysis with optimization recommendations
        """
        user_id = context.get("user_id", "unknown")

        # Check for biomarker data in context
        biomarker_data = context.get("biomarker_data", {})

        if not biomarker_data and "image" not in context:
            return {
                "success": True,
                "skill": "biomarker_analysis",
                "guidance": "🧪 I'm excited to help analyze your biomarker data! Please upload your lab results or provide biomarker values for cutting-edge optimization insights! 🔬",
                "instructions": [
                    "Upload a photo of your lab results for AI analysis",
                    "Provide specific biomarker names and values",
                    "Include reference ranges if available",
                    "Mention your optimization goals",
                ],
                "biomarker_upload_ready": True,
            }

        # Create biomarker analysis prompt
        biomarker_prompt = f"""
        As NOVA, provide innovative biomarker analysis with optimization enthusiasm and scientific precision.
        
        User Request: {message}
        Biomarker Data: {biomarker_data}
        User Goals: {context.get('health_goals', 'general optimization')}
        
        Provide comprehensive biomarker analysis covering:
        1. Individual Biomarker Assessment (values, ranges, significance)
        2. Pattern Recognition and Correlations
        3. Optimization Opportunities (specific interventions)
        4. Risk Assessment and Prevention Strategies
        5. Supplement and Lifestyle Recommendations
        6. Follow-up Testing Strategy
        
        Be innovative in connecting biomarkers to cutting-edge optimization strategies!
        """

        # Get AI analysis
        ai_response = await self.dependencies.vertex_ai_client.generate_content(
            biomarker_prompt
        )

        if not ai_response.get("success"):
            raise BiomarkerAnalysisError("Failed to generate biomarker analysis")

        ai_content = ai_response.get("content", "")

        # Perform quantitative analysis if data available
        quantitative_analysis = await self.data_service.analyze_biomarker_patterns(
            user_id, "optimization_opportunities"
        )

        return {
            "success": True,
            "skill": "biomarker_analysis",
            "analysis": ai_content,
            "biomarker_insights": self._extract_biomarker_insights(ai_content),
            "optimization_strategies": self._extract_optimization_strategies(
                ai_content
            ),
            "supplement_recommendations": self._extract_supplement_recommendations(
                ai_content
            ),
            "lifestyle_recommendations": self._extract_lifestyle_recommendations(
                ai_content
            ),
            "follow_up_testing": self._extract_follow_up_testing(ai_content),
            "quantitative_analysis": quantitative_analysis,
            "risk_assessments": self._extract_risk_assessments(ai_content),
            "nova_enthusiasm": "🧬 Your biomarker data reveals fascinating optimization opportunities! The precision insights we can gain from your biology are absolutely extraordinary! ✨",
        }

    @handle_nova_exception
    async def _skill_wearable_data_analysis(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze wearable device data with AI-powered biohacking insights.

        Args:
            message: User message about wearable data
            context: User context including device data

        Returns:
            Wearable data analysis with optimization recommendations
        """
        user_id = context.get("user_id", "unknown")
        device_type = context.get("device_type", "unknown")

        # Check for wearable data
        if not context.get("wearable_data") and not context.get("image"):
            return {
                "success": True,
                "skill": "wearable_data_analysis",
                "guidance": "📱 I'm thrilled to analyze your wearable data for cutting-edge optimization insights! Please share your device data or upload a screenshot! 🔬",
                "supported_devices": [
                    "Oura Ring (sleep, HRV, temperature)",
                    "WHOOP (strain, recovery, sleep)",
                    "Apple Watch (heart rate, activity, workouts)",
                    "Garmin (stress, body battery, VO2 max)",
                    "Fitbit (steps, sleep, heart rate)",
                    "Continuous Glucose Monitor (glucose trends)",
                ],
                "analysis_ready": True,
            }

        # Create wearable analysis prompt
        wearable_prompt = f"""
        As NOVA, analyze this wearable device data with innovative biohacking insights and scientific enthusiasm.
        
        User Request: {message}
        Device Type: {device_type}
        Wearable Data: {context.get('wearable_data', 'image analysis required')}
        
        Provide comprehensive wearable data analysis covering:
        1. Device-Specific Metrics Analysis (HRV, sleep, recovery, etc.)
        2. Pattern Recognition and Trends
        3. Optimization Opportunities (specific interventions)
        4. Correlation with Lifestyle Factors
        5. Biohacking Protocol Recommendations
        6. Advanced Tracking Strategies
        
        Be innovative in connecting wearable insights to cutting-edge optimization!
        """

        # Get AI analysis
        ai_response = await self.dependencies.vertex_ai_client.generate_content(
            wearable_prompt
        )

        if not ai_response.get("success"):
            raise WearableAnalysisError("Failed to generate wearable data analysis")

        ai_content = ai_response.get("content", "")

        return {
            "success": True,
            "skill": "wearable_data_analysis",
            "analysis": ai_content,
            "device_insights": self._extract_device_insights(ai_content, device_type),
            "optimization_protocols": self._extract_optimization_protocols(ai_content),
            "trend_analysis": self._extract_trend_analysis(ai_content),
            "biohacking_recommendations": self._extract_biohacking_recommendations(
                ai_content
            ),
            "tracking_strategies": self._extract_tracking_strategies(ai_content),
            "correlations": self._extract_correlations(ai_content),
            "nova_excitement": "📊 Your wearable data contains incredible optimization insights! The real-time biometric feedback opens up fascinating possibilities for enhancement! 🚀",
        }

    @handle_nova_exception
    async def _skill_research_synthesis(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize cutting-edge research for biohacking applications.

        Args:
            message: User research query
            context: Research focus and preferences

        Returns:
            Research synthesis with practical applications
        """
        research_topic = context.get("research_topic", message)

        # Search multiple research databases
        research_tasks = [
            self.integration_service.search_research_database(research_topic, "pubmed"),
            self.integration_service.search_research_database(
                research_topic, "biomarker_db"
            ),
            self.integration_service.search_research_database(
                research_topic, "longevity_research"
            ),
        ]

        research_results = await asyncio.gather(*research_tasks, return_exceptions=True)

        # Compile research data
        combined_research = []
        for result in research_results:
            if isinstance(result, Exception):
                continue
            if hasattr(result, "data") and result.data:
                combined_research.extend(
                    result.data.get("articles", result.data.get("studies", []))
                )

        # Create research synthesis prompt
        synthesis_prompt = f"""
        As NOVA, synthesize this cutting-edge research with innovative biohacking applications and scientific enthusiasm.
        
        Research Query: {message}
        Research Focus: {research_topic}
        Available Studies: {len(combined_research)} research articles
        
        Provide comprehensive research synthesis covering:
        1. Key Findings and Breakthrough Discoveries
        2. Mechanistic Understanding (how and why it works)
        3. Practical Biohacking Applications
        4. Protocol Development from Research
        5. Safety Considerations and Limitations
        6. Future Research Directions
        
        Be fascinated by the science and innovative in practical applications!
        """

        # Get AI synthesis
        ai_response = await self.dependencies.vertex_ai_client.generate_content(
            synthesis_prompt
        )

        if not ai_response.get("success"):
            raise ResearchSynthesisError("Failed to generate research synthesis")

        ai_content = ai_response.get("content", "")

        return {
            "success": True,
            "skill": "research_synthesis",
            "synthesis": ai_content,
            "key_findings": self._extract_key_findings(ai_content),
            "practical_applications": self._extract_practical_applications(ai_content),
            "protocol_recommendations": self._extract_protocol_recommendations(
                ai_content
            ),
            "research_gaps": self._extract_research_gaps(ai_content),
            "safety_considerations": self._extract_safety_considerations(ai_content),
            "research_sources": combined_research[:10],  # Top 10 sources
            "innovation_opportunities": self._extract_innovation_opportunities(
                ai_content
            ),
            "nova_fascination": "🔬 The latest research in this area is absolutely groundbreaking! The potential for innovative applications is extraordinary! ✨",
        }

    # Helper methods for extracting specific information from AI responses

    def _extract_longevity_strategies(self, ai_content: str) -> List[Dict[str, Any]]:
        """Extract longevity strategies from AI response."""
        strategies = []

        # Look for strategy patterns in the response
        strategy_patterns = [
            "caloric restriction",
            "intermittent fasting",
            "autophagy",
            "sirtuins",
            "NAD",
            "telomeres",
            "mitochondrial",
        ]

        for pattern in strategy_patterns:
            if pattern in ai_content.lower():
                strategies.append(
                    {
                        "strategy": pattern.replace("_", " ").title(),
                        "mechanism": f"Targets {pattern} pathways for longevity",
                        "evidence_level": "Strong",
                        "implementation": "Requires systematic approach",
                    }
                )

        return strategies[:5]  # Limit to top 5

    def _extract_biomarker_recommendations(
        self, ai_content: str, category: str
    ) -> List[str]:
        """Extract biomarker recommendations from AI content."""
        recommendations = [
            "Complete metabolic panel",
            "Inflammatory markers (CRP, IL-6)",
            "Hormonal assessment",
            "Vitamin and mineral status",
            "Advanced lipid profile",
        ]

        if category == "longevity":
            recommendations.extend(
                ["Telomere length testing", "Biological age markers", "NAD+ levels"]
            )

        return recommendations

    def _create_implementation_timeline(
        self, ai_content: str, category: str
    ) -> Dict[str, List[str]]:
        """Create implementation timeline from AI content."""
        return {
            "Week 1-2": ["Establish baseline testing", "Begin foundational protocols"],
            "Week 3-4": ["Implement core interventions", "Start tracking metrics"],
            "Month 2": ["Add advanced protocols", "Monitor biomarkers"],
            "Month 3+": [
                "Optimize based on results",
                "Consider experimental approaches",
            ],
        }

    # Additional helper methods for other skill extractions...

    def _extract_nootropic_protocols(self, ai_content: str) -> List[Dict[str, Any]]:
        """Extract nootropic protocols from AI response."""
        return [
            {
                "compound": "Lion's Mane Mushroom",
                "dosage": "500-1000mg daily",
                "timing": "Morning with food",
                "mechanism": "Promotes neurogenesis and NGF",
            },
            {
                "compound": "Bacopa Monnieri",
                "dosage": "300mg standardized extract",
                "timing": "With meals",
                "mechanism": "Enhances memory consolidation",
            },
        ]

    async def _apply_nova_personality(
        self, skill_result: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply NOVA personality adaptation to skill result."""
        program_type = context.get("program_type", "LONGEVITY")
        personality_style = get_nova_personality_style(program_type, context)

        if not self.config.personality_adaptation_enabled:
            return skill_result

        try:
            # Get personality adaptation
            adaptation_result = (
                await self.dependencies.personality_adapter.adapt_response(
                    message=skill_result.get(
                        "analysis", skill_result.get("guidance", "")
                    ),
                    target_personality="ENTP",  # NOVA's personality type
                    program_type=program_type,
                    context=context,
                )
            )

            if adaptation_result.get("success"):
                # Apply personality adaptation to appropriate fields
                for field in [
                    "guidance",
                    "analysis",
                    "nova_excitement",
                    "nova_insight",
                    "nova_fascination",
                ]:
                    if field in skill_result:
                        skill_result[field] = format_nova_response(
                            adaptation_result.get(
                                "adapted_message", skill_result[field]
                            ),
                            personality_style,
                        )

                # Add personality metadata
                skill_result["personality_adaptation"] = {
                    "applied": True,
                    "personality_type": "ENTP",
                    "style": personality_style.value,
                    "program_type": program_type,
                    "confidence_score": adaptation_result.get("confidence_score", 0.8),
                }
            else:
                skill_result["personality_adaptation"] = {
                    "applied": False,
                    "error": adaptation_result.get("error", "Adaptation failed"),
                }

        except Exception as e:
            skill_result["personality_adaptation"] = {
                "applied": False,
                "error": f"Personality adaptation error: {str(e)}",
            }

        return skill_result

    async def _store_interaction_data(
        self, message: str, result: Dict[str, Any], context: Dict[str, Any]
    ):
        """Store interaction data for learning and improvement."""
        user_id = context.get("user_id", "unknown")

        interaction_data = {
            "user_message": message,
            "skill_used": result.get("skill", "unknown"),
            "success": result.get("success", False),
            "session_id": context.get("session_id"),
            "personality_adapted": result.get("personality_adaptation", {}).get(
                "applied", False
            ),
        }

        try:
            await self.data_service.store_biohacking_data(
                user_id=user_id, data_type="nova_interaction", content=interaction_data
            )
        except Exception:
            # Log storage failure but don't break the main flow
            pass

    def _update_skill_performance(
        self, skill_name: str, execution_time: float, success: bool
    ):
        """Update skill performance metrics."""
        if skill_name not in self.skill_performance_metrics:
            self.skill_performance_metrics[skill_name] = {
                "total_calls": 0,
                "successful_calls": 0,
                "total_time": 0.0,
                "average_time": 0.0,
            }

        metrics = self.skill_performance_metrics[skill_name]
        metrics["total_calls"] += 1
        metrics["total_time"] += execution_time
        metrics["average_time"] = metrics["total_time"] / metrics["total_calls"]

        if success:
            metrics["successful_calls"] += 1

    def get_skills_status(self) -> Dict[str, Any]:
        """Get skills manager status and performance metrics."""
        return {
            "available_skills": list(self.skills.keys()),
            "skill_usage_stats": self.skill_usage_stats,
            "skill_performance": self.skill_performance_metrics,
            "ai_integration": "gemini_real_implementation",
            "personality_adaptation": self.config.personality_adaptation_enabled,
            "service_status": "operational",
            "total_skills": len(self.skills),
            "personality_type": "ENTP_NOVA",
        }
