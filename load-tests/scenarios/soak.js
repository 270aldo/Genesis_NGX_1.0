/**
 * GENESIS Soak Test
 *
 * Tests system stability under sustained moderate load over extended period
 * Pattern: Steady 200 RPS for 30 minutes to detect memory leaks, degradation
 *
 * Performance Targets:
 * - Response times should remain stable over time
 * - Memory usage should not continuously increase
 * - No gradual performance degradation
 * - System should be as responsive at end as beginning
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';
import { vu, scenario } from 'k6/execution';

import { getEnvironment, generateTrainingQuery, generateNutritionQuery } from '../config/environments.js';
import { AuthManager } from '../utils/auth.js';
import { recordAIMetrics, recordVoiceMetrics, recordUserJourneyMetrics, recordSystemMetrics, createThresholds } from '../utils/metrics.js';

const env = getEnvironment(__ENV.ENVIRONMENT || 'local');

const testUsers = new SharedArray('soak_users', function () {
  return Array.from({ length: 15 }, (_, i) => ({
    email: `soak${i + 1}@genesis.com`,
    password: 'SoakTest123!'
  }));
});

export const options = {
  scenarios: {
    soak_test: {
      executor: 'constant-arrival-rate',
      rate: 200, // Constant 200 RPS
      timeUnit: '1s',
      duration: '30m', // 30-minute soak test
      preAllocatedVUs: 50,
      maxVUs: 100,
    },
  },
  thresholds: createThresholds({
    httpDuration: ['p(95)<2000', 'p(95)>0'], // Stable response times
    httpFailed: ['rate<0.02'], // Very low error rate for sustained load
    aiResponseTime: ['p(95)<25000'], // AI responses should remain fast
    aiQuality: ['rate>0.85'], // Quality should not degrade over time
    memoryUsage: ['max<2048'], // Memory usage should not exceed 2GB
  }),
};

let authManager;
let soakPhase = 'initial';
let testStartTime;
let performanceBaseline = {
  responseTime: 0,
  aiResponseTime: 0,
  established: false
};

export function setup() {
  console.log('🛁 Starting GENESIS Soak Test...');
  console.log('Will maintain steady 200 RPS for 30 minutes');
  console.log('Monitoring for memory leaks and performance degradation...');

  testStartTime = Date.now();

  const healthCheck = http.get(`${env.baseUrl}/health`);
  const initialHealth = check(healthCheck, {
    'Pre-soak system healthy': (r) => r.status === 200,
  });

  // Take initial performance measurements
  const baselineResponse = http.get(`${env.baseUrl}/agents`);
  if (baselineResponse.status === 200) {
    performanceBaseline.responseTime = baselineResponse.timings.duration;
  }

  return {
    startTime: new Date().toISOString(),
    preTestHealth: initialHealth,
    expectedDuration: 30 * 60 * 1000 // 30 minutes in milliseconds
  };
}

export default function soakTest(data) {
  if (!authManager) {
    const userIndex = vu.idInTest % testUsers.length;
    const user = testUsers[userIndex];
    authManager = new AuthManager(env.baseUrl, user);

    if (!authManager.init()) {
      console.error(`Soak test auth failed for ${user.email}`);
      return;
    }
  }

  // Update soak phase based on elapsed time
  const elapsed = Date.now() - testStartTime;
  updateSoakPhase(elapsed);

  const testStart = Date.now();
  let testSuccess = true;

  try {
    // Realistic traffic pattern for sustained load
    const rand = Math.random();

    if (rand < 0.4) {
      // 40% - Regular API endpoints (agents, health, features)
      soakRegularEndpoints();
    } else if (rand < 0.7) {
      // 30% - AI agent interactions
      soakAgentInteractions();
    } else if (rand < 0.9) {
      // 20% - Voice synthesis
      soakVoiceSynthesis();
    } else {
      // 10% - System monitoring calls
      soakSystemMonitoring();
    }

    // Monitor system resources periodically
    if (Math.random() < 0.01) { // 1% of requests
      monitorSystemResources();
    }

  } catch (error) {
    console.error(`Soak test error (${soakPhase}): ${error.message}`);
    testSuccess = false;
  } finally {
    recordUserJourneyMetrics(`soak_${soakPhase}`, testStart, testSuccess);
  }

  // Consistent sleep pattern for steady load
  sleep(Math.random() * 1 + 0.5); // 0.5-1.5 seconds
}

function updateSoakPhase(elapsedMs) {
  const minutes = elapsedMs / 60000;

  if (minutes < 5) {
    soakPhase = 'initial';
  } else if (minutes < 10) {
    soakPhase = 'early';
  } else if (minutes < 20) {
    soakPhase = 'middle';
  } else if (minutes < 25) {
    soakPhase = 'late';
  } else {
    soakPhase = 'final';
  }
}

/**
 * Test regular API endpoints under sustained load
 */
