"""
GENESIS NGX Agents - Hybrid Intelligence Data Models
====================================================

Pydantic models for hybrid intelligence system data structures.
These models ensure type safety and validation for the two-layer
personalization system.

Author: Claude AI Assistant
Version: 1.0.0
Created: 2025-01-09
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class UserArchetype(str, Enum):
    """NGX User Archetypes for strategic personalization"""
    PRIME = "prime"
    LONGEVITY = "longevity"


class PersonalizationMode(str, Enum):
    """Personalization intensity modes"""
    BASIC = "basic"
    ADVANCED = "advanced"
    EXPERT = "expert"


class FitnessLevel(str, Enum):
    """User fitness levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class WorkoutIntensity(str, Enum):
    """Workout intensity levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    MAXIMUM = "maximum"


class BiomarkerData(BaseModel):
    """Biomarker data structure"""
    marker_name: str = Field(..., description="Name of the biomarker")
    value: float = Field(..., description="Measured value")
    unit: str = Field(..., description="Unit of measurement")
    reference_range: Optional[Dict[str, float]] = Field(None, description="Normal reference range")
    date_measured: datetime = Field(..., description="Date when measured")
    lab_source: Optional[str] = Field(None, description="Laboratory source")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class WorkoutData(BaseModel):
    """Individual workout data"""
    workout_id: str = Field(..., description="Unique workout identifier")
    date: datetime = Field(..., description="Workout date")
    type: str = Field(..., description="Type of workout")
    duration_minutes: int = Field(..., ge=1, description="Duration in minutes")
    intensity: WorkoutIntensity = Field(..., description="Workout intensity level")
    calories_burned: Optional[int] = Field(None, ge=0, description="Calories burned")
    exercises: List[Dict[str, Any]] = Field(default_factory=list, description="List of exercises")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserBiometrics(BaseModel):
    """Current user biometric data"""
    sleep_quality: Optional[float] = Field(None, ge=0.0, le=1.0, description="Sleep quality score (0-1)")
    sleep_duration: Optional[float] = Field(None, ge=0.0, le=24.0, description="Sleep duration in hours")
    stress_level: Optional[float] = Field(None, ge=0.0, le=1.0, description="Stress level (0-1)")
    energy_level: Optional[float] = Field(None, ge=0.0, le=1.0, description="Energy level (0-1)")
    heart_rate_resting: Optional[int] = Field(None, ge=30, le=200, description="Resting heart rate")
    heart_rate_variability: Optional[float] = Field(None, ge=0.0, description="HRV score")
    recovery_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Recovery score (0-1)")
    hydration_level: Optional[float] = Field(None, ge=0.0, le=1.0, description="Hydration level (0-1)")
    body_temperature: Optional[float] = Field(None, ge=35.0, le=42.0, description="Body temperature in Celsius")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserConstraints(BaseModel):
    """User constraints and preferences"""
    time_constraints: Dict[str, Any] = Field(default_factory=dict, description="Time availability constraints")
    equipment_access: List[str] = Field(default_factory=list, description="Available equipment")
    dietary_restrictions: List[str] = Field(default_factory=list, description="Dietary restrictions")
    physical_limitations: List[str] = Field(default_factory=list, description="Physical limitations")
    location_constraints: Dict[str, Any] = Field(default_factory=dict, description="Location constraints")
    budget_constraints: Optional[Dict[str, float]] = Field(None, description="Budget constraints")
    
    @validator('time_constraints')
    def validate_time_constraints(cls, v):
        """Validate time constraints structure"""
        if not isinstance(v, dict):
            raise ValueError("time_constraints must be a dictionary")
        return v


class UserProfileData(BaseModel):
    """Complete user profile data model"""
    user_id: str = Field(..., description="Unique user identifier")
    archetype: UserArchetype = Field(..., description="User archetype (PRIME or LONGEVITY)")
    
    # Demographics
    age: int = Field(..., ge=13, le=120, description="User age")
    gender: str = Field(..., description="User gender")
    weight_kg: Optional[float] = Field(None, ge=20.0, le=300.0, description="Weight in kg")
    height_cm: Optional[float] = Field(None, ge=100.0, le=250.0, description="Height in cm")
    
    # Fitness profile
    fitness_level: FitnessLevel = Field(default=FitnessLevel.INTERMEDIATE, description="Current fitness level")
    primary_goals: List[str] = Field(default_factory=list, description="Primary fitness goals")
    injury_history: List[str] = Field(default_factory=list, description="Previous injuries")
    current_medications: List[str] = Field(default_factory=list, description="Current medications")
    
    # Biometric data
    biometrics: UserBiometrics = Field(default_factory=UserBiometrics, description="Current biometric data")
    biomarkers: List[BiomarkerData] = Field(default_factory=list, description="Biomarker data")
    
    # Activity data
    recent_workouts: List[WorkoutData] = Field(default_factory=list, description="Recent workout data")
    
    # Constraints and preferences
    constraints: UserConstraints = Field(default_factory=UserConstraints, description="User constraints")
    
    # Learning data
    interaction_history: List[Dict[str, Any]] = Field(default_factory=list, description="Interaction history")
    preference_scores: Dict[str, float] = Field(default_factory=dict, description="Learned preferences")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now, description="Profile creation timestamp")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @validator('recent_workouts')
    def limit_recent_workouts(cls, v):
        """Limit recent workouts to last 30 entries"""
        return v[-30:] if len(v) > 30 else v


class PersonalizationContextData(BaseModel):
    """Context data for personalization requests"""
    user_profile: UserProfileData = Field(..., description="Complete user profile")
    agent_type: str = Field(..., description="Agent type handling the request")
    request_type: str = Field(..., description="Type of request")
    request_content: str = Field(..., description="Request content")
    current_time: datetime = Field(default_factory=datetime.now, description="Current timestamp")
    session_context: Dict[str, Any] = Field(default_factory=dict, description="Session context data")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ArchetypeAdaptationData(BaseModel):
    """Archetype adaptation result data"""
    communication_style: str = Field(..., description="Adapted communication style")
    motivation_approach: Dict[str, Any] = Field(..., description="Motivation approach")
    content_delivery: Dict[str, Any] = Field(..., description="Content delivery preferences")
    protocol_intensity: Dict[str, Any] = Field(..., description="Protocol intensity settings")
    focus_prioritization: Dict[str, Any] = Field(..., description="Focus area prioritization")
    decision_support: str = Field(..., description="Decision support style")
    goal_framework: str = Field(..., description="Goal framework approach")
    age_modulation: Dict[str, Any] = Field(..., description="Age-based modulation factors")


class PhysiologicalModulationData(BaseModel):
    """Physiological modulation result data"""
    intensity_adjustment: Dict[str, Any] = Field(..., description="Intensity adjustments")
    recovery_emphasis: Dict[str, Any] = Field(..., description="Recovery emphasis adjustments")
    safety_adjustments: Dict[str, Any] = Field(..., description="Safety-related adjustments")
    timing_optimization: Dict[str, Any] = Field(..., description="Timing optimizations")
    biomarker_considerations: Dict[str, Any] = Field(..., description="Biomarker-based considerations")
    real_time_adjustments: Dict[str, Any] = Field(..., description="Real-time physiological adjustments")


class PersonalizationResultData(BaseModel):
    """Complete personalization result data"""
    archetype_adaptation: ArchetypeAdaptationData = Field(..., description="Archetype adaptation results")
    physiological_modulation: PhysiologicalModulationData = Field(..., description="Physiological modulation results")
    combined_recommendations: Dict[str, Any] = Field(..., description="Combined recommendations")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    explanation: str = Field(..., description="Human-readable explanation")
    learning_data: Dict[str, Any] = Field(default_factory=dict, description="Learning data")
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.now, description="Generation timestamp")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LearningEntry(BaseModel):
    """Individual learning entry data"""
    timestamp: datetime = Field(..., description="Learning entry timestamp")
    user_id: str = Field(..., description="User identifier")
    archetype: UserArchetype = Field(..., description="User archetype")
    context: Dict[str, Any] = Field(..., description="Context data")
    personalization_result: Dict[str, Any] = Field(..., description="Personalization result")
    user_feedback: Dict[str, Any] = Field(default_factory=dict, description="User feedback")
    effectiveness_score: float = Field(..., ge=0.0, le=1.0, description="Effectiveness score")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserInsights(BaseModel):
    """User insights data model"""
    user_id: str = Field(..., description="User identifier")
    total_interactions: int = Field(..., ge=0, description="Total number of interactions")
    average_effectiveness: float = Field(..., ge=0.0, le=1.0, description="Average effectiveness score")
    recent_performance: float = Field(..., ge=0.0, le=1.0, description="Recent performance score")
    most_effective_contexts: List[Dict[str, Any]] = Field(default_factory=list, description="Most effective contexts")
    improvement_trends: Dict[str, Any] = Field(..., description="Improvement trends")
    personalization_preferences: Dict[str, Any] = Field(..., description="Learned preferences")
    generated_at: datetime = Field(default_factory=datetime.now, description="Generation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HybridIntelligenceRequest(BaseModel):
    """Request model for hybrid intelligence personalization"""
    user_profile: UserProfileData = Field(..., description="User profile data")
    agent_type: str = Field(..., description="Agent type")
    request_type: str = Field(..., description="Request type")
    request_content: str = Field(..., description="Request content")
    personalization_mode: PersonalizationMode = Field(default=PersonalizationMode.ADVANCED, description="Personalization mode")
    session_context: Dict[str, Any] = Field(default_factory=dict, description="Session context")


class HybridIntelligenceResponse(BaseModel):
    """Response model for hybrid intelligence personalization"""
    success: bool = Field(..., description="Success status")
    result: Optional[PersonalizationResultData] = Field(None, description="Personalization result")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Export all models
__all__ = [
    "UserArchetype",
    "PersonalizationMode", 
    "FitnessLevel",
    "WorkoutIntensity",
    "BiomarkerData",
    "WorkoutData",
    "UserBiometrics",
    "UserConstraints",
    "UserProfileData",
    "PersonalizationContextData",
    "ArchetypeAdaptationData",
    "PhysiologicalModulationData",
    "PersonalizationResultData",
    "LearningEntry",
    "UserInsights",
    "HybridIntelligenceRequest",
    "HybridIntelligenceResponse"
]