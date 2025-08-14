import { Page, Locator, expect } from '@playwright/test';

/**
 * Comprehensive Test Helper Utilities for GENESIS E2E Testing
 *
 * Provides reusable functions for common testing patterns across
 * the AI agent platform including authentication, chat interactions,
 * and AI response validation.
 */
export class TestHelpers {
  constructor(private page: Page) {}

  /**
   * Wait for network to be idle (useful after AI responses)
   */
  async waitForNetworkIdle(timeout: number = 5000) {
    await this.page.waitForLoadState('networkidle', { timeout });
  }

  /**
   * Wait for an element to be visible and stable
   */
  async waitForStableElement(selector: string, timeout: number = 10000): Promise<Locator> {
    const element = this.page.locator(selector);
    await element.waitFor({ state: 'visible', timeout });

    // Wait for element to be stable (no position changes)
    await this.page.waitForFunction(
      (sel) => {
        const el = document.querySelector(sel);
        if (!el) return false;

        const rect1 = el.getBoundingClientRect();
        return new Promise(resolve => {
          setTimeout(() => {
            const rect2 = el.getBoundingClientRect();
            resolve(rect1.top === rect2.top && rect1.left === rect2.left);
          }, 100);
        });
      },
      selector,
      { timeout: 5000 }
    );

    return element;
  }

  /**
   * Type with realistic human-like delays
   */
  async humanType(selector: string, text: string, delay: number = 100) {
    const element = await this.waitForStableElement(selector);

    // Clear existing content
    await element.clear();

    // Type with variable delays to simulate human typing
    for (const char of text) {
      await element.type(char);
      await this.page.waitForTimeout(delay + Math.random() * 50);
    }
  }

  /**
   * Simulate realistic mouse movement and click
   */
  async humanClick(selector: string) {
    const element = await this.waitForStableElement(selector);
    const box = await element.boundingBox();

    if (!box) throw new Error(`Element ${selector} not found or not visible`);

    // Move to element gradually
    const steps = 3;
    const currentMouse = await this.page.evaluate(() => ({ x: 0, y: 0 }));

    for (let i = 1; i <= steps; i++) {
      const progress = i / steps;
      const x = currentMouse.x + (box.x + box.width / 2 - currentMouse.x) * progress;
      const y = currentMouse.y + (box.y + box.height / 2 - currentMouse.y) * progress;

      await this.page.mouse.move(x, y);
      await this.page.waitForTimeout(50);
    }

    await element.click();
  }

  /**
   * Wait for AI response with timeout and validation
   */
  async waitForAIResponse(
    messageSelector: string = '[data-testid="chat-message"]:last-child',
    timeout: number = 30000
  ): Promise<string> {
    // Wait for loading indicator to appear
    await this.page.waitForSelector('[data-testid="ai-loading"]', {
      state: 'visible',
      timeout: 5000
    }).catch(() => {
      // Loading indicator might not appear for fast responses
    });

    // Wait for loading to disappear
    await this.page.waitForSelector('[data-testid="ai-loading"]', {
      state: 'hidden',
      timeout
    }).catch(() => {
      // Continue if loading indicator doesn't exist
    });

    // Wait for actual response message
    const messageElement = await this.waitForStableElement(messageSelector, timeout);
    const responseText = await messageElement.textContent();

    if (!responseText || responseText.trim().length === 0) {
      throw new Error('AI response was empty or not found');
    }

    return responseText.trim();
  }

  /**
   * Validate AI response contains expected elements
   */
  async validateAIResponse(responseText: string, expectedKeywords: string[] = []): Promise<boolean> {
    // Basic validation
    if (responseText.length < 10) {
      throw new Error(`AI response too short: "${responseText}"`);
    }

    // Check for error patterns
    const errorPatterns = [
      /error/i,
      /sorry, i (can't|cannot)/i,
      /something went wrong/i,
      /internal server error/i
    ];

    const hasError = errorPatterns.some(pattern => pattern.test(responseText));
    if (hasError) {
      throw new Error(`AI response contains error: "${responseText}"`);
    }

    // Check for expected keywords if provided
    if (expectedKeywords.length > 0) {
      const hasKeywords = expectedKeywords.some(keyword =>
        responseText.toLowerCase().includes(keyword.toLowerCase())
      );

      if (!hasKeywords) {
        console.warn(`AI response missing expected keywords: ${expectedKeywords.join(', ')}`);
        console.warn(`Response: "${responseText.substring(0, 100)}..."`);
        return false;
      }
    }

    return true;
  }

  /**
   * Take screenshot with timestamp and context
   */
  async takeContextualScreenshot(context: string, fullPage: boolean = false) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const fileName = `${context}-${timestamp}.png`;

    await this.page.screenshot({
      path: `test-results/screenshots/${fileName}`,
      fullPage
    });

    return fileName;
  }

