import { FullConfig } from '@playwright/test';
import { promises as fs } from 'fs';
import path from 'path';

/**
 * Global teardown for Playwright tests
 *
 * Responsibilities:
 * - Cleanup test data
 * - Generate consolidated reports
 * - Performance metrics collection
 * - Resource cleanup
 */
async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting GENESIS E2E Test Teardown...');

  try {
    // Generate consolidated test report
    await generateConsolidatedReport();

    // Clean up temporary files (but preserve results)
    const storageStatePath = path.join(__dirname, 'storage-state.json');
    try {
      await fs.unlink(storageStatePath);
      console.log('✅ Cleaned up authentication storage state');
    } catch (error) {
      // File might not exist, ignore error
    }

    // Performance metrics summary
    await generatePerformanceMetrics();

    console.log('✅ GENESIS E2E Test Teardown completed successfully');
  } catch (error) {
    console.error('❌ Error during teardown:', error);
  }
}

/**
 * Generate consolidated test report with metrics
 */
async function generateConsolidatedReport() {
  try {
    const resultsPath = path.join(__dirname, 'test-results/results.json');
    const resultsExist = await fs.access(resultsPath).then(() => true).catch(() => false);

    if (!resultsExist) {
      console.log('ℹ️  No test results found for consolidation');
      return;
    }

    const resultsContent = await fs.readFile(resultsPath, 'utf-8');
    const results = JSON.parse(resultsContent);

    const summary = {
      timestamp: new Date().toISOString(),
      totalTests: results.stats?.total || 0,
      passed: results.stats?.passed || 0,
      failed: results.stats?.failed || 0,
      skipped: results.stats?.skipped || 0,
      duration: results.stats?.duration || 0,
      projects: results.suites?.map((suite: any) => ({
        name: suite.title,
        tests: suite.specs?.length || 0,
        duration: suite.duration || 0
      })) || []
    };

    await fs.writeFile(
      path.join(__dirname, 'test-results/summary.json'),
      JSON.stringify(summary, null, 2)
    );

    console.log(`✅ Generated consolidated report: ${summary.passed}/${summary.totalTests} tests passed`);
  } catch (error) {
    console.error('❌ Failed to generate consolidated report:', error);
  }
}

/**
 * Generate performance metrics summary
 */
async function generatePerformanceMetrics() {
  try {
    const metricsPath = path.join(__dirname, 'test-results/performance-metrics.json');

    // Placeholder for performance metrics - would be populated by performance tests
    const performanceMetrics = {
      timestamp: new Date().toISOString(),
      pageLoadTimes: {
        landing: null,
        dashboard: null,
        chat: null
      },
      apiResponseTimes: {
        auth: null,
        agents: null,
        chat: null
      },
      aiResponseTimes: {
        training: null,
        nutrition: null,
        general: null
      },
      notes: "Performance metrics collected during E2E test execution"
    };

    await fs.writeFile(metricsPath, JSON.stringify(performanceMetrics, null, 2));
    console.log('✅ Generated performance metrics summary');
  } catch (error) {
    console.error('❌ Failed to generate performance metrics:', error);
  }
}

export default globalTeardown;
