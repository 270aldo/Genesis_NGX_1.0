"""
GENESIS NGX Agents - CODEX.072 Hybrid Intelligence Integration
=============================================================

Integration module for the CODEX.072 agent (Genetic Specialist) with the
Hybrid Intelligence Engine. This module provides specialized personalization
for genetic analysis, polymorphism interpretation, and genomic wellness.

Author: Claude AI Assistant
Version: 1.0.0
Created: 2025-01-10
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import json
import logging
from enum import Enum

# Import hybrid intelligence components
from core.hybrid_intelligence import (
    HybridIntelligenceEngine,
    UserProfile,
    PersonalizationContext,
    PersonalizationResult,
    UserArchetype,
    PersonalizationMode
)

# Import data models
from core.hybrid_intelligence.models import (
    UserProfileData,
    PersonalizationContextData,
    HybridIntelligenceRequest,
    HybridIntelligenceResponse,
    UserBiometrics
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeneticTestType(Enum):
    """Types of genetic tests for personalization"""
    HEALTH_PREDISPOSITION = "health_predisposition"
    PHARMACOGENOMICS = "pharmacogenomics"
    NUTRIGENOMICS = "nutrigenomics"
    FITNESS_GENETICS = "fitness_genetics"
    TRAIT_ANALYSIS = "trait_analysis"
    ANCESTRY = "ancestry"


class RiskLevel(Enum):
    """Genetic risk level classifications"""
    LOW = "low"
    MODERATE_LOW = "moderate_low"
    MODERATE = "moderate"
    MODERATE_HIGH = "moderate_high"
    HIGH = "high"
    UNKNOWN = "unknown"


class GeneticComplexity(Enum):
    """Complexity levels for genetic information presentation"""
    SIMPLE = "simple"           # Basic explanations
    INTERMEDIATE = "intermediate"  # Moderate detail
    ADVANCED = "advanced"       # Technical detail
    CLINICAL = "clinical"       # Medical professional level


class CODEXHybridIntelligenceIntegration:
    """
    Integration layer between CODEX.072 agent and Hybrid Intelligence Engine
    
    Specialized for genetic analysis with advanced personalization:
    - Archetype-specific genetic risk communication
    - Complexity-adapted genetic information presentation
    - Personalized intervention recommendations based on genetics
    - Privacy-conscious genetic counseling approaches
    - Culturally sensitive genetic interpretation
    """
    
    def __init__(self):
        """Initialize CODEX.072 Hybrid Intelligence Integration"""
        self.engine = HybridIntelligenceEngine()
        self.integration_name = "CODEX_GENETIC_SPECIALIST_HYBRID_INTELLIGENCE"
        self.version = "1.0.0"
        
        logger.info(f"Initialized {self.integration_name} v{self.version}")
    
    async def personalize_genetic_analysis(
        self,
        genetic_data: Dict[str, Any],
        user_profile: Dict[str, Any],
        analysis_focus: Optional[str] = "comprehensive"
    ) -> PersonalizationResult:
        """
        Personalize genetic analysis presentation based on user archetype and preferences
        
        Args:
            genetic_data: Raw genetic test results and polymorphisms
            user_profile: Complete user profile
            analysis_focus: Focus area for analysis (health, fitness, nutrition, etc.)
            
        Returns:
            PersonalizationResult with personalized genetic insights
        """
        try:
            # Assess genetic data complexity and risk levels
            complexity_assessment = self._assess_genetic_complexity(genetic_data)
            risk_profile = self._calculate_genetic_risk_profile(genetic_data)
            actionable_variants = self._identify_actionable_variants(genetic_data, user_profile)
            
            # Create genetic analysis context
            context = PersonalizationContext(
                user_profile=UserProfile.from_dict(user_profile),
                agent_type="code_genetic_specialist",
                request_type="genetic_analysis",
                session_data={
                    "genetic_data": genetic_data,
                    "analysis_focus": analysis_focus,
                    "complexity_assessment": complexity_assessment,
                    "risk_profile": risk_profile,
                    "actionable_variants": actionable_variants,
                    "analysis_timestamp": datetime.now().isoformat()
                }
            )
            
            # Execute hybrid intelligence personalization
            result = await self.engine.personalize_for_user(
                context=context,
                mode=PersonalizationMode.ADVANCED
            )
            
            # Apply genetics-specific enhancements
            enhanced_result = self._apply_genetic_analysis_enhancements(
                result, complexity_assessment, risk_profile, actionable_variants
            )
            
            logger.info(f"Genetic analysis personalized for {len(actionable_variants)} actionable variants")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error in personalized genetic analysis: {e}")
            return self._create_fallback_result(genetic_data, "genetic_analysis")
    
    async def personalize_risk_communication(
        self,
        risk_variants: List[Dict[str, Any]],
        user_profile: Dict[str, Any],
        communication_preferences: Optional[Dict[str, Any]] = None
    ) -> PersonalizationResult:
        """
        Personalize genetic risk communication based on user psychology and archetype
        
        Args:
            risk_variants: List of genetic variants with associated risks
            user_profile: Complete user profile
            communication_preferences: User's communication preferences
            
        Returns:
            PersonalizationResult with personalized risk communication strategy
        """
        try:
            # Assess user's risk tolerance and communication style
            risk_tolerance = self._assess_risk_tolerance(user_profile)
            communication_style = self._determine_communication_style(user_profile)
            support_needs = self._assess_genetic_counseling_needs(user_profile, risk_variants)
            
            # Create risk communication context
            context = PersonalizationContext(
                user_profile=UserProfile.from_dict(user_profile),
                agent_type="code_genetic_specialist",
                request_type="risk_communication",
                session_data={
                    "risk_variants": risk_variants,
                    "communication_preferences": communication_preferences or {},
                    "risk_tolerance": risk_tolerance,
                    "communication_style": communication_style,
                    "support_needs": support_needs,
                    "risk_communication_timestamp": datetime.now().isoformat()
                }
            )
            
            # Execute personalization
            result = await self.engine.personalize_for_user(
                context=context,
                mode=PersonalizationMode.ADVANCED
            )
            
            # Apply risk communication adaptations
            adapted_result = self._apply_risk_communication_adaptations(
                result, risk_tolerance, communication_style, support_needs
            )
            
            logger.info(f"Risk communication personalized for {len(risk_variants)} variants")
            return adapted_result
            
        except Exception as e:
            logger.error(f"Error in personalized risk communication: {e}")
            return self._create_fallback_result(risk_variants, "risk_communication")
    
    async def personalize_intervention_recommendations(
        self,
        genetic_findings: Dict[str, Any],
        user_profile: Dict[str, Any],
        lifestyle_data: Optional[Dict[str, Any]] = None
    ) -> PersonalizationResult:
        """
        Personalize intervention recommendations based on genetic findings and archetype
        
        Args:
            genetic_findings: Processed genetic analysis results
            user_profile: Complete user profile
            lifestyle_data: Current lifestyle and health data
            
        Returns:
            PersonalizationResult with personalized intervention strategies
        """
        try:
            # Analyze intervention opportunities
            intervention_priorities = self._prioritize_genetic_interventions(genetic_findings, user_profile)
            lifestyle_alignment = self._assess_lifestyle_genetic_alignment(genetic_findings, lifestyle_data or {})
            implementation_feasibility = self._assess_intervention_feasibility(user_profile)
            
            # Create intervention context
            context = PersonalizationContext(
                user_profile=UserProfile.from_dict(user_profile),
                agent_type="code_genetic_specialist",
                request_type="intervention_recommendations",
                session_data={
                    "genetic_findings": genetic_findings,
                    "lifestyle_data": lifestyle_data or {},
                    "intervention_priorities": intervention_priorities,
                    "lifestyle_alignment": lifestyle_alignment,
                    "implementation_feasibility": implementation_feasibility,
                    "intervention_timestamp": datetime.now().isoformat()
                }
            )
            
            # Execute personalization
            result = await self.engine.personalize_for_user(
                context=context,
                mode=PersonalizationMode.ADVANCED
            )
            
            # Apply intervention-specific adaptations
            adapted_result = self._apply_intervention_adaptations(
                result, intervention_priorities, lifestyle_alignment, implementation_feasibility
            )
            
            logger.info(f"Intervention recommendations personalized for {len(intervention_priorities)} priorities")
            return adapted_result
            
        except Exception as e:
            logger.error(f"Error in personalized intervention recommendations: {e}")
            return self._create_fallback_result(genetic_findings, "intervention_recommendations")
    
    def _assess_genetic_complexity(self, genetic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the complexity of genetic data for appropriate presentation"""
        try:
            variant_count = len(genetic_data.get('variants', []))
            high_impact_variants = len([v for v in genetic_data.get('variants', []) 
                                      if v.get('clinical_significance') in ['pathogenic', 'likely_pathogenic']])
            uncertain_variants = len([v for v in genetic_data.get('variants', [])
                                    if v.get('clinical_significance') == 'uncertain_significance'])
            
            complexity_score = min(10, (variant_count / 100) + (high_impact_variants * 2) + (uncertain_variants * 0.5))
            
            return {
                'variant_count': variant_count,
                'high_impact_count': high_impact_variants,
                'uncertain_count': uncertain_variants,
                'complexity_score': complexity_score,
                'recommended_presentation_level': self._determine_presentation_level(complexity_score)
            }
        except Exception as e:
            logger.warning(f"Error assessing genetic complexity: {e}")
            return {'complexity_score': 5.0, 'recommended_presentation_level': 'intermediate'}
    
    def _calculate_genetic_risk_profile(self, genetic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall genetic risk profile across different health areas"""
        risk_areas = {
            'cardiovascular': 0.0,
            'metabolic': 0.0,
            'neurological': 0.0,
            'cancer': 0.0,
            'autoimmune': 0.0,
            'pharmacogenomic': 0.0
        }
        
        try:
            for variant in genetic_data.get('variants', []):
                # Simplified risk calculation - in reality would use validated algorithms
                risk_factor = self._get_variant_risk_factor(variant)
                associated_conditions = variant.get('associated_conditions', [])
                
                for condition in associated_conditions:
                    condition_lower = condition.lower()
                    if any(cv_term in condition_lower for cv_term in ['heart', 'cardiac', 'cardiovascular']):
                        risk_areas['cardiovascular'] += risk_factor
                    elif any(met_term in condition_lower for met_term in ['diabetes', 'metabolic', 'obesity']):
                        risk_areas['metabolic'] += risk_factor
                    elif any(neuro_term in condition_lower for neuro_term in ['alzheimer', 'parkinson', 'neurological']):
                        risk_areas['neurological'] += risk_factor
                    elif 'cancer' in condition_lower:
                        risk_areas['cancer'] += risk_factor
                    elif any(auto_term in condition_lower for auto_term in ['autoimmune', 'rheumatoid', 'lupus']):
                        risk_areas['autoimmune'] += risk_factor
                    elif any(pharm_term in condition_lower for pharm_term in ['drug', 'medication', 'metabolism']):
                        risk_areas['pharmacogenomic'] += risk_factor
            
            # Normalize risk scores
            max_risk = max(risk_areas.values()) if risk_areas.values() else 1
            if max_risk > 0:
                risk_areas = {area: min(1.0, risk / max_risk) for area, risk in risk_areas.items()}
                
        except Exception as e:
            logger.warning(f"Error calculating genetic risk profile: {e}")
        
        return risk_areas
    
    def _identify_actionable_variants(self, genetic_data: Dict[str, Any], user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify genetic variants that have actionable interventions"""
        actionable_variants = []
        
        try:
            for variant in genetic_data.get('variants', []):
                # Check if variant has known interventions
                if variant.get('actionable', False) or variant.get('clinical_significance') in ['pathogenic', 'likely_pathogenic']:
                    # Check if intervention aligns with user's archetype and goals
                    if self._is_variant_relevant_to_user(variant, user_profile):
                        actionable_variants.append({
                            'variant_id': variant.get('id', 'unknown'),
                            'gene': variant.get('gene', 'unknown'),
                            'effect': variant.get('effect', 'unknown'),
                            'clinical_significance': variant.get('clinical_significance', 'unknown'),
                            'recommended_actions': variant.get('recommended_actions', []),
                            'evidence_level': variant.get('evidence_level', 'moderate'),
                            'user_relevance_score': self._calculate_user_relevance_score(variant, user_profile)
                        })
        except Exception as e:
            logger.warning(f"Error identifying actionable variants: {e}")
        
        # Sort by relevance score
        actionable_variants.sort(key=lambda x: x.get('user_relevance_score', 0), reverse=True)
        return actionable_variants[:10]  # Return top 10 most relevant
    
    def _assess_risk_tolerance(self, user_profile: Dict[str, Any]) -> str:
        """Assess user's risk tolerance for genetic information"""
        archetype = user_profile.get('archetype', 'PRIME')
        anxiety_level = user_profile.get('health_anxiety', 'normal')
        control_preference = user_profile.get('control_preference', 'moderate')
        
        if archetype == 'PRIME' and anxiety_level == 'low' and control_preference == 'high':
            return 'high_tolerance'
        elif anxiety_level == 'high':
            return 'low_tolerance'
        else:
            return 'moderate_tolerance'
    
    def _determine_communication_style(self, user_profile: Dict[str, Any]) -> str:
        """Determine optimal communication style for genetic information"""
        archetype = user_profile.get('archetype', 'PRIME')
        education_level = user_profile.get('education_level', 'undergraduate')
        technical_background = user_profile.get('technical_background', False)
        
        if archetype == 'PRIME' and (education_level in ['graduate', 'postgraduate'] or technical_background):
            return 'data_driven_detailed'
        elif archetype == 'LONGEVITY':
            return 'supportive_holistic'
        else:
            return 'balanced_accessible'
    
    def _assess_genetic_counseling_needs(self, user_profile: Dict[str, Any], risk_variants: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess if user needs additional genetic counseling support"""
        high_risk_count = len([v for v in risk_variants if v.get('clinical_significance') == 'pathogenic'])
        family_history_concerns = user_profile.get('family_history_concerns', False)
        support_system = user_profile.get('support_system_strength', 'moderate')
        
        needs_counseling = high_risk_count > 2 or family_history_concerns or support_system == 'low'
        
        return {
            'professional_counseling_recommended': needs_counseling,
            'support_level_needed': 'high' if needs_counseling else 'standard',
            'counseling_focus_areas': ['risk_interpretation', 'family_planning'] if needs_counseling else []
        }
    
    def _prioritize_genetic_interventions(self, genetic_findings: Dict[str, Any], user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize genetic interventions based on impact and user preferences"""
        interventions = []
        
        try:
            actionable_findings = genetic_findings.get('actionable_variants', [])
            user_goals = user_profile.get('goals', [])
            archetype = user_profile.get('archetype', 'PRIME')
            
            for finding in actionable_findings:
                intervention_score = 0
                
                # Score based on clinical evidence
                evidence_level = finding.get('evidence_level', 'moderate')
                if evidence_level == 'strong':
                    intervention_score += 3
                elif evidence_level == 'moderate':
                    intervention_score += 2
                else:
                    intervention_score += 1
                
                # Score based on user goals alignment
                recommended_actions = finding.get('recommended_actions', [])
                for action in recommended_actions:
                    if any(goal in str(action).lower() for goal in [str(g).lower() for g in user_goals]):
                        intervention_score += 2
                
                # Score based on archetype preferences
                if archetype == 'PRIME' and any(term in str(recommended_actions).lower() 
                                              for term in ['performance', 'optimization', 'efficiency']):
                    intervention_score += 1
                elif archetype == 'LONGEVITY' and any(term in str(recommended_actions).lower()
                                                    for term in ['prevention', 'wellness', 'longevity']):
                    intervention_score += 1
                
                interventions.append({
                    'finding': finding,
                    'priority_score': intervention_score,
                    'intervention_category': self._categorize_intervention(recommended_actions),
                    'implementation_complexity': self._assess_implementation_complexity(recommended_actions)
                })
            
            # Sort by priority score
            interventions.sort(key=lambda x: x['priority_score'], reverse=True)
            
        except Exception as e:
            logger.warning(f"Error prioritizing genetic interventions: {e}")
        
        return interventions[:5]  # Return top 5 priorities
    
    def _assess_lifestyle_genetic_alignment(self, genetic_findings: Dict[str, Any], lifestyle_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess how well current lifestyle aligns with genetic recommendations"""
        alignment_score = 0.5  # Default neutral alignment
        recommendations = []
        
        try:
            # Compare genetic recommendations with current lifestyle
            genetic_recommendations = genetic_findings.get('lifestyle_recommendations', [])
            current_habits = lifestyle_data.get('current_habits', {})
            
            aligned_areas = []
            misaligned_areas = []
            
            for recommendation in genetic_recommendations:
                rec_category = recommendation.get('category', '')
                if rec_category in current_habits:
                    current_value = current_habits[rec_category]
                    recommended_value = recommendation.get('recommended_value', '')
                    
                    if self._is_lifestyle_aligned(current_value, recommended_value):
                        aligned_areas.append(rec_category)
                        alignment_score += 0.1
                    else:
                        misaligned_areas.append({
                            'category': rec_category,
                            'current': current_value,
                            'recommended': recommended_value,
                            'genetic_basis': recommendation.get('genetic_basis', '')
                        })
                        alignment_score -= 0.1
            
            alignment_score = max(0, min(1, alignment_score))
            
        except Exception as e:
            logger.warning(f"Error assessing lifestyle genetic alignment: {e}")
        
        return {
            'overall_alignment_score': alignment_score,
            'aligned_areas': aligned_areas,
            'improvement_opportunities': misaligned_areas,
            'alignment_quality': 'high' if alignment_score > 0.7 else 'moderate' if alignment_score > 0.4 else 'low'
        }
    
    def _assess_intervention_feasibility(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Assess feasibility of implementing genetic interventions"""
        lifestyle_flexibility = user_profile.get('lifestyle_flexibility', 'moderate')
        change_readiness = user_profile.get('change_readiness', 'moderate')
        resources = user_profile.get('available_resources', 'moderate')
        
        feasibility_score = 0.5
        
        if lifestyle_flexibility == 'high':
            feasibility_score += 0.2
        elif lifestyle_flexibility == 'low':
            feasibility_score -= 0.2
        
        if change_readiness == 'high':
            feasibility_score += 0.2
        elif change_readiness == 'low':
            feasibility_score -= 0.2
        
        if resources == 'high':
            feasibility_score += 0.1
        elif resources == 'low':
            feasibility_score -= 0.1
        
        feasibility_score = max(0, min(1, feasibility_score))
        
        return {
            'overall_feasibility': feasibility_score,
            'implementation_timeline': 'immediate' if feasibility_score > 0.7 else 'gradual' if feasibility_score > 0.4 else 'long_term',
            'support_needs': 'minimal' if feasibility_score > 0.7 else 'moderate' if feasibility_score > 0.4 else 'intensive'
        }
    
    def _determine_presentation_level(self, complexity_score: float) -> str:
        """Determine appropriate presentation level based on complexity"""
        if complexity_score < 3:
            return 'simple'
        elif complexity_score < 6:
            return 'intermediate'
        elif complexity_score < 8:
            return 'advanced'
        else:
            return 'clinical'
    
    def _get_variant_risk_factor(self, variant: Dict[str, Any]) -> float:
        """Get risk factor for a genetic variant"""
        clinical_sig = variant.get('clinical_significance', 'uncertain')
        
        risk_factors = {
            'pathogenic': 1.0,
            'likely_pathogenic': 0.7,
            'uncertain_significance': 0.3,
            'likely_benign': 0.1,
            'benign': 0.0
        }
        
        return risk_factors.get(clinical_sig, 0.3)
    
    def _is_variant_relevant_to_user(self, variant: Dict[str, Any], user_profile: Dict[str, Any]) -> bool:
        """Check if a genetic variant is relevant to the user's goals and concerns"""
        user_goals = [str(g).lower() for g in user_profile.get('goals', [])]
        health_concerns = [str(c).lower() for c in user_profile.get('health_concerns', [])]
        
        variant_conditions = [str(c).lower() for c in variant.get('associated_conditions', [])]
        
        # Check for overlap between user interests and variant implications
        return any(goal in condition or condition in goal 
                  for goal in user_goals 
                  for condition in variant_conditions) or \
               any(concern in condition or condition in concern
                  for concern in health_concerns
                  for condition in variant_conditions)
    
    def _calculate_user_relevance_score(self, variant: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
        """Calculate how relevant a variant is to a specific user"""
        score = 0.0
        
        # Base score from clinical significance
        clinical_sig = variant.get('clinical_significance', 'uncertain')
        if clinical_sig == 'pathogenic':
            score += 1.0
        elif clinical_sig == 'likely_pathogenic':
            score += 0.7
        elif clinical_sig == 'uncertain_significance':
            score += 0.3
        
        # Bonus for alignment with user goals
        if self._is_variant_relevant_to_user(variant, user_profile):
            score += 0.5
        
        # Bonus for actionable variants
        if variant.get('actionable', False):
            score += 0.3
        
        return min(2.0, score)
    
    def _categorize_intervention(self, recommended_actions: List[str]) -> str:
        """Categorize the type of intervention"""
        actions_text = ' '.join(recommended_actions).lower()
        
        if any(term in actions_text for term in ['diet', 'nutrition', 'food']):
            return 'nutritional'
        elif any(term in actions_text for term in ['exercise', 'fitness', 'activity']):
            return 'lifestyle_fitness'
        elif any(term in actions_text for term in ['medication', 'drug', 'treatment']):
            return 'medical'
        elif any(term in actions_text for term in ['screening', 'monitoring', 'test']):
            return 'monitoring'
        else:
            return 'general_lifestyle'
    
    def _assess_implementation_complexity(self, recommended_actions: List[str]) -> str:
        """Assess how complex it would be to implement the recommended actions"""
        actions_text = ' '.join(recommended_actions).lower()
        
        complex_indicators = ['medical', 'clinical', 'specialist', 'prescription', 'surgery']
        moderate_indicators = ['regular', 'daily', 'monitoring', 'testing']
        
        if any(indicator in actions_text for indicator in complex_indicators):
            return 'high'
        elif any(indicator in actions_text for indicator in moderate_indicators):
            return 'moderate'
        else:
            return 'low'
    
    def _is_lifestyle_aligned(self, current_value: Any, recommended_value: Any) -> bool:
        """Check if current lifestyle value aligns with genetic recommendation"""
        # Simplified alignment check - would be more sophisticated in practice
        current_str = str(current_value).lower()
        recommended_str = str(recommended_value).lower()
        
        return current_str == recommended_str or recommended_str in current_str
    
    def _apply_genetic_analysis_enhancements(
        self,
        result: PersonalizationResult,
        complexity_assessment: Dict[str, Any],
        risk_profile: Dict[str, Any],
        actionable_variants: List[Dict[str, Any]]
    ) -> PersonalizationResult:
        """Apply genetic analysis specific enhancements"""
        
        enhanced_content = result.personalized_content.copy()
        enhanced_content.update({
            'genetic_analysis_summary': {
                'complexity_level': complexity_assessment.get('recommended_presentation_level'),
                'risk_profile': risk_profile,
                'actionable_variants_count': len(actionable_variants),
                'top_actionable_variants': actionable_variants[:3]
            },
            'personalized_insights': self._generate_personalized_genetic_insights(
                risk_profile, actionable_variants, result.archetype_adaptation
            )
        })
        
        return PersonalizationResult(
            archetype_adaptation=result.archetype_adaptation,
            physiological_modulation=result.physiological_modulation,
            personalized_content=enhanced_content,
            confidence_score=result.confidence_score,
            personalization_metadata={
                **result.personalization_metadata,
                'codex_genetic_analysis_applied': True,
                'complexity_level': complexity_assessment.get('recommended_presentation_level'),
                'actionable_variants_count': len(actionable_variants)
            }
        )
    
    def _apply_risk_communication_adaptations(
        self,
        result: PersonalizationResult,
        risk_tolerance: str,
        communication_style: str,
        support_needs: Dict[str, Any]
    ) -> PersonalizationResult:
        """Apply risk communication specific adaptations"""
        
        enhanced_content = result.personalized_content.copy()
        enhanced_content.update({
            'risk_communication_strategy': {
                'risk_tolerance_level': risk_tolerance,
                'communication_approach': communication_style,
                'support_recommendations': support_needs,
                'counseling_needed': support_needs.get('professional_counseling_recommended', False)
            }
        })
        
        return PersonalizationResult(
            archetype_adaptation=result.archetype_adaptation,
            physiological_modulation=result.physiological_modulation,
            personalized_content=enhanced_content,
            confidence_score=result.confidence_score,
            personalization_metadata={
                **result.personalization_metadata,
                'codex_risk_communication_adapted': True,
                'risk_tolerance': risk_tolerance
            }
        )
    
    def _apply_intervention_adaptations(
        self,
        result: PersonalizationResult,
        intervention_priorities: List[Dict[str, Any]],
        lifestyle_alignment: Dict[str, Any],
        implementation_feasibility: Dict[str, Any]
    ) -> PersonalizationResult:
        """Apply intervention specific adaptations"""
        
        enhanced_content = result.personalized_content.copy()
        enhanced_content.update({
            'intervention_strategy': {
                'top_priorities': intervention_priorities[:3],
                'lifestyle_alignment': lifestyle_alignment,
                'implementation_plan': implementation_feasibility,
                'personalized_recommendations': self._create_personalized_intervention_plan(
                    intervention_priorities, lifestyle_alignment, implementation_feasibility
                )
            }
        })
        
        return PersonalizationResult(
            archetype_adaptation=result.archetype_adaptation,
            physiological_modulation=result.physiological_modulation,
            personalized_content=enhanced_content,
            confidence_score=result.confidence_score,
            personalization_metadata={
                **result.personalization_metadata,
                'codex_intervention_adapted': True,
                'intervention_priorities_count': len(intervention_priorities)
            }
        )
    
    def _generate_personalized_genetic_insights(
        self,
        risk_profile: Dict[str, Any],
        actionable_variants: List[Dict[str, Any]],
        archetype_adaptation: Dict[str, Any]
    ) -> List[str]:
        """Generate personalized insights based on genetic analysis"""
        insights = []
        
        archetype = archetype_adaptation.get('user_archetype', 'PRIME')
        
        # Risk-based insights
        high_risk_areas = [area for area, risk in risk_profile.items() if risk > 0.6]
        if high_risk_areas:
            if archetype == 'PRIME':
                insights.append(f"Optimization opportunities identified in: {', '.join(high_risk_areas)}")
            else:
                insights.append(f"Prevention strategies recommended for: {', '.join(high_risk_areas)}")
        
        # Actionable insights
        if actionable_variants:
            if archetype == 'PRIME':
                insights.append(f"Performance optimization potential through {len(actionable_variants)} genetic interventions")
            else:
                insights.append(f"Wellness enhancement opportunities through {len(actionable_variants)} evidence-based strategies")
        
        return insights[:5]
    
    def _create_personalized_intervention_plan(
        self,
        priorities: List[Dict[str, Any]],
        alignment: Dict[str, Any],
        feasibility: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a personalized intervention implementation plan"""
        return {
            'immediate_actions': [p['finding'] for p in priorities[:2] if p.get('implementation_complexity') == 'low'],
            'medium_term_goals': [p['finding'] for p in priorities if p.get('implementation_complexity') == 'moderate'],
            'long_term_strategies': [p['finding'] for p in priorities if p.get('implementation_complexity') == 'high'],
            'lifestyle_optimizations': alignment.get('improvement_opportunities', [])[:3],
            'implementation_timeline': feasibility.get('implementation_timeline', 'gradual'),
            'support_level_needed': feasibility.get('support_needs', 'moderate')
        }
    
    def _create_fallback_result(self, data: Any, request_type: str) -> PersonalizationResult:
        """Create fallback result when personalization fails"""
        return PersonalizationResult(
            archetype_adaptation={
                'user_archetype': UserArchetype.PRIME,
                'adaptation_strategy': 'fallback_default',
                'request_type': request_type
            },
            physiological_modulation={
                'modulation_applied': False,
                'fallback_reason': 'personalization_error'
            },
            personalized_content={'original_data': str(data)},
            confidence_score=0.5,
            personalization_metadata={
                'fallback_mode': True,
                'timestamp': datetime.now().isoformat()
            }
        )


# Integration functions for easy usage
async def personalize_genetic_counseling(
    genetic_request: Dict[str, Any],
    user_profile: Dict[str, Any],
    counseling_type: str = "genetic_analysis",
    additional_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Complete genetic counseling personalization workflow
    
    Args:
        genetic_request: Genetic analysis or counseling request
        user_profile: Complete user profile
        counseling_type: Type of genetic counseling needed
        additional_data: Additional context data
        
    Returns:
        Complete personalized genetic counseling strategy
    """
    integration = CODEXHybridIntelligenceIntegration()
    
    try:
        if counseling_type == "genetic_analysis":
            result = await integration.personalize_genetic_analysis(
                genetic_request, user_profile, additional_data.get('analysis_focus') if additional_data else None
            )
        elif counseling_type == "risk_communication":
            result = await integration.personalize_risk_communication(
                genetic_request.get('risk_variants', []), user_profile, 
                additional_data.get('communication_preferences') if additional_data else None
            )
        elif counseling_type == "intervention_recommendations":
            result = await integration.personalize_intervention_recommendations(
                genetic_request, user_profile, additional_data.get('lifestyle_data') if additional_data else None
            )
        else:
            result = await integration.personalize_genetic_analysis(genetic_request, user_profile)
        
        return {
            'personalized_genetic_counsel': result.personalized_content,
            'archetype_considerations': result.archetype_adaptation,
            'genetic_modulation': result.physiological_modulation,
            'confidence_score': result.confidence_score,
            'metadata': result.personalization_metadata
        }
        
    except Exception as e:
        logger.error(f"Error in genetic counseling personalization: {e}")
        return {
            'error': str(e),
            'fallback_mode': True,
            'timestamp': datetime.now().isoformat()
        }


# Export the integration class
__all__ = ['CODEXHybridIntelligenceIntegration', 'personalize_genetic_counseling']