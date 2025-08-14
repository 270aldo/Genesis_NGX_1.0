import { chromium, FullConfig } from '@playwright/test';
import dotenv from 'dotenv';
import { promises as fs } from 'fs';
import path from 'path';

// Load environment variables
dotenv.config();

/**
 * Global setup for Playwright tests
 *
 * Responsibilities:
 * - Environment validation
 * - Test data preparation
 * - Authentication setup
 * - Database seeding (if needed)
 * - Service health checks
 */
async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting GENESIS E2E Test Setup...');

  // Validate required environment variables
  const requiredEnvVars = [
    'E2E_BASE_URL',
    'E2E_API_URL',
    'E2E_TEST_EMAIL',
    'E2E_TEST_PASSWORD'
  ];

  const missingEnvVars = requiredEnvVars.filter(envVar => !process.env[envVar]);
  if (missingEnvVars.length > 0) {
    console.error(`❌ Missing required environment variables: ${missingEnvVars.join(', ')}`);
    process.exit(1);
  }

  // Create test results directory
  const testResultsDir = path.join(__dirname, 'test-results');
  await fs.mkdir(testResultsDir, { recursive: true });

  // Health check for backend API
  try {
    const response = await fetch(`${process.env.E2E_API_URL}/health`);
    if (!response.ok) {
      throw new Error(`Backend health check failed: ${response.status}`);
    }
    console.log('✅ Backend API health check passed');
  } catch (error) {
    console.error('❌ Backend API health check failed:', error);
    // Don't exit - allow tests to handle service availability
  }

  // Setup authenticated browser context for tests that need it
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Navigate to login page and authenticate
    await page.goto(`${process.env.E2E_BASE_URL}/signin`);
    await page.fill('[data-testid="email-input"]', process.env.E2E_TEST_EMAIL!);
    await page.fill('[data-testid="password-input"]', process.env.E2E_TEST_PASSWORD!);
    await page.click('[data-testid="signin-button"]');

    // Wait for successful authentication (dashboard redirect)
    await page.waitForURL('**/dashboard', { timeout: 10000 });

    // Save authenticated state for tests
    await context.storageState({
      path: path.join(__dirname, 'storage-state.json')
    });

    console.log('✅ Authentication setup completed');
  } catch (error) {
    console.warn('⚠️  Authentication setup failed - some tests may not work:', error);
    // Don't exit - allow tests to handle authentication independently
  } finally {
    await browser.close();
  }

  // Initialize test data files
  const testDataDir = path.join(__dirname, 'test-data');
  await fs.mkdir(testDataDir, { recursive: true });

  // Create sample test data for AI agent testing
  const agentTestData = {
    trainingQueries: [
      "I want to build muscle mass, can you create a workout plan?",
      "I'm a beginner, what's a good starting routine?",
      "I have knee problems, what exercises should I avoid?",
      "Create a 30-day transformation program"
    ],
    nutritionQueries: [
      "I'm vegetarian, help me plan my meals",
      "What should I eat to lose weight?",
      "I want to gain muscle, what's the best diet?",
      "Create a meal plan for diabetes management"
    ],
    progressQueries: [
      "Track my workout progress",
      "Show me my fitness metrics",
      "How am I doing compared to my goals?",
      "Generate a progress report"
    ]
  };

  await fs.writeFile(
    path.join(testDataDir, 'agent-queries.json'),
    JSON.stringify(agentTestData, null, 2)
  );

  // Create visual regression baseline directory
  const visualBaselineDir = path.join(__dirname, 'tests/visual/baselines');
  await fs.mkdir(visualBaselineDir, { recursive: true });

  console.log('✅ GENESIS E2E Test Setup completed successfully');
}

export default globalSetup;
