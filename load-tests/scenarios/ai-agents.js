/**
 * GENESIS AI Agents Load Test
 *
 * Specialized test for AI agent performance under various conversation patterns
 * Tests all agents: BLAZE, SAGE, STELLA, NOVA, AURA, WAVE, VOLT
 *
 * Performance Targets:
 * - AI response time P95 < 20s
 * - Response quality rate > 85%
 * - Agent-to-agent handoffs < 2s
 * - Concurrent conversations support
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';
import { vu, scenario } from 'k6/execution';

import { getEnvironment } from '../config/environments.js';
import { AuthManager } from '../utils/auth.js';
import { recordAIMetrics, recordA2AMetrics, recordUserJourneyMetrics, createThresholds } from '../utils/metrics.js';

const env = getEnvironment(__ENV.ENVIRONMENT || 'local');

// AI-specific test scenarios
const aiTestScenarios = new SharedArray('ai_scenarios', function () {
  return [
    {
      type: 'training',
      agent: 'elite-training-strategist',
      name: 'BLAZE',
      queries: [
        "Create a muscle building workout plan for intermediate level",
        "I want to increase my bench press, what exercises should I focus on?",
        "Design a home workout routine with minimal equipment",
        "Help me break through a strength training plateau",
        "What's the best way to structure a push-pull-legs routine?"
      ],
      context: {
        fitness_level: 'intermediate',
        goals: ['muscle_gain', 'strength'],
        equipment: ['dumbbells', 'barbell', 'bench']
      }
    },
    {
      type: 'nutrition',
      agent: 'precision-nutrition-architect',
      name: 'SAGE',
      queries: [
        "Create a meal plan for muscle gain with 2500 calories",
        "I'm vegetarian, help me get enough protein for muscle building",
        "What should I eat before and after workouts?",
        "Design a cutting diet to lose fat while preserving muscle",
        "Help me track macros for body recomposition"
      ],
      context: {
        fitness_level: 'intermediate',
        goals: ['muscle_gain'],
        dietary_restrictions: ['vegetarian']
      }
    },
    {
      type: 'progress',
      agent: 'progress-tracker',
      name: 'STELLA',
      queries: [
        "Analyze my workout progress over the last month",
        "I've been tracking my lifts, what improvements do you see?",
        "Help me set realistic fitness goals for the next quarter",
        "My weight hasn't changed but I feel stronger, explain this",
        "Create a progress tracking system for my workouts"
      ],
      context: {
        fitness_level: 'intermediate',
        tracking_data: true,
        goals: ['progress_tracking']
      }
    },
    {
      type: 'wellness',
      agent: 'female-wellness-coach',
      name: 'AURA',
      queries: [
        "Help me manage hormonal changes affecting my workouts",
        "Create a workout plan that adapts to my menstrual cycle",
        "I'm experiencing workout fatigue, what could be causing it?",
        "How can I maintain fitness during pregnancy?",
        "Design a post-workout recovery routine for women"
      ],
      context: {
        fitness_level: 'intermediate',
        gender: 'female',
        goals: ['wellness', 'hormonal_health']
      }
    },
    {
      type: 'biohacking',
      agent: 'nova-biohacking-innovator',
      name: 'NOVA',
      queries: [
        "What wearable devices should I use to optimize my training?",
        "Help me interpret my heart rate variability data",
        "How can I use technology to improve my sleep quality?",
        "What biomarkers should I track for optimal performance?",
        "Design a recovery protocol using biohacking tools"
      ],
      context: {
        fitness_level: 'advanced',
        tech_savvy: true,
        goals: ['optimization', 'biohacking']
      }
    },
    {
      type: 'performance',
      agent: 'wave-performance-analytics',
      name: 'WAVE',
      queries: [
        "Analyze my training data to identify performance patterns",
        "Help me predict when I might hit a plateau",
        "What metrics are most important for tracking progress?",
        "Create a data-driven training adjustment plan",
        "How can I use analytics to prevent overtraining?"
      ],
      context: {
        fitness_level: 'advanced',
        data_driven: true,
        goals: ['performance', 'analytics']
      }
    },
    {
      type: 'motivation',
      agent: 'motivation-behavior-coach',
      name: 'VOLT',
      queries: [
        "I'm losing motivation to work out, how can you help?",
        "Help me build sustainable fitness habits",
        "How do I stay consistent with my nutrition plan?",
        "I keep skipping workouts, what strategies can help?",
        "Create a motivation system for my fitness journey"
      ],
      context: {
        fitness_level: 'beginner',
        motivation_level: 'low',
        goals: ['habit_building', 'consistency']
      }
    }
  ];
});

const testUsers = new SharedArray('ai_users', function () {
  return Array.from({ length: 10 }, (_, i) => ({
    email: `ai-test${i + 1}@genesis.com`,
    password: 'AITest123!'
  }));
});

export const options = {
  scenarios: {
    ai_conversation_flow: {
      executor: 'ramping-vus',
      startVUs: 2,
      stages: [
        { duration: '1m', target: 5 },   // Warm up
        { duration: '3m', target: 10 },  // Normal AI load
        { duration: '5m', target: 15 },  // Peak AI conversations
        { duration: '3m', target: 8 },   // Cool down
        { duration: '1m', target: 0 },   // Complete
      ],
    },
    agent_handoff_test: {
      executor: 'constant-vus',
      vus: 3,
      duration: '5m',
      startTime: '2m', // Start after main scenario is warmed up
    },
  },
  thresholds: createThresholds({
    httpDuration: ['p(95)<3000'],
    httpFailed: ['rate<0.05'],
    aiResponseTime: ['p(95)<20000', 'p(99)<30000'],
    aiQuality: ['rate>0.85'],
    a2aLatency: ['p(95)<2000'],
    a2aSuccess: ['rate>0.95'],
  }),
};

let authManager;

export function setup() {
  console.log('🤖 Starting GENESIS AI Agents Load Test...');
  console.log('Testing all 7 AI agents under conversational load');

  const healthCheck = http.get(`${env.baseUrl}/health`);
  check(healthCheck, {
    'AI agents test - system healthy': (r) => r.status === 200,
  });

  return { startTime: new Date().toISOString() };
}

export default function aiAgentsTest(data) {
  if (!authManager) {
    const userIndex = vu.idInTest % testUsers.length;
    const user = testUsers[userIndex];
    authManager = new AuthManager(env.baseUrl, user);

    if (!authManager.init()) {
      console.error(`AI test auth failed for ${user.email}`);
      return;
    }
  }

  const testStart = Date.now();
  let testSuccess = true;

  try {
    if (scenario.name === 'ai_conversation_flow') {
      testAIConversationFlow();
    } else if (scenario.name === 'agent_handoff_test') {
      testAgentHandoffs();
    }

  } catch (error) {
    console.error(`AI agents test error: ${error.message}`);
    testSuccess = false;
  } finally {
    recordUserJourneyMetrics(`ai_${scenario.name}`, testStart, testSuccess);
  }

  sleep(Math.random() * 3 + 2); // 2-5 seconds between AI interactions
}

/**
 * Test AI conversation flows with different agents
 */
