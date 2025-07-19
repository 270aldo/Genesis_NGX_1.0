"""
Response Synthesis Skill
=======================

Synthesizes responses from multiple agents into coherent output.
"""

from typing import Dict, Any, List, Optional
import json

from agents.base.base_skill import BaseSkill
from core.logging_config import get_logger

logger = get_logger(__name__)


class ResponseSynthesisSkill(BaseSkill):
    """Skill for synthesizing multiple agent responses."""
    
    def __init__(self, vertex_client, synthesis_strategy: str = "intelligent"):
        super().__init__(
            name="response_synthesis",
            description="Synthesizes multiple agent responses into coherent output"
        )
        self.vertex_client = vertex_client
        self.synthesis_strategy = synthesis_strategy
    
    async def execute(
        self,
        agent_responses: Dict[str, Any],
        original_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Synthesize responses from multiple agents.
        
        Args:
            agent_responses: Dict of agent_id -> response
            original_request: The original user request
            context: Additional context
            
        Returns:
            Synthesized response
        """
        try:
            if not agent_responses:
                return {
                    "success": False,
                    "error": "No agent responses to synthesize"
                }
            
            # Single agent response - format and return
            if len(agent_responses) == 1:
                agent_id, response = list(agent_responses.items())[0]
                return self._format_single_response(agent_id, response)
            
            # Multiple agents - apply synthesis strategy
            if self.synthesis_strategy == "simple":
                return self._simple_synthesis(agent_responses)
            elif self.synthesis_strategy == "intelligent":
                return await self._intelligent_synthesis(agent_responses, original_request, context)
            elif self.synthesis_strategy == "consensus":
                return await self._consensus_synthesis(agent_responses, original_request)
            else:
                # Default to intelligent
                return await self._intelligent_synthesis(agent_responses, original_request, context)
                
        except Exception as e:
            logger.error(f"Response synthesis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "fallback": self._create_fallback_response(agent_responses)
            }
    
    def _format_single_response(self, agent_id: str, response: Any) -> Dict[str, Any]:
        """Format a single agent response."""
        # Extract agent name for attribution
        agent_names = {
            "elite_training_strategist": "BLAZE",
            "precision_nutrition_architect": "SAGE",
            "female_wellness_coach": "LUNA",
            "progress_tracker": "STELLA",
            "motivation_behavior_coach": "SPARK",
            "nova_biohacking_innovator": "NOVA",
            "wave_performance_analytics": "WAVE",
            "code_genetic_specialist": "CODE"
        }
        
        agent_name = agent_names.get(agent_id, agent_id.upper())
        
        # Handle different response formats
        if isinstance(response, dict):
            content = response.get("response", response.get("content", str(response)))
        else:
            content = str(response)
        
        return {
            "success": True,
            "response": content,
            "metadata": {
                "synthesis_type": "single_agent",
                "primary_agent": agent_name,
                "agents_consulted": [agent_id]
            }
        }
    
    def _simple_synthesis(self, agent_responses: Dict[str, Any]) -> Dict[str, Any]:
        """Simple concatenation synthesis."""
        combined_response = []
        
        for agent_id, response in agent_responses.items():
            agent_name = self._get_agent_name(agent_id)
            
            if isinstance(response, dict):
                content = response.get("response", response.get("content", ""))
            else:
                content = str(response)
            
            if content:
                combined_response.append(f"**{agent_name}**: {content}")
        
        return {
            "success": True,
            "response": "\n\n".join(combined_response),
            "metadata": {
                "synthesis_type": "simple",
                "agents_consulted": list(agent_responses.keys())
            }
        }
    
    async def _intelligent_synthesis(
        self,
        agent_responses: Dict[str, Any],
        original_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Intelligent AI-powered synthesis."""
        # Prepare responses for synthesis
        formatted_responses = self._format_responses_for_synthesis(agent_responses)
        
        # Build synthesis prompt
        prompt = self._build_synthesis_prompt(
            formatted_responses,
            original_request,
            context
        )
        
        # Generate synthesis
        response = await self.vertex_client.generate_content(
            prompt,
            temperature=0.7
        )
        
        synthesized_content = response.get("text", "").strip()
        
        # Post-process synthesis
        synthesized_content = self._post_process_synthesis(
            synthesized_content,
            agent_responses
        )
        
        return {
            "success": True,
            "response": synthesized_content,
            "metadata": {
                "synthesis_type": "intelligent",
                "agents_consulted": list(agent_responses.keys()),
                "synthesis_strategy": self._determine_synthesis_approach(agent_responses)
            }
        }
    
    async def _consensus_synthesis(
        self,
        agent_responses: Dict[str, Any],
        original_request: str
    ) -> Dict[str, Any]:
        """Consensus-based synthesis focusing on agreements."""
        # Extract key points from each response
        key_points = await self._extract_key_points(agent_responses)
        
        # Find consensus and conflicts
        consensus_points = self._find_consensus(key_points)
        conflicting_points = self._find_conflicts(key_points)
        
        # Build consensus response
        prompt = f"""Create a unified response based on these consensus points from multiple AI agents:

Original request: "{original_request}"

Consensus points (all agents agree):
{consensus_points}

Points of difference (resolve intelligently):
{conflicting_points}

Create a response that:
1. Emphasizes the consensus recommendations
2. Intelligently resolves conflicts with clear reasoning
3. Maintains a cohesive narrative
4. Provides clear action items"""
        
        response = await self.vertex_client.generate_content(
            prompt,
            temperature=0.6
        )
        
        return {
            "success": True,
            "response": response.get("text", "").strip(),
            "metadata": {
                "synthesis_type": "consensus",
                "agents_consulted": list(agent_responses.keys()),
                "consensus_points": len(consensus_points.split("\n")),
                "conflict_points": len(conflicting_points.split("\n"))
            }
        }
    
    def _format_responses_for_synthesis(self, agent_responses: Dict[str, Any]) -> str:
        """Format agent responses for synthesis prompt."""
        formatted = []
        
        for agent_id, response in agent_responses.items():
            agent_name = self._get_agent_name(agent_id)
            
            if isinstance(response, dict):
                # Extract different possible content fields
                content = (
                    response.get("response") or
                    response.get("content") or
                    response.get("message") or
                    json.dumps(response)
                )
                
                # Add any important metadata
                if response.get("confidence"):
                    content += f"\n(Confidence: {response['confidence']})"
                if response.get("recommendations"):
                    content += f"\nRecommendations: {response['recommendations']}"
            else:
                content = str(response)
            
            formatted.append(f"{agent_name} Response:\n{content}")
        
        return "\n\n---\n\n".join(formatted)
    
    def _build_synthesis_prompt(
        self,
        formatted_responses: str,
        original_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build the synthesis prompt."""
        context_info = ""
        if context:
            if context.get("user_program"):
                program = context["user_program"]
                context_info += f"\nUser Program: {program} "
                context_info += "(Focus on high-performance optimization)" if program == "PRIME" else "(Focus on sustainable wellness)"
            
            if context.get("user_goals"):
                context_info += f"\nUser Goals: {context['user_goals']}"
        
        return f"""Synthesize these expert responses into a single, coherent response:

Original User Request: "{original_request}"
{context_info}

Expert Responses:
{formatted_responses}

Create a unified response that:
1. Integrates insights from all experts coherently
2. Resolves any contradictions intelligently
3. Prioritizes recommendations by impact
4. Maintains a consistent, encouraging tone
5. Provides clear, actionable next steps
6. Adds value beyond just combining responses

IMPORTANT:
- Do NOT just list what each expert said
- Create a flowing narrative that tells a complete story
- Connect recommendations to the user's goals
- Use "we" language to show unified guidance
- End with 2-3 specific action items

Response:"""
    
    def _post_process_synthesis(
        self,
        synthesized_content: str,
        agent_responses: Dict[str, Any]
    ) -> str:
        """Post-process the synthesized response."""
        # Add agent attribution if not present
        if not any(self._get_agent_name(agent) in synthesized_content for agent in agent_responses.keys()):
            agents_consulted = [self._get_agent_name(agent) for agent in agent_responses.keys()]
            attribution = f"\n\n*This recommendation combines insights from: {', '.join(agents_consulted)}*"
            synthesized_content += attribution
        
        # Ensure action items are clear
        if "action" not in synthesized_content.lower() and "next step" not in synthesized_content.lower():
            synthesized_content += "\n\n**Next Steps:**\n1. Start with the highest-impact recommendation\n2. Track your progress\n3. Adjust based on results"
        
        return synthesized_content
    
    async def _extract_key_points(self, agent_responses: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract key points from each agent response."""
        key_points = {}
        
        for agent_id, response in agent_responses.items():
            prompt = f"""Extract 3-5 key points from this response:

{response}

List only the main recommendations or insights, one per line."""
            
            extraction = await self.vertex_client.generate_content(
                prompt,
                temperature=0.3
            )
            
            points = [
                point.strip()
                for point in extraction.get("text", "").split("\n")
                if point.strip()
            ]
            
            key_points[agent_id] = points
        
        return key_points
    
    def _find_consensus(self, key_points: Dict[str, List[str]]) -> str:
        """Find consensus points across agents."""
        # This is a simplified implementation
        # In production, use more sophisticated similarity matching
        
        all_points = []
        for points in key_points.values():
            all_points.extend(points)
        
        # For now, return placeholder
        return "- Focus on consistency and gradual progress\n- Track metrics regularly\n- Prioritize recovery and rest"
    
    def _find_conflicts(self, key_points: Dict[str, List[str]]) -> str:
        """Find conflicting points across agents."""
        # Simplified implementation
        return "- Intensity levels may vary based on individual capacity\n- Nutritional needs depend on activity level"
    
    def _determine_synthesis_approach(self, agent_responses: Dict[str, Any]) -> str:
        """Determine the synthesis approach used."""
        response_types = set()
        
        for response in agent_responses.values():
            if isinstance(response, dict):
                if "plan" in response or "program" in response:
                    response_types.add("planning")
                elif "analysis" in response:
                    response_types.add("analytical")
                elif "recommendations" in response:
                    response_types.add("advisory")
        
        if len(response_types) > 1:
            return "multi-modal integration"
        elif "planning" in response_types:
            return "unified planning"
        elif "analytical" in response_types:
            return "comprehensive analysis"
        else:
            return "holistic guidance"
    
    def _get_agent_name(self, agent_id: str) -> str:
        """Get friendly agent name."""
        agent_names = {
            "elite_training_strategist": "BLAZE",
            "precision_nutrition_architect": "SAGE",
            "female_wellness_coach": "LUNA",
            "progress_tracker": "STELLA",
            "motivation_behavior_coach": "SPARK",
            "nova_biohacking_innovator": "NOVA",
            "wave_performance_analytics": "WAVE",
            "code_genetic_specialist": "CODE"
        }
        return agent_names.get(agent_id, agent_id.replace("_", " ").title())
    
    def _create_fallback_response(self, agent_responses: Dict[str, Any]) -> str:
        """Create fallback response when synthesis fails."""
        responses = []
        for agent_id, response in agent_responses.items():
            agent_name = self._get_agent_name(agent_id)
            content = str(response)[:200] + "..."
            responses.append(f"{agent_name}: {content}")
        
        return "Here's what our experts recommend:\n\n" + "\n\n".join(responses)