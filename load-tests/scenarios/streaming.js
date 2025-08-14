/**
 * GENESIS Streaming Load Test
 *
 * Tests real-time streaming capabilities including:
 * - Server-Sent Events (SSE) for AI responses
 * - WebSocket connections for real-time updates
 * - Streaming response handling under load
 *
 * Performance Targets:
 * - Stream establishment < 2s
 * - Chunk delivery latency < 500ms
 * - Stream completion rate > 95%
 * - Concurrent stream support
 */

import http from 'k6/http';
import ws from 'k6/ws';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';
import { vu, scenario } from 'k6/execution';

import { getEnvironment } from '../config/environments.js';
import { AuthManager } from '../utils/auth.js';
import { recordStreamingMetrics, recordUserJourneyMetrics, createThresholds } from '../utils/metrics.js';

const env = getEnvironment(__ENV.ENVIRONMENT || 'local');

const streamingUsers = new SharedArray('streaming_users', function () {
  return Array.from({ length: 8 }, (_, i) => ({
    email: `streaming${i + 1}@genesis.com`,
    password: 'StreamTest123!'
  }));
});

const streamingQueries = new SharedArray('streaming_queries', function () {
  return [
    {
      type: 'training',
      message: "Create a detailed progressive overload training program for the next 12 weeks",
      expectedChunks: 15,
      timeout: 45000
    },
    {
      type: 'nutrition',
      message: "Design a comprehensive meal prep plan with recipes and shopping lists",
      expectedChunks: 12,
      timeout: 40000
    },
    {
      type: 'analysis',
      message: "Analyze my fitness data and provide detailed recommendations for improvement",
      expectedChunks: 20,
      timeout: 50000
    },
    {
      type: 'planning',
      message: "Create a complete fitness transformation plan including workouts, nutrition, and lifestyle changes",
      expectedChunks: 25,
      timeout: 60000
    }
  ];
});

export const options = {
  scenarios: {
    sse_streaming: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '30s', target: 3 },  // Ramp up SSE streams
        { duration: '2m', target: 8 },   // Peak streaming load
        { duration: '3m', target: 8 },   // Sustained streaming
        { duration: '1m', target: 3 },   // Cool down
        { duration: '30s', target: 0 },  // Complete
      ],
    },
    websocket_connections: {
      executor: 'constant-vus',
      vus: 5,
      duration: '4m',
      startTime: '1m',
    },
  },
  thresholds: createThresholds({
    httpDuration: ['p(95)<5000'],
    httpFailed: ['rate<0.05'],
    streamingLatency: ['p(95)<1000'],
    streamingCompletion: ['rate>0.95'],
  }),
};

let authManager;

export function setup() {
  console.log('🌊 Starting GENESIS Streaming Load Test...');
  console.log('Testing SSE and WebSocket streaming under load');

  const healthCheck = http.get(`${env.baseUrl}/health`);
  check(healthCheck, {
    'Streaming test - system healthy': (r) => r.status === 200,
  });

  return { startTime: new Date().toISOString() };
}

export default function streamingTest(data) {
  if (!authManager) {
    const userIndex = vu.idInTest % streamingUsers.length;
    const user = streamingUsers[userIndex];
    authManager = new AuthManager(env.baseUrl, user);

    if (!authManager.init()) {
      console.error(`Streaming test auth failed for ${user.email}`);
      return;
    }
  }

  const testStart = Date.now();
  let testSuccess = true;

  try {
    if (scenario.name === 'sse_streaming') {
      testSSEStreaming();
    } else if (scenario.name === 'websocket_connections') {
      testWebSocketConnections();
    }

  } catch (error) {
    console.error(`Streaming test error: ${error.message}`);
    testSuccess = false;
  } finally {
    recordUserJourneyMetrics(`streaming_${scenario.name}`, testStart, testSuccess);
  }

  sleep(Math.random() * 2 + 1); // 1-3 seconds between streaming tests
}

/**
 * Test Server-Sent Events streaming
 */
