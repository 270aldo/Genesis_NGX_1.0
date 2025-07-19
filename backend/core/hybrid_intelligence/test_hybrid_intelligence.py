"""
GENESIS NGX Agents - Hybrid Intelligence Engine Test Suite
==========================================================

Comprehensive test suite for the Hybrid Intelligence Engine.
Tests both individual components and full integration scenarios.

Author: Claude AI Assistant
Version: 1.0.0
Created: 2025-01-09
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any

# Import system components
from hybrid_intelligence_engine import (
    HybridIntelligenceEngine,
    UserProfile,
    PersonalizationContext,
    PersonalizationResult,
    UserArchetype,
    PersonalizationMode,
    ArchetypeAdaptationLayer,
    PhysiologicalModulationLayer,
    ContinuousLearningEngine
)

from models import (
    UserProfileData,
    UserBiometrics,
    WorkoutData,
    WorkoutIntensity,
    FitnessLevel,
    BiomarkerData
)


class TestHybridIntelligenceEngine:
    """Test suite for the main Hybrid Intelligence Engine"""
    
    @pytest.fixture
    def sample_user_profile(self):
        """Create a sample user profile for testing"""
        return UserProfile(
            user_id="test_user_001",
            archetype=UserArchetype.PRIME,
            age=32,
            gender="male",
            fitness_level="advanced",
            injury_history=["knee_strain_2023"],
            sleep_quality=0.7,
            stress_level=0.4,
            energy_level=0.8,
            recent_workouts=[
                {
                    "date": "2025-01-08",
                    "type": "strength",
                    "intensity": 0.8,
                    "duration": 60
                },
                {
                    "date": "2025-01-06",
                    "type": "cardio",
                    "intensity": 0.6,
                    "duration": 45
                }
            ],
            time_constraints={"weekdays": 60, "weekends": 90},
            equipment_access=["gym", "home_weights"],
            biomarkers={"testosterone": 650, "cortisol": 12},
            preference_scores={"high_intensity": 0.9, "compound_movements": 0.8}
        )
    
    @pytest.fixture
    def sample_longevity_profile(self):
        """Create a sample longevity user profile"""
        return UserProfile(
            user_id="test_user_002",
            archetype=UserArchetype.LONGEVITY,
            age=45,
            gender="female",
            fitness_level="intermediate",
            injury_history=["shoulder_impingement_2022"],
            sleep_quality=0.6,
            stress_level=0.6,
            energy_level=0.5,
            recent_workouts=[
                {
                    "date": "2025-01-07",
                    "type": "yoga",
                    "intensity": 0.4,
                    "duration": 60
                }
            ],
            time_constraints={"weekdays": 45, "weekends": 60},
            equipment_access=["home_basic"],
            preference_scores={"flexibility": 0.9, "balance": 0.8}
        )
    
    @pytest.fixture
    def hybrid_engine(self):
        """Create a Hybrid Intelligence Engine instance"""
        return HybridIntelligenceEngine()
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, hybrid_engine):
        """Test engine initialization"""
        assert hybrid_engine.archetype_layer is not None
        assert hybrid_engine.physiological_layer is not None
        assert hybrid_engine.learning_engine is not None
        assert isinstance(hybrid_engine.archetype_layer, ArchetypeAdaptationLayer)
        assert isinstance(hybrid_engine.physiological_layer, PhysiologicalModulationLayer)
        assert isinstance(hybrid_engine.learning_engine, ContinuousLearningEngine)
    
    @pytest.mark.asyncio
    async def test_prime_user_personalization(self, hybrid_engine, sample_user_profile):
        """Test personalization for PRIME archetype user"""
        
        context = PersonalizationContext(
            user_profile=sample_user_profile,
            agent_type="elite_training_strategist",
            request_type="training_plan",
            request_content="I want to build muscle and strength efficiently"
        )
        
        result = await hybrid_engine.personalize_for_user(
            context=context,
            mode=PersonalizationMode.ADVANCED
        )
        
        # Verify result structure
        assert isinstance(result, PersonalizationResult)
        assert result.confidence_score > 0.0
        assert result.confidence_score <= 1.0
        assert len(result.explanation) > 0
        
        # Verify archetype-specific adaptations
        combined_recs = result.combined_recommendations
        assert combined_recs["personalization_metadata"]["archetype"] == "prime"
        
        # Verify PRIME-specific characteristics
        comm_style = combined_recs["communication_adaptations"]["style"]
        assert comm_style == "direct_performance"
        
        # Verify physiological modulation applied
        assert "physiological_modulation" in combined_recs["protocol_adaptations"]
        assert "readiness_score" in combined_recs["personalization_metadata"]
    
    @pytest.mark.asyncio
    async def test_longevity_user_personalization(self, hybrid_engine, sample_longevity_profile):
        """Test personalization for LONGEVITY archetype user"""
        
        context = PersonalizationContext(
            user_profile=sample_longevity_profile,
            agent_type="elite_training_strategist",
            request_type="wellness_plan",
            request_content="I want to maintain health and prevent injuries"
        )
        
        result = await hybrid_engine.personalize_for_user(
            context=context,
            mode=PersonalizationMode.ADVANCED
        )
        
        # Verify result structure
        assert isinstance(result, PersonalizationResult)
        assert result.confidence_score > 0.0
        
        # Verify archetype-specific adaptations
        combined_recs = result.combined_recommendations
        assert combined_recs["personalization_metadata"]["archetype"] == "longevity"
        
        # Verify LONGEVITY-specific characteristics
        comm_style = combined_recs["communication_adaptations"]["style"]
        assert comm_style == "supportive_educational"
        
        # Verify age-appropriate intensity adjustments
        age_factor = combined_recs["personalization_metadata"]["age_factor"]
        assert age_factor["intensity"] <= 0.9  # Reduced intensity for 45-year-old
        assert age_factor["safety_factor"] >= 1.0  # Increased safety emphasis
    
    @pytest.mark.asyncio
    async def test_physiological_state_impact(self, hybrid_engine, sample_user_profile):
        """Test how physiological state impacts personalization"""
        
        # Test with poor physiological state
        poor_state_profile = sample_user_profile
        poor_state_profile.sleep_quality = 0.3
        poor_state_profile.stress_level = 0.8
        poor_state_profile.energy_level = 0.2
        
        context = PersonalizationContext(
            user_profile=poor_state_profile,
            agent_type="elite_training_strategist",
            request_type="training_plan",
            request_content="I need a workout plan"
        )
        
        result = await hybrid_engine.personalize_for_user(context)
        
        # Verify intensity was reduced due to poor state
        protocol_adaptations = result.combined_recommendations["protocol_adaptations"]
        intensity_mod = protocol_adaptations["physiological_modulation"]["modulated_intensity"]
        assert intensity_mod < 0.7  # Should be reduced
        
        # Verify recovery emphasis increased
        recovery_focus = protocol_adaptations["recovery_focus"]
        assert recovery_focus["adjusted_recovery_focus"] > 1.0
    
    @pytest.mark.asyncio
    async def test_confidence_scoring(self, hybrid_engine, sample_user_profile):
        """Test confidence scoring mechanism"""
        
        # Test with complete data
        complete_profile = sample_user_profile
        complete_profile.biomarkers = {"testosterone": 650, "cortisol": 12, "vitamin_d": 45}
        
        context = PersonalizationContext(
            user_profile=complete_profile,
            agent_type="elite_training_strategist",
            request_type="training_plan",
            request_content="Detailed training plan request"
        )
        
        result_complete = await hybrid_engine.personalize_for_user(context)
        
        # Test with minimal data
        minimal_profile = UserProfile(
            user_id="minimal_user",
            archetype=UserArchetype.PRIME,
            age=30,
            gender="male"
        )
        
        context_minimal = PersonalizationContext(
            user_profile=minimal_profile,
            agent_type="elite_training_strategist",
            request_type="training_plan",
            request_content="Basic training plan"
        )
        
        result_minimal = await hybrid_engine.personalize_for_user(context_minimal)
        
        # Complete profile should have higher confidence
        assert result_complete.confidence_score > result_minimal.confidence_score
    
    @pytest.mark.asyncio
    async def test_learning_integration(self, hybrid_engine, sample_user_profile):
        """Test learning engine integration"""
        
        context = PersonalizationContext(
            user_profile=sample_user_profile,
            agent_type="elite_training_strategist",
            request_type="training_plan",
            request_content="Test learning integration"
        )
        
        result = await hybrid_engine.personalize_for_user(context)
        
        # Simulate user feedback
        feedback = {
            "satisfaction": 0.9,
            "outcome_success": 0.8,
            "found_helpful": True,
            "intensity_appropriate": True
        }
        
        # Test learning from feedback
        await hybrid_engine.learning_engine.learn_from_interaction(
            context=context,
            result=result,
            user_feedback=feedback
        )
        
        # Verify learning data was stored
        user_learning_data = hybrid_engine.learning_engine.learning_data.get(sample_user_profile.user_id)
        assert user_learning_data is not None
        assert len(user_learning_data) > 0
        
        effectiveness_score = user_learning_data[0]["effectiveness_score"]
        assert effectiveness_score > 0.7  # Should be high due to positive feedback
    
    @pytest.mark.asyncio
    async def test_user_insights(self, hybrid_engine, sample_user_profile):
        """Test user insights generation"""
        
        # Create multiple interactions
        for i in range(5):
            context = PersonalizationContext(
                user_profile=sample_user_profile,
                agent_type="elite_training_strategist",
                request_type=f"request_type_{i}",
                request_content=f"Request {i}"
            )
            
            result = await hybrid_engine.personalize_for_user(context)
            
            # Simulate varying feedback
            feedback = {
                "satisfaction": 0.8 + (i * 0.05),  # Improving satisfaction
                "outcome_success": 0.7 + (i * 0.05)
            }
            
            await hybrid_engine.learning_engine.learn_from_interaction(
                context=context,
                result=result,
                user_feedback=feedback
            )
        
        # Get user insights
        insights = await hybrid_engine.get_user_insights(sample_user_profile.user_id)
        
        # Verify insights structure
        assert "total_interactions" in insights
        assert "average_effectiveness" in insights
        assert "recent_performance" in insights
        assert "improvement_trends" in insights
        
        # Verify data accuracy
        assert insights["total_interactions"] == 5
        assert insights["average_effectiveness"] > 0.0
        assert insights["recent_performance"] > insights["average_effectiveness"]  # Should be improving
    
    @pytest.mark.asyncio
    async def test_basic_vs_advanced_modes(self, hybrid_engine, sample_user_profile):
        """Test different personalization modes"""
        
        context = PersonalizationContext(
            user_profile=sample_user_profile,
            agent_type="elite_training_strategist",
            request_type="training_plan",
            request_content="Compare personalization modes"
        )
        
        # Test basic mode
        result_basic = await hybrid_engine.personalize_for_user(
            context=context,
            mode=PersonalizationMode.BASIC
        )
        
        # Test advanced mode
        result_advanced = await hybrid_engine.personalize_for_user(
            context=context,
            mode=PersonalizationMode.ADVANCED
        )
        
        # Advanced mode should have more detailed physiological modulation
        basic_physio = result_basic.physiological_modulation
        advanced_physio = result_advanced.physiological_modulation
        
        assert basic_physio.get("status") == "basic_mode"
        assert advanced_physio.get("status") != "basic_mode"
        assert "real_time_adjustments" in advanced_physio
    
    @pytest.mark.asyncio
    async def test_age_adaptations(self, hybrid_engine):
        """Test age-based adaptations"""
        
        # Test young user (25)
        young_profile = UserProfile(
            user_id="young_user",
            archetype=UserArchetype.PRIME,
            age=25,
            gender="male",
            fitness_level="advanced"
        )
        
        # Test older user (55)
        older_profile = UserProfile(
            user_id="older_user",
            archetype=UserArchetype.PRIME,
            age=55,
            gender="male",
            fitness_level="advanced"
        )
        
        # Test both
        for profile in [young_profile, older_profile]:
            context = PersonalizationContext(
                user_profile=profile,
                agent_type="elite_training_strategist",
                request_type="training_plan",
                request_content="Age-appropriate training"
            )
            
            result = await hybrid_engine.personalize_for_user(context)
            age_factor = result.combined_recommendations["personalization_metadata"]["age_factor"]
            
            if profile.age == 25:
                assert age_factor["intensity"] >= 0.9  # High intensity for young
                assert age_factor["safety_factor"] <= 0.9  # Lower safety emphasis
            else:  # 55 years old
                assert age_factor["intensity"] <= 0.8  # Reduced intensity
                assert age_factor["safety_factor"] >= 1.0  # Higher safety emphasis
    
    @pytest.mark.asyncio
    async def test_injury_history_impact(self, hybrid_engine):
        """Test impact of injury history on personalization"""
        
        # Profile with extensive injury history
        injured_profile = UserProfile(
            user_id="injured_user",
            archetype=UserArchetype.PRIME,
            age=30,
            gender="male",
            injury_history=["knee_acl_2022", "shoulder_impingement_2023", "lower_back_2024"],
            fitness_level="intermediate"
        )
        
        context = PersonalizationContext(
            user_profile=injured_profile,
            agent_type="elite_training_strategist",
            request_type="training_plan",
            request_content="Safe training with injury history"
        )
        
        result = await hybrid_engine.personalize_for_user(context)
        
        # Verify safety adaptations
        safety_mods = result.combined_recommendations["protocol_adaptations"]["safety_modifications"]
        assert safety_mods["safety_factor"] > 1.0  # Increased safety
        assert len(safety_mods["injury_considerations"]) == 3  # All injuries considered
        assert len(safety_mods["safety_recommendations"]) > 0
    
    @pytest.mark.asyncio
    async def test_archetype_differences(self, hybrid_engine):
        """Test clear differences between PRIME and LONGEVITY archetypes"""
        
        # Create identical profiles except for archetype
        base_profile_data = {
            "user_id": "comparison_user",
            "age": 35,
            "gender": "female",
            "fitness_level": "intermediate",
            "sleep_quality": 0.7,
            "stress_level": 0.5,
            "energy_level": 0.6
        }
        
        prime_profile = UserProfile(**base_profile_data, archetype=UserArchetype.PRIME)
        longevity_profile = UserProfile(**base_profile_data, archetype=UserArchetype.LONGEVITY)
        
        # Test both archetypes
        prime_context = PersonalizationContext(
            user_profile=prime_profile,
            agent_type="elite_training_strategist",
            request_type="training_plan",
            request_content="Fitness plan comparison"
        )
        
        longevity_context = PersonalizationContext(
            user_profile=longevity_profile,
            agent_type="elite_training_strategist",
            request_type="training_plan",
            request_content="Fitness plan comparison"
        )
        
        prime_result = await hybrid_engine.personalize_for_user(prime_context)
        longevity_result = await hybrid_engine.personalize_for_user(longevity_context)
        
        # Compare results
        prime_comm = prime_result.combined_recommendations["communication_adaptations"]
        longevity_comm = longevity_result.combined_recommendations["communication_adaptations"]
        
        assert prime_comm["style"] == "direct_performance"
        assert longevity_comm["style"] == "supportive_educational"
        
        # Verify different focus areas
        prime_focus = prime_result.archetype_adaptation["focus_prioritization"]["primary_areas"]
        longevity_focus = longevity_result.archetype_adaptation["focus_prioritization"]["primary_areas"]
        
        assert "performance_metrics" in prime_focus or "strength" in prime_focus
        assert "mobility" in longevity_focus or "preventive_care" in longevity_focus


class TestArchetypeAdaptationLayer:
    """Test suite for the Archetype Adaptation Layer"""
    
    @pytest.fixture
    def archetype_layer(self):
        return ArchetypeAdaptationLayer()
    
    @pytest.mark.asyncio
    async def test_prime_archetype_adaptation(self, archetype_layer):
        """Test PRIME archetype adaptation"""
        
        context = PersonalizationContext(
            user_profile=UserProfile(
                user_id="prime_test",
                archetype=UserArchetype.PRIME,
                age=28,
                gender="male"
            ),
            agent_type="elite_training_strategist",
            request_type="training_plan",
            request_content="High performance training"
        )
        
        adaptation = await archetype_layer.adapt_for_archetype(context)
        
        assert adaptation["communication_style"] == "direct_performance"
        assert "competition" in adaptation["motivation_approach"]["primary_triggers"]
        assert "performance_data" in adaptation["content_delivery"]["preferred_formats"]
        assert adaptation["goal_framework"] == "achievement_focused"
    
    @pytest.mark.asyncio
    async def test_longevity_archetype_adaptation(self, archetype_layer):
        """Test LONGEVITY archetype adaptation"""
        
        context = PersonalizationContext(
            user_profile=UserProfile(
                user_id="longevity_test",
                archetype=UserArchetype.LONGEVITY,
                age=50,
                gender="female"
            ),
            agent_type="elite_training_strategist",
            request_type="wellness_plan",
            request_content="Sustainable wellness plan"
        )
        
        adaptation = await archetype_layer.adapt_for_archetype(context)
        
        assert adaptation["communication_style"] == "supportive_educational"
        assert "wellness" in adaptation["motivation_approach"]["primary_triggers"]
        assert "educational" in adaptation["content_delivery"]["preferred_formats"]
        assert adaptation["goal_framework"] == "process_focused"
    
    @pytest.mark.asyncio
    async def test_age_factor_calculation(self, archetype_layer):
        """Test age factor calculation for both archetypes"""
        
        # Test PRIME archetype at different ages
        prime_young = archetype_layer._calculate_age_factor(25, UserArchetype.PRIME)
        prime_middle = archetype_layer._calculate_age_factor(40, UserArchetype.PRIME)
        prime_older = archetype_layer._calculate_age_factor(55, UserArchetype.PRIME)
        
        # Verify intensity decreases with age for PRIME
        assert prime_young["intensity"] > prime_middle["intensity"]
        assert prime_middle["intensity"] > prime_older["intensity"]
        
        # Verify safety factor increases with age
        assert prime_young["safety_factor"] < prime_older["safety_factor"]
        
        # Test LONGEVITY archetype
        longevity_young = archetype_layer._calculate_age_factor(35, UserArchetype.LONGEVITY)
        longevity_older = archetype_layer._calculate_age_factor(65, UserArchetype.LONGEVITY)
        
        # LONGEVITY should have lower intensity overall
        assert longevity_young["intensity"] < prime_young["intensity"]
        assert longevity_older["intensity"] < prime_older["intensity"]


class TestPhysiologicalModulationLayer:
    """Test suite for the Physiological Modulation Layer"""
    
    @pytest.fixture
    def physio_layer(self):
        return PhysiologicalModulationLayer()
    
    @pytest.mark.asyncio
    async def test_physiological_state_assessment(self, physio_layer):
        """Test physiological state assessment"""
        
        profile = UserProfile(
            user_id="physio_test",
            archetype=UserArchetype.PRIME,
            age=30,
            gender="male",
            sleep_quality=0.8,
            stress_level=0.3,
            energy_level=0.9,
            recent_workouts=[
                {"date": "2025-01-07", "intensity": 0.7, "duration": 60}
            ]
        )
        
        physio_state = await physio_layer._assess_physiological_state(profile)
        
        assert physio_state["sleep_quality"] == 0.8
        assert physio_state["stress_level"] == 0.3
        assert physio_state["energy_level"] == 0.9
        assert physio_state["readiness_score"] > 0.7  # Should be high
    
    @pytest.mark.asyncio
    async def test_intensity_modulation(self, physio_layer):
        """Test intensity modulation based on physiological state"""
        
        # High readiness state
        high_readiness_state = {
            "readiness_score": 0.9,
            "sleep_quality": 0.9,
            "stress_level": 0.2,
            "energy_level": 0.9,
            "recovery_status": 0.8,
            "injury_risk": 0.1
        }
        
        # Low readiness state
        low_readiness_state = {
            "readiness_score": 0.3,
            "sleep_quality": 0.4,
            "stress_level": 0.8,
            "energy_level": 0.3,
            "recovery_status": 0.2,
            "injury_risk": 0.6
        }
        
        base_intensity = {"base_intensity": "high_performance", "intensity": 0.9}
        
        high_modulation = physio_layer._modulate_intensity(base_intensity, high_readiness_state)
        low_modulation = physio_layer._modulate_intensity(base_intensity, low_readiness_state)
        
        assert high_modulation["modulated_intensity"] > low_modulation["modulated_intensity"]
        assert high_modulation["recommendation"] == "proceed_as_planned"
        assert low_modulation["recommendation"] == "recovery_focus"
    
    @pytest.mark.asyncio
    async def test_recovery_modulation(self, physio_layer):
        """Test recovery focus modulation"""
        
        # Profile requiring more recovery
        high_stress_profile = UserProfile(
            user_id="high_stress",
            archetype=UserArchetype.PRIME,
            age=35,
            gender="male",
            stress_level=0.8,
            sleep_quality=0.4,
            energy_level=0.3
        )
        
        # Low stress profile
        low_stress_profile = UserProfile(
            user_id="low_stress",
            archetype=UserArchetype.PRIME,
            age=35,
            gender="male",
            stress_level=0.2,
            sleep_quality=0.8,
            energy_level=0.8
        )
        
        # Test both profiles
        high_stress_state = await physio_layer._assess_physiological_state(high_stress_profile)
        low_stress_state = await physio_layer._assess_physiological_state(low_stress_profile)
        
        base_archetype = {"protocol_intensity": {"recovery_emphasis": 1.0}}
        
        high_stress_recovery = physio_layer._modulate_recovery_focus(base_archetype, high_stress_state)
        low_stress_recovery = physio_layer._modulate_recovery_focus(base_archetype, low_stress_state)
        
        assert high_stress_recovery["adjusted_recovery_focus"] > low_stress_recovery["adjusted_recovery_focus"]
        assert len(high_stress_recovery["recovery_recommendations"]) > 0


class TestContinuousLearningEngine:
    """Test suite for the Continuous Learning Engine"""
    
    @pytest.fixture
    def learning_engine(self):
        return ContinuousLearningEngine()
    
    @pytest.mark.asyncio
    async def test_learning_from_interaction(self, learning_engine):
        """Test learning from user interactions"""
        
        context = PersonalizationContext(
            user_profile=UserProfile(
                user_id="learning_test",
                archetype=UserArchetype.PRIME,
                age=30,
                gender="male"
            ),
            agent_type="elite_training_strategist",
            request_type="training_plan",
            request_content="Test learning"
        )
        
        result = PersonalizationResult(
            archetype_adaptation={"test": "data"},
            physiological_modulation={"test": "data"},
            combined_recommendations={"test": "data"},
            confidence_score=0.85,
            explanation="Test explanation"
        )
        
        feedback = {
            "satisfaction": 0.9,
            "outcome_success": 0.8,
            "found_helpful": True
        }
        
        await learning_engine.learn_from_interaction(context, result, feedback)
        
        # Verify learning data was stored
        user_data = learning_engine.learning_data.get("learning_test")
        assert user_data is not None
        assert len(user_data) == 1
        assert user_data[0]["effectiveness_score"] > 0.8
    
    @pytest.mark.asyncio
    async def test_effectiveness_calculation(self, learning_engine):
        """Test effectiveness score calculation"""
        
        result = PersonalizationResult(
            archetype_adaptation={},
            physiological_modulation={},
            combined_recommendations={},
            confidence_score=0.7,
            explanation="Test"
        )
        
        # Test with positive feedback
        positive_feedback = {
            "satisfaction": 0.9,
            "outcome_success": 0.8
        }
        
        positive_score = learning_engine._calculate_effectiveness_score(result, positive_feedback)
        
        # Test with negative feedback
        negative_feedback = {
            "satisfaction": 0.3,
            "outcome_success": 0.2
        }
        
        negative_score = learning_engine._calculate_effectiveness_score(result, negative_feedback)
        
        assert positive_score > negative_score
        assert positive_score > 0.7
        assert negative_score < 0.5
    
    @pytest.mark.asyncio
    async def test_adaptation_patterns(self, learning_engine):
        """Test adaptation pattern tracking"""
        
        # Create multiple learning entries for PRIME archetype
        for i in range(10):
            context = PersonalizationContext(
                user_profile=UserProfile(
                    user_id=f"user_{i}",
                    archetype=UserArchetype.PRIME,
                    age=30,
                    gender="male"
                ),
                agent_type="elite_training_strategist",
                request_type="training_plan",
                request_content=f"Training request {i}"
            )
            
            result = PersonalizationResult(
                archetype_adaptation={},
                physiological_modulation={},
                combined_recommendations={},
                confidence_score=0.8,
                explanation="Test"
            )
            
            feedback = {
                "satisfaction": 0.7 + (i * 0.02),  # Gradually improving
                "outcome_success": 0.6 + (i * 0.02)
            }
            
            await learning_engine.learn_from_interaction(context, result, feedback)
        
        # Check adaptation patterns
        prime_patterns = learning_engine.adaptation_patterns.get("prime")
        assert prime_patterns is not None
        assert prime_patterns["total_interactions"] == 10
        assert prime_patterns["average_effectiveness"] > 0.7
        assert len(prime_patterns["successful_patterns"]) > 0


# Integration tests
class TestBLAZEIntegration:
    """Test suite for BLAZE agent integration"""
    
    @pytest.fixture
    def blaze_integration(self):
        """Create BLAZE integration instance"""
        from agents.elite_training_strategist.hybrid_intelligence_integration import BLAZEHybridIntelligenceIntegration
        return BLAZEHybridIntelligenceIntegration()
    
    @pytest.mark.asyncio
    async def test_blaze_personalization_integration(self, blaze_integration):
        """Test BLAZE personalization integration"""
        
        user_data = {
            "user_id": "blaze_test_user",
            "archetype": "prime",
            "age": 28,
            "gender": "male",
            "fitness_level": "advanced",
            "sleep_quality": 0.8,
            "stress_level": 0.3,
            "energy_level": 0.9,
            "recent_workouts": [
                {"date": "2025-01-07", "type": "strength", "intensity": 0.8}
            ],
            "equipment_access": ["gym", "home_weights"],
            "training_preferences": {"high_intensity": 0.9}
        }
        
        result = await blaze_integration.personalize_training_response(
            user_data=user_data,
            request_type="training_plan",
            request_content="Create high-intensity training plan"
        )
        
        assert result["personalization_applied"] is True
        assert result["confidence_score"] > 0.0
        assert "communication_style" in result
        assert "training_adaptations" in result
        assert "motivation_approach" in result
        
        # Verify BLAZE-specific adaptations
        comm_style = result["communication_style"]
        assert comm_style["style"] in ["motivational_direct", "data_driven_coaching"]
        assert comm_style["voice_adaptations"]["tone"] in ["energetic", "encouraging"]
    
    @pytest.mark.asyncio
    async def test_blaze_training_adaptations(self, blaze_integration):
        """Test BLAZE training adaptations"""
        
        user_data = {
            "user_id": "blaze_training_test",
            "archetype": "prime",
            "age": 32,
            "gender": "male",
            "fitness_level": "advanced",
            "injury_history": ["knee_strain_2023"],
            "sleep_quality": 0.6,  # Moderate sleep
            "stress_level": 0.7,   # Higher stress
            "energy_level": 0.5    # Lower energy
        }
        
        result = await blaze_integration.personalize_training_response(
            user_data=user_data,
            request_type="training_plan",
            request_content="Training plan with injury considerations"
        )
        
        training_adaptations = result["training_adaptations"]
        
        # Should have reduced intensity due to poor physiological state
        assert training_adaptations["intensity_adjustment"] < 0.8
        
        # Should emphasize recovery
        assert training_adaptations["recovery_emphasis"]["adjusted_recovery_focus"] > 1.0
        
        # Should have injury prevention focus
        injury_prevention = training_adaptations["injury_prevention"]
        assert injury_prevention["safety_factor"] > 1.0
        assert len(injury_prevention["injury_considerations"]) > 0


if __name__ == "__main__":
    # Run specific test categories
    import sys
    
    if len(sys.argv) > 1:
        test_category = sys.argv[1]
        if test_category == "engine":
            pytest.main(["-v", "TestHybridIntelligenceEngine"])
        elif test_category == "archetype":
            pytest.main(["-v", "TestArchetypeAdaptationLayer"])
        elif test_category == "physio":
            pytest.main(["-v", "TestPhysiologicalModulationLayer"])
        elif test_category == "learning":
            pytest.main(["-v", "TestContinuousLearningEngine"])
        elif test_category == "blaze":
            pytest.main(["-v", "TestBLAZEIntegration"])
        else:
            print("Available test categories: engine, archetype, physio, learning, blaze")
    else:
        # Run all tests
        pytest.main(["-v", __file__])