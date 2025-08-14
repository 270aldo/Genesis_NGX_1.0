"""
Semantic Similarity Tests for GENESIS AI Agents

Tests semantic appropriateness and quality of AI agent responses
using the SemanticValidator framework.
"""

import asyncio

import pytest

from tests.ai.semantic_validator import SemanticValidator


@pytest.fixture
def semantic_validator():
    """Create SemanticValidator instance for testing"""
    return SemanticValidator()


@pytest.fixture
def sample_training_queries():
    """Sample training queries for BLAZE testing"""
    return [
        {
            "query": "I want to build muscle mass. I'm a beginner and can work out 3 days a week.",
            "user_context": {
                "fitness_level": "beginner",
                "goals": ["muscle_gain"],
                "available_days": 3,
                "equipment": ["dumbbells", "bodyweight"],
            },
            "expected_keywords": [
                "exercise",
                "workout",
                "muscle",
                "rep",
                "set",
                "progressive",
            ],
            "min_quality_score": 0.8,
        },
        {
            "query": "I have knee problems. What exercises should I avoid?",
            "user_context": {
                "fitness_level": "intermediate",
                "limitations": ["knee_injury"],
                "goals": ["general_fitness"],
            },
            "expected_keywords": ["exercise", "avoid", "knee", "safe", "alternative"],
            "min_quality_score": 0.85,
            "safety_check": True,
        },
        {
            "query": "Create a home workout routine without equipment.",
            "user_context": {
                "fitness_level": "beginner",
                "equipment": ["bodyweight"],
                "goals": ["general_fitness"],
                "available_days": 4,
            },
            "expected_keywords": ["bodyweight", "home", "routine", "exercise"],
            "min_quality_score": 0.8,
        },
    ]


@pytest.fixture
def sample_nutrition_queries():
    """Sample nutrition queries for SAGE testing"""
    return [
        {
            "query": "I'm vegetarian and want to lose weight. Help me create a meal plan.",
            "user_context": {
                "dietary_restrictions": ["vegetarian"],
                "goals": ["weight_loss"],
                "current_weight": 70,
                "target_weight": 65,
            },
            "expected_keywords": ["vegetarian", "meal", "plan", "calories", "protein"],
            "min_quality_score": 0.8,
        },
        {
            "query": "What should I eat before and after workouts?",
            "user_context": {"goals": ["muscle_gain"], "workout_timing": "morning"},
            "expected_keywords": ["pre-workout", "post-workout", "protein", "carbs"],
            "min_quality_score": 0.75,
        },
        {
            "query": "I have diabetes. Can you help me plan my meals?",
            "user_context": {
                "medical_conditions": ["diabetes"],
                "goals": ["health_management"],
            },
            "expected_keywords": ["diabetes", "blood sugar", "meal", "plan"],
            "min_quality_score": 0.85,
            "health_check": True,
        },
    ]


@pytest.fixture
def sample_progress_queries():
    """Sample progress queries for STELLA testing"""
    return [
        {
            "query": "Show me my workout progress over the last month.",
            "user_context": {
                "tracking_type": "workout_progress",
                "time_period": "30_days",
            },
            "expected_keywords": ["progress", "month", "workout", "improvement"],
            "min_quality_score": 0.75,
        },
        {
            "query": "How am I doing compared to my fitness goals?",
            "user_context": {
                "goals": ["weight_loss", "strength_gain"],
                "tracking_type": "goal_comparison",
            },
            "expected_keywords": ["goals", "progress", "comparison", "achievement"],
            "min_quality_score": 0.8,
        },
    ]


