"""
GENESIS NGX Agents - GUARDIAN Hybrid Intelligence Integration
============================================================

Integration module for the GUARDIAN agent (Security & Compliance) with the
Hybrid Intelligence Engine. This module provides specialized personalization
for security protocols, compliance management, and privacy protection.

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


class SecurityLevel(Enum):
    """Security level classifications"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"


class ComplianceFramework(Enum):
    """Compliance frameworks for personalization"""
    HIPAA = "hipaa"
    GDPR = "gdpr"
    CCPA = "ccpa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    CUSTOM = "custom"


class PrivacyPreference(Enum):
    """User privacy preference levels"""
    MINIMAL_SHARING = "minimal_sharing"
    SELECTIVE_SHARING = "selective_sharing"
    STANDARD_SHARING = "standard_sharing"
    OPEN_SHARING = "open_sharing"


class GUARDIANHybridIntelligenceIntegration:
    """
    Integration layer between GUARDIAN agent and Hybrid Intelligence Engine
    
    Specialized for security and compliance with advanced personalization:
    - Archetype-specific security protocols and recommendations
    - Personalized privacy settings based on user comfort levels
    - Adaptive compliance monitoring based on user roles and regulations
    - Risk-aware security interventions based on user behavior patterns
    - Customized audit and reporting based on user preferences
    """
    
    def __init__(self):
        """Initialize GUARDIAN Hybrid Intelligence Integration"""
        self.engine = HybridIntelligenceEngine()
        self.integration_name = "GUARDIAN_SECURITY_COMPLIANCE_HYBRID_INTELLIGENCE"
        self.version = "1.0.0"
        
        logger.info(f"Initialized {self.integration_name} v{self.version}")
    
    async def personalize_security_protocols(
        self,
        security_assessment: Dict[str, Any],
        user_profile: Dict[str, Any],
        threat_context: Optional[Dict[str, Any]] = None
    ) -> PersonalizationResult:
        """
        Personalize security protocols based on user archetype and risk profile
        
        Args:
            security_assessment: Current security posture assessment
            user_profile: Complete user profile
            threat_context: Current threat landscape and context
            
        Returns:
            PersonalizationResult with personalized security recommendations
        """
        try:
            # Assess user security preferences and risk tolerance
            security_comfort_level = self._assess_security_comfort_level(user_profile)
            risk_tolerance = self._assess_security_risk_tolerance(user_profile)
            technical_proficiency = self._assess_technical_proficiency(user_profile)
            
            # Create security personalization context
            context = PersonalizationContext(
                user_profile=UserProfile.from_dict(user_profile),
                agent_type="security_guardian",
                request_type="security_protocols",
                session_data={
                    "security_assessment": security_assessment,
                    "threat_context": threat_context or {},
                    "security_comfort_level": security_comfort_level,
                    "risk_tolerance": risk_tolerance,
                    "technical_proficiency": technical_proficiency,
                    "security_timestamp": datetime.now().isoformat()
                }
            )
            
            # Execute hybrid intelligence personalization
            result = await self.engine.personalize_for_user(
                context=context,
                mode=PersonalizationMode.ADVANCED
            )
            
            # Apply security-specific enhancements
            enhanced_result = self._apply_security_protocol_enhancements(
                result, security_comfort_level, risk_tolerance, technical_proficiency
            )
            
            logger.info(f"Security protocols personalized for {security_comfort_level} comfort level")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error in personalized security protocols: {e}")
            return self._create_fallback_result(security_assessment, "security_protocols")
    
    async def personalize_privacy_settings(
        self,
        privacy_request: Dict[str, Any],
        user_profile: Dict[str, Any],
        data_categories: Optional[List[str]] = None
    ) -> PersonalizationResult:
        """
        Personalize privacy settings based on user preferences and archetype
        
        Args:
            privacy_request: Privacy configuration request
            user_profile: Complete user profile
            data_categories: Categories of data to configure privacy for
            
        Returns:
            PersonalizationResult with personalized privacy configuration
        """
        try:
            # Assess privacy preferences
            privacy_preference = self._assess_privacy_preference(user_profile)
            data_sensitivity_awareness = self._assess_data_sensitivity_awareness(user_profile)
            sharing_comfort_levels = self._assess_sharing_comfort_levels(user_profile, data_categories or [])
            
            # Create privacy personalization context
            context = PersonalizationContext(
                user_profile=UserProfile.from_dict(user_profile),
                agent_type="security_guardian",
                request_type="privacy_settings",
                session_data={
                    "privacy_request": privacy_request,
                    "data_categories": data_categories or [],
                    "privacy_preference": privacy_preference.value,
                    "data_sensitivity_awareness": data_sensitivity_awareness,
                    "sharing_comfort_levels": sharing_comfort_levels,
                    "privacy_timestamp": datetime.now().isoformat()
                }
            )
            
            # Execute personalization
            result = await self.engine.personalize_for_user(
                context=context,
                mode=PersonalizationMode.ADVANCED
            )
            
            # Apply privacy-specific adaptations
            adapted_result = self._apply_privacy_setting_adaptations(
                result, privacy_preference, data_sensitivity_awareness, sharing_comfort_levels
            )
            
            logger.info(f"Privacy settings personalized for {privacy_preference.value} preference")
            return adapted_result
            
        except Exception as e:
            logger.error(f"Error in personalized privacy settings: {e}")
            return self._create_fallback_result(privacy_request, "privacy_settings")
    
    async def personalize_compliance_monitoring(
        self,
        compliance_requirements: Dict[str, Any],
        user_profile: Dict[str, Any],
        regulatory_context: Optional[Dict[str, Any]] = None
    ) -> PersonalizationResult:
        """
        Personalize compliance monitoring based on user role and requirements
        
        Args:
            compliance_requirements: Required compliance frameworks and standards
            user_profile: Complete user profile
            regulatory_context: Current regulatory environment context
            
        Returns:
            PersonalizationResult with personalized compliance strategy
        """
        try:
            # Assess compliance needs and preferences
            user_role_compliance_needs = self._assess_user_role_compliance_needs(user_profile)
            compliance_automation_preference = self._assess_compliance_automation_preference(user_profile)
            reporting_preferences = self._assess_compliance_reporting_preferences(user_profile)
            
            # Create compliance personalization context
            context = PersonalizationContext(
                user_profile=UserProfile.from_dict(user_profile),
                agent_type="security_guardian",
                request_type="compliance_monitoring",
                session_data={
                    "compliance_requirements": compliance_requirements,
                    "regulatory_context": regulatory_context or {},
                    "role_compliance_needs": user_role_compliance_needs,
                    "automation_preference": compliance_automation_preference,
                    "reporting_preferences": reporting_preferences,
                    "compliance_timestamp": datetime.now().isoformat()
                }
            )
            
            # Execute personalization
            result = await self.engine.personalize_for_user(
                context=context,
                mode=PersonalizationMode.STANDARD
            )
            
            # Apply compliance-specific adaptations
            adapted_result = self._apply_compliance_monitoring_adaptations(
                result, user_role_compliance_needs, compliance_automation_preference, reporting_preferences
            )
            
            logger.info(f"Compliance monitoring personalized for role: {user_role_compliance_needs.get('primary_role', 'user')}")
            return adapted_result
            
        except Exception as e:
            logger.error(f"Error in personalized compliance monitoring: {e}")
            return self._create_fallback_result(compliance_requirements, "compliance_monitoring")
    
    def _assess_security_comfort_level(self, user_profile: Dict[str, Any]) -> str:
        """Assess user's comfort level with security measures"""
        archetype = user_profile.get('archetype', 'PRIME')
        technical_background = user_profile.get('technical_background', False)
        security_experience = user_profile.get('security_experience', 'basic')
        convenience_preference = user_profile.get('convenience_vs_security_preference', 'balanced')
        
        # PRIME users typically prefer efficiency but accept security when necessary
        if archetype == 'PRIME':
            if technical_background and security_experience in ['advanced', 'expert']:
                return 'high_comfort'
            elif convenience_preference == 'security_focused':
                return 'moderate_comfort'
            else:
                return 'efficiency_focused'
        else:  # LONGEVITY
            if convenience_preference == 'security_focused':
                return 'high_comfort'
            elif technical_background:
                return 'moderate_comfort'
            else:
                return 'guidance_needed'
    
    def _assess_security_risk_tolerance(self, user_profile: Dict[str, Any]) -> str:
        """Assess user's risk tolerance for security decisions"""
        archetype = user_profile.get('archetype', 'PRIME')
        risk_appetite = user_profile.get('general_risk_appetite', 'moderate')
        data_sensitivity = user_profile.get('data_sensitivity_level', 'moderate')
        
        if archetype == 'PRIME' and risk_appetite == 'high' and data_sensitivity == 'low':
            return 'high_tolerance'
        elif data_sensitivity == 'high' or risk_appetite == 'low':
            return 'low_tolerance'
        else:
            return 'moderate_tolerance'
    
    def _assess_technical_proficiency(self, user_profile: Dict[str, Any]) -> str:
        """Assess user's technical proficiency for security configurations"""
        technical_background = user_profile.get('technical_background', False)
        security_knowledge = user_profile.get('security_knowledge_level', 'basic')
        self_service_preference = user_profile.get('self_service_preference', 'moderate')
        
        if technical_background and security_knowledge in ['advanced', 'expert']:
            return 'high'
        elif technical_background or security_knowledge == 'intermediate':
            return 'moderate'
        else:
            return 'basic'
    
    def _assess_privacy_preference(self, user_profile: Dict[str, Any]) -> PrivacyPreference:
        """Assess user's privacy sharing preference"""
        privacy_concern_level = user_profile.get('privacy_concern_level', 'moderate')
        data_sharing_comfort = user_profile.get('data_sharing_comfort', 'selective')
        social_sharing_tendency = user_profile.get('social_sharing_tendency', 'moderate')
        
        if privacy_concern_level == 'high' or data_sharing_comfort == 'minimal':
            return PrivacyPreference.MINIMAL_SHARING
        elif privacy_concern_level == 'low' and social_sharing_tendency == 'high':
            return PrivacyPreference.OPEN_SHARING
        elif data_sharing_comfort == 'selective':
            return PrivacyPreference.SELECTIVE_SHARING
        else:
            return PrivacyPreference.STANDARD_SHARING
    
    def _assess_data_sensitivity_awareness(self, user_profile: Dict[str, Any]) -> str:
        """Assess user's awareness of data sensitivity levels"""
        education_level = user_profile.get('education_level', 'undergraduate')
        privacy_training = user_profile.get('privacy_training_completed', False)
        data_breach_experience = user_profile.get('data_breach_experience', False)
        
        if privacy_training or data_breach_experience or education_level in ['graduate', 'postgraduate']:
            return 'high_awareness'
        elif education_level == 'undergraduate':
            return 'moderate_awareness'
        else:
            return 'basic_awareness'
    
    def _assess_sharing_comfort_levels(self, user_profile: Dict[str, Any], data_categories: List[str]) -> Dict[str, str]:
        """Assess comfort levels for sharing different categories of data"""
        default_comfort = user_profile.get('data_sharing_comfort', 'selective')
        privacy_preference = self._assess_privacy_preference(user_profile)
        
        comfort_levels = {}
        
        sensitive_categories = ['health', 'financial', 'biometric', 'genetic']
        moderate_categories = ['fitness', 'nutrition', 'lifestyle']
        low_sensitivity_categories = ['preferences', 'goals', 'progress']
        
        for category in data_categories:
            if category.lower() in sensitive_categories:
                if privacy_preference == PrivacyPreference.MINIMAL_SHARING:
                    comfort_levels[category] = 'no_sharing'
                elif privacy_preference == PrivacyPreference.SELECTIVE_SHARING:
                    comfort_levels[category] = 'limited_sharing'
                else:
                    comfort_levels[category] = 'controlled_sharing'
            elif category.lower() in moderate_categories:
                if privacy_preference == PrivacyPreference.MINIMAL_SHARING:
                    comfort_levels[category] = 'limited_sharing'
                else:
                    comfort_levels[category] = 'controlled_sharing'
            else:  # Low sensitivity
                if privacy_preference == PrivacyPreference.MINIMAL_SHARING:
                    comfort_levels[category] = 'controlled_sharing'
                else:
                    comfort_levels[category] = 'open_sharing'
        
        return comfort_levels
    
    def _assess_user_role_compliance_needs(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Assess compliance needs based on user role and context"""
        user_role = user_profile.get('professional_role', 'individual_user')
        industry = user_profile.get('industry', 'general')
        geographic_location = user_profile.get('location', {}).get('country', 'US')
        
        compliance_needs = {
            'primary_role': user_role,
            'applicable_frameworks': [],
            'risk_level': 'standard',
            'monitoring_intensity': 'standard'
        }
        
        # Determine applicable frameworks based on context
        if industry in ['healthcare', 'medical']:
            compliance_needs['applicable_frameworks'].append('HIPAA')
            compliance_needs['risk_level'] = 'high'
        
        if geographic_location in ['EU', 'EEA'] or user_profile.get('eu_data_subject', False):
            compliance_needs['applicable_frameworks'].append('GDPR')
        
        if geographic_location == 'CA':
            compliance_needs['applicable_frameworks'].append('CCPA')
        
        if industry in ['finance', 'banking']:
            compliance_needs['applicable_frameworks'].extend(['SOX', 'PCI_DSS'])
            compliance_needs['risk_level'] = 'high'
            compliance_needs['monitoring_intensity'] = 'enhanced'
        
        return compliance_needs
    
    def _assess_compliance_automation_preference(self, user_profile: Dict[str, Any]) -> str:
        """Assess preference for automated vs manual compliance management"""
        archetype = user_profile.get('archetype', 'PRIME')
        technical_proficiency = self._assess_technical_proficiency(user_profile)
        control_preference = user_profile.get('control_vs_automation_preference', 'balanced')
        
        if archetype == 'PRIME' and control_preference in ['automation_focused', 'balanced']:
            return 'high_automation'
        elif technical_proficiency == 'high' and control_preference == 'control_focused':
            return 'manual_with_automation_assist'
        else:
            return 'guided_automation'
    
    def _assess_compliance_reporting_preferences(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Assess preferences for compliance reporting"""
        archetype = user_profile.get('archetype', 'PRIME')
        detail_preference = user_profile.get('reporting_detail_preference', 'summary')
        frequency_preference = user_profile.get('reporting_frequency_preference', 'monthly')
        
        if archetype == 'PRIME':
            return {
                'format': 'executive_summary',
                'detail_level': 'high_level_with_drill_down',
                'frequency': frequency_preference,
                'delivery_method': 'dashboard_with_alerts'
            }
        else:  # LONGEVITY
            return {
                'format': 'comprehensive_narrative',
                'detail_level': detail_preference,
                'frequency': frequency_preference,
                'delivery_method': 'detailed_report'
            }
    
    def _apply_security_protocol_enhancements(
        self,
        result: PersonalizationResult,
        comfort_level: str,
        risk_tolerance: str,
        technical_proficiency: str
    ) -> PersonalizationResult:
        """Apply security protocol specific enhancements"""
        
        # Determine appropriate security level
        security_level = self._determine_security_level(comfort_level, risk_tolerance, technical_proficiency)
        security_recommendations = self._generate_security_recommendations(security_level, comfort_level)
        
        enhanced_content = result.personalized_content.copy()
        enhanced_content.update({
            'security_configuration': {
                'recommended_security_level': security_level.value,
                'comfort_level': comfort_level,
                'risk_tolerance': risk_tolerance,
                'technical_proficiency': technical_proficiency,
                'security_recommendations': security_recommendations
            },
            'personalized_security_measures': self._create_personalized_security_measures(
                security_level, comfort_level, result.archetype_adaptation
            )
        })
        
        return PersonalizationResult(
            archetype_adaptation=result.archetype_adaptation,
            physiological_modulation=result.physiological_modulation,
            personalized_content=enhanced_content,
            confidence_score=result.confidence_score,
            personalization_metadata={
                **result.personalization_metadata,
                'guardian_security_enhancement_applied': True,
                'security_level': security_level.value,
                'comfort_level': comfort_level
            }
        )
    
    def _apply_privacy_setting_adaptations(
        self,
        result: PersonalizationResult,
        privacy_preference: PrivacyPreference,
        data_sensitivity_awareness: str,
        sharing_comfort_levels: Dict[str, str]
    ) -> PersonalizationResult:
        """Apply privacy setting specific adaptations"""
        
        enhanced_content = result.personalized_content.copy()
        enhanced_content.update({
            'privacy_configuration': {
                'privacy_preference_level': privacy_preference.value,
                'data_sensitivity_awareness': data_sensitivity_awareness,
                'category_sharing_preferences': sharing_comfort_levels,
                'recommended_privacy_settings': self._generate_privacy_settings(
                    privacy_preference, data_sensitivity_awareness
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
                'guardian_privacy_adaptation_applied': True,
                'privacy_preference': privacy_preference.value
            }
        )
    
    def _apply_compliance_monitoring_adaptations(
        self,
        result: PersonalizationResult,
        role_compliance_needs: Dict[str, Any],
        automation_preference: str,
        reporting_preferences: Dict[str, Any]
    ) -> PersonalizationResult:
        """Apply compliance monitoring specific adaptations"""
        
        enhanced_content = result.personalized_content.copy()
        enhanced_content.update({
            'compliance_strategy': {
                'role_based_needs': role_compliance_needs,
                'automation_level': automation_preference,
                'reporting_configuration': reporting_preferences,
                'monitoring_plan': self._create_compliance_monitoring_plan(
                    role_compliance_needs, automation_preference, reporting_preferences
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
                'guardian_compliance_adaptation_applied': True,
                'automation_preference': automation_preference
            }
        )
    
    def _determine_security_level(self, comfort_level: str, risk_tolerance: str, technical_proficiency: str) -> SecurityLevel:
        """Determine appropriate security level based on user factors"""
        if comfort_level == 'high_comfort' and technical_proficiency == 'high':
            return SecurityLevel.ENHANCED
        elif risk_tolerance == 'low_tolerance':
            return SecurityLevel.ENHANCED
        elif comfort_level == 'efficiency_focused' and risk_tolerance == 'high_tolerance':
            return SecurityLevel.STANDARD
        elif comfort_level == 'guidance_needed':
            return SecurityLevel.STANDARD
        else:
            return SecurityLevel.ENHANCED
    
    def _generate_security_recommendations(self, security_level: SecurityLevel, comfort_level: str) -> List[str]:
        """Generate security recommendations based on level and comfort"""
        recommendations = []
        
        if security_level == SecurityLevel.ENHANCED:
            recommendations.extend([
                'Enable two-factor authentication for all accounts',
                'Use strong, unique passwords with password manager',
                'Regular security audits and monitoring'
            ])
        
        if comfort_level == 'guidance_needed':
            recommendations.extend([
                'Automated security updates and patches',
                'Simple security awareness training',
                'Clear security guidance and notifications'
            ])
        elif comfort_level == 'efficiency_focused':
            recommendations.extend([
                'Streamlined security workflows',
                'Single sign-on integration',
                'Minimal security friction'
            ])
        
        return recommendations[:5]
    
    def _create_personalized_security_measures(
        self,
        security_level: SecurityLevel,
        comfort_level: str,
        archetype_adaptation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create personalized security measures"""
        archetype = archetype_adaptation.get('user_archetype', 'PRIME')
        
        if archetype == 'PRIME':
            return {
                'authentication_method': 'biometric_with_backup',
                'notification_style': 'summary_with_alerts',
                'security_automation': 'high',
                'user_control_level': 'dashboard_overview'
            }
        else:  # LONGEVITY
            return {
                'authentication_method': 'guided_two_factor',
                'notification_style': 'detailed_explanations',
                'security_automation': 'moderate_with_guidance',
                'user_control_level': 'detailed_settings'
            }
    
    def _generate_privacy_settings(self, privacy_preference: PrivacyPreference, awareness_level: str) -> Dict[str, Any]:
        """Generate recommended privacy settings"""
        settings = {
            'data_collection': 'minimal',
            'data_retention': 'short_term',
            'sharing_default': 'opt_in',
            'anonymization': 'enabled'
        }
        
        if privacy_preference == PrivacyPreference.MINIMAL_SHARING:
            settings.update({
                'data_collection': 'essential_only',
                'data_retention': 'minimal',
                'sharing_default': 'explicit_opt_in',
                'anonymization': 'maximum'
            })
        elif privacy_preference == PrivacyPreference.OPEN_SHARING:
            settings.update({
                'data_collection': 'comprehensive',
                'data_retention': 'extended',
                'sharing_default': 'opt_out',
                'anonymization': 'standard'
            })
        
        if awareness_level == 'basic_awareness':
            settings['guidance_level'] = 'comprehensive'
            settings['explanation_detail'] = 'simple'
        elif awareness_level == 'high_awareness':
            settings['guidance_level'] = 'minimal'
            settings['explanation_detail'] = 'technical'
        
        return settings
    
    def _create_compliance_monitoring_plan(
        self,
        role_needs: Dict[str, Any],
        automation_preference: str,
        reporting_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create personalized compliance monitoring plan"""
        plan = {
            'monitoring_frequency': 'continuous',
            'alert_thresholds': 'standard',
            'audit_schedule': 'quarterly',
            'compliance_automation': automation_preference
        }
        
        if role_needs.get('risk_level') == 'high':
            plan.update({
                'monitoring_frequency': 'real_time',
                'alert_thresholds': 'strict',
                'audit_schedule': 'monthly'
            })
        
        plan['reporting'] = {
            'format': reporting_preferences.get('format', 'executive_summary'),
            'frequency': reporting_preferences.get('frequency', 'monthly'),
            'delivery': reporting_preferences.get('delivery_method', 'dashboard_with_alerts')
        }
        
        return plan
    
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
async def personalize_security_compliance(
    security_request: Dict[str, Any],
    user_profile: Dict[str, Any],
    security_type: str = "security_protocols",
    additional_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Complete security and compliance personalization workflow
    
    Args:
        security_request: Security or compliance request
        user_profile: Complete user profile
        security_type: Type of security personalization needed
        additional_data: Additional context data
        
    Returns:
        Complete personalized security strategy
    """
    integration = GUARDIANHybridIntelligenceIntegration()
    
    try:
        if security_type == "security_protocols":
            result = await integration.personalize_security_protocols(
                security_request, user_profile, additional_data.get('threat_context') if additional_data else None
            )
        elif security_type == "privacy_settings":
            result = await integration.personalize_privacy_settings(
                security_request, user_profile, additional_data.get('data_categories') if additional_data else None
            )
        elif security_type == "compliance_monitoring":
            result = await integration.personalize_compliance_monitoring(
                security_request, user_profile, additional_data.get('regulatory_context') if additional_data else None
            )
        else:
            result = await integration.personalize_security_protocols(security_request, user_profile)
        
        return {
            'personalized_security': result.personalized_content,
            'archetype_considerations': result.archetype_adaptation,
            'security_modulation': result.physiological_modulation,
            'confidence_score': result.confidence_score,
            'metadata': result.personalization_metadata
        }
        
    except Exception as e:
        logger.error(f"Error in security compliance personalization: {e}")
        return {
            'error': str(e),
            'fallback_mode': True,
            'timestamp': datetime.now().isoformat()
        }


# Export the integration class
__all__ = ['GUARDIANHybridIntelligenceIntegration', 'personalize_security_compliance']