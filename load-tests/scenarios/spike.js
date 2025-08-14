/**
 * GENESIS Spike Test
 *
 * Tests system behavior during sudden traffic surges (viral events, promotions)
 * Pattern: Normal load → Sudden 10x spike → Recovery monitoring
 *
 * Performance Targets:
 * - System should remain stable during normal load
 * - Circuit breakers should activate during spike
 * - System should gracefully degrade, not crash
 * - Recovery should be quick and complete
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';
import { vu, scenario } from 'k6/execution';

import { getEnvironment, generateTrainingQuery, generateNutritionQuery } from '../config/environments.js';
import { AuthManager } from '../utils/auth.js';
import { recordAIMetrics, recordVoiceMetrics, recordUserJourneyMetrics, createThresholds } from '../utils/metrics.js';

const env = getEnvironment(__ENV.ENVIRONMENT || 'local');

const testUsers = new SharedArray('spike_users', function () {
  return Array.from({ length: 30 }, (_, i) => ({
    email: `spike${i + 1}@genesis.com`,
    password: 'SpikeTest123!'
  }));
});

export const options = {
  scenarios: {
    spike_test: {
      executor: 'ramping-arrival-rate',
      startRate: 100,
      timeUnit: '1s',
      preAllocatedVUs: 100,
      maxVUs: 500,
      stages: [
        { duration: '2m', target: 100 },   // Normal baseline load
        { duration: '30s', target: 100 },  // Stable period
        { duration: '10s', target: 1500 }, // Sudden spike (15x increase)
        { duration: '1m', target: 1500 },  // Sustain spike
        { duration: '10s', target: 100 },  // Quick recovery
        { duration: '3m', target: 100 },   // Monitor recovery
        { duration: '30s', target: 0 },    // Ramp down
      ],
    },
  },
  thresholds: createThresholds({
    httpDuration: ['p(95)<10000'], // Allow higher latency during spike
    httpFailed: ['rate<0.2'],      // 20% failure acceptable during extreme spike
    aiResponseTime: ['p(95)<60000'], // AI responses may take much longer
    aiQuality: ['rate>0.5'],       // Quality may significantly degrade
  }),
};

let authManager;
let spikePhase = 'baseline';

export function setup() {
  console.log('⚡ Starting GENESIS Spike Test...');
  console.log('Will test sudden traffic surge from 100 to 1500 RPS');

  const healthCheck = http.get(`${env.baseUrl}/health`);
  const initialHealth = check(healthCheck, {
    'Pre-spike system healthy': (r) => r.status === 200,
  });

  if (!initialHealth) {
    console.warn('⚠️  System not fully healthy before spike test');
  }

  return {
    startTime: new Date().toISOString(),
    preTestHealth: initialHealth
  };
}

export default function spikeTest(data) {
  if (!authManager) {
    const userIndex = vu.idInTest % testUsers.length;
    const user = testUsers[userIndex];
    authManager = new AuthManager(env.baseUrl, user);

    if (!authManager.init()) {
      // During spike, auth failures are expected
      if (spikePhase !== 'spike' && spikePhase !== 'sustain_spike') {
        console.error(`Spike test auth failed for ${user.email}`);
      }
      return;
    }
  }

  // Determine current phase
  const elapsed = scenario.iterationInTest;
  updateSpikePhase(elapsed);

  const testStart = Date.now();
  let testSuccess = true;

  try {
    switch (spikePhase) {
      case 'baseline':
      case 'stable':
      case 'recovery':
        normalSpikeOperations();
        break;
      case 'spike':
      case 'sustain_spike':
        spikeOperations();
        break;
      case 'ramp_down':
        recoveryOperations();
        break;
    }

  } catch (error) {
    testSuccess = false;
    if (spikePhase === 'spike' || spikePhase === 'sustain_spike') {
      // Errors expected during spike
      console.log(`Expected error during ${spikePhase}: ${error.message}`);
    } else {
      console.error(`Unexpected error during ${spikePhase}: ${error.message}`);
    }
  } finally {
    recordUserJourneyMetrics(`spike_${spikePhase}`, testStart, testSuccess);
  }

  // Sleep patterns vary by phase
  if (spikePhase === 'spike' || spikePhase === 'sustain_spike') {
    sleep(Math.random() * 0.1); // Minimal sleep during spike
  } else {
    sleep(Math.random() * 1 + 0.5); // Normal sleep
  }
}

function updateSpikePhase(iteration) {
  if (iteration < 12000) spikePhase = 'baseline';
  else if (iteration < 15000) spikePhase = 'stable';
  else if (iteration < 16500) spikePhase = 'spike';
  else if (iteration < 25500) spikePhase = 'sustain_spike';
  else if (iteration < 26500) spikePhase = 'ramp_down';
  else if (iteration < 44500) spikePhase = 'recovery';
  else spikePhase = 'complete';
}

/**
 * Normal operations during baseline and recovery phases
 */