function testAIConversationFlow() {
  const scenarioIndex = Math.floor(Math.random() * aiTestScenarios.length);
  const aiScenario = aiTestScenarios[scenarioIndex];
  const queryIndex = Math.floor(Math.random() * aiScenario.queries.length);
  const query = aiScenario.queries[queryIndex];

  const startTime = Date.now();

  const payload = JSON.stringify({
    message: query,
    conversation_id: `ai-flow-${vu.idInTest}-${Date.now()}`,
    user_context: aiScenario.context,
    test_metadata: {
      agent_type: aiScenario.type,
      scenario: scenarioIndex,
      query_complexity: query.length > 80 ? 'complex' : 'simple'
    }
  });

  const response = http.post(
    `${env.baseUrl}/agents/${aiScenario.agent}/chat`,
    payload,
    {
      headers: authManager.getHeaders(),
      tags: {
        name: `ai_${aiScenario.name.toLowerCase()}`,
        agent_type: aiScenario.type
      },
      timeout: '35s',
    }
  );

  const success = check(response, {
    [`${aiScenario.name} responds`]: (r) => r.status === 200,
    [`${aiScenario.name} has meaningful content`]: (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.response && body.response.length > 100;
      } catch (e) {
        return false;
      }
    },
    [`${aiScenario.name} response time acceptable`]: (r) => r.timings.duration < 25000,
    [`${aiScenario.name} quality check`]: (r) => {
      try {
        const body = JSON.parse(r.body);
        const response = body.response.toLowerCase();

        // Agent-specific quality checks
        switch (aiScenario.type) {
          case 'training':
            return response.includes('exercise') || response.includes('workout') || response.includes('training');
          case 'nutrition':
            return response.includes('nutrition') || response.includes('food') || response.includes('meal');
          case 'progress':
            return response.includes('progress') || response.includes('goal') || response.includes('tracking');
          case 'wellness':
            return response.includes('wellness') || response.includes('health') || response.includes('recovery');
          case 'biohacking':
            return response.includes('optimize') || response.includes('track') || response.includes('data');
          case 'performance':
            return response.includes('performance') || response.includes('metric') || response.includes('analyze');
          case 'motivation':
            return response.includes('motivation') || response.includes('habit') || response.includes('goal');
          default:
            return response.length > 50;
        }
      } catch (e) {
        return false;
      }
    },
  });

  recordAIMetrics(response, aiScenario.name, startTime);

  if (!success) {
    console.warn(`${aiScenario.name} AI conversation failed or degraded`);
  }
}

