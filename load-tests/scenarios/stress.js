/**
 * GENESIS Stress Test
 *
 * Gradually increases load to find breaking point and performance degradation
 * Pattern: Ramp from 50 to 1000 RPS over 15 minutes
 *
 * Performance Targets:
 * - System should gracefully handle load increases
 * - Error rate should remain <5% up to 500 RPS
 * - Response times may degrade but should not timeout
 * - System should recover after load reduction
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';
import { vu, scenario } from 'k6/execution';

import { getEnvironment, generateTrainingQuery, generateNutritionQuery } from '../config/environments.js';
import { AuthManager } from '../utils/auth.js';
import { recordAIMetrics, recordVoiceMetrics, recordUserJourneyMetrics, createThresholds } from '../utils/metrics.js';

const env = getEnvironment(__ENV.ENVIRONMENT || 'local');

const testUsers = new SharedArray('stress_users', function () {
  return Array.from({ length: 20 }, (_, i) => ({
    email: `stress${i + 1}@genesis.com`,
    password: 'StressTest123!'
  }));
});

export const options = {
  scenarios: {
    stress_ramp: {
      executor: 'ramping-arrival-rate',
      startRate: 50,
      timeUnit: '1s',
      preAllocatedVUs: 50,
      maxVUs: 200,
      stages: [
        { duration: '2m', target: 100 },   // Ramp to 100 RPS
        { duration: '3m', target: 100 },   // Sustain 100 RPS
        { duration: '2m', target: 300 },   // Ramp to 300 RPS
        { duration: '3m', target: 300 },   // Sustain 300 RPS
        { duration: '2m', target: 600 },   // Ramp to 600 RPS
        { duration: '2m', target: 600 },   // Sustain 600 RPS
        { duration: '1m', target: 1000 },  // Spike to 1000 RPS
        { duration: '2m', target: 1000 },  // Sustain spike
        { duration: '2m', target: 100 },   // Recovery ramp down
        { duration: '1m', target: 0 },     // Complete ramp down
      ],
    },
  },
  thresholds: createThresholds({
    httpDuration: ['p(95)<5000'],  // Allow higher latency under stress
    httpFailed: ['rate<0.1'],      // 10% error rate acceptable under extreme load
    aiResponseTime: ['p(95)<45000'], // AI responses can take longer under stress
    aiQuality: ['rate>0.7'],       // Quality may degrade under load
  }),
};

let authManager;
let stressPhase = 'warmup';

export function setup() {
  console.log('🔥 Starting GENESIS Stress Test...');
  console.log('Will gradually increase load from 50 to 1000 RPS');

  const healthCheck = http.get(`${env.baseUrl}/health`);
  check(healthCheck, {
    'Pre-stress health check': (r) => r.status === 200,
  });

  return {
    startTime: new Date().toISOString(),
    phases: ['warmup', 'ramp1', 'sustain1', 'ramp2', 'sustain2', 'ramp3', 'sustain3', 'spike', 'peak', 'recovery', 'cooldown']
  };
}

export default function stressTest(data) {
  if (!authManager) {
    const userIndex = vu.idInTest % testUsers.length;
    const user = testUsers[userIndex];
    authManager = new AuthManager(env.baseUrl, user);

    if (!authManager.init()) {
      console.error(`Stress test auth failed for ${user.email}`);
      return;
    }
  }

  // Determine current test phase based on scenario iteration
  const currentIteration = scenario.iterationInTest;
  updateStressPhase(currentIteration);

  const testStart = Date.now();
  let testSuccess = true;

  try {
    // Adjust request patterns based on stress level
    const rand = Math.random();

    if (stressPhase === 'spike' || stressPhase === 'peak') {
      // During spike, focus on core endpoints
      if (rand < 0.6) {
        stressCoreEndpoints();
      } else if (rand < 0.9) {
        stressAgentInteractions();
      } else {
        stressHealthChecks();
      }
    } else {
      // Normal distribution during ramp
      if (rand < 0.3) {
        stressHealthChecks();
      } else if (rand < 0.7) {
        stressAgentInteractions();
      } else {
        stressVoiceAndStreaming();
      }
    }

  } catch (error) {
    console.error(`Stress test error (${stressPhase}): ${error.message}`);
    testSuccess = false;
  } finally {
    recordUserJourneyMetrics(`stress_${stressPhase}`, testStart, testSuccess);
  }

  // Minimal sleep during stress test
  sleep(Math.random() * 0.5 + 0.1); // 0.1-0.6 seconds
}

function updateStressPhase(iteration) {
  // Rough phase detection based on iteration count
  if (iteration < 6000) stressPhase = 'warmup';
  else if (iteration < 18000) stressPhase = 'ramp1';
  else if (iteration < 36000) stressPhase = 'sustain1';
  else if (iteration < 48000) stressPhase = 'ramp2';
  else if (iteration < 66000) stressPhase = 'sustain2';
  else if (iteration < 78000) stressPhase = 'ramp3';
  else if (iteration < 90000) stressPhase = 'sustain3';
  else if (iteration < 96000) stressPhase = 'spike';
  else if (iteration < 108000) stressPhase = 'peak';
  else if (iteration < 120000) stressPhase = 'recovery';
  else stressPhase = 'cooldown';
}

/**
 * Test core health endpoints under stress
 */