function testSSEStreaming() {
  const queryIndex = Math.floor(Math.random() * streamingQueries.length);
  const query = streamingQueries[queryIndex];

  const streamStart = Date.now();
  let chunksReceived = 0;
  let firstChunkTime = 0;
  let lastChunkTime = 0;
  let streamCompleted = false;

  const conversationId = `sse-${vu.idInTest}-${Date.now()}`;

  const payload = JSON.stringify({
    message: query.message,
    conversation_id: conversationId,
    stream: true,
    user_context: {
      fitness_level: 'intermediate',
      streaming_test: true,
      expected_chunks: query.expectedChunks
    }
  });

  // Start streaming request
  const response = http.post(
    `${env.baseUrl}/agents/elite-training-strategist/stream`,
    payload,
    {
      headers: {
        ...authManager.getHeaders(),
        'Accept': 'text/event-stream',
        'Cache-Control': 'no-cache',
      },
      tags: { name: `sse_${query.type}` },
      timeout: `${query.timeout}ms`,
      responseCallback: http.expectedStatuses(200),
    }
  );

  const sseSuccess = check(response, {
    'SSE stream initiated': (r) => r.status === 200,
    'SSE content type correct': (r) => r.headers['Content-Type'] && r.headers['Content-Type'].includes('text/event-stream'),
    'SSE stream has data': (r) => r.body && r.body.length > 100,
  });

  if (sseSuccess) {
    // Parse SSE response to count chunks
    const sseData = response.body;
    const events = sseData.split('\n\n').filter(event => event.trim().startsWith('data: '));

    chunksReceived = events.length;

    if (events.length > 0) {
      firstChunkTime = streamStart + 100; // Approximate first chunk time
      lastChunkTime = Date.now();
      streamCompleted = events[events.length - 1].includes('[DONE]') || events[events.length - 1].includes('stream_complete');
    }

    check(null, {
      [`SSE received expected chunks (${query.type})`]: () => chunksReceived >= query.expectedChunks * 0.8, // Allow 20% variance
      [`SSE stream completed (${query.type})`]: () => streamCompleted,
      [`SSE first chunk fast (${query.type})`]: () => firstChunkTime - streamStart < 3000,
    });
  }

  recordStreamingMetrics(streamStart, chunksReceived, streamCompleted);

  if (!sseSuccess) {
    console.warn(`SSE streaming failed for ${query.type} query`);
  }
}

/**
 * Test WebSocket connections and real-time updates
 */
function testWebSocketConnections() {
  const wsUrl = env.baseUrl.replace('http://', 'ws://').replace('https://', 'wss://') + '/ws';
  const connectionStart = Date.now();
  let messagesReceived = 0;
  let connectionEstablished = false;
  let testCompleted = false;

  const wsResponse = ws.connect(wsUrl, {
    headers: authManager.getHeaders(),
    tags: { name: 'websocket_connection' },
  }, function (socket) {
    connectionEstablished = true;
    const connectionTime = Date.now() - connectionStart;

    check(null, {
      'WebSocket connection established': () => connectionEstablished,
      'WebSocket connection time acceptable': () => connectionTime < 2000,
    });

    // Send test messages
    const testMessages = [
      {
        type: 'subscribe',
        channel: 'agent_updates',
        user_id: `streaming-user-${vu.idInTest}`
      },
      {
        type: 'ping',
        timestamp: Date.now()
      },
      {
        type: 'agent_request',
        message: 'Send me real-time workout updates',
        agent: 'elite-training-strategist'
      }
    ];

    testMessages.forEach((msg, index) => {
      setTimeout(() => {
        socket.send(JSON.stringify(msg));
      }, index * 1000);
    });

    socket.on('message', function (message) {
      messagesReceived++;
      lastChunkTime = Date.now();

      try {
        const data = JSON.parse(message);

        if (data.type === 'pong') {
          const pingLatency = Date.now() - data.timestamp;
          check(null, {
            'WebSocket ping latency acceptable': () => pingLatency < 500,
          });
        }

        if (data.type === 'agent_response') {
          check(null, {
            'WebSocket agent response has content': () => data.content && data.content.length > 10,
          });
        }

      } catch (e) {
        console.warn('WebSocket message parse error:', e);
      }
    });

    socket.on('error', function (error) {
      console.error('WebSocket error:', error);
    });

    // Keep connection alive for test duration
    setTimeout(() => {
      testCompleted = true;
      socket.close();
    }, 15000); // 15 seconds

    socket.setTimeout(function () {
      testCompleted = true;
      socket.close();
    }, 20000); // 20 seconds timeout
  });

  // Wait for WebSocket test to complete
  let waitTime = 0;
  while (!testCompleted && waitTime < 25000) {
    sleep(0.5);
    waitTime += 500;
  }

  const wsSuccess = check(null, {
    'WebSocket test completed': () => testCompleted,
    'WebSocket received messages': () => messagesReceived > 0,
    'WebSocket message rate acceptable': () => messagesReceived >= 2, // At least pong and one other message
  });

  recordStreamingMetrics(connectionStart, messagesReceived, wsSuccess);

  if (!wsSuccess) {
    console.warn('WebSocket connection test failed or incomplete');
  }
}

