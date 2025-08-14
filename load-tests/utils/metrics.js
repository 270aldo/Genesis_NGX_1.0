/**
 * Custom Metrics for GENESIS Load Testing
 *
 * Defines custom metrics specific to AI agent performance,
 * voice synthesis quality, and streaming response metrics.
 */

import { Counter, Gauge, Histogram, Rate, Trend } from 'k6/metrics';

// AI Agent Performance Metrics
export const aiResponseTime = new Trend('ai_response_time');
export const aiResponseQuality = new Rate('ai_response_quality');
export const aiResponseLength = new Trend('ai_response_length');
export const aiTokensUsed = new Counter('ai_tokens_used');
export const aiErrorRate = new Rate('ai_error_rate');

// Voice Synthesis Metrics
export const voiceSynthesisTime = new Trend('voice_synthesis_time');
export const voiceSynthesisSuccess = new Rate('voice_synthesis_success');
export const voiceAudioSize = new Trend('voice_audio_size');
export const voiceQualityScore = new Trend('voice_quality_score');

// Streaming Response Metrics
export const streamingLatency = new Trend('streaming_latency');
export const streamingChunks = new Counter('streaming_chunks_received');
export const streamingCompletionRate = new Rate('streaming_completion_rate');
export const streamingDuration = new Trend('streaming_total_duration');

// Agent-Specific Metrics
export const blazeResponseTime = new Trend('blaze_response_time');
export const sageResponseTime = new Trend('sage_response_time');
export const stellaResponseTime = new Trend('stella_response_time');

// A2A Communication Metrics
export const a2aMessageLatency = new Trend('a2a_message_latency');
export const a2aRoutingSuccess = new Rate('a2a_routing_success');
export const agentLoadBalance = new Gauge('agent_load_balance');

// User Journey Metrics
export const userJourneyCompletionTime = new Trend('user_journey_completion_time');
export const userJourneySuccess = new Rate('user_journey_success');
export const conversationLength = new Trend('conversation_length');

// Database and Cache Metrics
export const cacheHitRate = new Rate('cache_hit_rate');
export const databaseQueryTime = new Trend('database_query_time');
export const redisConnectionTime = new Trend('redis_connection_time');

// Resource Utilization Metrics
export const memoryUsage = new Gauge('memory_usage_mb');
export const cpuUsage = new Gauge('cpu_usage_percent');
export const activeConnections = new Gauge('active_connections');

/**
 * Record AI agent response metrics
 * @param {Object} response - HTTP response object
 * @param {string} agentName - Name of the agent
 * @param {number} startTime - Request start time
 */
export function recordAIMetrics(response, agentName, startTime) {
  const responseTime = Date.now() - startTime;

  // Record general AI metrics
  aiResponseTime.add(responseTime);
  aiErrorRate.add(response.status >= 400);

  // Record agent-specific metrics
  switch (agentName.toLowerCase()) {
    case 'blaze':
    case 'elite-training-strategist':
      blazeResponseTime.add(responseTime);
      break;
    case 'sage':
    case 'precision-nutrition-architect':
      sageResponseTime.add(responseTime);
      break;
    case 'stella':
    case 'progress-tracker':
      stellaResponseTime.add(responseTime);
      break;
  }

  // Analyze response quality if successful
  if (response.status === 200) {
    try {
      const body = JSON.parse(response.body);
      const responseText = body.response || '';

      // Record response length
      aiResponseLength.add(responseText.length);

      // Basic quality assessment
      const qualityScore = assessResponseQuality(responseText, agentName);
      aiResponseQuality.add(qualityScore > 0.7);

      // Estimate tokens used (rough approximation)
      const estimatedTokens = Math.ceil(responseText.length / 4);
      aiTokensUsed.add(estimatedTokens);

    } catch (e) {
      aiResponseQuality.add(0);
    }
  } else {
    aiResponseQuality.add(0);
  }
}

/**
 * Record voice synthesis metrics
 * @param {Object} response - HTTP response object
 * @param {string} text - Original text for synthesis
 * @param {number} startTime - Request start time
 */
export function recordVoiceMetrics(response, text, startTime) {
  const synthesisTime = Date.now() - startTime;

  voiceSynthesisTime.add(synthesisTime);
  voiceSynthesisSuccess.add(response.status === 200);

  if (response.status === 200) {
    // Record audio file size
    const audioSize = response.body ? response.body.length : 0;
    voiceAudioSize.add(audioSize);

    // Estimate quality based on size vs text length ratio
    const qualityRatio = audioSize / (text.length * 100); // Rough estimate
    voiceQualityScore.add(Math.min(qualityRatio, 1.0));
  } else {
    voiceQualityScore.add(0);
  }
}

/**
 * Record streaming response metrics
 * @param {number} startTime - Stream start time
 * @param {number} chunks - Number of chunks received
 * @param {boolean} completed - Whether stream completed successfully
 */
