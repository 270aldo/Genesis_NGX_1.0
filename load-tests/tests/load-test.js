/**
 * GENESIS Load Test - Main Load Testing Scenario
 *
 * Tests normal expected load patterns including:
 * - User authentication
 * - Agent interactions (BLAZE, SAGE, STELLA)
 * - Voice synthesis
 * - Chat conversations
 * - Feature flag requests
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';
import { vu, scenario } from 'k6/execution';

import { getEnvironment, testScenarios, generateTrainingQuery, generateNutritionQuery } from '../config/environments.js';
import { AuthManager } from '../utils/auth.js';
import { recordAIMetrics, recordVoiceMetrics, recordUserJourneyMetrics, createThresholds } from '../utils/metrics.js';

// Get environment configuration
const env = getEnvironment(__ENV.ENVIRONMENT || 'local');

// Load test data
const testUsers = new SharedArray('users', function () {
  return [
    { email: 'loadtest1@genesis.com', password: 'LoadTest123!' },
    { email: 'loadtest2@genesis.com', password: 'LoadTest123!' },
    { email: 'loadtest3@genesis.com', password: 'LoadTest123!' },
    { email: 'loadtest4@genesis.com', password: 'LoadTest123!' },
    { email: 'loadtest5@genesis.com', password: 'LoadTest123!' },
  ];
});

// Test configuration
export const options = {
  scenarios: {
    load_test: testScenarios.load,
  },
  thresholds: createThresholds({
    httpDuration: ['p(95)<3000'],
    httpFailed: ['rate<0.05'],
    aiResponseTime: ['p(95)<25000'],
    aiQuality: ['rate>0.85'],
  }),
};

// Per-VU authentication manager
let authManager;

export function setup() {
  console.log('🚀 Starting GENESIS Load Test Setup...');

  // Verify API health before starting
  const healthCheck = http.get(`${env.baseUrl}/health`);
  const isHealthy = check(healthCheck, {
    'API is healthy': (r) => r.status === 200,
  });

  if (!isHealthy) {
    throw new Error('API health check failed - aborting test');
  }

  console.log('✅ API health check passed');
  console.log(`📊 Load test configuration: ${options.scenarios.load_test.vus} VUs for ${options.scenarios.load_test.duration}`);

  return { apiHealthy: true };
}

export default function loadTest(data) {
  // Initialize auth manager for this VU if not already done
  if (!authManager) {
    const userIndex = vu.idInTest % testUsers.length;
    const user = testUsers[userIndex];
    authManager = new AuthManager(env.baseUrl, user);

    if (!authManager.init()) {
      console.error(`Failed to authenticate user ${user.email}`);
      return;
    }
  }

  const journeyStartTime = Date.now();
  let journeySuccess = false;

  try {
    // 1. Test agent list endpoint (20% of requests)
    if (Math.random() < 0.2) {
      testAgentsList();
    }

    // 2. Test agent interactions (60% of requests)
    if (Math.random() < 0.6) {
      const agentType = Math.random() < 0.5 ? 'training' : 'nutrition';
      testAgentInteraction(agentType);
    }

    // 3. Test voice synthesis (10% of requests)
    if (Math.random() < 0.1) {
      testVoiceSynthesis();
    }

    // 4. Test feature flags (10% of requests)
    if (Math.random() < 0.1) {
      testFeatureFlags();
    }

    journeySuccess = true;

  } catch (error) {
    console.error(`Load test error: ${error.message}`);
    journeySuccess = false;
  } finally {
    recordUserJourneyMetrics('load_test', journeyStartTime, journeySuccess);
  }

  // Random sleep between 1-3 seconds to simulate user behavior
  sleep(Math.random() * 2 + 1);
}

/**
 * Test agents list endpoint
 */
