import { defineConfig, devices } from '@playwright/test';
import dotenv from 'dotenv';
import path from 'path';

// Load environment variables
dotenv.config({ path: path.resolve(__dirname, '.env') });

/**
 * Comprehensive Playwright Configuration for GENESIS E2E Testing
 *
 * Features:
 * - Cross-browser testing (Chrome, Firefox, Safari)
 * - Mobile device testing (Chrome Mobile, Safari Mobile)
 * - Visual regression testing
 * - API testing
 * - Parallel execution
 * - Test retry and timeout configuration
 * - Screenshot and video recording on failures
 */
export default defineConfig({
  // Test directory structure
  testDir: './tests',

  // Global test timeout (30 seconds)
  timeout: 30 * 1000,

  // Test execution configuration
  expect: {
    // Timeout for expect() assertions (10 seconds)
    timeout: 10 * 1000,
    // Visual comparison threshold (5% pixel difference)
    threshold: 0.05,
  },

  // Retry failed tests
  retries: process.env.CI ? 3 : 1,

  // Parallel execution (limit based on CI vs local)
  workers: process.env.CI ? 4 : undefined,

  // Reporter configuration
  reporter: [
    ['html', {
      outputFolder: 'test-results/html-report',
      open: process.env.CI ? 'never' : 'on-failure'
    }],
    ['json', {
      outputFile: 'test-results/results.json'
    }],
    ['junit', {
      outputFile: 'test-results/junit.xml'
    }],
    ['github'],
    ['list']
  ],

  // Global test configuration
  use: {
    // Base URL for tests
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:5173',

    // API endpoint for backend tests
    extraHTTPHeaders: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },

    // Browser context settings
    ignoreHTTPSErrors: true,

    // Screenshot settings
    screenshot: 'only-on-failure',

    // Video recording
    video: 'retain-on-failure',

    // Trace collection (for debugging)
    trace: 'retain-on-failure',

    // Action timeout (10 seconds)
    actionTimeout: 10 * 1000,

    // Navigation timeout (30 seconds)
    navigationTimeout: 30 * 1000,
  },

  // Output directory for artifacts
  outputDir: 'test-results/artifacts',

  // Project configurations for different browsers and scenarios
  projects: [
    // Desktop Browsers
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 },
      },
    },
    {
      name: 'firefox',
      use: {
        ...devices['Desktop Firefox'],
        viewport: { width: 1920, height: 1080 },
      },
    },
    {
      name: 'webkit',
      use: {
        ...devices['Desktop Safari'],
        viewport: { width: 1920, height: 1080 },
      },
    },

    // Mobile Browsers
    {
      name: 'mobile-chrome',
      use: {
        ...devices['Pixel 5'],
      },
    },
    {
      name: 'mobile-safari',
      use: {
        ...devices['iPhone 13'],
      },
    },

    // Tablet Testing
    {
      name: 'tablet',
      use: {
        ...devices['iPad Pro'],
      },
    },

    // Visual Regression Testing
    {
      name: 'visual-regression',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 },
      },
      testMatch: '**/visual/**/*.spec.ts',
    },

    // API Testing (headless)
    {
      name: 'api-tests',
      use: {
        baseURL: process.env.E2E_API_URL || 'http://localhost:8000',
      },
      testMatch: '**/api/**/*.spec.ts',
    },

    // Performance Testing
    {
      name: 'performance',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 },
      },
      testMatch: '**/performance/**/*.spec.ts',
    },

    // AI Agent Testing (extended timeouts for LLM responses)
    {
      name: 'ai-agents',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 },
        actionTimeout: 30 * 1000, // 30s for AI responses
        navigationTimeout: 60 * 1000, // 60s for complex AI operations
      },
      timeout: 120 * 1000, // 2 minutes for AI test scenarios
      testMatch: '**/agents/**/*.spec.ts',
    },
  ],

  // Global setup and teardown
  globalSetup: require.resolve('./global-setup'),
  globalTeardown: require.resolve('./global-teardown'),

  // Web Server configuration (auto-start frontend and backend for tests)
  webServer: [
    {
      command: 'cd ../frontend && npm run build && npm run preview',
      port: 5173,
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
    },
    {
      command: 'cd ../backend && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000',
      port: 8000,
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
    }
  ],
});