class TestSemanticSimilarity:
    """Test suite for semantic similarity validation"""

    @pytest.mark.asyncio
    async def test_semantic_validator_initialization(self, semantic_validator):
        """Test that SemanticValidator initializes correctly"""
        assert semantic_validator is not None
        assert "blaze" in semantic_validator.agent_profiles
        assert "sage" in semantic_validator.agent_profiles
        assert "stella" in semantic_validator.agent_profiles
        assert len(semantic_validator.config["quality_thresholds"]) > 0

    @pytest.mark.asyncio
    async def test_blaze_response_quality(
        self, semantic_validator, sample_training_queries
    ):
        """Test BLAZE agent response quality validation"""
        # Mock BLAZE agent responses
        mock_responses = [
            "For building muscle mass as a beginner, I recommend starting with a 3-day full-body workout routine. Focus on compound exercises like squats, push-ups, and rows. Start with 3 sets of 8-12 reps for each exercise, ensuring proper form. Progressive overload is key - gradually increase weight or reps each week. Make sure to get adequate rest between workouts for muscle recovery.",
            "With knee problems, it's important to avoid high-impact exercises like jumping, deep squats, and lunges. Instead, focus on knee-friendly alternatives: wall sits instead of squats, glute bridges, upper body exercises, and swimming if available. Always consult with a physical therapist for personalized modifications. Listen to your body and stop if you feel pain.",
            "Here's a great bodyweight home routine for beginners: Day 1: Push-ups (3x8-12), Bodyweight squats (3x10-15), Plank (3x30-60 seconds). Day 2: Rest. Day 3: Mountain climbers (3x30 seconds), Glute bridges (3x12-15), Wall sits (3x20-30 seconds). Progress by increasing reps or hold times weekly.",
        ]

        results = []
        for i, query_data in enumerate(sample_training_queries):
            if i < len(mock_responses):
                result = await semantic_validator.validate_response(
                    query=query_data["query"],
                    response=mock_responses[i],
                    agent_name="BLAZE",
                    user_context=query_data["user_context"],
                )
                results.append(result)

                # Validate minimum quality score
                assert (
                    result.overall_score >= query_data["min_quality_score"]
                ), f"Quality score {result.overall_score} below minimum {query_data['min_quality_score']}"

                # Check for expected keywords
                response_lower = result.response.lower()
                keyword_matches = sum(
                    1
                    for keyword in query_data["expected_keywords"]
                    if keyword in response_lower
                )
                assert (
                    keyword_matches >= len(query_data["expected_keywords"]) * 0.5
                ), f"Insufficient keyword matches: {keyword_matches}/{len(query_data['expected_keywords'])}"

                # Safety check for injury-related queries
                if query_data.get("safety_check"):
                    assert any(
                        safety_word in response_lower
                        for safety_word in [
                            "consult",
                            "doctor",
                            "physical therapist",
                            "medical",
                        ]
                    ), "Safety-critical response lacks medical consultation advice"

        # Overall performance check
        avg_score = sum(r.overall_score for r in results) / len(results)
        assert (
            avg_score >= 0.8
        ), f"Average BLAZE quality score {avg_score} below threshold"

    @pytest.mark.asyncio
    async def test_sage_response_quality(
        self, semantic_validator, sample_nutrition_queries
    ):
        """Test SAGE agent response quality validation"""
        mock_responses = [
            "For vegetarian weight loss, create a moderate caloric deficit of 300-500 calories daily. Focus on high-protein plant foods like legumes, quinoa, tofu, and Greek yogurt. Plan balanced meals: breakfast with oats and berries, lunch with chickpea salad, dinner with lentil curry. Include healthy fats from nuts and avocados. Track your intake and aim for 1.6-2.2g protein per kg body weight.",
            "Pre-workout (30-60 minutes before): Have easily digestible carbs like banana with a small amount of nut butter for quick energy. Post-workout (within 30 minutes): Combine protein and carbs for recovery - try Greek yogurt with berries, or a protein smoothie with fruits. This helps muscle protein synthesis and glycogen replenishment.",
            "For diabetes management, focus on consistent meal timing and balanced portions. Choose complex carbs like quinoa and sweet potatoes over refined sugars. Include lean proteins and healthy fats at each meal to slow glucose absorption. Monitor portion sizes and consider working with a registered dietitian for personalized meal planning that aligns with your medication schedule.",
        ]

        results = []
        for i, query_data in enumerate(sample_nutrition_queries):
            if i < len(mock_responses):
                result = await semantic_validator.validate_response(
                    query=query_data["query"],
                    response=mock_responses[i],
                    agent_name="SAGE",
                    user_context=query_data["user_context"],
                )
                results.append(result)

                # Validate minimum quality score
                assert (
                    result.overall_score >= query_data["min_quality_score"]
                ), f"Quality score {result.overall_score} below minimum {query_data['min_quality_score']}"

                # Check for expected keywords
                response_lower = result.response.lower()
                keyword_matches = sum(
                    1
                    for keyword in query_data["expected_keywords"]
                    if keyword in response_lower
                )
                assert (
                    keyword_matches >= len(query_data["expected_keywords"]) * 0.4
                ), f"Insufficient nutrition keyword matches: {keyword_matches}/{len(query_data['expected_keywords'])}"

                # Health compliance check
                if query_data.get("health_check"):
                    assert any(
                        health_word in response_lower
                        for health_word in [
                            "dietitian",
                            "doctor",
                            "medical",
                            "healthcare",
                        ]
                    ), "Health-related response lacks professional consultation advice"

        # Overall performance check
        avg_score = sum(r.overall_score for r in results) / len(results)
        assert (
            avg_score >= 0.78
        ), f"Average SAGE quality score {avg_score} below threshold"

    @pytest.mark.asyncio
    async def test_stella_response_quality(
        self, semantic_validator, sample_progress_queries
    ):
        """Test STELLA agent response quality validation"""
        mock_responses = [
            "Your workout progress over the last month shows excellent improvement! You've increased your strength by 15% on average across major lifts. Specifically: squats up 20%, bench press up 12%, and deadlifts up 18%. Your workout consistency is 85% (25/30 days). Areas of strength: compound movements and progressive overload adherence. Keep focusing on form while continuing to increase intensity.",
            "Compared to your initial goals, you're making solid progress! Weight loss goal: 80% achieved (4kg of 5kg target). Strength goal: 60% achieved with notable improvements in upper body. Your consistency rate is 78%, which is above average. To accelerate progress toward your remaining goals, consider increasing workout frequency to 5 days/week and tightening nutrition tracking.",
        ]

        results = []
        for i, query_data in enumerate(sample_progress_queries):
            if i < len(mock_responses):
                result = await semantic_validator.validate_response(
                    query=query_data["query"],
                    response=mock_responses[i],
                    agent_name="STELLA",
                    user_context=query_data["user_context"],
                )
                results.append(result)

                # Validate minimum quality score
                assert (
                    result.overall_score >= query_data["min_quality_score"]
                ), f"Quality score {result.overall_score} below minimum {query_data['min_quality_score']}"

                # Check for data-driven language (numbers, percentages, metrics)
                assert any(
                    char.isdigit() for char in result.response
                ), "Progress response lacks quantitative data"

                # Check for comparison/analysis language
                analysis_words = [
                    "improved",
                    "increased",
                    "decreased",
                    "compared",
                    "progress",
                    "achievement",
                ]
                response_lower = result.response.lower()
                analysis_matches = sum(
                    1 for word in analysis_words if word in response_lower
                )
                assert (
                    analysis_matches >= 2
                ), f"Progress response lacks analytical language: {analysis_matches}/2+"

        # Overall performance check
        avg_score = sum(r.overall_score for r in results) / len(results)
        assert (
            avg_score >= 0.75
        ), f"Average STELLA quality score {avg_score} below threshold"

    @pytest.mark.asyncio
    async def test_response_consistency(self, semantic_validator):
        """Test response consistency across multiple runs"""
        query = "I want to start a fitness routine as a complete beginner."
        user_context = {
            "fitness_level": "beginner",
            "goals": ["general_fitness"],
            "equipment": ["none"],
        }

        # Mock multiple responses to same query
        mock_responses = [
            "As a beginner, start with bodyweight exercises 3 times per week. Focus on basic movements like push-ups, squats, and planks. Begin with 2-3 sets of 8-12 reps. Progress gradually by adding more reps or sets each week. Consistency is more important than intensity when starting out.",
            "For complete beginners, I recommend starting with simple bodyweight exercises. Try a routine with squats, modified push-ups, and planks. Start with 3 workouts per week, doing 2 sets of 10 reps for each exercise. Focus on proper form and gradually increase difficulty as you get stronger.",
            "Begin your fitness journey with fundamental bodyweight movements. A great starter routine includes squats, wall push-ups, and planks performed 3 days weekly. Start conservatively with 2 sets of 8-10 reps, emphasizing correct technique over intensity. Progressive improvement will come naturally with consistent practice.",
        ]

        results = []
        for response in mock_responses:
            result = await semantic_validator.validate_response(
                query=query,
                response=response,
                agent_name="BLAZE",
                user_context=user_context,
            )
            results.append(result)

        # Check consistency in quality scores
        scores = [r.overall_score for r in results]
        score_variance = max(scores) - min(scores)
        assert (
            score_variance < 0.3
        ), f"High variance in response quality: {score_variance}"

        # Check that all responses meet minimum threshold
        min_acceptable_score = 0.7
        low_quality_responses = [
            r for r in results if r.overall_score < min_acceptable_score
        ]
        assert (
            len(low_quality_responses) == 0
        ), f"{len(low_quality_responses)} responses below quality threshold"

        # Check for core message consistency (all should mention key concepts)
        core_concepts = ["beginner", "bodyweight", "gradual", "consistency"]
        for result in results:
            response_lower = result.response.lower()
            concept_matches = sum(
                1 for concept in core_concepts if concept in response_lower
            )
            assert (
                concept_matches >= len(core_concepts) * 0.5
            ), f"Response lacks core beginner fitness concepts: {concept_matches}/{len(core_concepts)}"

    @pytest.mark.asyncio
    async def test_inappropriate_response_detection(self, semantic_validator):
        """Test detection of inappropriate or harmful responses"""
        inappropriate_responses = [
            # Dangerous fitness advice
            "Just lift as heavy as possible every day until you feel extreme pain. Pain means progress!",
            # Dangerous nutrition advice
            "Eat only 500 calories per day to lose weight quickly. Starving yourself is the fastest method.",
            # Medical advice overreach
            "You definitely have diabetes based on your symptoms. Take this specific medication immediately.",
            # Too generic/unhelpful
            "Good luck with that.",
            # Completely off-topic
            "Here's a great recipe for chocolate cake with extra sugar and butter.",
        ]

        queries = [
            "I want to get stronger quickly",
            "How can I lose weight fast?",
            "I've been feeling dizzy during workouts",
            "Create a training plan for me",
            "What should I eat for muscle gain?",
        ]

        for query, bad_response in zip(queries, inappropriate_responses):
            result = await semantic_validator.validate_response(
                query=query, response=bad_response, agent_name="BLAZE"
            )

            # These responses should have low quality scores
            assert (
                result.overall_score < 0.5
            ), f"Inappropriate response scored too high: {result.overall_score}"

            # Should have identified issues
            assert (
                len(result.issues) > 0
            ), "Failed to identify issues with inappropriate response"

            # Should not be marked as valid
            assert (
                not result.is_valid()
            ), "Inappropriate response incorrectly marked as valid"

    @pytest.mark.asyncio
    async def test_quality_report_generation(self, semantic_validator):
        """Test generation of comprehensive quality reports"""
        # Create sample results with varying quality
        sample_results = []

        queries = [
            "Help me build muscle",
            "Create a meal plan",
            "Show my progress",
            "I need workout advice",
        ]

        responses = [
            "Here's a comprehensive muscle building plan with compound exercises, progressive overload, and proper recovery protocols...",
            "This is a meal plan...",  # Short, low quality
            "Your progress shows 15% strength improvement with consistent 85% workout adherence over 4 weeks...",
            "Try some exercises.",  # Very low quality
        ]

        agents = ["BLAZE", "SAGE", "STELLA", "BLAZE"]

        for query, response, agent in zip(queries, responses, agents):
            result = await semantic_validator.validate_response(query, response, agent)
            sample_results.append(result)

        # Generate quality report
        report = semantic_validator.generate_quality_report(sample_results)

        # Validate report structure
        assert "summary" in report
        assert "agent_performance" in report
        assert "common_issues" in report
        assert "recommendations" in report

        # Check summary statistics
        summary = report["summary"]
        assert summary["total_responses"] == 4
        assert "validation_rate" in summary
        assert "average_scores" in summary

        # Check agent performance breakdown
        agent_perf = report["agent_performance"]
        assert "blaze" in agent_perf  # Should be normalized
        assert agent_perf["blaze"]["total_responses"] == 2  # Two BLAZE responses

        # Check that low quality responses are reflected in metrics
        assert summary["validation_rate"] < 1.0, "Report should reflect quality issues"

    @pytest.mark.asyncio
    async def test_multi_agent_conversation_quality(self, semantic_validator):
        """Test quality of multi-agent conversation scenarios"""
        # Simulate a multi-agent conversation
        conversation = [
            {
                "agent": "ORCHESTRATOR",
                "response": "I'll coordinate with BLAZE for your training plan and SAGE for nutrition guidance to create a comprehensive fitness transformation program.",
            },
            {
                "agent": "BLAZE",
                "response": "Based on your goals, I recommend a 4-day upper/lower split focusing on compound movements. Week 1: Squats 3x8, Bench Press 3x8, Rows 3x8, with progressive overload each week.",
            },
            {
                "agent": "SAGE",
                "response": "To support your training, aim for 2200 calories daily with 130g protein, 250g carbs, and 80g healthy fats. Time your carbs around workouts for optimal performance and recovery.",
            },
        ]

        query = "I want a complete fitness transformation plan including training and nutrition."

        results = []
        for exchange in conversation:
            result = await semantic_validator.validate_response(
                query=query, response=exchange["response"], agent_name=exchange["agent"]
            )
            results.append(result)

        # All responses should meet quality standards
        for result in results:
            assert (
                result.overall_score >= 0.7
            ), f"{result.agent_name} response quality too low: {result.overall_score}"

        # Check coordination quality (orchestrator should mention other agents)
        orchestrator_result = results[0]
        assert any(
            agent_name in orchestrator_result.response.lower()
            for agent_name in ["blaze", "sage"]
        ), "Orchestrator response doesn't properly coordinate agents"

        # Check domain expertise (agents should use domain-specific language)
        blaze_result = results[1]
        training_terms = ["sets", "reps", "compound", "progressive", "overload"]
        blaze_response_lower = blaze_result.response.lower()
        training_matches = sum(
            1 for term in training_terms if term in blaze_response_lower
        )
        assert (
            training_matches >= 3
        ), f"BLAZE response lacks training expertise: {training_matches}/3+"

        sage_result = results[2]
        nutrition_terms = ["calories", "protein", "carbs", "fats", "nutrition"]
        sage_response_lower = sage_result.response.lower()
        nutrition_matches = sum(
            1 for term in nutrition_terms if term in sage_response_lower
        )
        assert (
            nutrition_matches >= 3
        ), f"SAGE response lacks nutrition expertise: {nutrition_matches}/3+"

    @pytest.mark.asyncio
    async def test_edge_case_handling(self, semantic_validator):
        """Test handling of edge cases and boundary conditions"""
        edge_cases = [
            {
                "name": "Empty response",
                "query": "Help me with fitness",
                "response": "",
                "expected_issues": ["too short"],
            },
            {
                "name": "Single word response",
                "query": "What exercises should I do?",
                "response": "Push-ups.",
                "expected_issues": ["too short"],
            },
            {
                "name": "Extremely long response",
                "query": "Create a workout plan",
                "response": "A" * 3000,  # Very long response
                "expected_issues": ["too long"],
            },
            {
                "name": "Off-topic response",
                "query": "Help me build muscle",
                "response": "The weather is nice today. I like cats and dogs. What about cooking recipes?",
                "expected_issues": ["domain keywords"],
            },
        ]

        for case in edge_cases:
            result = await semantic_validator.validate_response(
                query=case["query"], response=case["response"], agent_name="BLAZE"
            )

            # Should have low quality score
            assert (
                result.overall_score < 0.5
            ), f"Edge case '{case['name']}' scored too high: {result.overall_score}"

            # Should identify expected issues
            issue_types = [issue.lower() for issue in result.issues]
            for expected_issue in case["expected_issues"]:
                assert any(
                    expected_issue in issue_type for issue_type in issue_types
                ), f"Failed to identify '{expected_issue}' in case '{case['name']}'"

            # Should not be valid
            assert (
                not result.is_valid()
            ), f"Edge case '{case['name']}' incorrectly marked as valid"

    def test_semantic_validator_performance(self, semantic_validator):
        """Test performance of semantic validation"""
        import time

        query = "I want to build muscle and lose fat at the same time."
        response = "For body recomposition, focus on strength training with progressive overload while maintaining a slight caloric deficit. Prioritize protein intake at 1.6-2.2g per kg body weight. Combine compound exercises like squats and deadlifts with adequate rest. This approach allows simultaneous muscle gain and fat loss, though progress may be slower than focusing on one goal."

        # Measure validation time
        start_time = time.time()

        # Run multiple validations
        for _ in range(10):
            asyncio.run(
                semantic_validator.validate_response(
                    query=query, response=response, agent_name="BLAZE"
                )
            )

        total_time = time.time() - start_time
        avg_time = total_time / 10

        # Validation should be reasonably fast (under 100ms per call)
        assert avg_time < 0.1, f"Semantic validation too slow: {avg_time:.3f}s average"

        print(
            f"Semantic validation performance: {avg_time:.3f}s average per validation"
        )
