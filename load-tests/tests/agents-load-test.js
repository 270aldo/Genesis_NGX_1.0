/**
 * GENESIS AI Agents Load Test
 *
 * Focused load testing specifically for AI agent interactions:
 * - BLAZE (Elite Training Strategist)
 * - SAGE (Precision Nutrition Architect)
 * - STELLA (Progress Tracker)
 * - Multi-agent coordination scenarios
 * - A2A communication patterns
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';
import { vu } from 'k6/execution';

import { getEnvironment, testScenarios } from '../config/environments.js';
import { AuthManager } from '../utils/auth.js';
import { recordAIMetrics, recordA2AMetrics, createThresholds } from '../utils/metrics.js';

// Get environment configuration
const env = getEnvironment(__ENV.ENVIRONMENT || 'local');

// Agent-specific test scenarios
const agentScenarios = new SharedArray('agent_scenarios', function () {
  return [
    // BLAZE (Training) scenarios
    {
      agent: 'elite-training-strategist',
      agentName: 'BLAZE',
      queries: [
        {
          message: "I want to build muscle mass. I'm 25 years old, 70kg, and can work out 4 days a week.",
          context: {
            fitness_level: 'intermediate',
            goals: ['muscle_gain'],
            available_days: 4,
            equipment: ['dumbbells', 'barbell', 'bench']
          }
        },
        {
          message: "Create a home workout routine for strength training without any equipment.",
          context: {
            fitness_level: 'beginner',
            goals: ['strength'],
            available_days: 3,
            equipment: ['bodyweight']
          }
        },
        {
          message: "I have knee problems. What exercises should I avoid and what's safe for me?",
          context: {
            fitness_level: 'intermediate',
            goals: ['general_fitness'],
            limitations: ['knee_injury'],
            equipment: ['dumbbells']
          }
        }
      ]
    },

    // SAGE (Nutrition) scenarios
    {
      agent: 'precision-nutrition-architect',
      agentName: 'SAGE',
      queries: [
        {
          message: "I'm vegetarian and want to lose 5kg in 3 months. Help me create a meal plan.",
          context: {
            dietary_restrictions: ['vegetarian'],
            goals: ['weight_loss'],
            current_weight: 75,
            target_weight: 70,
            timeline: '3_months'
          }
        },
        {
          message: "What should I eat before and after my workout for muscle gain?",
          context: {
            goals: ['muscle_gain'],
            workout_timing: 'morning',
            dietary_restrictions: []
          }
        },
        {
          message: "I have diabetes. Can you help me plan my meals to manage blood sugar?",
          context: {
            medical_conditions: ['diabetes'],
            goals: ['health_management'],
            dietary_restrictions: ['low_sugar']
          }
        }
      ]
    },

    // STELLA (Progress Tracking) scenarios
    {
      agent: 'progress-tracker',
      agentName: 'STELLA',
      queries: [
        {
          message: "Track my workout progress and show me how I'm improving over time.",
          context: {
            tracking_type: 'workout_progress',
            time_period: '30_days'
          }
        },
        {
          message: "Generate a weekly progress report for my fitness goals.",
          context: {
            tracking_type: 'comprehensive',
            time_period: '7_days',
            goals: ['weight_loss', 'strength_gain']
          }
        }
      ]
    }
  ];
});

// Test users for authentication
const testUsers = new SharedArray('users', function () {
  return [
    { email: 'agent-test1@genesis.com', password: 'AgentTest123!' },
    { email: 'agent-test2@genesis.com', password: 'AgentTest123!' },
    { email: 'agent-test3@genesis.com', password: 'AgentTest123!' },
    { email: 'agent-test4@genesis.com', password: 'AgentTest123!' },
    { email: 'agent-test5@genesis.com', password: 'AgentTest123!' },
  ];
});

// Test configuration optimized for AI agents
export const options = {
  scenarios: {
    agents_load: {
      ...testScenarios.aiAgents,
      executor: 'ramping-vus',
      stages: [
        { duration: '2m', target: 5 },   // Slow ramp for AI
        { duration: '5m', target: 5 },   // Sustained AI load
        { duration: '2m', target: 10 },  // Increase AI load
        { duration: '5m', target: 10 },  // Peak AI load
        { duration: '2m', target: 15 },  // Stress test
        { duration: '3m', target: 15 },  // Sustained stress
        { duration: '1m', target: 0 },   // Ramp down
      ],
    },
  },
  thresholds: createThresholds({
    httpDuration: ['p(95)<5000'],
    httpFailed: ['rate<0.05'],
    aiResponseTime: ['p(95)<45000'],   // Longer timeout for complex AI
    aiQuality: ['rate>0.9'],           // Higher quality expectation
    aiErrorRate: ['rate<0.02'],        // Very low error tolerance
  }),
};

let authManager;

export function setup() {
  console.log('🤖 Starting GENESIS AI Agents Load Test...');

  // Health check
  const healthCheck = http.get(`${env.baseUrl}/health`);
  const isHealthy = check(healthCheck, {
    'API is healthy': (r) => r.status === 200,
  });

  if (!isHealthy) {
    throw new Error('API health check failed');
  }

  // Check agent availability
  const agentsCheck = http.get(`${env.baseUrl}/agents`);
  const agentsAvailable = check(agentsCheck, {
    'Agents endpoint accessible': (r) => r.status === 200 || r.status === 401, // Auth may be required
  });

  console.log('✅ AI Agents Load Test Setup Complete');
  return { ready: true };
}

export default function agentsLoadTest() {
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

  // Select random agent scenario
  const scenario = agentScenarios[Math.floor(Math.random() * agentScenarios.length)];
  const query = scenario.queries[Math.floor(Math.random() * scenario.queries.length)];

  // Test single agent interaction
  testAgentInteraction(scenario.agent, scenario.agentName, query);

  // Occasionally test multi-agent coordination (10% of requests)
  if (Math.random() < 0.1) {
    testMultiAgentCoordination();
  }

  // Test A2A communication patterns (5% of requests)
  if (Math.random() < 0.05) {
    testA2ACommunication();
  }

  // Variable sleep to simulate real user patterns
  sleep(Math.random() * 3 + 2); // 2-5 seconds between requests
}

/**
 * Test individual agent interaction
 */