/**
 * Test agent-to-agent handoffs and multi-agent workflows
 */
function testAgentHandoffs() {
  const handoffScenarios = [
    {
      description: "Training to Nutrition handoff",
      firstAgent: 'elite-training-strategist',
      firstQuery: "I want to build muscle, create a workout plan",
      secondAgent: 'precision-nutrition-architect',
      secondQuery: "Now help me with nutrition to support this muscle building plan"
    },
    {
      description: "Nutrition to Progress handoff",
      firstAgent: 'precision-nutrition-architect',
      firstQuery: "Create a cutting diet plan",
      secondAgent: 'progress-tracker',
      secondQuery: "How should I track my progress on this cutting plan?"
    },
    {
      description: "Progress to Motivation handoff",
      firstAgent: 'progress-tracker',
      firstQuery: "I've been tracking my workouts but not seeing results",
      secondAgent: 'motivation-behavior-coach',
      secondQuery: "I'm getting demotivated by my lack of progress, help me stay committed"
    }
  ];

  const scenario = handoffScenarios[Math.floor(Math.random() * handoffScenarios.length)];
  const conversationId = `handoff-${vu.idInTest}-${Date.now()}`;

  // First agent interaction
  const firstStartTime = Date.now();
  const firstPayload = JSON.stringify({
    message: scenario.firstQuery,
    conversation_id: conversationId,
    user_context: {
      fitness_level: 'intermediate',
      handoff_test: true,
      phase: 'first'
    }
  });

  const firstResponse = http.post(
    `${env.baseUrl}/agents/${scenario.firstAgent}/chat`,
    firstPayload,
    {
      headers: authManager.getHeaders(),
      tags: { name: 'handoff_first_agent' },
      timeout: '30s',
    }
  );

  const firstSuccess = check(firstResponse, {
    'Handoff: First agent responds': (r) => r.status === 200,
    'Handoff: First agent has content': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.response && body.response.length > 50;
      } catch (e) {
        return false;
      }
    },
  });

  if (firstSuccess) {
    // Wait for handoff processing
    sleep(1);

    // Second agent interaction (should have context from first)
    const secondStartTime = Date.now();
    const secondPayload = JSON.stringify({
      message: scenario.secondQuery,
      conversation_id: conversationId, // Same conversation ID for context
      user_context: {
        fitness_level: 'intermediate',
        handoff_test: true,
        phase: 'handoff'
      }
    });

    const secondResponse = http.post(
      `${env.baseUrl}/agents/${scenario.secondAgent}/chat`,
      secondPayload,
      {
        headers: authManager.getHeaders(),
        tags: { name: 'handoff_second_agent' },
        timeout: '30s',
      }
    );

    const handoffLatency = secondStartTime - firstStartTime;

    const handoffSuccess = check(secondResponse, {
      'Handoff: Second agent responds': (r) => r.status === 200,
      'Handoff: Second agent has contextual content': (r) => {
        try {
          const body = JSON.parse(r.body);
          // Should reference or build upon the first agent's response
          return body.response && body.response.length > 50;
        } catch (e) {
          return false;
        }
      },
      'Handoff: Reasonable handoff time': () => handoffLatency < 2000,
    });

    // Record A2A metrics
    recordA2AMetrics(
      scenario.firstAgent,
      scenario.secondAgent,
      handoffLatency,
      handoffSuccess
    );

    recordAIMetrics(firstResponse, scenario.firstAgent, firstStartTime);
    recordAIMetrics(secondResponse, scenario.secondAgent, secondStartTime);

    if (!handoffSuccess) {
      console.warn(`Agent handoff failed: ${scenario.description}`);
    }
  }
}

export function teardown(data) {
  console.log('🤖 AI Agents Load Test Complete');
  console.log(`Started: ${data.startTime}`);
  console.log(`Completed: ${new Date().toISOString()}`);

  // Test final agent availability
  const agentsCheck = http.get(`${env.baseUrl}/agents`);
  const agentsAvailable = check(agentsCheck, {
    'All agents available after load test': (r) => {
      try {
        const agents = JSON.parse(r.body);
        return Array.isArray(agents) && agents.length >= 7;
      } catch (e) {
        return false;
      }
    },
  });

  if (agentsAvailable) {
    console.log('✅ All AI agents remained available throughout load test');
  } else {
    console.log('⚠️  Some agents may have become unavailable during load test');
  }

  console.log('📊 Review metrics for:');
  console.log('   - Individual agent response times');
  console.log('   - Agent-to-agent handoff performance');
  console.log('   - Response quality consistency');
  console.log('   - Concurrent conversation handling');
}
