/**
 * Environment Configuration for GENESIS Load Tests
 *
 * Manages different environment settings for load testing
 * across local, staging, and production environments.
 */

export const environments = {
  local: {
    baseUrl: 'http://localhost:8000',
    frontendUrl: 'http://localhost:5173',
    maxVUs: 50,
    duration: '5m',
    thresholds: {
      http_req_duration: ['p(95)<2000'], // 95% of requests under 2s
      http_req_failed: ['rate<0.1'],     // Error rate under 10%
    }
  },

  staging: {
    baseUrl: 'https://api-staging.genesis.com',
    frontendUrl: 'https://staging.genesis.com',
    maxVUs: 200,
    duration: '10m',
    thresholds: {
      http_req_duration: ['p(95)<3000'], // 95% of requests under 3s
      http_req_failed: ['rate<0.05'],    // Error rate under 5%
    }
  },

  production: {
    baseUrl: 'https://api.genesis.com',
    frontendUrl: 'https://app.genesis.com',
    maxVUs: 500,
    duration: '15m',
    thresholds: {
      http_req_duration: ['p(95)<1500'], // 95% of requests under 1.5s
      http_req_failed: ['rate<0.01'],    // Error rate under 1%
    }
  }
};

// Get environment configuration
export function getEnvironment(env = 'local') {
  return environments[env] || environments.local;
}

// Test scenarios for different load patterns
export const testScenarios = {
  smoke: {
    executor: 'constant-vus',
    vus: 1,
    duration: '1m',
  },

  load: {
    executor: 'constant-vus',
    vus: 10,
    duration: '5m',
  },

  stress: {
    executor: 'ramping-vus',
    stages: [
      { duration: '2m', target: 100 },  // Ramp up
      { duration: '5m', target: 100 },  // Stay at 100 users
      { duration: '2m', target: 200 },  // Ramp to 200 users
      { duration: '5m', target: 200 },  // Stay at 200 users
      { duration: '2m', target: 0 },    // Ramp down
    ],
  },

  spike: {
    executor: 'ramping-vus',
    stages: [
      { duration: '10s', target: 100 }, // Fast ramp-up
      { duration: '1m', target: 100 },  // Stay at 100 users
      { duration: '10s', target: 1400 }, // Spike to 1400 users
      { duration: '3m', target: 1400 }, // Stay at 1400 users
      { duration: '10s', target: 100 }, // Quick ramp-down to 100 users
      { duration: '3m', target: 100 },  // Recovery at 100 users
      { duration: '10s', target: 0 },   // Ramp-down to 0 users
    ],
  },

  // AI-specific scenarios with longer durations for LLM responses
  aiAgents: {
    executor: 'ramping-vus',
    stages: [
      { duration: '1m', target: 5 },   // Slow ramp for AI
      { duration: '3m', target: 5 },   // Sustained AI load
      { duration: '1m', target: 10 },  // Increase AI load
      { duration: '3m', target: 10 },  // Peak AI load
      { duration: '1m', target: 0 },   // Ramp down
    ],
  },

  // Voice synthesis load pattern
  voice: {
    executor: 'constant-vus',
    vus: 3, // Limited concurrent voice synthesis
    duration: '2m',
  },

  // Streaming responses pattern
  streaming: {
    executor: 'constant-vus',
    vus: 5, // Limited concurrent streams
    duration: '3m',
  }
};

// Performance thresholds for different test types
export const performanceThresholds = {
  api: {
    http_req_duration: ['p(95)<1000'],
    http_req_failed: ['rate<0.05'],
    http_reqs: ['rate>10'], // At least 10 requests per second
  },

  agents: {
    http_req_duration: ['p(95)<30000'], // AI responses can take up to 30s
    http_req_failed: ['rate<0.1'],
    ai_response_quality: ['rate>0.8'],  // Custom metric for AI quality
  },

  voice: {
    http_req_duration: ['p(95)<15000'], // Voice synthesis up to 15s
    http_req_failed: ['rate<0.05'],
    voice_generation_success: ['rate>0.95'], // Custom metric
  },

  streaming: {
    http_req_duration: ['p(95)<60000'], // Streaming can take up to 1 minute
    http_req_failed: ['rate<0.05'],
    stream_completion_rate: ['rate>0.9'], // Custom metric
  }
};

// Test data for load testing
export const testData = {
  users: [
    { email: 'loadtest1@genesis.com', password: 'LoadTest123!' },
    { email: 'loadtest2@genesis.com', password: 'LoadTest123!' },
    { email: 'loadtest3@genesis.com', password: 'LoadTest123!' },
    { email: 'loadtest4@genesis.com', password: 'LoadTest123!' },
    { email: 'loadtest5@genesis.com', password: 'LoadTest123!' },
  ],

  trainingQueries: [
    "I want to build muscle mass, create a workout plan",
    "I'm a beginner, what exercises should I start with?",
    "Help me create a home workout routine",
    "I want to lose weight and tone up",
    "Create a 3-day split workout program"
  ],

  nutritionQueries: [
    "I'm vegetarian and want to gain muscle, help with meal planning",
    "Create a low-carb diet plan for weight loss",
    "What should I eat before and after workouts?",
    "Help me plan meals for a 2000 calorie diet",
    "I have diabetes, what's a safe eating plan?"
  ],

  voiceTexts: [
    "Hello! Welcome to GENESIS. How can I help you today?",
    "Great job on completing your workout! Keep up the excellent progress.",
    "Here's your personalized nutrition plan for this week.",
    "Remember to stay hydrated and get enough rest for optimal recovery.",
    "Your fitness journey is looking fantastic! Let's review your goals."
  ]
};

// Utility functions for load testing
export function getRandomItem(array) {
  return array[Math.floor(Math.random() * array.length)];
}

export function generateTestUser() {
  return getRandomItem(testData.users);
}

export function generateTrainingQuery() {
  return getRandomItem(testData.trainingQueries);
}

export function generateNutritionQuery() {
  return getRandomItem(testData.nutritionQueries);
}

export function generateVoiceText() {
  return getRandomItem(testData.voiceTexts);
}