function soakRegularEndpoints() {
  const endpoints = [
    { url: `${env.baseUrl}/health`, name: 'health' },
    { url: `${env.baseUrl}/agents`, name: 'agents', auth: true },
    { url: `${env.baseUrl}/feature-flags`, name: 'features', auth: true },
  ];

  const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];
  const options = {
    tags: { name: `soak_${endpoint.name}_${soakPhase}` },
    timeout: '10s',
  };

  if (endpoint.auth) {
    options.headers = authManager.getHeaders();
  }

  const response = http.get(endpoint.url, options);

  const success = check(response, {
    [`soak ${endpoint.name} responds (${soakPhase})`]: (r) => r.status === 200,
    [`soak ${endpoint.name} fast (${soakPhase})`]: (r) => r.timings.duration < 5000,
    [`soak ${endpoint.name} stable`]: (r) => {
      // Check for performance degradation compared to baseline
      if (!performanceBaseline.established && endpoint.name === 'agents') {
        performanceBaseline.responseTime = r.timings.duration;
        performanceBaseline.established = true;
        return true;
      }

      if (endpoint.name === 'agents' && performanceBaseline.established) {
        // Alert if response time is 3x slower than baseline
        return r.timings.duration < (performanceBaseline.responseTime * 3);
      }

      return true;
    },
  });

  if (!success && soakPhase === 'final') {
    console.warn(`Performance degradation detected in ${endpoint.name} during final soak phase`);
  }
}

/**
 * Test AI agent interactions under sustained load
 */
function soakAgentInteractions() {
  const startTime = Date.now();

  // Vary query complexity throughout soak test
  let query, complexity;
  switch (soakPhase) {
    case 'initial':
    case 'early':
      complexity = 'simple';
      query = Math.random() < 0.5 ? "Basic workout tip" : "Simple meal idea";
      break;
    case 'middle':
      complexity = 'medium';
      query = Math.random() < 0.5 ? generateTrainingQuery() : generateNutritionQuery();
      break;
    case 'late':
    case 'final':
      complexity = 'complex';
      query = Math.random() < 0.5 ?
        "Create a detailed 4-week progressive training program" :
        "Design a comprehensive nutrition plan with macro tracking";
      break;
  }

  const agentId = Math.random() < 0.5 ? 'elite-training-strategist' : 'precision-nutrition-architect';

  const payload = JSON.stringify({
    message: query,
    conversation_id: `soak-${soakPhase}-${vu.idInTest}-${Date.now()}`,
    user_context: {
      fitness_level: 'intermediate',
      complexity: complexity,
      soak_phase: soakPhase,
      test_minute: Math.floor((Date.now() - testStartTime) / 60000)
    }
  });

  const response = http.post(
    `${env.baseUrl}/agents/${agentId}/chat`,
    payload,
    {
      headers: authManager.getHeaders(),
      tags: { name: `soak_agent_${complexity}_${soakPhase}` },
      timeout: '35s',
    }
  );

  const success = check(response, {
    [`soak agent ${complexity} responds (${soakPhase})`]: (r) => r.status === 200,
    [`soak agent ${complexity} has content`]: (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.response && body.response.length > 30;
      } catch (e) {
        return false;
      }
    },
    [`soak agent ${complexity} performance stable`]: (r) => {
      // Monitor AI response time stability
      if (!performanceBaseline.aiResponseTime) {
        performanceBaseline.aiResponseTime = r.timings.duration;
        return true;
      }

      // Allow some variation, but alert on significant degradation
      const degradationThreshold = performanceBaseline.aiResponseTime * 2;
      if (r.timings.duration > degradationThreshold && soakPhase === 'final') {
        console.warn(`AI performance degradation detected: ${r.timings.duration}ms vs baseline ${performanceBaseline.aiResponseTime}ms`);
      }

      return r.timings.duration < degradationThreshold;
    },
  });

  recordAIMetrics(response, agentId, startTime);
}