function testAgentsList() {
  const response = http.get(`${env.baseUrl}/agents`, {
    headers: authManager.getHeaders(),
    tags: { name: 'get_agents_list' },
  });

  check(response, {
    'agents list status is 200': (r) => r.status === 200,
    'agents list response time < 2s': (r) => r.timings.duration < 2000,
    'agents list has content': (r) => {
      try {
        const agents = JSON.parse(r.body);
        return Array.isArray(agents) && agents.length > 0;
      } catch (e) {
        return false;
      }
    },
  });
}

/**
 * Test agent interactions
 * @param {string} agentType - Type of agent ('training' or 'nutrition')
 */
function testAgentInteraction(agentType) {
  const startTime = Date.now();
  let agentId, query, agentName;

  if (agentType === 'training') {
    agentId = 'elite-training-strategist';
    agentName = 'BLAZE';
    query = generateTrainingQuery();
  } else {
    agentId = 'precision-nutrition-architect';
    agentName = 'SAGE';
    query = generateNutritionQuery();
  }

  const payload = JSON.stringify({
    message: query,
    conversation_id: `load-test-${vu.idInTest}-${Date.now()}`,
    user_context: {
      fitness_level: 'intermediate',
      goals: agentType === 'training' ? ['muscle_gain'] : ['weight_loss'],
      equipment: ['dumbbells', 'resistance_bands']
    }
  });

  const response = http.post(
    `${env.baseUrl}/agents/${agentId}/chat`,
    payload,
    {
      headers: authManager.getHeaders(),
      tags: { name: `chat_${agentType}`, agent: agentName },
      timeout: '35s', // Allow time for AI processing
    }
  );

  const agentSuccess = check(response, {
    [`${agentName} chat status is 200`]: (r) => r.status === 200,
    [`${agentName} response has content`]: (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.response && body.response.length > 50;
      } catch (e) {
        return false;
      }
    },
    [`${agentName} response time reasonable`]: (r) => r.timings.duration < 30000,
  });

  // Record AI metrics
  recordAIMetrics(response, agentName, startTime);

  if (!agentSuccess) {
    console.warn(`${agentName} agent interaction failed: ${response.status}`);
  }
}

/**
 * Test voice synthesis
 */
function testVoiceSynthesis() {
  const startTime = Date.now();
  const testTexts = [
    "Great job on completing your workout!",
    "Here's your personalized nutrition plan.",
    "Your fitness progress is looking fantastic!",
    "Remember to stay hydrated throughout the day.",
  ];

  const text = testTexts[Math.floor(Math.random() * testTexts.length)];

  const payload = JSON.stringify({
    text: text,
    voice_id: "21m00Tcm4TlvDq8ikWAM",
    voice_settings: {
      stability: 0.75,
      similarity_boost: 0.75
    }
  });

  const response = http.post(
    `${env.baseUrl}/voice/synthesize`,
    payload,
    {
      headers: authManager.getHeaders(),
      tags: { name: 'voice_synthesis' },
      timeout: '20s',
    }
  );

  const voiceSuccess = check(response, {
    'voice synthesis status is 200': (r) => r.status === 200,
    'voice synthesis has audio data': (r) => r.body && r.body.length > 1000,
    'voice synthesis time < 15s': (r) => r.timings.duration < 15000,
  });

  recordVoiceMetrics(response, text, startTime);

  if (!voiceSuccess) {
    console.warn(`Voice synthesis failed: ${response.status}`);
  }
}

/**
 * Test feature flags endpoint
 */
function testFeatureFlags() {
  const response = http.get(`${env.baseUrl}/feature-flags`, {
    headers: authManager.getHeaders(),
    tags: { name: 'get_feature_flags' },
  });

  check(response, {
    'feature flags status is 200': (r) => r.status === 200,
    'feature flags response time < 1s': (r) => r.timings.duration < 1000,
    'feature flags has content': (r) => {
      try {
        const flags = JSON.parse(r.body);
        return typeof flags === 'object' && Object.keys(flags).length > 0;
      } catch (e) {
        return false;
      }
    },
  });
}

export function teardown(data) {
  console.log('🧹 Load Test Teardown Complete');
  console.log('📊 Check the results for performance metrics and threshold violations');
}