export function recordStreamingMetrics(startTime, chunks, completed) {
  const totalDuration = Date.now() - startTime;

  streamingDuration.add(totalDuration);
  streamingChunks.add(chunks);
  streamingCompletionRate.add(completed);

  if (completed && chunks > 0) {
    const averageLatency = totalDuration / chunks;
    streamingLatency.add(averageLatency);
  }
}

/**
 * Record A2A communication metrics
 * @param {string} fromAgent - Source agent
 * @param {string} toAgent - Target agent
 * @param {number} latency - Message latency in ms
 * @param {boolean} success - Whether routing was successful
 */
export function recordA2AMetrics(fromAgent, toAgent, latency, success) {
  a2aMessageLatency.add(latency);
  a2aRoutingSuccess.add(success);
}

/**
 * Record user journey metrics
 * @param {string} journeyType - Type of user journey
 * @param {number} startTime - Journey start time
 * @param {boolean} success - Whether journey completed successfully
 * @param {number} steps - Number of steps in journey
 */
export function recordUserJourneyMetrics(journeyType, startTime, success, steps = 1) {
  const completionTime = Date.now() - startTime;

  userJourneyCompletionTime.add(completionTime);
  userJourneySuccess.add(success);
  conversationLength.add(steps);
}

/**
 * Assess response quality based on content and agent type
 * @param {string} responseText - AI response text
 * @param {string} agentName - Name of the responding agent
 * @returns {number} Quality score between 0 and 1
 */
function assessResponseQuality(responseText, agentName) {
  let score = 0;

  // Basic length check
  if (responseText.length > 50) score += 0.2;
  if (responseText.length > 200) score += 0.2;

  // Check for agent-specific keywords
  const lowerText = responseText.toLowerCase();

  switch (agentName.toLowerCase()) {
    case 'blaze':
    case 'elite-training-strategist':
      const trainingKeywords = ['exercise', 'workout', 'training', 'muscle', 'strength', 'rep', 'set'];
      const trainingMatches = trainingKeywords.filter(keyword => lowerText.includes(keyword)).length;
      score += Math.min(trainingMatches / trainingKeywords.length, 0.4);
      break;

    case 'sage':
    case 'precision-nutrition-architect':
      const nutritionKeywords = ['nutrition', 'diet', 'meal', 'calories', 'protein', 'carbs', 'food'];
      const nutritionMatches = nutritionKeywords.filter(keyword => lowerText.includes(keyword)).length;
      score += Math.min(nutritionMatches / nutritionKeywords.length, 0.4);
      break;

    case 'stella':
    case 'progress-tracker':
      const progressKeywords = ['progress', 'goal', 'tracking', 'metrics', 'achievement', 'improvement'];
      const progressMatches = progressKeywords.filter(keyword => lowerText.includes(keyword)).length;
      score += Math.min(progressMatches / progressKeywords.length, 0.4);
      break;

    default:
      score += 0.2; // Generic response bonus
  }

  // Check for helpful structure (questions, lists, recommendations)
  if (lowerText.includes('?')) score += 0.1;
  if (lowerText.match(/\d+\./)) score += 0.1; // Numbered lists
  if (lowerText.includes('recommend') || lowerText.includes('suggest')) score += 0.1;

  return Math.min(score, 1.0);
}

/**
 * Record resource utilization metrics
 * @param {Object} systemMetrics - System resource metrics
 */
export function recordSystemMetrics(systemMetrics) {
  if (systemMetrics.memory) {
    memoryUsage.add(systemMetrics.memory);
  }
  if (systemMetrics.cpu) {
    cpuUsage.add(systemMetrics.cpu);
  }
  if (systemMetrics.connections) {
    activeConnections.add(systemMetrics.connections);
  }
}

/**
 * Create a custom threshold configuration
 * @param {Object} config - Threshold configuration
 * @returns {Object} K6 threshold configuration
 */
export function createThresholds(config = {}) {
  return {
    // Default HTTP thresholds
    'http_req_duration': config.httpDuration || ['p(95)<2000'],
    'http_req_failed': config.httpFailed || ['rate<0.1'],

    // AI-specific thresholds
    'ai_response_time': config.aiResponseTime || ['p(95)<30000'],
    'ai_response_quality': config.aiQuality || ['rate>0.8'],
    'ai_error_rate': config.aiErrorRate || ['rate<0.1'],

    // Voice thresholds
    'voice_synthesis_time': config.voiceTime || ['p(95)<15000'],
    'voice_synthesis_success': config.voiceSuccess || ['rate>0.95'],

    // Streaming thresholds
    'streaming_completion_rate': config.streamingCompletion || ['rate>0.9'],
    'streaming_latency': config.streamingLatency || ['p(95)<5000'],

    // A2A thresholds
    'a2a_message_latency': config.a2aLatency || ['p(95)<1000'],
    'a2a_routing_success': config.a2aSuccess || ['rate>0.95'],

    // User journey thresholds
    'user_journey_success': config.journeySuccess || ['rate>0.9'],
    'user_journey_completion_time': config.journeyTime || ['p(95)<60000'],
  };
}