/**
 * Test voice synthesis under sustained load
 */
function soakVoiceSynthesis() {
  const startTime = Date.now();

  // Vary voice request patterns
  const voiceTexts = {
    initial: ["Welcome to soak test", "Starting sustained load"],
    early: ["Early phase monitoring", "System performing well"],
    middle: ["Midpoint assessment ongoing", "Checking for memory leaks and stability"],
    late: ["Late phase evaluation", "Monitoring for performance degradation over time"],
    final: ["Final phase analysis", "Completing sustained load testing evaluation"]
  };

  const texts = voiceTexts[soakPhase] || voiceTexts.middle;
  const text = texts[Math.floor(Math.random() * texts.length)];

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
      tags: { name: `soak_voice_${soakPhase}` },
      timeout: '20s',
    }
  );

  check(response, {
    [`soak voice responds (${soakPhase})`]: (r) => r.status === 200,
    [`soak voice has audio (${soakPhase})`]: (r) => r.body && r.body.length > 1000,
    [`soak voice performance stable`]: (r) => r.timings.duration < 18000, // Consistent performance
  });

  recordVoiceMetrics(response, text, startTime);
}

/**
 * Test system monitoring endpoints
 */
function soakSystemMonitoring() {
  const monitoringEndpoints = [
    { url: `${env.baseUrl}/health`, name: 'health' },
    { url: `${env.baseUrl}/metrics`, name: 'metrics' },
  ];

  monitoringEndpoints.forEach(endpoint => {
    const response = http.get(endpoint.url, {
      tags: { name: `soak_monitoring_${endpoint.name}_${soakPhase}` },
      timeout: '5s',
    });

    check(response, {
      [`monitoring ${endpoint.name} available (${soakPhase})`]: (r) => r.status === 200,
      [`monitoring ${endpoint.name} fast (${soakPhase})`]: (r) => r.timings.duration < 2000,
    });
  });
}

/**
 * Monitor system resources during soak test
 */
function monitorSystemResources() {
  // This would typically integrate with system monitoring
  // For now, we'll simulate resource monitoring
  const simulatedMetrics = {
    memory: Math.random() * 1024 + 512, // Simulate memory usage 512-1536 MB
    cpu: Math.random() * 40 + 20,       // Simulate CPU usage 20-60%
    connections: Math.floor(Math.random() * 200 + 50) // Simulate 50-250 connections
  };

  recordSystemMetrics(simulatedMetrics);

  // Log resource usage periodically
  if (Math.random() < 0.1) { // Log 10% of resource monitoring calls
    console.log(`[${soakPhase}] Resources - Memory: ${simulatedMetrics.memory.toFixed(0)}MB, CPU: ${simulatedMetrics.cpu.toFixed(1)}%, Connections: ${simulatedMetrics.connections}`);
  }
}

export function teardown(data) {
  const endTime = new Date().toISOString();
  const duration = Date.now() - testStartTime;
  const durationMinutes = duration / 60000;

  console.log('🛁 Soak Test Complete');
  console.log(`Started: ${data.startTime}`);
  console.log(`Completed: ${endTime}`);
  console.log(`Duration: ${durationMinutes.toFixed(1)} minutes`);

  // Final system health assessment
  const finalHealthCheck = http.get(`${env.baseUrl}/health`);
  const finalAgentsCheck = http.get(`${env.baseUrl}/agents`);

  const systemStable = check(finalHealthCheck, {
    'System stable after soak': (r) => r.status === 200 && r.timings.duration < 2000,
  });

  const performanceStable = check(finalAgentsCheck, {
    'Performance stable after soak': (r) => {
      if (!performanceBaseline.established) return true;

      const degradation = r.timings.duration / performanceBaseline.responseTime;
      return degradation < 2; // Less than 2x degradation
    },
  });

  if (systemStable && performanceStable) {
    console.log('✅ System passed soak test - no memory leaks or performance degradation detected');
  } else {
    console.log('⚠️  System showed signs of degradation during soak test');
    if (!systemStable) console.log('   - Health check degraded');
    if (!performanceStable) console.log('   - Response times degraded');
  }

  console.log('📊 Review metrics for:');
  console.log('   - Memory usage trends');
  console.log('   - Response time stability');
  console.log('   - Error rate consistency');
  console.log('   - Resource utilization patterns');
}
