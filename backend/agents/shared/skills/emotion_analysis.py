"""
Shared Emotion Analysis Skills
==============================

Consolidated emotion analysis functionality used across multiple agents.
Eliminates duplication between motivation, wellness, and other agents.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re

from core.logging_config import get_logger
from clients.vertex_ai.client import VertexAIClient

logger = get_logger(__name__)


class EmotionAnalysisSkill:
    """
    Unified emotion analysis skill for all NGX agents.
    
    Provides consistent emotion detection and analysis across:
    - Text analysis
    - Voice tone analysis
    - Behavioral pattern recognition
    - Emotional state tracking
    """
    
    # Emotion categories with indicators
    EMOTION_INDICATORS = {
        "happy": {
            "keywords": ["happy", "joy", "excited", "great", "wonderful", "amazing", "fantastic"],
            "emojis": ["😊", "😄", "🎉", "✨", "💪", "🙌"],
            "patterns": [r"\b(love|loving|loved)\b", r"\b(awesome|excellent)\b"],
            "score_weight": 1.0
        },
        "motivated": {
            "keywords": ["motivated", "determined", "ready", "pumped", "focused", "driven"],
            "emojis": ["💪", "🔥", "⚡", "🎯", "🚀"],
            "patterns": [r"\b(can't wait|let's go|bring it on)\b", r"\b(goal|achieve|success)\b"],
            "score_weight": 0.9
        },
        "stressed": {
            "keywords": ["stressed", "overwhelmed", "anxious", "worried", "pressure", "tense"],
            "emojis": ["😰", "😟", "😣", "😩"],
            "patterns": [r"\b(too much|can't handle|struggling)\b", r"\b(deadline|busy|hectic)\b"],
            "score_weight": -0.8
        },
        "sad": {
            "keywords": ["sad", "down", "depressed", "unhappy", "disappointed", "lonely"],
            "emojis": ["😢", "😭", "💔", "😞"],
            "patterns": [r"\b(miss|missing|lost)\b", r"\b(alone|isolated)\b"],
            "score_weight": -1.0
        },
        "frustrated": {
            "keywords": ["frustrated", "angry", "annoyed", "irritated", "mad", "upset"],
            "emojis": ["😤", "😠", "😡", "🤬"],
            "patterns": [r"\b(not working|broken|failed)\b", r"\b(hate|sick of|tired of)\b"],
            "score_weight": -0.7
        },
        "neutral": {
            "keywords": ["okay", "fine", "alright", "normal", "regular"],
            "emojis": ["😐", "🤷"],
            "patterns": [r"\b(same as usual|nothing special)\b"],
            "score_weight": 0.0
        }
    }
    
    def __init__(self, vertex_client: Optional[VertexAIClient] = None):
        """Initialize emotion analysis skill."""
        self.vertex_client = vertex_client or VertexAIClient()
        self._emotion_history: Dict[str, List[Dict[str, Any]]] = {}
    
    async def analyze_text_emotion(self, text: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze emotional content in text.
        
        Args:
            text: Text to analyze
            user_id: Optional user ID for tracking history
            
        Returns:
            Dict containing emotion analysis results
        """
        try:
            # Basic analysis using patterns
            emotion_scores = self._analyze_with_patterns(text)
            
            # Enhanced analysis with AI if available
            if self.vertex_client:
                ai_analysis = await self._analyze_with_ai(text)
                emotion_scores = self._merge_analyses(emotion_scores, ai_analysis)
            
            # Determine primary emotion
            primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
            
            # Calculate overall sentiment
            sentiment_score = sum(
                score * self.EMOTION_INDICATORS[emotion]["score_weight"]
                for emotion, score in emotion_scores.items()
            )
            
            result = {
                "primary_emotion": primary_emotion,
                "emotion_scores": emotion_scores,
                "sentiment": self._classify_sentiment(sentiment_score),
                "sentiment_score": sentiment_score,
                "confidence": self._calculate_confidence(emotion_scores),
                "timestamp": datetime.now().isoformat()
            }
            
            # Track history if user_id provided
            if user_id:
                self._track_emotion_history(user_id, result)
            
            logger.info(f"Emotion analysis complete: {primary_emotion} ({sentiment_score:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Error in emotion analysis: {e}")
            return self._create_fallback_analysis()
    
    async def analyze_voice_emotion(self, voice_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze emotion from voice features.
        
        Args:
            voice_features: Voice analysis features (pitch, tempo, energy, etc.)
            
        Returns:
            Dict containing voice emotion analysis
        """
        try:
            # Map voice features to emotions
            emotion_scores = {
                "happy": self._score_happy_voice(voice_features),
                "motivated": self._score_motivated_voice(voice_features),
                "stressed": self._score_stressed_voice(voice_features),
                "sad": self._score_sad_voice(voice_features),
                "frustrated": self._score_frustrated_voice(voice_features),
                "neutral": 0.3  # Base neutral score
            }
            
            # Normalize scores
            total = sum(emotion_scores.values())
            if total > 0:
                emotion_scores = {k: v/total for k, v in emotion_scores.items()}
            
            return {
                "emotion_scores": emotion_scores,
                "primary_emotion": max(emotion_scores.items(), key=lambda x: x[1])[0],
                "voice_energy": voice_features.get("energy", 0.5),
                "voice_variance": voice_features.get("pitch_variance", 0.5)
            }
            
        except Exception as e:
            logger.error(f"Error in voice emotion analysis: {e}")
            return {"emotion_scores": {"neutral": 1.0}, "primary_emotion": "neutral"}
    
    def get_emotion_trend(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Get emotion trend for a user over specified days.
        
        Args:
            user_id: User identifier
            days: Number of days to analyze
            
        Returns:
            Dict containing emotion trends and insights
        """
        history = self._emotion_history.get(user_id, [])
        
        if not history:
            return {
                "trend": "no_data",
                "insights": ["No emotion data available yet"],
                "recommendations": ["Continue tracking your emotional state"]
            }
        
        # Analyze recent emotions
        recent_emotions = history[-days*10:]  # Assume ~10 interactions per day
        
        # Calculate emotion frequencies
        emotion_counts = {}
        sentiment_scores = []
        
        for entry in recent_emotions:
            emotion = entry["primary_emotion"]
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            sentiment_scores.append(entry["sentiment_score"])
        
        # Determine trend
        trend = self._calculate_trend(sentiment_scores)
        
        # Generate insights
        insights = self._generate_emotion_insights(emotion_counts, trend)
        
        # Generate recommendations
        recommendations = self._generate_emotion_recommendations(emotion_counts, trend)
        
        return {
            "trend": trend,
            "dominant_emotions": sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            "average_sentiment": sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0,
            "insights": insights,
            "recommendations": recommendations
        }
    
    def suggest_emotion_regulation(self, current_emotion: str) -> List[Dict[str, str]]:
        """
        Suggest emotion regulation techniques based on current emotional state.
        
        Args:
            current_emotion: Current emotional state
            
        Returns:
            List of regulation techniques
        """
        techniques = {
            "stressed": [
                {
                    "technique": "Deep Breathing",
                    "description": "Take 5 deep breaths: 4 seconds in, hold for 4, out for 6",
                    "duration": "2-3 minutes"
                },
                {
                    "technique": "Progressive Muscle Relaxation",
                    "description": "Tense and release muscle groups from toes to head",
                    "duration": "5-10 minutes"
                },
                {
                    "technique": "Quick Walk",
                    "description": "Take a brisk 5-minute walk to clear your mind",
                    "duration": "5 minutes"
                }
            ],
            "sad": [
                {
                    "technique": "Gratitude Practice",
                    "description": "Write down 3 things you're grateful for today",
                    "duration": "5 minutes"
                },
                {
                    "technique": "Connect with Someone",
                    "description": "Reach out to a friend or loved one for a quick chat",
                    "duration": "10-15 minutes"
                },
                {
                    "technique": "Uplifting Music",
                    "description": "Listen to your favorite energizing playlist",
                    "duration": "10 minutes"
                }
            ],
            "frustrated": [
                {
                    "technique": "Physical Release",
                    "description": "Do 20 jumping jacks or push-ups to release tension",
                    "duration": "2 minutes"
                },
                {
                    "technique": "Reframe Thoughts",
                    "description": "Write down the frustration and 3 alternative perspectives",
                    "duration": "5 minutes"
                },
                {
                    "technique": "Cool Down",
                    "description": "Splash cold water on face and wrists",
                    "duration": "1 minute"
                }
            ],
            "happy": [
                {
                    "technique": "Capture the Moment",
                    "description": "Write down what's making you happy to revisit later",
                    "duration": "2 minutes"
                },
                {
                    "technique": "Share the Joy",
                    "description": "Share your happiness with someone who would appreciate it",
                    "duration": "5 minutes"
                }
            ],
            "motivated": [
                {
                    "technique": "Channel the Energy",
                    "description": "Start working on your most important task right now",
                    "duration": "25 minutes (Pomodoro)"
                },
                {
                    "technique": "Set Clear Goals",
                    "description": "Write down 3 specific things to accomplish today",
                    "duration": "5 minutes"
                }
            ]
        }
        
        return techniques.get(current_emotion, techniques.get("neutral", []))
    
    # ==================== Private Methods ====================
    
    def _analyze_with_patterns(self, text: str) -> Dict[str, float]:
        """Analyze text using keyword and pattern matching."""
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, indicators in self.EMOTION_INDICATORS.items():
            score = 0.0
            
            # Check keywords
            for keyword in indicators["keywords"]:
                if keyword in text_lower:
                    score += 0.3
            
            # Check emojis
            for emoji in indicators["emojis"]:
                if emoji in text:
                    score += 0.4
            
            # Check patterns
            for pattern in indicators["patterns"]:
                if re.search(pattern, text_lower):
                    score += 0.5
            
            emotion_scores[emotion] = min(score, 1.0)  # Cap at 1.0
        
        # Normalize if needed
        total = sum(emotion_scores.values())
        if total > 0:
            emotion_scores = {k: v/total for k, v in emotion_scores.items()}
        
        return emotion_scores
    
    async def _analyze_with_ai(self, text: str) -> Dict[str, float]:
        """Use AI for deeper emotion analysis."""
        try:
            prompt = f"""Analyze the emotional content of this text and provide scores (0-1) for each emotion:
            
            Text: "{text}"
            
            Emotions to score:
            - happy
            - motivated  
            - stressed
            - sad
            - frustrated
            - neutral
            
            Respond with just the emotion scores in JSON format."""
            
            response = await self.vertex_client.generate_content(prompt)
            # Parse AI response (implementation depends on response format)
            # For now, return empty dict as fallback
            return {}
            
        except Exception as e:
            logger.warning(f"AI emotion analysis failed: {e}")
            return {}
    
    def _merge_analyses(self, pattern_scores: Dict[str, float], ai_scores: Dict[str, float]) -> Dict[str, float]:
        """Merge pattern-based and AI-based analyses."""
        merged = {}
        
        all_emotions = set(pattern_scores.keys()) | set(ai_scores.keys())
        
        for emotion in all_emotions:
            pattern_score = pattern_scores.get(emotion, 0)
            ai_score = ai_scores.get(emotion, 0)
            
            # Weighted average (pattern analysis gets 40%, AI gets 60%)
            merged[emotion] = (pattern_score * 0.4) + (ai_score * 0.6)
        
        return merged
    
    def _classify_sentiment(self, score: float) -> str:
        """Classify overall sentiment based on score."""
        if score >= 0.6:
            return "very_positive"
        elif score >= 0.2:
            return "positive"
        elif score >= -0.2:
            return "neutral"
        elif score >= -0.6:
            return "negative"
        else:
            return "very_negative"
    
    def _calculate_confidence(self, emotion_scores: Dict[str, float]) -> float:
        """Calculate confidence in emotion detection."""
        if not emotion_scores:
            return 0.0
        
        # Higher confidence when one emotion dominates
        max_score = max(emotion_scores.values())
        avg_score = sum(emotion_scores.values()) / len(emotion_scores)
        
        confidence = (max_score - avg_score) / (1 - avg_score) if avg_score < 1 else 1.0
        return min(max(confidence, 0.0), 1.0)
    
    def _score_happy_voice(self, features: Dict[str, Any]) -> float:
        """Score happiness indicators in voice."""
        score = 0.0
        
        # Higher pitch variation
        if features.get("pitch_variance", 0) > 0.6:
            score += 0.3
        
        # Higher energy
        if features.get("energy", 0) > 0.7:
            score += 0.4
        
        # Faster tempo
        if features.get("tempo", 0) > 0.6:
            score += 0.3
        
        return min(score, 1.0)
    
    def _score_motivated_voice(self, features: Dict[str, Any]) -> float:
        """Score motivation indicators in voice."""
        score = 0.0
        
        # Strong, steady energy
        if 0.6 <= features.get("energy", 0) <= 0.8:
            score += 0.4
        
        # Clear articulation
        if features.get("clarity", 0) > 0.7:
            score += 0.3
        
        # Confident tone
        if features.get("confidence", 0) > 0.6:
            score += 0.3
        
        return min(score, 1.0)
    
    def _score_stressed_voice(self, features: Dict[str, Any]) -> float:
        """Score stress indicators in voice."""
        score = 0.0
        
        # High pitch
        if features.get("pitch", 0) > 0.7:
            score += 0.3
        
        # Irregular rhythm
        if features.get("rhythm_variance", 0) > 0.6:
            score += 0.4
        
        # Tension indicators
        if features.get("tension", 0) > 0.5:
            score += 0.3
        
        return min(score, 1.0)
    
    def _score_sad_voice(self, features: Dict[str, Any]) -> float:
        """Score sadness indicators in voice."""
        score = 0.0
        
        # Lower pitch
        if features.get("pitch", 0) < 0.3:
            score += 0.3
        
        # Low energy
        if features.get("energy", 0) < 0.3:
            score += 0.4
        
        # Slower tempo
        if features.get("tempo", 0) < 0.4:
            score += 0.3
        
        return min(score, 1.0)
    
    def _score_frustrated_voice(self, features: Dict[str, Any]) -> float:
        """Score frustration indicators in voice."""
        score = 0.0
        
        # Sharp changes
        if features.get("intensity_variance", 0) > 0.7:
            score += 0.4
        
        # Clipped speech
        if features.get("articulation_sharpness", 0) > 0.6:
            score += 0.3
        
        # Increased volume
        if features.get("volume", 0) > 0.7:
            score += 0.3
        
        return min(score, 1.0)
    
    def _track_emotion_history(self, user_id: str, analysis: Dict[str, Any]) -> None:
        """Track emotion history for trend analysis."""
        if user_id not in self._emotion_history:
            self._emotion_history[user_id] = []
        
        self._emotion_history[user_id].append(analysis)
        
        # Keep only last 1000 entries per user
        if len(self._emotion_history[user_id]) > 1000:
            self._emotion_history[user_id] = self._emotion_history[user_id][-1000:]
    
    def _calculate_trend(self, sentiment_scores: List[float]) -> str:
        """Calculate emotion trend from sentiment scores."""
        if len(sentiment_scores) < 2:
            return "stable"
        
        # Simple linear regression
        n = len(sentiment_scores)
        x_mean = (n - 1) / 2
        y_mean = sum(sentiment_scores) / n
        
        numerator = sum((i - x_mean) * (score - y_mean) for i, score in enumerate(sentiment_scores))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        if slope > 0.1:
            return "improving"
        elif slope < -0.1:
            return "declining"
        else:
            return "stable"
    
    def _generate_emotion_insights(self, emotion_counts: Dict[str, int], trend: str) -> List[str]:
        """Generate insights based on emotion patterns."""
        insights = []
        
        total = sum(emotion_counts.values())
        if total == 0:
            return ["No emotion data to analyze"]
        
        # Dominant emotion insight
        dominant = max(emotion_counts.items(), key=lambda x: x[1])
        percentage = (dominant[1] / total) * 100
        insights.append(f"Your dominant emotion has been '{dominant[0]}' ({percentage:.0f}% of interactions)")
        
        # Trend insight
        trend_messages = {
            "improving": "Your emotional state has been improving recently! 📈",
            "declining": "Your emotional state seems to be declining. Let's work on improving it 💪",
            "stable": "Your emotional state has been relatively stable"
        }
        insights.append(trend_messages.get(trend, ""))
        
        # Variety insight
        emotion_variety = len([e for e, c in emotion_counts.items() if c > 0])
        if emotion_variety >= 4:
            insights.append("You're experiencing a wide range of emotions, which is normal and healthy")
        elif emotion_variety <= 2:
            insights.append("Your emotional range seems limited. Try exploring what might be causing this pattern")
        
        return insights
    
    def _generate_emotion_recommendations(self, emotion_counts: Dict[str, int], trend: str) -> List[str]:
        """Generate recommendations based on emotion patterns."""
        recommendations = []
        
        # Get most common emotions
        sorted_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_emotions:
            return ["Continue tracking your emotions for personalized recommendations"]
        
        dominant_emotion = sorted_emotions[0][0]
        
        # Recommendations based on dominant emotion
        if dominant_emotion in ["stressed", "frustrated"]:
            recommendations.extend([
                "Consider incorporating daily stress-reduction techniques",
                "Try scheduling regular breaks throughout your day",
                "Explore mindfulness or meditation practices"
            ])
        elif dominant_emotion == "sad":
            recommendations.extend([
                "Reach out to friends or family for support",
                "Consider engaging in activities that typically bring you joy",
                "Maintain regular exercise and sleep schedules"
            ])
        elif dominant_emotion in ["happy", "motivated"]:
            recommendations.extend([
                "Keep up the positive momentum!",
                "Share your success strategies with others",
                "Set new challenging but achievable goals"
            ])
        
        # Trend-based recommendations
        if trend == "declining":
            recommendations.append("Consider talking to a wellness coach about recent changes")
        elif trend == "improving":
            recommendations.append("Whatever you're doing is working - keep it up!")
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def _create_fallback_analysis(self) -> Dict[str, Any]:
        """Create fallback emotion analysis when analysis fails."""
        return {
            "primary_emotion": "neutral",
            "emotion_scores": {"neutral": 1.0},
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "confidence": 0.0,
            "timestamp": datetime.now().isoformat(),
            "fallback": True
        }