function testAgentInteraction(agentId, agentName, queryData) {
  const startTime = Date.now();

  const payload = JSON.stringify({
    message: queryData.message,
    conversation_id: `agent-load-${vu.idInTest}-${Date.now()}`,
    user_context: queryData.context
  });

  const response = http.post(
    `${env.baseUrl}/agents/${agentId}/chat`,
    payload,
    {
      headers: authManager.getHeaders(),
      tags: {
        name: `agent_${agentId}`,
        agent: agentName,
        query_type: queryData.context.goals ? queryData.context.goals[0] : 'general'
      },
      timeout: '60s', // Extended timeout for complex AI processing
    }
  );

  const success = check(response, {
    [`${agentName} response status is 200`]: (r) => r.status === 200,
    [`${agentName} response time < 45s`]: (r) => r.timings.duration < 45000,
    [`${agentName} has substantial response`]: (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.response && body.response.length > 100;
      } catch (e) {
        return false;
      }
    },
    [`${agentName} response quality indicators`]: (r) => {
      if (r.status !== 200) return false;
      try {
        const body = JSON.parse(r.body);
        const response = body.response.toLowerCase();

        // Check for agent-specific quality indicators
        switch (agentName) {
          case 'BLAZE':
            return /workout|exercise|training|muscle|strength|rep|set/.test(response);
          case 'SAGE':
            return /nutrition|diet|meal|calories|protein|vitamins|food/.test(response);
          case 'STELLA':
            return /progress|goal|track|metric|improvement|achievement/.test(response);
          default:
            return response.length > 50;
        }
      } catch (e) {
        return false;
      }
    }
  });

  recordAIMetrics(response, agentName, startTime);

  if (!success && response.status !== 200) {
    console.warn(`${agentName} agent failed: ${response.status} - ${response.body}`);
  }

  // Test follow-up question (20% of the time)
  if (success && Math.random() < 0.2) {
    testFollowUpQuestion(agentId, agentName, payload);
  }
}

/**
 * Test follow-up questions in same conversation
 */