function stressHealthChecks() {
  const responses = http.batch([
    ['GET', `${env.baseUrl}/health`, null, { tags: { name: 'stress_health' } }],
    ['GET', `${env.baseUrl}/metrics`, null, { tags: { name: 'stress_metrics' } }],
    ['GET', `${env.baseUrl}/feature-flags`, null, {
      headers: authManager.getHeaders(),
      tags: { name: 'stress_flags' }
    }],
  ]);

  responses.forEach((response, index) => {
    const endpointNames = ['health', 'metrics', 'feature_flags'];
    check(response, {
      [`stress ${endpointNames[index]} responds`]: (r) => r.status < 500,
      [`stress ${endpointNames[index]} reasonably fast`]: (r) => r.timings.duration < 10000,
    });
  });
}

/**
 * Test core API endpoints under stress
 */
function stressCoreEndpoints() {
  const agentsResponse = http.get(`${env.baseUrl}/agents`, {
    headers: authManager.getHeaders(),
    tags: { name: 'stress_agents_list' },
    timeout: '10s',
  });

  check(agentsResponse, {
    'stress agents list responds': (r) => r.status < 500,
    'stress agents list has data': (r) => r.status === 200 && r.body.length > 10,
  });
}

/**
 * Test AI agent interactions under stress
 */
function stressAgentInteractions() {
  const startTime = Date.now();

  // Use shorter queries during stress to reduce processing time
  const stressQueries = [
    "Quick workout tip",
    "Simple meal idea",
    "Basic exercise form",
    "Nutrition fact",
    "Fitness advice"
  ];

  const query = stressQueries[Math.floor(Math.random() * stressQueries.length)];
  const agentId = Math.random() < 0.5 ? 'elite-training-strategist' : 'precision-nutrition-architect';

  const payload = JSON.stringify({
    message: query,
    conversation_id: `stress-${stressPhase}-${vu.idInTest}-${Date.now()}`,
    user_context: {
      fitness_level: 'beginner', // Simpler context for faster processing
      stress_test: true
    }
  });

  const response = http.post(
    `${env.baseUrl}/agents/${agentId}/chat`,
    payload,
    {
      headers: authManager.getHeaders(),
      tags: { name: `stress_agent_${stressPhase}` },
      timeout: '30s',
    }
  );

  const success = check(response, {
    'stress agent responds': (r) => r.status < 500,
    'stress agent completes': (r) => r.status === 200 || r.status === 503, // 503 is acceptable under extreme load
  });

  recordAIMetrics(response, agentId, startTime);
}

/**
 * Test voice and streaming under stress
 */
function stressVoiceAndStreaming() {
  const startTime = Date.now();

  const shortTexts = [
    "Stress test active",
    "System under load",
    "Performance monitoring"
  ];

  const text = shortTexts[Math.floor(Math.random() * shortTexts.length)];

  const payload = JSON.stringify({
    text: text,
    voice_id: "21m00Tcm4TlvDq8ikWAM",
    voice_settings: {
      stability: 0.5, // Lower quality for faster processing
      similarity_boost: 0.5
    }
  });

  const response = http.post(
    `${env.baseUrl}/voice/synthesize`,
    payload,
    {
      headers: authManager.getHeaders(),
      tags: { name: `stress_voice_${stressPhase}` },
      timeout: '20s',
    }
  );

  check(response, {
    'stress voice responds': (r) => r.status < 500,
    'stress voice completes': (r) => r.status === 200 || r.status === 503,
  });

  recordVoiceMetrics(response, text, startTime);
}

export function teardown(data) {
  console.log('🔥 Stress Test Complete');
  console.log(`Started: ${data.startTime}`);
  console.log(`Completed: ${new Date().toISOString()}`);
  console.log('📊 Analyzing system behavior under increasing load...');

  // Final health check
  const finalHealthCheck = http.get(`${env.baseUrl}/health`);
  const systemRecovered = check(finalHealthCheck, {
    'System recovered after stress': (r) => r.status === 200,
  });

  if (systemRecovered) {
    console.log('✅ System successfully recovered from stress test');
  } else {
    console.log('⚠️  System may need time to fully recover from stress test');
  }
}