function normalSpikeOperations() {
  const rand = Math.random();

  if (rand < 0.3) {
    // Health monitoring
    testSystemHealth();
  } else if (rand < 0.7) {
    // Normal agent interactions
    testNormalAgentChat();
  } else {
    // Light voice synthesis
    testLightVoiceSynthesis();
  }
}

/**
 * Operations during traffic spike
 */
function spikeOperations() {
  const rand = Math.random();

  if (rand < 0.5) {
    // Most requests should be light operations during spike
    testSpikeSurvivalEndpoints();
  } else if (rand < 0.8) {
    // Some agent requests (expect many failures)
    testSpikeAgentRequests();
  } else {
    // Minimal voice requests
    testEmergencyVoice();
  }
}

/**
 * Recovery monitoring operations
 */
function recoveryOperations() {
  // Focus on system recovery validation
  const rand = Math.random();

  if (rand < 0.6) {
    testRecoveryHealth();
  } else {
    testRecoveryFunctionality();
  }
}

/**
 * Test system health during normal phases
 */
function testSystemHealth() {
  const healthResponse = http.get(`${env.baseUrl}/health`, {
    tags: { name: `spike_health_${spikePhase}` },
    timeout: '5s',
  });

  check(healthResponse, {
    [`health responds during ${spikePhase}`]: (r) => r.status === 200,
    [`health fast during ${spikePhase}`]: (r) => r.timings.duration < 2000,
  });

  // Also check metrics endpoint
  const metricsResponse = http.get(`${env.baseUrl}/metrics`, {
    tags: { name: `spike_metrics_${spikePhase}` },
    timeout: '5s',
  });

  check(metricsResponse, {
    [`metrics available during ${spikePhase}`]: (r) => r.status === 200,
  });
}

/**
 * Test lightweight endpoints that should survive the spike
 */
function testSpikeSurvivalEndpoints() {
  const responses = http.batch([
    ['GET', `${env.baseUrl}/health`, null, {
      tags: { name: 'spike_survival_health' },
      timeout: '3s'
    }],
    ['GET', `${env.baseUrl}/agents`, null, {
      headers: authManager ? authManager.getHeaders() : {},
      tags: { name: 'spike_survival_agents' },
      timeout: '5s'
    }],
  ]);

  responses.forEach((response, index) => {
    const endpoints = ['health', 'agents'];
    check(response, {
      [`spike survival ${endpoints[index]} responds`]: (r) => r.status < 500,
    });
  });
}

/**
 * Test normal agent interactions
 */
function testNormalAgentChat() {
  const startTime = Date.now();
  const query = Math.random() < 0.5 ? generateTrainingQuery() : generateNutritionQuery();
  const agentId = Math.random() < 0.5 ? 'elite-training-strategist' : 'precision-nutrition-architect';

  const payload = JSON.stringify({
    message: query,
    conversation_id: `spike-normal-${vu.idInTest}-${Date.now()}`,
    user_context: {
      fitness_level: 'intermediate',
      spike_phase: spikePhase
    }
  });

  const response = http.post(
    `${env.baseUrl}/agents/${agentId}/chat`,
    payload,
    {
      headers: authManager.getHeaders(),
      tags: { name: `spike_normal_chat` },
      timeout: '25s',
    }
  );

  check(response, {
    'normal chat during spike test': (r) => r.status === 200,
    'normal chat has content': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.response && body.response.length > 20;
      } catch (e) {
        return false;
      }
    },
  });

  recordAIMetrics(response, agentId, startTime);
}

/**
 * Test agent requests during spike (expect failures)
 */
