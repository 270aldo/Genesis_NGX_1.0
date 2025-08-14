# AI-Specific Testing Framework for GENESIS

This directory contains specialized testing utilities for AI agent validation, including semantic similarity testing, response quality assessment, and non-deterministic behavior validation.

## Testing Approach

### 1. Semantic Similarity Validation

- **Purpose**: Validate that AI responses are semantically appropriate and relevant
- **Method**: Uses embedding-based similarity comparison against expected response patterns
- **Thresholds**: Configurable similarity scores for different agent types

### 2. Response Quality Assessment

- **Content Analysis**: Length, structure, and completeness validation
- **Domain-Specific Keywords**: Training, nutrition, and progress-related terminology
- **Helpfulness Metrics**: Actionable advice, specificity, and user engagement

### 3. Non-Deterministic Testing

- **Multiple Run Validation**: Same query tested multiple times
- **Consistency Checks**: Core message consistency across variations
- **Quality Range Assessment**: Acceptable variance in response quality

### 4. Agent-Specific Validation

- **BLAZE (Training)**: Exercise terminology, program structure, safety considerations
- **SAGE (Nutrition)**: Dietary guidance, macro calculations, meal planning
- **STELLA (Progress)**: Metrics analysis, goal tracking, improvement suggestions

## Test Categories

### Unit Tests

- Individual agent response validation
- Prompt engineering effectiveness
- Context handling accuracy

### Integration Tests

- Multi-agent coordination quality
- A2A communication semantic consistency
- End-to-end conversation flow

### Performance Tests

- Response time vs quality trade-offs
- Token usage optimization
- Caching effectiveness

### Regression Tests

- Response quality over time
- Model update impact assessment
- Prompt modification validation

## Running AI Tests

```bash
# Run all AI tests
pytest tests/ai/ -v

# Run semantic similarity tests only
pytest tests/ai/test_semantic_similarity.py -v

# Run agent-specific tests
pytest tests/ai/test_blaze_responses.py -v
pytest tests/ai/test_sage_responses.py -v
pytest tests/ai/test_stella_responses.py -v

# Run with quality reporting
pytest tests/ai/ --ai-quality-report

# Run non-deterministic tests (multiple iterations)
pytest tests/ai/test_response_consistency.py --iterations=10
```

## Configuration

### Quality Thresholds

```python
QUALITY_THRESHOLDS = {
    'blaze': {
        'semantic_similarity': 0.85,
        'min_response_length': 100,
        'required_keywords': ['exercise', 'workout', 'training'],
        'safety_check': True
    },
    'sage': {
        'semantic_similarity': 0.80,
        'min_response_length': 80,
        'required_keywords': ['nutrition', 'diet', 'calories'],
        'health_compliance': True
    },
    'stella': {
        'semantic_similarity': 0.75,
        'min_response_length': 60,
        'required_keywords': ['progress', 'goal', 'metric'],
        'data_accuracy': True
    }
}
```

### Test Data Management

- **Golden Datasets**: Curated query-response pairs for validation
- **Edge Case Scenarios**: Boundary conditions and error cases
- **User Journey Simulations**: Real-world conversation patterns

## Quality Metrics

### Semantic Similarity Metrics

- **Cosine Similarity**: Vector similarity between expected and actual responses
- **BLEU Score**: N-gram based similarity for structured responses
- **Domain Relevance**: Subject-specific terminology presence

### Response Quality Metrics

- **Completeness**: Addresses all aspects of the query
- **Actionability**: Provides specific, implementable advice
- **Safety**: Avoids harmful or dangerous recommendations
- **Personalization**: Incorporates user context appropriately

### Consistency Metrics

- **Core Message Stability**: Essential information consistency across runs
- **Variation Appropriateness**: Acceptable differences in expression
- **Context Maintenance**: Conversation history preservation

## Test Data Structure

### Query Templates

```json
{
  "category": "training",
  "subcategory": "muscle_building",
  "query": "I want to build muscle mass...",
  "user_context": {
    "fitness_level": "beginner",
    "equipment": ["dumbbells"],
    "goals": ["muscle_gain"]
  },
  "expected_elements": [
    "progressive_overload",
    "compound_exercises",
    "rest_periods"
  ],
  "quality_threshold": 0.85
}
```

### Expected Response Patterns

```json
{
  "response_id": "training_muscle_building_001",
  "expected_structure": {
    "greeting": true,
    "assessment": true,
    "recommendations": true,
    "next_steps": true
  },
  "required_elements": [
    "exercise_selection",
    "rep_ranges",
    "progression_plan"
  ],
  "semantic_embeddings": [0.1, 0.2, ...],
  "quality_indicators": {
    "specificity": 0.9,
    "actionability": 0.85,
    "safety": 1.0
  }
}
```

## Advanced Testing Features

### Prompt Injection Testing

- **Malicious Input Resistance**: Validates agent behavior with adversarial prompts
- **Context Boundary Testing**: Ensures agents stay within their domain expertise
- **Safety Filter Validation**: Confirms harmful content detection

### Multi-Language Support

- **Response Language Consistency**: Validates language detection and response matching
- **Cultural Sensitivity**: Tests culturally appropriate responses
- **Translation Quality**: If multilingual support is available

### Contextual Awareness Testing

- **Conversation History**: Tests memory and context retention
- **User Profile Integration**: Validates personalization based on user data
- **Environmental Context**: Tests adaptation to user's current situation

## Reporting and Analytics

### Quality Reports

- **Agent Performance Comparison**: Side-by-side quality metrics
- **Temporal Quality Trends**: Response quality over time
- **Query Category Analysis**: Performance by query type

### Regression Detection

- **Quality Degradation Alerts**: Automated detection of performance drops
- **A/B Testing Framework**: Compare different model versions or prompts
- **Canary Deployment Validation**: Safe rollout of AI model updates

## Integration with CI/CD

### Automated Quality Gates

- **Minimum Quality Thresholds**: Block deployments below quality standards
- **Regression Prevention**: Compare against baseline performance
- **Performance Impact Assessment**: Monitor resource usage vs quality

### Continuous Monitoring

- **Real-time Quality Tracking**: Live monitoring of AI response quality
- **User Feedback Integration**: Incorporate user ratings into quality metrics
- **Alert System**: Notify when quality drops below thresholds
