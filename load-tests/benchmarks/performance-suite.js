/**
 * GENESIS Performance Benchmark Suite
 *
 * Comprehensive benchmarking tool that measures and validates all performance targets
 * Runs focused tests to collect specific performance metrics
 *
 * Benchmark Categories:
 * 1. API Response Times
 * 2. Database Query Performance
 * 3. Cache Hit Ratios
 * 4. AI Agent Response Times
 * 5. Memory and CPU Usage
 * 6. Throughput Measurements
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';
import { vu, scenario } from 'k6/execution';
import { htmlReport } from 'https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js';

import { getEnvironment } from '../config/environments.js';
import { AuthManager } from '../utils/auth.js';
import { recordAIMetrics, recordSystemMetrics, createThresholds } from '../utils/metrics.js';

const env = getEnvironment(__ENV.ENVIRONMENT || 'local');

const benchmarkUsers = new SharedArray('benchmark_users', function () {
  return [
    { email: 'benchmark1@genesis.com', password: 'BenchmarkTest123!' },
    { email: 'benchmark2@genesis.com', password: 'BenchmarkTest123!' },
    { email: 'benchmark3@genesis.com', password: 'BenchmarkTest123!' },
  ];
});

export const options = {
  scenarios: {
    api_benchmarks: {
      executor: 'shared-iterations',
      vus: 1,
      iterations: 100,
      maxDuration: '5m',
    },
    database_benchmarks: {
      executor: 'shared-iterations',
      vus: 1,
      iterations: 50,
      maxDuration: '3m',
      startTime: '5m',
    },
    cache_benchmarks: {
      executor: 'shared-iterations',
      vus: 1,
      iterations: 200,
      maxDuration: '4m',
      startTime: '8m',
    },
    ai_benchmarks: {
      executor: 'shared-iterations',
      vus: 2,
      iterations: 20,
      maxDuration: '10m',
      startTime: '12m',
    },
    throughput_benchmarks: {
      executor: 'constant-arrival-rate',
      rate: 100,
      timeUnit: '1s',
      duration: '2m',
      preAllocatedVUs: 10,
      maxVUs: 20,
      startTime: '22m',
    },
  },
  thresholds: {
    // API Response Time Targets
    'http_req_duration{scenario:api_benchmarks}': ['p(50)<100', 'p(95)<500', 'p(99)<1000'],
    'http_req_failed{scenario:api_benchmarks}': ['rate<0.01'],

    // Database Performance Targets
    'http_req_duration{scenario:database_benchmarks}': ['p(95)<2000'],

    // Cache Performance Targets
    'http_req_duration{scenario:cache_benchmarks}': ['p(95)<50'],
    'cache_hit_rate': ['rate>0.90'],

    // AI Performance Targets
    'ai_response_time{scenario:ai_benchmarks}': ['p(95)<20000'],
    'ai_response_quality': ['rate>0.90'],

    // Throughput Targets
    'http_reqs{scenario:throughput_benchmarks}': ['rate>100'],
    'http_req_duration{scenario:throughput_benchmarks}': ['p(95)<2000'],
  },
};

let authManager;
let benchmarkResults = {
  api: [],
  database: [],
  cache: [],
  ai: [],
  throughput: [],
  system: []
};

export function setup() {
  console.log('🎯 Starting GENESIS Performance Benchmark Suite...');
  console.log('Collecting comprehensive performance metrics across all system components');

  const healthCheck = http.get(`${env.baseUrl}/health`);
  const systemHealthy = check(healthCheck, {
    'Benchmark pre-test system health': (r) => r.status === 200,
  });

  if (!systemHealthy) {
    throw new Error('System not healthy - cannot run reliable benchmarks');
  }

  return {
    startTime: new Date().toISOString(),
    environment: env,
    targets: {
      p50_latency: 100,
      p95_latency: 500,
      p99_latency: 1000,
      error_rate: 0.01,
      throughput: 100,
      cache_hit_rate: 0.90,
      ai_response_time: 20000,
      ai_quality: 0.90
    }
  };
}

export default function performanceBenchmark(data) {
  if (!authManager) {
    const user = benchmarkUsers[0]; // Use consistent user for benchmarking
    authManager = new AuthManager(env.baseUrl, user);

    if (!authManager.init()) {
      console.error('Benchmark authentication failed');
      return;
    }
  }

  const testStart = Date.now();

  try {
    switch (scenario.name) {
      case 'api_benchmarks':
        benchmarkAPIPerformance();
        break;
      case 'database_benchmarks':
        benchmarkDatabasePerformance();
        break;
      case 'cache_benchmarks':
        benchmarkCachePerformance();
        break;
      case 'ai_benchmarks':
        benchmarkAIPerformance();
        break;
      case 'throughput_benchmarks':
        benchmarkThroughput();
        break;
    }

  } catch (error) {
    console.error(`Benchmark error in ${scenario.name}: ${error.message}`);
  }

  sleep(0.1); // Minimal sleep for precise benchmarking
}

/**
 * Benchmark core API endpoint performance
 */