function testSpikeAgentRequests() {
  const startTime = Date.now();

  // Use very short queries during spike
  const emergencyQueries = [
    "Help",
    "Quick tip",
    "Basic info",
    "Simple answer"
  ];

  const query = emergencyQueries[Math.floor(Math.random() * emergencyQueries.length)];
  const agentId = 'elite-training-strategist'; // Use one agent to focus load

  const payload = JSON.stringify({
    message: query,
    conversation_id: `spike-emergency-${vu.idInTest}`,
    user_context: {
      priority: 'emergency',
      spike_test: true
    }
  });

  const response = http.post(
    `${env.baseUrl}/agents/${agentId}/chat`,
    payload,
    {
      headers: authManager ? authManager.getHeaders() : {},
      tags: { name: 'spike_agent_emergency' },
      timeout: '15s',
    }
  );

  // More lenient checks during spike
  check(response, {
    'spike agent request handled': (r) => r.status < 500 || r.status === 503, // 503 Service Unavailable is acceptable
    'spike agent responds or degrades gracefully': (r) => r.status !== 0, // Not connection failure
  });

  recordAIMetrics(response, agentId, startTime);
}

/**
 * Test light voice synthesis
 */
function testLightVoiceSynthesis() {
  const startTime = Date.now();
  const text = "Test message";

  const payload = JSON.stringify({
    text: text,
    voice_id: "21m00Tcm4TlvDq8ikWAM",
    voice_settings: {
      stability: 0.5,
      similarity_boost: 0.5
    }
  });

  const response = http.post(
    `${env.baseUrl}/voice/synthesize`,
    payload,
    {
      headers: authManager.getHeaders(),
      tags: { name: 'spike_voice_light' },
      timeout: '10s',
    }
  );

  check(response, {
    'light voice synthesis works': (r) => r.status === 200,
  });

  recordVoiceMetrics(response, text, startTime);
}

/**
 * Test emergency voice during spike
 */
function testEmergencyVoice() {
  const startTime = Date.now();
  const text = "Alert"; // Minimal text

  const payload = JSON.stringify({
    text: text,
    voice_id: "21m00Tcm4TlvDq8ikWAM",
    voice_settings: {
      stability: 0.3, // Lower quality for speed
      similarity_boost: 0.3
    }
  });

  const response = http.post(
    `${env.baseUrl}/voice/synthesize`,
    payload,
    {
      headers: authManager ? authManager.getHeaders() : {},
      tags: { name: 'spike_voice_emergency' },
      timeout: '8s',
    }
  );

  check(response, {
    'emergency voice handled': (r) => r.status < 500,
  });

  recordVoiceMetrics(response, text, startTime);
}

/**
 * Test recovery health
 */
function testRecoveryHealth() {
  const healthResponse = http.get(`${env.baseUrl}/health`, {
    tags: { name: 'spike_recovery_health' },
    timeout: '5s',
  });

  check(healthResponse, {
    'system healthy during recovery': (r) => r.status === 200,
    'recovery health fast': (r) => r.timings.duration < 1000,
  });
}

/**
 * Test recovery functionality
 */
function testRecoveryFunctionality() {
  // Test that full functionality is restored
  const agentsResponse = http.get(`${env.baseUrl}/agents`, {
    headers: authManager.getHeaders(),
    tags: { name: 'spike_recovery_agents' },
  });

  check(agentsResponse, {
    'agents restored after spike': (r) => r.status === 200,
    'agents data complete after spike': (r) => {
      try {
        const agents = JSON.parse(r.body);
        return Array.isArray(agents) && agents.length > 0;
      } catch (e) {
        return false;
      }
    },
  });
}

export function teardown(data) {
  console.log('⚡ Spike Test Complete');
  console.log(`Started: ${data.startTime}`);
  console.log(`Completed: ${new Date().toISOString()}`);

  // Final system health assessment
  const finalHealthCheck = http.get(`${env.baseUrl}/health`);
  const systemRecovered = check(finalHealthCheck, {
    'System fully recovered from spike': (r) => r.status === 200 && r.timings.duration < 1000,
  });

  if (systemRecovered) {
    console.log('✅ System successfully handled traffic spike and recovered');
  } else {
    console.log('⚠️  System may need additional time to fully recover from spike');
  }

  console.log('📊 Review metrics for circuit breaker activation and degradation patterns');
}