  /**
   * Check for console errors and warnings
   */
  async checkConsoleErrors(): Promise<{ errors: string[], warnings: string[] }> {
    const errors: string[] = [];
    const warnings: string[] = [];

    this.page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      } else if (msg.type() === 'warning') {
        warnings.push(msg.text());
      }
    });

    return { errors, warnings };
  }

  /**
   * Monitor network requests for specific patterns
   */
  async monitorNetworkRequests(pattern: RegExp, timeout: number = 10000): Promise<any[]> {
    const requests: any[] = [];

    const requestHandler = (request: any) => {
      if (pattern.test(request.url())) {
        requests.push({
          url: request.url(),
          method: request.method(),
          timestamp: Date.now()
        });
      }
    };

    this.page.on('request', requestHandler);

    // Wait for specified timeout
    await this.page.waitForTimeout(timeout);

    this.page.off('request', requestHandler);

    return requests;
  }

  /**
   * Simulate voice interaction (for voice testing)
   */
  async simulateVoiceInput(text: string) {
    // This would integrate with actual voice testing tools
    // For now, simulate by triggering voice button and typing
    await this.humanClick('[data-testid="voice-button"]');
    await this.page.waitForTimeout(500);

    // Simulate voice input result
    await this.page.evaluate((voiceText) => {
      // Trigger voice input event with text
      window.dispatchEvent(new CustomEvent('voice-input', {
        detail: { text: voiceText }
      }));
    }, text);
  }

  /**
   * Wait for streaming response to complete
   */
  async waitForStreamingComplete(
    streamingSelector: string = '[data-testid="streaming-message"]',
    timeout: number = 60000
  ) {
    // Wait for streaming to start
    await this.page.waitForSelector(streamingSelector, {
      state: 'visible',
      timeout: 5000
    });

    // Wait for streaming to complete (element should have final content)
    await this.page.waitForFunction(
      (selector) => {
        const element = document.querySelector(selector);
        if (!element) return false;

        // Check if streaming cursor/indicator is gone
        const hasCursor = element.querySelector('.streaming-cursor') !== null;
        const hasContent = element.textContent && element.textContent.length > 10;

        return !hasCursor && hasContent;
      },
      streamingSelector,
      { timeout }
    );
  }

  /**
   * Validate page performance metrics
   */
  async validatePagePerformance(): Promise<{
    loadTime: number,
    domContentLoaded: number,
    firstContentfulPaint: number | null
  }> {
    const performanceMetrics = await this.page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;

      return {
        loadTime: navigation.loadEventEnd - navigation.loadEventStart,
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        firstContentfulPaint: null // Would need additional setup for FCP
      };
    });

    // Validate reasonable load times
    if (performanceMetrics.loadTime > 5000) {
      console.warn(`Slow page load detected: ${performanceMetrics.loadTime}ms`);
    }

    return performanceMetrics;
  }
}

/**
 * Semantic similarity validation for AI responses
 */
export class SemanticValidator {
  /**
   * Simple semantic similarity check using keyword matching
   * In production, this would use embeddings/ML models
   */
  static validateSimilarity(response: string, expectedConcepts: string[]): number {
    const responseWords = response.toLowerCase().split(/\s+/);
    const conceptWords = expectedConcepts.flatMap(concept =>
      concept.toLowerCase().split(/\s+/)
    );

    const matches = conceptWords.filter(word =>
      responseWords.some(responseWord =>
        responseWord.includes(word) || word.includes(responseWord)
      )
    );

    return matches.length / conceptWords.length;
  }

  /**
   * Validate training-related response quality
   */
  static validateTrainingResponse(response: string): {
    isValid: boolean,
    score: number,
    issues: string[]
  } {
    const trainingKeywords = [
      'exercise', 'workout', 'training', 'rep', 'set', 'muscle',
      'strength', 'cardio', 'fitness', 'routine', 'program'
    ];

    const score = this.validateSimilarity(response, trainingKeywords);
    const issues: string[] = [];

    if (score < 0.3) {
      issues.push('Response lacks training-specific terminology');
    }

    if (response.length < 100) {
      issues.push('Response is too brief for comprehensive training advice');
    }

    if (!/\b\d+\b/.test(response)) {
      issues.push('Response lacks specific numbers (sets, reps, duration)');
    }

    return {
      isValid: score >= 0.3 && issues.length === 0,
      score,
      issues
    };
  }

  /**
   * Validate nutrition-related response quality
   */
  static validateNutritionResponse(response: string): {
    isValid: boolean,
    score: number,
    issues: string[]
  } {
    const nutritionKeywords = [
      'nutrition', 'diet', 'meal', 'protein', 'carbs', 'calories',
      'vitamins', 'nutrients', 'food', 'eating', 'macro'
    ];

    const score = this.validateSimilarity(response, nutritionKeywords);
    const issues: string[] = [];

    if (score < 0.3) {
      issues.push('Response lacks nutrition-specific terminology');
    }

    if (response.length < 100) {
      issues.push('Response is too brief for comprehensive nutrition advice');
    }

    return {
      isValid: score >= 0.3 && issues.length === 0,
      score,
      issues
    };
  }
}