function testFollowUpQuestion(agentId, agentName, originalPayload) {
  const startTime = Date.now();

  try {
    const original = JSON.parse(originalPayload);
    const followUps = {
      'elite-training-strategist': [
        "Can you modify this plan for home workouts only?",
        "How should I progress the weights over time?",
        "What if I can only work out 3 days instead of 4?"
      ],
      'precision-nutrition-architect': [
        "Can you suggest specific meal prep ideas?",
        "What about healthy snack options?",
        "How should I adjust portions for my activity level?"
      ],
      'progress-tracker': [
        "Show me my strength improvements this month",
        "How does my progress compare to similar users?",
        "What areas need more focus?"
      ]
    };

    const followUpMessage = followUps[agentId] ?
      followUps[agentId][Math.floor(Math.random() * followUps[agentId].length)] :
      "Can you provide more details on that?";

    const followUpPayload = JSON.stringify({
      message: followUpMessage,
      conversation_id: original.conversation_id, // Same conversation
      user_context: original.user_context
    });

    const response = http.post(
      `${env.baseUrl}/agents/${agentId}/chat`,
      followUpPayload,
      {
        headers: authManager.getHeaders(),
        tags: {
          name: `followup_${agentId}`,
          agent: agentName,
          type: 'followup'
        },
        timeout: '45s',
      }
    );

    check(response, {
      [`${agentName} follow-up response successful`]: (r) => r.status === 200,
      [`${agentName} follow-up maintains context`]: (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.conversation_id === original.conversation_id;
        } catch (e) {
          return false;
        }
      }
    });

    recordAIMetrics(response, `${agentName}_followup`, startTime);

  } catch (e) {
    console.warn(`Follow-up test failed: ${e.message}`);
  }
}

/**
 * Test multi-agent coordination
 */
function testMultiAgentCoordination() {
  const startTime = Date.now();

  // Test orchestrator endpoint for multi-agent scenarios
  const payload = JSON.stringify({
    message: "I want a complete fitness transformation plan including training and nutrition.",
    conversation_id: `multi-agent-${vu.idInTest}-${Date.now()}`,
    user_context: {
      fitness_level: 'beginner',
      goals: ['weight_loss', 'muscle_gain'],
      available_days: 4,
      dietary_restrictions: [],
      timeline: '3_months'
    },
    require_agents: ['elite-training-strategist', 'precision-nutrition-architect']
  });

  const response = http.post(
    `${env.baseUrl}/agents/orchestrator/chat`,
    payload,
    {
      headers: authManager.getHeaders(),
      tags: {
        name: 'multi_agent_coordination',
        type: 'orchestration'
      },
      timeout: '90s', // Extended timeout for coordination
    }
  );

  const coordinationSuccess = check(response, {
    'Multi-agent coordination successful': (r) => r.status === 200,
    'Coordination response comprehensive': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.response && body.response.length > 200; // Expect comprehensive response
      } catch (e) {
        return false;
      }
    },
    'Coordination response time reasonable': (r) => r.timings.duration < 90000,
  });

  recordAIMetrics(response, 'ORCHESTRATOR', startTime);

  if (!coordinationSuccess) {
    console.warn(`Multi-agent coordination failed: ${response.status}`);
  }
}

/**
 * Test A2A communication patterns
 */
function testA2ACommunication() {
  const startTime = Date.now();

  // Test A2A status endpoint if available
  const response = http.get(`${env.baseUrl}/a2a/status`, {
    headers: authManager.getHeaders(),
    tags: { name: 'a2a_status' },
    timeout: '10s',
  });

  const a2aSuccess = check(response, {
    'A2A status accessible': (r) => [200, 401, 404].includes(r.status),
    'A2A response time fast': (r) => r.timings.duration < 2000,
  });

  const latency = Date.now() - startTime;
  recordA2AMetrics('load-test', 'a2a-server', latency, response.status === 200);
}

export function teardown() {
  console.log('🤖 AI Agents Load Test Complete');
  console.log('📊 Review metrics for:');
  console.log('   - AI response times and quality');
  console.log('   - Agent-specific performance');
  console.log('   - Multi-agent coordination efficiency');
  console.log('   - A2A communication latency');
}