function benchmarkAPIPerformance() {
  const apiEndpoints = [
    { url: `${env.baseUrl}/health`, name: 'health', target: 50 },
    { url: `${env.baseUrl}/agents`, name: 'agents', target: 200, auth: true },
    { url: `${env.baseUrl}/feature-flags`, name: 'feature_flags', target: 100, auth: true },
    { url: `${env.baseUrl}/metrics`, name: 'metrics', target: 300 },
  ];

  apiEndpoints.forEach(endpoint => {
    const startTime = Date.now();

    const options = {
      tags: { name: `api_bench_${endpoint.name}` },
      timeout: '5s',
    };

    if (endpoint.auth) {
      options.headers = authManager.getHeaders();
    }

    const response = http.get(endpoint.url, options);
    const responseTime = Date.now() - startTime;

    const success = check(response, {
      [`API ${endpoint.name} responds`]: (r) => r.status === 200,
      [`API ${endpoint.name} meets target`]: (r) => r.timings.duration < endpoint.target,
      [`API ${endpoint.name} has content`]: (r) => r.body && r.body.length > 10,
    });

    // Record benchmark result
    benchmarkResults.api.push({
      endpoint: endpoint.name,
      responseTime: responseTime,
      target: endpoint.target,
      success: success,
      status: response.status,
      size: response.body ? response.body.length : 0
    });
  });
}

/**
 * Benchmark database query performance
 */
function benchmarkDatabasePerformance() {
  const databaseEndpoints = [
    {
      url: `${env.baseUrl}/agents`,
      name: 'agent_list_query',
      description: 'Agent list database query',
      target: 1000
    },
    {
      url: `${env.baseUrl}/agents/elite-training-strategist`,
      name: 'agent_detail_query',
      description: 'Single agent query',
      target: 500
    },
    // Simulate complex queries by requesting with filters
    {
      url: `${env.baseUrl}/agents?category=training&active=true`,
      name: 'filtered_agent_query',
      description: 'Filtered agent query',
      target: 1500
    }
  ];

  databaseEndpoints.forEach(endpoint => {
    const startTime = Date.now();

    const response = http.get(endpoint.url, {
      headers: authManager.getHeaders(),
      tags: { name: `db_bench_${endpoint.name}` },
      timeout: '10s',
    });

    const queryTime = Date.now() - startTime;

    const success = check(response, {
      [`DB ${endpoint.name} query successful`]: (r) => r.status === 200,
      [`DB ${endpoint.name} meets performance target`]: (r) => r.timings.duration < endpoint.target,
      [`DB ${endpoint.name} returns data`]: (r) => {
        try {
          const data = JSON.parse(r.body);
          return data && (Array.isArray(data) ? data.length > 0 : Object.keys(data).length > 0);
        } catch (e) {
          return false;
        }
      },
    });

    benchmarkResults.database.push({
      query: endpoint.name,
      description: endpoint.description,
      queryTime: queryTime,
      target: endpoint.target,
      success: success,
      status: response.status
    });
  });
}

