"""
Semantic Similarity Validation for AI Agent Responses

Provides comprehensive validation of AI response quality using:
- Semantic similarity comparison
- Domain-specific keyword analysis
- Response structure validation
- Quality scoring algorithms
"""

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

# For production use, these would be actual ML libraries
# For now, we'll implement basic similarity functions
# import openai  # For embeddings
# import sentence_transformers
# from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


@dataclass
class SemanticValidationResult:
    """Result of semantic validation"""

    query: str
    response: str
    agent_name: str
    similarity_score: float
    quality_score: float
    keyword_score: float
    structure_score: float
    overall_score: float
    issues: List[str]
    recommendations: List[str]
    timestamp: datetime

    def is_valid(self, threshold: float = 0.7) -> bool:
        """Check if response meets quality threshold"""
        return self.overall_score >= threshold

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting"""
        return {
            "query": self.query,
            "response": (
                self.response[:200] + "..."
                if len(self.response) > 200
                else self.response
            ),
            "agent_name": self.agent_name,
            "similarity_score": round(self.similarity_score, 3),
            "quality_score": round(self.quality_score, 3),
            "keyword_score": round(self.keyword_score, 3),
            "structure_score": round(self.structure_score, 3),
            "overall_score": round(self.overall_score, 3),
            "is_valid": self.is_valid(),
            "issues": self.issues,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp.isoformat(),
        }


class SemanticValidator:
    """
    Semantic validation engine for AI agent responses

    Provides comprehensive quality assessment including:
    - Semantic similarity to expected patterns
    - Domain-specific keyword validation
    - Response structure analysis
    - Quality scoring and recommendations
    """

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.agent_profiles = self._load_agent_profiles()
        self.golden_responses = self._load_golden_responses()

        # Initialize embedding models (mock for now)
        # self.embedding_model = sentence_transformers.SentenceTransformer('all-MiniLM-L6-v2')

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load semantic validation configuration"""
        default_config = {
            "quality_thresholds": {
                "blaze": {
                    "semantic_similarity": 0.85,
                    "min_response_length": 100,
                    "max_response_length": 2000,
                    "required_keywords_min": 2,
                    "safety_check": True,
                },
                "sage": {
                    "semantic_similarity": 0.80,
                    "min_response_length": 80,
                    "max_response_length": 1500,
                    "required_keywords_min": 2,
                    "health_compliance": True,
                },
                "stella": {
                    "semantic_similarity": 0.75,
                    "min_response_length": 60,
                    "max_response_length": 1000,
                    "required_keywords_min": 1,
                    "data_accuracy": True,
                },
                "orchestrator": {
                    "semantic_similarity": 0.70,
                    "min_response_length": 80,
                    "max_response_length": 2500,
                    "required_keywords_min": 1,
                    "coordination_check": True,
                },
            },
            "scoring_weights": {
                "semantic_similarity": 0.4,
                "keyword_relevance": 0.3,
                "response_structure": 0.2,
                "domain_expertise": 0.1,
            },
        }

        if config_path and Path(config_path).exists():
            with open(config_path, "r") as f:
                custom_config = json.load(f)
                default_config.update(custom_config)

        return default_config

    def _load_agent_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Load agent-specific validation profiles"""
        return {
            "blaze": {
                "keywords": [
                    "workout",
                    "exercise",
                    "training",
                    "muscle",
                    "strength",
                    "rep",
                    "set",
                    "program",
                    "routine",
                    "progressive",
                    "overload",
                    "compound",
                    "isolation",
                    "form",
                    "technique",
                    "recovery",
                    "rest",
                    "intensity",
                    "volume",
                ],
                "negative_keywords": [
                    "injury",
                    "pain",
                    "medical",
                    "dangerous",
                    "harmful",
                ],
                "structure_patterns": [
                    r"\b(?:exercise|workout|training)\b.*plan",
                    r"\b(?:sets?|reps?)\b",
                    r"\b(?:week|day)s?\b.*\d+",
                    r"\b(?:beginner|intermediate|advanced)\b",
                ],
                "safety_patterns": [
                    r"\bproper\s+form\b",
                    r"\bwarm\s*up\b",
                    r"\bprogressive\b",
                    r"\bconsult.*doctor\b",
                ],
            },
            "sage": {
                "keywords": [
                    "nutrition",
                    "diet",
                    "meal",
                    "calories",
                    "protein",
                    "carbs",
                    "fat",
                    "macro",
                    "micro",
                    "vitamins",
                    "minerals",
                    "healthy",
                    "balanced",
                    "portion",
                    "serving",
                    "intake",
                    "nutritional",
                    "food",
                    "eating",
                ],
                "negative_keywords": [
                    "starve",
                    "extreme",
                    "dangerous",
                    "medical",
                    "diagnose",
                    "medication",
                ],
                "structure_patterns": [
                    r"\bcalories?\b",
                    r"\b(?:protein|carb|fat)s?\b",
                    r"\bmeal\s+plan\b",
                    r"\b(?:breakfast|lunch|dinner|snack)\b",
                    r"\bserving\s+size\b",
                ],
                "health_patterns": [
                    r"\bbalanced\s+diet\b",
                    r"\bnutrient\s+dense\b",
                    r"\bmoderation\b",
                    r"\bconsult.*nutritionist\b",
                ],
            },
            "stella": {
                "keywords": [
                    "progress",
                    "tracking",
                    "goal",
                    "metric",
                    "improvement",
                    "achievement",
                    "milestone",
                    "measurement",
                    "data",
                    "trend",
                    "analysis",
                    "report",
                    "performance",
                    "results",
                    "statistics",
                    "comparison",
                ],
                "structure_patterns": [
                    r"\b\d+%\b",
                    r"\b(?:week|month|day)s?\s+\d+\b",
                    r"\bgoal.*(?:reached|achieved|met)\b",
                    r"\bimprove.*by\b",
                ],
                "data_patterns": [
                    r"\b\d+\s*(?:kg|lb|%|cm|inch)\b",
                    r"\b(?:increased|decreased|improved)\b.*\d+",
                    r"\baverage.*\d+",
                    r"\btrend.*(?:up|down|stable)\b",
                ],
            },
        }

    def _load_golden_responses(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load golden response examples for comparison"""
        # In production, this would load from a database or file
        return {
            "blaze_training_beginner": [
                {
                    "query_type": "muscle_building_beginner",
                    "expected_elements": [
                        "exercise_selection",
                        "rep_ranges",
                        "progression",
                    ],
                    "sample_response": "For muscle building as a beginner, focus on compound exercises like squats, deadlifts, and push-ups. Start with 3 sets of 8-12 reps...",
                    "quality_score": 0.95,
                }
            ],
            "sage_nutrition_weight_loss": [
                {
                    "query_type": "weight_loss_meal_plan",
                    "expected_elements": [
                        "caloric_deficit",
                        "balanced_macros",
                        "meal_timing",
                    ],
                    "sample_response": "For healthy weight loss, create a moderate caloric deficit of 300-500 calories. Focus on protein-rich foods...",
                    "quality_score": 0.90,
                }
            ],
            "stella_progress_tracking": [
                {
                    "query_type": "fitness_progress_analysis",
                    "expected_elements": [
                        "metric_analysis",
                        "trend_identification",
                        "recommendations",
                    ],
                    "sample_response": "Your fitness progress shows a 15% strength improvement over the past month. Key achievements include...",
                    "quality_score": 0.88,
                }
            ],
        }

    async def validate_response(
        self,
        query: str,
        response: str,
        agent_name: str,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> SemanticValidationResult:
        """
        Validate AI response quality and semantic appropriateness

        Args:
            query: User's original query
            response: AI agent's response
            agent_name: Name of the responding agent
            user_context: Optional user context information

        Returns:
            SemanticValidationResult with comprehensive quality assessment
        """
        agent_key = self._normalize_agent_name(agent_name)
        agent_profile = self.agent_profiles.get(agent_key, {})
        thresholds = self.config["quality_thresholds"].get(agent_key, {})

        # Calculate individual scores
        similarity_score = await self._calculate_semantic_similarity(
            query, response, agent_key
        )
        keyword_score = self._calculate_keyword_score(response, agent_profile)
        structure_score = self._calculate_structure_score(response, agent_profile)
        quality_score = self._calculate_quality_score(response, thresholds)

        # Calculate overall score with weights
        weights = self.config["scoring_weights"]
        overall_score = (
            similarity_score * weights["semantic_similarity"]
            + keyword_score * weights["keyword_relevance"]
            + structure_score * weights["response_structure"]
            + quality_score * weights["domain_expertise"]
        )

        # Identify issues and recommendations
        issues = self._identify_issues(response, agent_profile, thresholds)
        recommendations = self._generate_recommendations(issues, agent_key)

        return SemanticValidationResult(
            query=query,
            response=response,
            agent_name=agent_name,
            similarity_score=similarity_score,
            quality_score=quality_score,
            keyword_score=keyword_score,
            structure_score=structure_score,
            overall_score=overall_score,
            issues=issues,
            recommendations=recommendations,
            timestamp=datetime.utcnow(),
        )

    async def _calculate_semantic_similarity(
        self, query: str, response: str, agent_key: str
    ) -> float:
        """
        Calculate semantic similarity between query and response

        In production, this would use embeddings from models like:
        - OpenAI embeddings
        - Sentence-BERT
        - Universal Sentence Encoder
        """
        # Mock implementation - would use actual embeddings
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())

        # Basic Jaccard similarity as placeholder
        intersection = len(query_words.intersection(response_words))
        union = len(query_words.union(response_words))

        basic_similarity = intersection / union if union > 0 else 0

        # Enhance with domain-specific matching
        agent_keywords = self.agent_profiles.get(agent_key, {}).get("keywords", [])
        domain_matches = sum(
            1 for keyword in agent_keywords if keyword in response.lower()
        )
        domain_boost = (
            min(domain_matches / len(agent_keywords), 0.5) if agent_keywords else 0
        )

        return min(basic_similarity + domain_boost, 1.0)

    def _calculate_keyword_score(
        self, response: str, agent_profile: Dict[str, Any]
    ) -> float:
        """Calculate relevance score based on domain-specific keywords"""
        keywords = agent_profile.get("keywords", [])
        negative_keywords = agent_profile.get("negative_keywords", [])

        if not keywords:
            return 0.5  # Neutral score if no keywords defined

        response_lower = response.lower()

        # Count positive keywords
        positive_matches = sum(1 for keyword in keywords if keyword in response_lower)
        positive_score = min(positive_matches / len(keywords), 1.0)

        # Penalize negative keywords
        negative_matches = sum(
            1 for keyword in negative_keywords if keyword in response_lower
        )
        negative_penalty = min(negative_matches * 0.2, 0.5)

        return max(positive_score - negative_penalty, 0.0)

    def _calculate_structure_score(
        self, response: str, agent_profile: Dict[str, Any]
    ) -> float:
        """Calculate score based on response structure and formatting"""
        structure_patterns = agent_profile.get("structure_patterns", [])

        if not structure_patterns:
            # Basic structure checks
            score = 0.0

            # Check for reasonable length
            if 50 <= len(response) <= 2000:
                score += 0.3

            # Check for proper sentences
            if response.count(".") >= 2:
                score += 0.2

            # Check for organization (lists, numbers, etc.)
            if re.search(r"\b\d+\.", response) or response.count("\n") >= 2:
                score += 0.3

            # Check for engagement (questions, calls to action)
            if "?" in response or any(
                word in response.lower() for word in ["you", "your", "try", "consider"]
            ):
                score += 0.2

            return min(score, 1.0)

        # Use agent-specific patterns
        pattern_matches = sum(
            1
            for pattern in structure_patterns
            if re.search(pattern, response, re.IGNORECASE)
        )
        return min(pattern_matches / len(structure_patterns), 1.0)

    def _calculate_quality_score(
        self, response: str, thresholds: Dict[str, Any]
    ) -> float:
        """Calculate overall quality score based on various factors"""
        score = 0.0

        # Length appropriateness
        min_length = thresholds.get("min_response_length", 50)
        max_length = thresholds.get("max_response_length", 2000)

        if min_length <= len(response) <= max_length:
            score += 0.3
        elif len(response) < min_length:
            score += max(0, 0.3 * (len(response) / min_length))
        else:  # Too long
            score += max(0, 0.3 * (max_length / len(response)))

        # Completeness (addresses the query)
        if len(response.split(".")) >= 3:  # Multiple sentences
            score += 0.2

        # Actionability (provides specific advice)
        actionable_words = [
            "should",
            "can",
            "try",
            "recommend",
            "suggest",
            "start",
            "focus",
            "consider",
        ]
        if any(word in response.lower() for word in actionable_words):
            score += 0.2

        # Specificity (includes numbers, examples)
        if re.search(r"\b\d+\b", response):
            score += 0.15

        # Personalization (uses "you", "your")
        personal_pronouns = response.lower().count("you") + response.lower().count(
            "your"
        )
        if personal_pronouns >= 2:
            score += 0.15

        return min(score, 1.0)

    def _identify_issues(
        self, response: str, agent_profile: Dict[str, Any], thresholds: Dict[str, Any]
    ) -> List[str]:
        """Identify specific issues with the response"""
        issues = []

        # Length issues
        min_length = thresholds.get("min_response_length", 50)
        max_length = thresholds.get("max_response_length", 2000)

        if len(response) < min_length:
            issues.append(
                f"Response too short ({len(response)} chars, min {min_length})"
            )
        elif len(response) > max_length:
            issues.append(
                f"Response too long ({len(response)} chars, max {max_length})"
            )

        # Keyword issues
        keywords = agent_profile.get("keywords", [])
        negative_keywords = agent_profile.get("negative_keywords", [])
        required_min = thresholds.get("required_keywords_min", 1)

        response_lower = response.lower()
        keyword_matches = sum(1 for keyword in keywords if keyword in response_lower)

        if keyword_matches < required_min:
            issues.append(
                f"Insufficient domain keywords ({keyword_matches}/{required_min})"
            )

        # Negative keyword check
        for neg_keyword in negative_keywords:
            if neg_keyword in response_lower:
                issues.append(f"Contains concerning term: '{neg_keyword}'")

        # Structure issues
        if not re.search(r"[.!?]", response):
            issues.append("Response lacks proper sentence structure")

        if response.count("\n") == 0 and len(response) > 200:
            issues.append("Long response lacks paragraph breaks")

        # Safety checks for specific agents
        if thresholds.get("safety_check"):
            safety_patterns = agent_profile.get("safety_patterns", [])
            if not any(
                re.search(pattern, response, re.IGNORECASE)
                for pattern in safety_patterns
            ):
                issues.append("Response may lack safety considerations")

        return issues

    def _generate_recommendations(self, issues: List[str], agent_key: str) -> List[str]:
        """Generate improvement recommendations based on identified issues"""
        recommendations = []

        for issue in issues:
            if "too short" in issue:
                recommendations.append(
                    f"Expand response with more detailed {agent_key}-specific advice"
                )
            elif "too long" in issue:
                recommendations.append(
                    "Break response into more concise, focused paragraphs"
                )
            elif "domain keywords" in issue:
                keywords = self.agent_profiles.get(agent_key, {}).get("keywords", [])
                sample_keywords = keywords[:3] if keywords else []
                recommendations.append(
                    f"Include more {agent_key}-specific terms like: {', '.join(sample_keywords)}"
                )
            elif "concerning term" in issue:
                recommendations.append(
                    "Review response for potential safety concerns and disclaimer needs"
                )
            elif "sentence structure" in issue:
                recommendations.append(
                    "Improve response formatting with proper punctuation and structure"
                )
            elif "paragraph breaks" in issue:
                recommendations.append("Add paragraph breaks to improve readability")
            elif "safety considerations" in issue:
                recommendations.append(
                    "Add appropriate safety disclaimers and form reminders"
                )

        # General recommendations based on agent type
        agent_specific_recs = {
            "blaze": [
                "Include specific rep ranges and set recommendations",
                "Mention proper form and progression principles",
                "Add safety disclaimers for exercise recommendations",
            ],
            "sage": [
                "Include specific nutritional values when relevant",
                "Mention balanced macro distribution",
                "Add disclaimers about individual dietary needs",
            ],
            "stella": [
                "Include specific metrics and measurement methods",
                "Provide comparative analysis when possible",
                "Suggest actionable next steps for improvement",
            ],
        }

        if not recommendations and agent_key in agent_specific_recs:
            recommendations.extend(
                agent_specific_recs[agent_key][:1]
            )  # Add one general recommendation

        return recommendations

    def _normalize_agent_name(self, agent_name: str) -> str:
        """Normalize agent name to standard key"""
        name_lower = agent_name.lower()

        if "blaze" in name_lower or "training" in name_lower:
            return "blaze"
        elif "sage" in name_lower or "nutrition" in name_lower:
            return "sage"
        elif "stella" in name_lower or "progress" in name_lower:
            return "stella"
        elif "orchestrator" in name_lower:
            return "orchestrator"
        else:
            return "general"

    def generate_quality_report(
        self, results: List[SemanticValidationResult]
    ) -> Dict[str, Any]:
        """Generate comprehensive quality report from validation results"""
        if not results:
            return {"error": "No validation results provided"}

        total_results = len(results)
        valid_results = [r for r in results if r.is_valid()]

        # Overall statistics
        avg_scores = {
            "similarity": np.mean([r.similarity_score for r in results]),
            "keyword": np.mean([r.keyword_score for r in results]),
            "structure": np.mean([r.structure_score for r in results]),
            "quality": np.mean([r.quality_score for r in results]),
            "overall": np.mean([r.overall_score for r in results]),
        }

        # Agent-specific analysis
        agents = {}
        for result in results:
            agent_key = self._normalize_agent_name(result.agent_name)
            if agent_key not in agents:
                agents[agent_key] = []
            agents[agent_key].append(result)

        agent_stats = {}
        for agent, agent_results in agents.items():
            agent_stats[agent] = {
                "total_responses": len(agent_results),
                "valid_responses": len([r for r in agent_results if r.is_valid()]),
                "avg_overall_score": np.mean([r.overall_score for r in agent_results]),
                "common_issues": self._get_common_issues(agent_results),
            }

        # Issue analysis
        all_issues = []
        for result in results:
            all_issues.extend(result.issues)

        issue_frequency = {}
        for issue in all_issues:
            issue_type = self._categorize_issue(issue)
            issue_frequency[issue_type] = issue_frequency.get(issue_type, 0) + 1

        return {
            "summary": {
                "total_responses": total_results,
                "valid_responses": len(valid_results),
                "validation_rate": (
                    len(valid_results) / total_results if total_results > 0 else 0
                ),
                "average_scores": {k: round(v, 3) for k, v in avg_scores.items()},
            },
            "agent_performance": agent_stats,
            "common_issues": dict(
                sorted(issue_frequency.items(), key=lambda x: x[1], reverse=True)
            ),
            "recommendations": self._generate_global_recommendations(results),
            "generated_at": datetime.utcnow().isoformat(),
        }

    def _get_common_issues(self, results: List[SemanticValidationResult]) -> List[str]:
        """Get most common issues for a set of results"""
        issues = []
        for result in results:
            issues.extend(result.issues)

        issue_counts = {}
        for issue in issues:
            issue_type = self._categorize_issue(issue)
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1

        # Return top 3 most common issues
        return [
            issue
            for issue, _ in sorted(
                issue_counts.items(), key=lambda x: x[1], reverse=True
            )[:3]
        ]

    def _categorize_issue(self, issue: str) -> str:
        """Categorize issue into general types"""
        issue_lower = issue.lower()

        if "length" in issue_lower or "short" in issue_lower or "long" in issue_lower:
            return "Response Length"
        elif "keyword" in issue_lower:
            return "Domain Relevance"
        elif "structure" in issue_lower or "sentence" in issue_lower:
            return "Response Structure"
        elif "safety" in issue_lower or "concerning" in issue_lower:
            return "Safety Concerns"
        else:
            return "Other"

    def _generate_global_recommendations(
        self, results: List[SemanticValidationResult]
    ) -> List[str]:
        """Generate global recommendations based on all results"""
        all_recommendations = []
        for result in results:
            all_recommendations.extend(result.recommendations)

        # Count recommendation frequency
        rec_counts = {}
        for rec in all_recommendations:
            rec_counts[rec] = rec_counts.get(rec, 0) + 1

        # Return top recommendations
        top_recs = [
            rec
            for rec, _ in sorted(rec_counts.items(), key=lambda x: x[1], reverse=True)[
                :5
            ]
        ]

        if not top_recs:
            top_recs = [
                "Continue monitoring response quality across all agents",
                "Consider expanding training data for underperforming categories",
                "Implement regular quality threshold reviews",
            ]

        return top_recs
