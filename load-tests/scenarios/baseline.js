/**
 * GENESIS Baseline Load Test
 *
 * Tests normal expected load patterns to establish performance baselines
 * Target: 100 RPS sustained for 5 minutes
 *
 * Performance Targets:
 * - P50 latency: <100ms
 * - P95 latency: <500ms
 * - P99 latency: <1000ms
 * - Error rate: <1%
 * - Throughput: >100 RPS
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';
import { vu, scenario } from 'k6/execution';

import { getEnvironment, generateTrainingQuery, generateNutritionQuery } from '../config/environments.js';
import { AuthManager } from '../utils/auth.js';
import { recordAIMetrics, recordVoiceMetrics, recordUserJourneyMetrics, createThresholds } from '../utils/metrics.js';

// Environment configuration
const env = getEnvironment(__ENV.ENVIRONMENT || 'local');

// Test user pool
const testUsers = new SharedArray('users', function () {
  return [
    { email: 'baseline1@genesis.com', password: 'LoadTest123!' },
    { email: 'baseline2@genesis.com', password: 'LoadTest123!' },
    { email: 'baseline3@genesis.com', password: 'LoadTest123!' },
    { email: 'baseline4@genesis.com', password: 'LoadTest123!' },
    { email: 'baseline5@genesis.com', password: 'LoadTest123!' },
  ];
});

// Test configuration
export const options = {
  scenarios: {
    baseline_load: {
      executor: 'constant-arrival-rate',
      rate: 100, // 100 RPS
      timeUnit: '1s',
      duration: '5m',
      preAllocatedVUs: 20,
      maxVUs: 50,
    },
  },
  thresholds: createThresholds({
    httpDuration: ['p(50)<100', 'p(95)<500', 'p(99)<1000'],
    httpFailed: ['rate<0.01'],
    aiResponseTime: ['p(95)<20000'],
    aiQuality: ['rate>0.90'],
  }),
};

// Per-VU authentication manager
let authManager;

export function setup() {
  console.log('🎯 Starting GENESIS Baseline Load Test...');

  // Health check
  const healthCheck = http.get(`${env.baseUrl}/health`);
  const isHealthy = check(healthCheck, {
    'API is healthy': (r) => r.status === 200,
  });

  if (!isHealthy) {
    throw new Error('API health check failed - baseline test aborted');
  }

  console.log('✅ Baseline test ready - targeting 100 RPS for 5 minutes');
  return { timestamp: new Date().toISOString() };
}

export default function baselineTest(data) {
  // Initialize authentication
  if (!authManager) {
    const userIndex = vu.idInTest % testUsers.length;
    const user = testUsers[userIndex];
    authManager = new AuthManager(env.baseUrl, user);

    if (!authManager.init()) {
      console.error(`Failed to authenticate user ${user.email}`);
      return;
    }
  }

  const testStart = Date.now();
  let testSuccess = true;

  try {
    // Weighted request distribution (baseline traffic pattern)
    const rand = Math.random();

    if (rand < 0.4) {
      // 40% - Health checks and feature flags (fast endpoints)
      testHealthAndFlags();
    } else if (rand < 0.7) {
      // 30% - Agent interactions (AI workload)
      testAgentInteraction();
    } else if (rand < 0.9) {
      // 20% - Agent listing and metadata
      testAgentMetadata();
    } else {
      // 10% - Voice synthesis
      testVoiceSynthesis();
    }

  } catch (error) {
    console.error(`Baseline test error: ${error.message}`);
    testSuccess = false;
  } finally {
    recordUserJourneyMetrics('baseline', testStart, testSuccess);
  }

  // Realistic user think time
  sleep(Math.random() * 2 + 0.5); // 0.5-2.5 seconds
}

/**
 * Test fast endpoints (health checks, feature flags)
 */
function testHealthAndFlags() {
  // Health check
  const healthResponse = http.get(`${env.baseUrl}/health`, {
    tags: { name: 'health_check' },
  });

  check(healthResponse, {
    'health check successful': (r) => r.status === 200,
    'health check fast': (r) => r.timings.duration < 100,
  });

  // Feature flags
  const flagsResponse = http.get(`${env.baseUrl}/feature-flags`, {
    headers: authManager.getHeaders(),
    tags: { name: 'feature_flags' },
  });

  check(flagsResponse, {
    'feature flags successful': (r) => r.status === 200,
    'feature flags fast': (r) => r.timings.duration < 200,
  });
}

/**
 * Test agent interactions
 */
function testAgentInteraction() {
  const startTime = Date.now();
  const agentType = Math.random() < 0.6 ? 'training' : 'nutrition';

  let agentId, query;
  if (agentType === 'training') {
    agentId = 'elite-training-strategist';
    query = generateTrainingQuery();
  } else {
    agentId = 'precision-nutrition-architect';
    query = generateNutritionQuery();
  }

  const payload = JSON.stringify({
    message: query,
    conversation_id: `baseline-${vu.idInTest}-${Date.now()}`,
    user_context: {
      fitness_level: 'intermediate',
      goals: agentType === 'training' ? ['muscle_gain'] : ['weight_loss'],
    }
  });

  const response = http.post(
    `${env.baseUrl}/agents/${agentId}/chat`,
    payload,
    {
      headers: authManager.getHeaders(),
      tags: { name: `agent_${agentType}` },
      timeout: '25s',
    }
  );

  const success = check(response, {
    [`${agentType} agent responds`]: (r) => r.status === 200,
    [`${agentType} agent has content`]: (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.response && body.response.length > 30;
      } catch (e) {
        return false;
      }
    },
  });

  recordAIMetrics(response, agentId, startTime);
}

/**
 * Test agent metadata endpoints
 */
function testAgentMetadata() {
  // List agents
  const agentsResponse = http.get(`${env.baseUrl}/agents`, {
    headers: authManager.getHeaders(),
    tags: { name: 'list_agents' },
  });

  check(agentsResponse, {
    'agents list successful': (r) => r.status === 200,
    'agents list has data': (r) => {
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
 * Test voice synthesis
 */
function testVoiceSynthesis() {
  const startTime = Date.now();
  const voiceTexts = [
    "Welcome to your baseline performance test",
    "System is operating at normal capacity",
    "Baseline metrics are being collected"
  ];

  const text = voiceTexts[Math.floor(Math.random() * voiceTexts.length)];

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
      timeout: '15s',
    }
  );

  check(response, {
    'voice synthesis successful': (r) => r.status === 200,
    'voice synthesis has audio': (r) => r.body && r.body.length > 500,
  });

  recordVoiceMetrics(response, text, startTime);
}

export function teardown(data) {
  console.log('📊 Baseline Load Test Complete');
  console.log('Results will help establish performance baselines for GENESIS');
  console.log(`Test started at: ${data.timestamp}`);
  console.log(`Test completed at: ${new Date().toISOString()}`);
}