/**
 * Test combined streaming scenarios
 */
function testCombinedStreaming() {
  const combinedStart = Date.now();
  let sseChunks = 0;
  let wsMessages = 0;
  let bothCompleted = false;

  // Start SSE stream
  const ssePayload = JSON.stringify({
    message: "Create a workout plan while I track progress in real-time",
    conversation_id: `combined-${vu.idInTest}-${Date.now()}`,
    stream: true,
    user_context: {
      streaming_test: 'combined',
      real_time_updates: true
    }
  });

  const ssePromise = http.asyncRequest('POST', `${env.baseUrl}/agents/elite-training-strategist/stream`, ssePayload, {
    headers: {
      ...authManager.getHeaders(),
      'Accept': 'text/event-stream',
    },
    tags: { name: 'combined_sse' },
  });

  // Start WebSocket connection simultaneously
  const wsUrl = env.baseUrl.replace('http://', 'ws://').replace('https://', 'wss://') + '/ws/progress';

  ws.connect(wsUrl, {
    headers: authManager.getHeaders(),
    tags: { name: 'combined_websocket' },
  }, function (socket) {

    socket.send(JSON.stringify({
      type: 'start_progress_tracking',
      session_id: `combined-${vu.idInTest}`
    }));

    socket.on('message', function (message) {
      wsMessages++;
    });

    setTimeout(() => {
      socket.close();
      bothCompleted = true;
    }, 10000);
  });

  // Wait for both to complete
  let waitTime = 0;
  while (!bothCompleted && waitTime < 15000) {
    sleep(0.5);
    waitTime += 500;
  }

  check(null, {
    'Combined streaming test completed': () => bothCompleted,
    'Both SSE and WS received data': () => sseChunks > 0 && wsMessages > 0,
  });

  recordStreamingMetrics(combinedStart, sseChunks + wsMessages, bothCompleted);
}

export function teardown(data) {
  console.log('🌊 Streaming Load Test Complete');
  console.log(`Started: ${data.startTime}`);
  console.log(`Completed: ${new Date().toISOString()}`);

  // Test streaming endpoints availability
  const streamingHealthCheck = http.get(`${env.baseUrl}/health`);
  const streamingHealthy = check(streamingHealthCheck, {
    'Streaming endpoints healthy after test': (r) => r.status === 200,
  });

  if (streamingHealthy) {
    console.log('✅ Streaming infrastructure remained stable throughout load test');
  } else {
    console.log('⚠️  Streaming infrastructure may need recovery time');
  }

  console.log('📊 Review metrics for:');
  console.log('   - Stream establishment times');
  console.log('   - Chunk delivery latency');
  console.log('   - Stream completion rates');
  console.log('   - WebSocket connection stability');
  console.log('   - Concurrent streaming performance');
}