/**
 * Benchmark cache performance
 */
function benchmarkCachePerformance() {
  // Test cache hits by making repeated requests
  const cacheEndpoints = [
    `${env.baseUrl}/agents`,
    `${env.baseUrl}/feature-flags`,
    `${env.baseUrl}/health`,
  ];

  cacheEndpoints.forEach(url => {
    const endpointName = url.split('/').pop();

    // First request (likely cache miss)
    const firstStartTime = Date.now();
    const firstResponse = http.get(url, {
      headers: authManager.getHeaders(),
      tags: { name: `cache_miss_${endpointName}` },
    });
    const firstResponseTime = Date.now() - firstStartTime;

    sleep(0.1); // Brief pause

    // Second request (should be cache hit)
    const secondStartTime = Date.now();
    const secondResponse = http.get(url, {
      headers: authManager.getHeaders(),
      tags: { name: `cache_hit_${endpointName}` },
    });
    const secondResponseTime = Date.now() - secondStartTime;

    const cacheHit = secondResponseTime < firstResponseTime * 0.5; // Cache hit if 50% faster

    check(null, {
      [`Cache ${endpointName} hit detected`]: () => cacheHit,
      [`Cache ${endpointName} hit fast`]: () => secondResponse.timings.duration < 50,
    });

    benchmarkResults.cache.push({
      endpoint: endpointName,
      firstRequestTime: firstResponseTime,
      secondRequestTime: secondResponseTime,
      cacheHit: cacheHit,
      improvement: firstResponseTime - secondResponseTime,
      improvementPercent: ((firstResponseTime - secondResponseTime) / firstResponseTime) * 100
    });
  });
}

/**
 * Benchmark AI agent performance
 */
function benchmarkAIPerformance() {
  const aiTests = [
    {
      agent: 'elite-training-strategist',
      name: 'BLAZE',
      query: 'Quick workout tip for muscle building',
      complexity: 'simple',
      target: 15000
    },
    {
      agent: 'precision-nutrition-architect',
      name: 'SAGE',
      query: 'Provide a basic meal planning guideline',
      complexity: 'simple',
      target: 15000
    },
    {
      agent: 'elite-training-strategist',
      name: 'BLAZE',
      query: 'Create a detailed 8-week progressive overload training program with exercise variations',
      complexity: 'complex',
      target: 25000
    }
  ];

  aiTests.forEach(test => {
    const startTime = Date.now();

    const payload = JSON.stringify({
      message: test.query,
      conversation_id: `benchmark-${test.complexity}-${Date.now()}`,
      user_context: {
        fitness_level: 'intermediate',
        benchmark_test: true,
        complexity: test.complexity
      }
    });

    const response = http.post(
      `${env.baseUrl}/agents/${test.agent}/chat`,
      payload,
      {
        headers: authManager.getHeaders(),
        tags: { name: `ai_bench_${test.name.toLowerCase()}_${test.complexity}` },
        timeout: '40s',
      }
    );

    const aiResponseTime = Date.now() - startTime;

    const success = check(response, {
      [`AI ${test.name} ${test.complexity} responds`]: (r) => r.status === 200,
      [`AI ${test.name} ${test.complexity} meets target`]: (r) => r.timings.duration < test.target,
      [`AI ${test.name} ${test.complexity} quality`]: (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.response && body.response.length > (test.complexity === 'simple' ? 50 : 200);
        } catch (e) {
          return false;
        }
      },
    });

    recordAIMetrics(response, test.name, startTime);

    benchmarkResults.ai.push({
      agent: test.name,
      complexity: test.complexity,
      query: test.query.substring(0, 50) + '...',
      responseTime: aiResponseTime,
      target: test.target,
      success: success,
      status: response.status
    });
  });
}

