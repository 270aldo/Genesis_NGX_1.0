import { test, expect } from '@playwright/test';
import { AuthPage } from '../../pages/auth-page';
import { ChatPage } from '../../pages/chat-page';
import { TestHelpers } from '../../utils/test-helpers';

/**
 * Complete User Onboarding Journey Tests
 *
 * Tests the full user onboarding experience from signup to first AI interaction.
 * This represents one of the most critical user journeys for GENESIS.
 */

test.describe('Complete User Onboarding Journey', () => {
  let authPage: AuthPage;
  let chatPage: ChatPage;
  let helpers: TestHelpers;

  // Test data for new user
  const newUser = {
    firstName: 'John',
    lastName: 'Doe',
    email: `test-user-${Date.now()}@example.com`,
    password: 'TestPassword123!'
  };

  test.beforeEach(async ({ page }) => {
    authPage = new AuthPage(page);
    chatPage = new ChatPage(page);
    helpers = new TestHelpers(page);

    // Start from landing page
    await page.goto('/');
  });

  test('Complete onboarding flow - signup to first AI interaction', async ({ page }) => {
    // Step 1: Navigate to signup from landing page
    await test.step('Navigate to signup', async () => {
      const signupButton = page.locator('[data-testid="get-started-button"], [data-testid="signup-button"]').first();
      await signupButton.click();

      await page.waitForURL('**/signup');
      expect(page.url()).toContain('/signup');
    });

    // Step 2: Complete user registration
    await test.step('Complete user registration', async () => {
      await authPage.fillSignupForm(newUser);
      await authPage.submitSignupForm();

      // Wait for successful signup
      await authPage.waitForSignupComplete();

      // Should be redirected to dashboard or onboarding
      const currentUrl = page.url();
      expect(currentUrl).toMatch(/\/(dashboard|onboarding|chat)/);
    });

    // Step 3: Complete profile setup (if onboarding flow exists)
    await test.step('Complete profile setup', async () => {
      // Check if onboarding flow exists
      const onboardingExists = await page.locator('[data-testid="onboarding-container"]').isVisible().catch(() => false);

      if (onboardingExists) {
        // Fill fitness goals
        const fitnessGoals = page.locator('[data-testid="fitness-goals"]');
        if (await fitnessGoals.isVisible()) {
          await page.locator('[data-testid="goal-muscle-gain"]').click();
          await page.locator('[data-testid="goal-general-fitness"]').click();
        }

        // Set fitness level
        const fitnessLevel = page.locator('[data-testid="fitness-level-intermediate"]');
        if (await fitnessLevel.isVisible()) {
          await fitnessLevel.click();
        }

        // Set available equipment
        const equipment = page.locator('[data-testid="equipment-dumbbells"]');
        if (await equipment.isVisible()) {
          await equipment.click();
        }

        // Complete onboarding
        const completeButton = page.locator('[data-testid="complete-onboarding"]');
        if (await completeButton.isVisible()) {
          await completeButton.click();
        }

        // Wait for onboarding completion
        await page.waitForURL('**/dashboard', { timeout: 10000 });
      }
    });

    // Step 4: Navigate to chat interface
    await test.step('Navigate to chat interface', async () => {
      // If not already in chat, navigate there
      if (!page.url().includes('/chat')) {
        const chatNavButton = page.locator('[data-testid="nav-chat"], [data-testid="start-chat-button"]').first();
        await chatNavButton.click();

        await page.waitForURL('**/chat');
      }

      await chatPage.waitForChatLoad();
      expect(page.url()).toContain('/chat');
    });

    // Step 5: Interact with agent selector
    await test.step('Explore available agents', async () => {
      // Check that agents are available
      const availableAgents = await chatPage.getAvailableAgents();
      expect(availableAgents.length).toBeGreaterThan(0);

      // Should include core agents
      const expectedAgents = ['elite-training-strategist', 'precision-nutrition-architect'];
      const hasExpectedAgents = expectedAgents.some(agent =>
        availableAgents.some(available => available.includes(agent))
      );
      expect(hasExpectedAgents).toBe(true);

      // Take screenshot of agent selection
      await helpers.takeContextualScreenshot('agent-selection');
    });

    // Step 6: First interaction with BLAZE (training agent)
    await test.step('First interaction with BLAZE', async () => {
      // Select BLAZE for training guidance
      await chatPage.selectAgent('elite-training-strategist');

      // Wait for agent to be ready
      await chatPage.waitForAgentOnline('elite-training-strategist');

      // Send first message
      const firstQuery = "Hi! I'm new here. I want to build muscle and get stronger. Can you help me create a workout plan?";
      await chatPage.sendMessage(firstQuery);

      // Validate response
      const response = await chatPage.getLastAgentMessage();
      expect(response.length).toBeGreaterThan(50);

      // Validate response quality
      const isValidResponse = await chatPage.validateAgentResponse(
        firstQuery,
        response,
        'BLAZE',
        ['workout', 'muscle', 'strength', 'plan']
      );
      expect(isValidResponse).toBe(true);

      // Take screenshot of first interaction
      await helpers.takeContextualScreenshot('first-blaze-interaction');
    });

    // Step 7: Follow-up question to test conversation flow
    await test.step('Follow-up conversation', async () => {
      const followUpQuery = "I can work out 3 days a week and I'm a complete beginner. What specific exercises should I start with?";
      await chatPage.sendMessage(followUpQuery);

      const response = await chatPage.getLastAgentMessage();
      expect(response.length).toBeGreaterThan(30);

      // Should maintain context and provide beginner-appropriate advice
      const responseLower = response.toLowerCase();
      const hasBeginnerContext = ['beginner', 'start', 'basic', 'simple'].some(word =>
        responseLower.includes(word)
      );
      expect(hasBeginnerContext).toBe(true);

      // Should mention specific exercises
      const hasSpecificExercises = ['push-up', 'squat', 'plank', 'row'].some(exercise =>
        responseLower.includes(exercise)
      );
      expect(hasSpecificExercises).toBe(true);
    });

    // Step 8: Test agent switching (SAGE for nutrition)
    await test.step('Switch to nutrition agent (SAGE)', async () => {
      await chatPage.selectAgent('precision-nutrition-architect');
      await chatPage.waitForAgentOnline('precision-nutrition-architect');

      const nutritionQuery = "Now that I have a workout plan, what should I eat to support muscle growth?";
      await chatPage.sendMessage(nutritionQuery);

      const response = await chatPage.getLastAgentMessage();
      expect(response.length).toBeGreaterThan(50);

      // Validate nutrition-specific response
      const isValidNutritionResponse = await chatPage.validateAgentResponse(
        nutritionQuery,
        response,
        'SAGE',
        ['protein', 'nutrition', 'muscle', 'calories']
      );
      expect(isValidNutritionResponse).toBe(true);
    });

    // Step 9: Test quick actions (if available)
    await test.step('Explore quick actions', async () => {
      const quickActions = await chatPage.getAvailableQuickActions();

      if (quickActions.length > 0) {
        // Use first available quick action
        await chatPage.useQuickAction(quickActions[0]);

        // Should trigger some response or action
        await helpers.waitForNetworkIdle();

        // Take screenshot of quick actions
        await helpers.takeContextualScreenshot('quick-actions-used');
      }
    });

    // Step 10: Test voice interaction (if enabled)
    await test.step('Test voice capabilities', async () => {
      const voiceButton = page.locator('[data-testid="voice-button"]');
      const isVoiceAvailable = await voiceButton.isVisible();

      if (isVoiceAvailable) {
        // Test voice interface opening
        await chatPage.simulateVoiceInput("What's my next workout?");

        // Should process voice input and respond
        const response = await chatPage.getLastAgentMessage();
        expect(response.length).toBeGreaterThan(20);

        // Take screenshot of voice interface
        await helpers.takeContextualScreenshot('voice-interaction');
      }
    });

    // Step 11: Validate overall experience
    await test.step('Validate complete onboarding experience', async () => {
      // Check conversation history
      const messages = await chatPage.getAllMessages();
      expect(messages.length).toBeGreaterThan(4); // At least 2 exchanges

      // Validate message types
      const userMessages = messages.filter(m => m.type === 'user');
      const agentMessages = messages.filter(m => m.type === 'agent');

      expect(userMessages.length).toBeGreaterThan(2);
      expect(agentMessages.length).toBeGreaterThan(2);

      // All agent messages should be substantial
      const substantialResponses = agentMessages.filter(m => m.content.length > 30);
      expect(substantialResponses.length).toBe(agentMessages.length);

      // Take final screenshot
      await helpers.takeContextualScreenshot('onboarding-complete');

      // Validate no critical errors in console
      const { errors } = await helpers.checkConsoleErrors();
      const criticalErrors = errors.filter(error =>
        !error.includes('favicon') && !error.includes('sourcemap')
      );
      expect(criticalErrors.length).toBe(0);
    });

    // Step 12: Test session persistence
    await test.step('Test session persistence', async () => {
      // Refresh page
      await page.reload();
      await chatPage.waitForChatLoad();

      // Should still be authenticated
      expect(await page.locator('[data-testid="user-menu"]').isVisible()).toBe(true);

      // Conversation should be preserved
      const messagesAfterRefresh = await chatPage.getAllMessages();
      expect(messagesAfterRefresh.length).toBeGreaterThan(0);
    });
  });

  test('Onboarding with error recovery', async ({ page }) => {
    // Test onboarding resilience with network issues
    await test.step('Signup with simulated network delay', async () => {
      // Add network delay to simulate slow connection
      await page.route('**/auth/signup', async route => {
        await new Promise(resolve => setTimeout(resolve, 2000));
        await route.continue();
      });

      await page.goto('/signup');
      await authPage.fillSignupForm(newUser);
      await authPage.submitSignupForm();

      // Should still complete successfully
      await authPage.waitForSignupComplete(15000); // Extended timeout
    });

    await test.step('Chat with agent unavailable scenario', async () => {
      // Navigate to chat
      await page.goto('/chat');
      await chatPage.waitForChatLoad();

      // Simulate agent unavailable
      await page.route('**/agents/*/chat', async route => {
        await route.fulfill({ status: 503, body: 'Service Unavailable' });
      });

      await chatPage.selectAgent('elite-training-strategist');
      await chatPage.sendMessage('Test message');

      // Should show appropriate error handling
      const errorMessage = page.locator('[data-testid="error-message"], [data-testid="agent-unavailable"]');
      await expect(errorMessage).toBeVisible({ timeout: 10000 });
    });
  });

  test('Mobile onboarding experience', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    await test.step('Mobile signup process', async () => {
      await page.goto('/signup');

      // Check mobile optimization
      const layoutIssues = await chatPage.validateChatLayout();
      expect(layoutIssues.issues.length).toBe(0);

      await authPage.fillSignupForm(newUser);
      await authPage.submitSignupForm();
      await authPage.waitForSignupComplete();
    });

    await test.step('Mobile chat interaction', async () => {
      await page.goto('/chat');
      await chatPage.waitForChatLoad();

      // Mobile-specific UI elements
      const mobileMenu = page.locator('[data-testid="mobile-menu-button"]');
      if (await mobileMenu.isVisible()) {
        await mobileMenu.click();
      }

      await chatPage.selectAgent('elite-training-strategist');
      await chatPage.sendMessage('Mobile test message');

      const response = await chatPage.getLastAgentMessage();
      expect(response.length).toBeGreaterThan(20);

      // Take mobile screenshot
      await helpers.takeContextualScreenshot('mobile-chat');
    });
  });

  test('Accessibility during onboarding', async ({ page }) => {
    await test.step('Keyboard navigation through signup', async () => {
      await page.goto('/signup');

      // Test tab navigation
      await page.keyboard.press('Tab'); // First name
      await page.keyboard.type(newUser.firstName);

      await page.keyboard.press('Tab'); // Last name
      await page.keyboard.type(newUser.lastName);

      await page.keyboard.press('Tab'); // Email
      await page.keyboard.type(newUser.email);

      await page.keyboard.press('Tab'); // Password
      await page.keyboard.type(newUser.password);

      await page.keyboard.press('Tab'); // Confirm password
      await page.keyboard.type(newUser.password);

      await page.keyboard.press('Tab'); // Terms checkbox
      await page.keyboard.press('Space');

      await page.keyboard.press('Tab'); // Submit button
      await page.keyboard.press('Enter');

      await authPage.waitForSignupComplete();
    });

    await test.step('Screen reader compatibility in chat', async () => {
      await page.goto('/chat');
      await chatPage.waitForChatLoad();

      // Check for proper ARIA labels and roles
      const messageInput = page.locator('[data-testid="message-input"]');
      const ariaLabel = await messageInput.getAttribute('aria-label');
      expect(ariaLabel).toBeTruthy();

      const sendButton = page.locator('[data-testid="send-button"]');
      const buttonRole = await sendButton.getAttribute('role');
      expect(buttonRole === 'button' || await sendButton.evaluate(el => el.tagName) === 'BUTTON').toBe(true);
    });
  });

  // Performance benchmarks for onboarding
  test('Onboarding performance benchmarks', async ({ page }) => {
    const performanceMetrics = [];

    await test.step('Measure signup page load', async () => {
      const startTime = Date.now();
      await page.goto('/signup');
      await page.waitForLoadState('networkidle');
      const loadTime = Date.now() - startTime;

      expect(loadTime).toBeLessThan(3000); // 3 seconds max
      performanceMetrics.push({ page: 'signup', loadTime });
    });

    await test.step('Measure chat interface load', async () => {
      const startTime = Date.now();
      await page.goto('/chat');
      await chatPage.waitForChatLoad();
      const loadTime = Date.now() - startTime;

      expect(loadTime).toBeLessThan(5000); // 5 seconds max for chat
      performanceMetrics.push({ page: 'chat', loadTime });
    });

    await test.step('Measure AI response time', async () => {
      await chatPage.selectAgent('elite-training-strategist');

      const timing = await chatPage.measureResponseTime('Quick performance test message');
      expect(timing.totalTime).toBeLessThan(30000); // 30 seconds max

      performanceMetrics.push({
        operation: 'ai_response',
        totalTime: timing.totalTime,
        receiveTime: timing.receiveTime
      });
    });

    // Log performance metrics for monitoring
    console.log('Onboarding Performance Metrics:', JSON.stringify(performanceMetrics, null, 2));
  });
});