/**
 * Benchmark system throughput
 */
function benchmarkThroughput() {
  const throughputEndpoints = [
    `${env.baseUrl}/health`,
    `${env.baseUrl}/agents`,
    `${env.baseUrl}/feature-flags`,
  ];

  const endpoint = throughputEndpoints[Math.floor(Math.random() * throughputEndpoints.length)];
  const endpointName = endpoint.split('/').pop();

  const startTime = Date.now();

  const options = {
    tags: { name: `throughput_${endpointName}` },
    timeout: '5s',
  };

  if (endpoint !== `${env.baseUrl}/health`) {
    options.headers = authManager.getHeaders();
  }

  const response = http.get(endpoint, options);
  const responseTime = Date.now() - startTime;

  check(response, {
    [`Throughput ${endpointName} responds`]: (r) => r.status === 200,
    [`Throughput ${endpointName} fast enough`]: (r) => r.timings.duration < 2000,
  });

  benchmarkResults.throughput.push({
    endpoint: endpointName,
    responseTime: responseTime,
    status: response.status,
    timestamp: Date.now()
  });
}

export function handleSummary(data) {
  return {
    'results/benchmark-summary.html': htmlReport(data),
    'results/benchmark-results.json': JSON.stringify({
      summary: data,
      benchmarks: benchmarkResults,
      timestamp: new Date().toISOString(),
      environment: env,
      performanceTargets: {
        p50_latency_target: 100,
        p95_latency_target: 500,
        p99_latency_target: 1000,
        error_rate_target: 0.01,
        throughput_target: 100,
        cache_hit_rate_target: 0.90,
        ai_response_time_target: 20000,
        ai_quality_target: 0.90
      }
    }, null, 2),
  };
}

export function teardown(data) {
  console.log('🎯 Performance Benchmark Suite Complete');

  // Calculate summary metrics
  const apiResults = benchmarkResults.api;
  const dbResults = benchmarkResults.database;
  const cacheResults = benchmarkResults.cache;
  const aiResults = benchmarkResults.ai;

  console.log('📊 Benchmark Results Summary:');

  if (apiResults.length > 0) {
    const avgApiTime = apiResults.reduce((sum, r) => sum + r.responseTime, 0) / apiResults.length;
    const apiSuccessRate = apiResults.filter(r => r.success).length / apiResults.length;
    console.log(`   API Performance: ${avgApiTime.toFixed(0)}ms avg, ${(apiSuccessRate * 100).toFixed(1)}% success`);
  }

  if (dbResults.length > 0) {
    const avgDbTime = dbResults.reduce((sum, r) => sum + r.queryTime, 0) / dbResults.length;
    const dbSuccessRate = dbResults.filter(r => r.success).length / dbResults.length;
    console.log(`   Database Performance: ${avgDbTime.toFixed(0)}ms avg, ${(dbSuccessRate * 100).toFixed(1)}% success`);
  }

  if (cacheResults.length > 0) {
    const cacheHitRate = cacheResults.filter(r => r.cacheHit).length / cacheResults.length;
    const avgImprovement = cacheResults.reduce((sum, r) => sum + r.improvementPercent, 0) / cacheResults.length;
    console.log(`   Cache Performance: ${(cacheHitRate * 100).toFixed(1)}% hit rate, ${avgImprovement.toFixed(1)}% improvement`);
  }

  if (aiResults.length > 0) {
    const avgAiTime = aiResults.reduce((sum, r) => sum + r.responseTime, 0) / aiResults.length;
    const aiSuccessRate = aiResults.filter(r => r.success).length / aiResults.length;
    console.log(`   AI Performance: ${avgAiTime.toFixed(0)}ms avg, ${(aiSuccessRate * 100).toFixed(1)}% success`);
  }

  console.log('');
  console.log('✅ Detailed benchmark results saved to:');
  console.log('   - results/benchmark-summary.html');
  console.log('   - results/benchmark-results.json');
}
