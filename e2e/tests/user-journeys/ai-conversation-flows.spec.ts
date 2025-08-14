import { test, expect } from '@playwright/test';
import { ChatPage } from '../../pages/chat-page';
import { AuthPage } from '../../pages/auth-page';
import { TestHelpers, SemanticValidator } from '../../utils/test-helpers';

/**
 * AI Conversation Flow Tests
 *
 * Tests comprehensive AI conversation scenarios including:
 * - Single agent deep conversations
 * - Multi-agent coordination
 * - Context preservation
 * - Error handling and recovery
 * - Voice interactions
 */

test.describe('AI Conversation Flows', () => {
  let chatPage: ChatPage;
  let authPage: AuthPage;
  let helpers: TestHelpers;

  test.beforeEach(async ({ page }) => {
    chatPage = new ChatPage(page);
    authPage = new AuthPage(page);
    helpers = new TestHelpers(page);

    // Authenticate user (use storage state if available)
    const storageStatePath = './storage-state.json';
    try {
      await page.context().addInitScript(() => {
        // Set authenticated state
        localStorage.setItem('auth-token', 'test-token-for-e2e');
        localStorage.setItem('user-authenticated', 'true');
      });
      await page.goto('/chat');
      await chatPage.waitForChatLoad();
    } catch {
      // Fallback to manual authentication
      await authPage.goToSignin();
      await authPage.signin(
        process.env.E2E_TEST_EMAIL || 'test@genesis.com',
        process.env.E2E_TEST_PASSWORD || 'TestPassword123!'
      );
      await page.waitForURL('**/chat');
      await chatPage.waitForChatLoad();
    }
  });

  test.describe('BLAZE Training Agent Conversations', () => {
    test.beforeEach(async () => {
      await chatPage.selectAgent('elite-training-strategist');
      await chatPage.waitForAgentOnline('elite-training-strategist');
    });

    test('Complete muscle building consultation', async () => {
      const conversation = [
        {
          query: "I want to build muscle mass. I'm 25 years old, weigh 70kg, and I'm a complete beginner.",
          expectedKeywords: ['beginner', 'muscle', 'program', 'compound', 'progressive'],
          minResponseLength: 150
        },
        {
          query: "I can only work out 3 days a week. What split should I use?",
          expectedKeywords: ['full body', 'split', '3 days', 'frequency'],
          minResponseLength: 100
        },
        {
          query: "I have dumbbells at home but no barbell. Can you modify the program?",
          expectedKeywords: ['dumbbells', 'home', 'alternative', 'modification'],
          minResponseLength: 120
        },
        {
          query: "How do I know if I'm progressing? What should I track?",
          expectedKeywords: ['progress', 'track', 'weights', 'reps', 'strength'],
          minResponseLength: 100
        }
      ];

      for (let i = 0; i < conversation.length; i++) {
        const step = conversation[i];

        await test.step(`Conversation step ${i + 1}: ${step.query.substring(0, 50)}...`, async () => {
          await chatPage.sendMessage(step.query);
          const response = await chatPage.getLastAgentMessage();

          // Validate response quality
          expect(response.length).toBeGreaterThan(step.minResponseLength);

          const isValidResponse = await chatPage.validateAgentResponse(
            step.query,
            response,
            'BLAZE',
            step.expectedKeywords
          );
          expect(isValidResponse).toBe(true);

          // Validate semantic appropriateness
          const responseLower = response.toLowerCase();
          const keywordMatches = step.expectedKeywords.filter(keyword =>
            responseLower.includes(keyword)
          );
          expect(keywordMatches.length).toBeGreaterThan(step.expectedKeywords.length * 0.4);
        });
      }

      // Validate conversation context preservation
      await test.step('Validate context preservation', async () => {
        const contextQuery = "Based on everything we've discussed, can you summarize my program?";
        await chatPage.sendMessage(contextQuery);
        const summary = await chatPage.getLastAgentMessage();

        // Should reference previous conversation elements
        const summaryLower = summary.toLowerCase();
        expect(summaryLower).toMatch(/3 days|three days/);
        expect(summaryLower).toMatch(/dumbbells|home/);
        expect(summaryLower).toMatch(/beginner|starting/);
      });
    });

    test('Injury modification and safety guidance', async () => {
      const injuryScenario = [
        {
          query: "I have a previous knee injury. What exercises should I avoid?",
          expectedKeywords: ['knee', 'avoid', 'injury', 'safe', 'alternative'],
          safetyCheck: true
        },
        {
          query: "What knee-friendly leg exercises can I do instead?",
          expectedKeywords: ['leg', 'alternative', 'knee-friendly', 'safe']
        },
        {
          query: "How do I know if an exercise is causing problems?",
          expectedKeywords: ['pain', 'stop', 'listen', 'body', 'warning']
        }
      ];

      for (const step of injuryScenario) {
        await chatPage.sendMessage(step.query);
        const response = await chatPage.getLastAgentMessage();

        expect(response.length).toBeGreaterThan(80);

        if (step.safetyCheck) {
          // Should include safety disclaimers for injury-related queries
          const responseLower = response.toLowerCase();
          const hasSafetyAdvice = [
            'consult', 'doctor', 'physical therapist', 'medical', 'professional'
          ].some(term => responseLower.includes(term));

          expect(hasSafetyAdvice).toBe(true);
        }
      }
    });

    test('Advanced training program progression', async () => {
      await test.step('Simulate experienced user consultation', async () => {
        const advancedQuery = "I've been lifting for 2 years. Current bench: 100kg, squat: 140kg, deadlift: 160kg. I want to break through a strength plateau.";

        await chatPage.sendMessage(advancedQuery);
        const response = await chatPage.getLastAgentMessage();

        expect(response.length).toBeGreaterThan(150);

        // Should address advanced concepts
        const responseLower = response.toLowerCase();
        const hasAdvancedConcepts = [
          'plateau', 'periodization', 'deload', 'intensity', 'volume', 'recovery'
        ].some(concept => responseLower.includes(concept));

        expect(hasAdvancedConcepts).toBe(true);
      });
    });
  });

  test.describe('SAGE Nutrition Agent Conversations', () => {
    test.beforeEach(async () => {
      await chatPage.selectAgent('precision-nutrition-architect');
      await chatPage.waitForAgentOnline('precision-nutrition-architect');
    });

    test('Comprehensive nutrition consultation', async () => {
      const nutritionFlow = [
        {
          query: "I'm vegetarian and want to lose 5kg while maintaining muscle. I weigh 75kg and exercise 4 times a week.",
          expectedKeywords: ['vegetarian', 'protein', 'deficit', 'muscle', 'calories']
        },
        {
          query: "What should my daily calorie and macro targets be?",
          expectedKeywords: ['calories', 'protein', 'carbs', 'fat', 'macro']
        },
        {
          query: "Can you suggest specific vegetarian protein sources?",
          expectedKeywords: ['protein', 'vegetarian', 'legumes', 'tofu', 'quinoa']
        },
        {
          query: "What should I eat before and after workouts?",
          expectedKeywords: ['pre-workout', 'post-workout', 'timing', 'recovery']
        }
      ];

      for (const step of nutritionFlow) {
        await chatPage.sendMessage(step.query);
        const response = await chatPage.getLastAgentMessage();

        expect(response.length).toBeGreaterThan(100);

        const isValidResponse = await chatPage.validateAgentResponse(
          step.query,
          response,
          'SAGE',
          step.expectedKeywords
        );
        expect(isValidResponse).toBe(true);
      }
    });

    test('Medical condition nutrition guidance', async () => {
      const medicalQuery = "I have Type 2 diabetes. How should this affect my meal planning?";

      await chatPage.sendMessage(medicalQuery);
      const response = await chatPage.getLastAgentMessage();

      expect(response.length).toBeGreaterThan(120);

      // Should include appropriate medical disclaimers
      const responseLower = response.toLowerCase();
      const hasMedicalDisclaimer = [
        'doctor', 'healthcare', 'medical', 'professional', 'dietitian'
      ].some(term => responseLower.includes(term));

      expect(hasMedicalDisclaimer).toBe(true);

      // Should address diabetes-specific concerns
      const hasDiabetesGuidance = [
        'blood sugar', 'glucose', 'carbohydrate', 'glycemic', 'insulin'
      ].some(term => responseLower.includes(term));

      expect(hasDiabetesGuidance).toBe(true);
    });
  });

  test.describe('Multi-Agent Coordination', () => {
    test('Training and nutrition coordination', async () => {
      await test.step('Start with BLAZE for training plan', async () => {
        await chatPage.selectAgent('elite-training-strategist');
        await chatPage.waitForAgentOnline('elite-training-strategist');

        const trainingQuery = "Create a 4-day muscle building program for me. I want to gain 5kg of muscle over 6 months.";
        await chatPage.sendMessage(trainingQuery);
        const trainingResponse = await chatPage.getLastAgentMessage();

        expect(trainingResponse.length).toBeGreaterThan(150);
      });

      await test.step('Switch to SAGE for complementary nutrition plan', async () => {
        await chatPage.selectAgent('precision-nutrition-architect');
        await chatPage.waitForAgentOnline('precision-nutrition-architect');

        const nutritionQuery = "I just got a 4-day muscle building program from BLAZE. What nutrition plan would support this goal of gaining 5kg muscle in 6 months?";
        await chatPage.sendMessage(nutritionQuery);
        const nutritionResponse = await chatPage.getLastAgentMessage();

        expect(nutritionResponse.length).toBeGreaterThan(120);

        // Should acknowledge the training context
        const responseLower = nutritionResponse.toLowerCase();
        const acknowledgesTraining = [
          'muscle building', 'training', 'workout', 'exercise'
        ].some(term => responseLower.includes(term));

        expect(acknowledgesTraining).toBe(true);
      });

      await test.step('Get progress tracking guidance from STELLA', async () => {
        await chatPage.selectAgent('progress-tracker');
        await chatPage.waitForAgentOnline('progress-tracker');

        const progressQuery = "I have a training and nutrition plan for muscle gain. How should I track my progress over the next 6 months?";
        await chatPage.sendMessage(progressQuery);
        const progressResponse = await chatPage.getLastAgentMessage();

        expect(progressResponse.length).toBeGreaterThan(100);

        // Should mention specific metrics
        const responseLower = progressResponse.toLowerCase();
        const hasMetrics = [
          'weight', 'measurements', 'strength', 'progress', 'track', 'measure'
        ].some(term => responseLower.includes(term));

        expect(hasMetrics).toBe(true);
      });
    });

    test('Orchestrator multi-agent coordination', async () => {
      await test.step('Use orchestrator for comprehensive planning', async () => {
        await chatPage.selectAgent('orchestrator');
        await chatPage.waitForAgentOnline('orchestrator');

        const comprehensiveQuery = "I want a complete fitness transformation. I need training, nutrition, and progress tracking all working together. Can you coordinate the other agents to create a comprehensive plan?";

        await chatPage.sendMessage(comprehensiveQuery, { timeout: 60000 });
        const orchestratorResponse = await chatPage.getLastAgentMessage();

        expect(orchestratorResponse.length).toBeGreaterThan(200);

        // Should mention coordination with other agents
        const responseLower = orchestratorResponse.toLowerCase();
        const mentionsAgents = [
          'blaze', 'sage', 'stella', 'training', 'nutrition', 'progress'
        ].filter(term => responseLower.includes(term));

        expect(mentionsAgents.length).toBeGreaterThan(3);
      });
    });
  });

  test.describe('Voice Conversation Flows', () => {
    test('Voice interaction with AI agents', async () => {
      const voiceButton = chatPage.page.locator('[data-testid="voice-button"]');
      const isVoiceEnabled = await voiceButton.isVisible();

      test.skip(!isVoiceEnabled, 'Voice features not available');

      await test.step('Voice query to BLAZE', async () => {
        await chatPage.selectAgent('elite-training-strategist');
        await chatPage.waitForAgentOnline('elite-training-strategist');

        // Simulate voice input
        await chatPage.simulateVoiceInput("What's the best workout for beginners?");

        const response = await chatPage.getLastAgentMessage();
        expect(response.length).toBeGreaterThan(80);

        // Should be appropriate for voice interaction (conversational)
        const responseLower = response.toLowerCase();
        const isConversational = [
          'you', 'your', 'i recommend', "let's", 'try'
        ].some(term => responseLower.includes(term));

        expect(isConversational).toBe(true);
      });

      await test.step('Voice response playback', async () => {
        // Test voice synthesis if available
        const playButton = chatPage.page.locator('[data-testid="voice-play-button"]').last();
        const canPlayVoice = await playButton.isVisible();

        if (canPlayVoice) {
          await chatPage.playVoiceResponse();

          // Should start audio playback
          await chatPage.page.waitForTimeout(2000);

          // Take screenshot of voice interface
          await helpers.takeContextualScreenshot('voice-playback');
        }
      });
    });
  });

  test.describe('Error Handling and Recovery', () => {
    test('Network interruption during conversation', async () => {
      await test.step('Simulate network failure', async () => {
        await chatPage.selectAgent('elite-training-strategist');
        await chatPage.waitForAgentOnline('elite-training-strategist');

        // Intercept and fail API requests
        await chatPage.page.route('**/agents/*/chat', route => {
          route.abort('failed');
        });

        await chatPage.sendMessage('Test message during network failure', {
          waitForResponse: false
        });

        // Should show error state
        const errorMessage = chatPage.page.locator('[data-testid="error-message"], [data-testid="network-error"]');
        await expect(errorMessage).toBeVisible({ timeout: 10000 });
      });

      await test.step('Network recovery', async () => {
        // Remove network interceptor
        await chatPage.page.unroute('**/agents/*/chat');

        // Wait for connection to recover
        await chatPage.waitForConnection();

        // Should be able to send messages again
        await chatPage.sendMessage('Test message after recovery');
        const response = await chatPage.getLastAgentMessage();
        expect(response.length).toBeGreaterThan(20);
      });
    });

    test('Agent unavailable handling', async () => {
      await test.step('Simulate agent unavailable', async () => {
        // Mock agent as unavailable
        await chatPage.page.route('**/agents/elite-training-strategist/chat', route => {
          route.fulfill({
            status: 503,
            body: JSON.stringify({ detail: 'Agent temporarily unavailable' })
          });
        });

        await chatPage.selectAgent('elite-training-strategist');
        await chatPage.sendMessage('Test with unavailable agent', {
          waitForResponse: false
        });

        // Should show agent unavailable message
        const unavailableMessage = chatPage.page.locator(
          '[data-testid="agent-unavailable"], [data-testid="error-message"]:has-text("unavailable")'
        );
        await expect(unavailableMessage).toBeVisible({ timeout: 10000 });
      });
    });

    test('Timeout handling for slow responses', async () => {
      await test.step('Simulate slow agent response', async () => {
        // Add significant delay to agent responses
        await chatPage.page.route('**/agents/*/chat', async route => {
          await new Promise(resolve => setTimeout(resolve, 35000)); // 35 second delay
          await route.continue();
        });

        await chatPage.selectAgent('elite-training-strategist');
        await chatPage.sendMessage('Test slow response', {
          waitForResponse: false
        });

        // Should show timeout handling
        const timeoutMessage = chatPage.page.locator(
          '[data-testid="timeout-message"], [data-testid="slow-response-warning"]'
        );
        await expect(timeoutMessage).toBeVisible({ timeout: 40000 });
      });
    });
  });

  test.describe('Context and Memory Management', () => {
    test('Long conversation context preservation', async () => {
      await chatPage.selectAgent('elite-training-strategist');
      await chatPage.waitForAgentOnline('elite-training-strategist');

      const longConversation = [
        "I'm starting a fitness journey. I'm 28, weigh 80kg, and want to build muscle.",
        "I can work out 4 days a week and have access to a full gym.",
        "I've never done deadlifts before. Are they safe for beginners?",
        "What about squats? I'm worried about knee injury.",
        "How much protein should I eat daily for muscle gain?",
        "Should I do cardio on my off days?",
        "Based on everything we discussed, what's my complete weekly schedule?"
      ];

      for (let i = 0; i < longConversation.length; i++) {
        await test.step(`Message ${i + 1}: Context preservation`, async () => {
          await chatPage.sendMessage(longConversation[i]);
          const response = await chatPage.getLastAgentMessage();

          expect(response.length).toBeGreaterThan(50);

          // Final message should reference earlier conversation
          if (i === longConversation.length - 1) {
            const responseLower = response.toLowerCase();
            const hasContext = [
              '4 days', 'four days', '80kg', 'muscle', 'gym', 'beginner'
            ].some(term => responseLower.includes(term));

            expect(hasContext).toBe(true);
          }
        });
      }
    });

    test('Cross-session memory persistence', async () => {
      await test.step('Initial conversation', async () => {
        await chatPage.selectAgent('elite-training-strategist');
        await chatPage.waitForAgentOnline('elite-training-strategist');

        await chatPage.sendMessage("My name is Alex and I want to focus on powerlifting. I can bench 80kg currently.");
        const response1 = await chatPage.getLastAgentMessage();
        expect(response1.length).toBeGreaterThan(50);
      });

      await test.step('Simulate session break', async () => {
        // Refresh page to simulate new session
        await chatPage.page.reload();
        await chatPage.waitForChatLoad();

        // Should maintain conversation history
        const messages = await chatPage.getAllMessages();
        expect(messages.length).toBeGreaterThan(0);
      });

      await test.step('Reference previous conversation', async () => {
        await chatPage.selectAgent('elite-training-strategist');
        await chatPage.sendMessage("What was my current bench press max again?");

        const response = await chatPage.getLastAgentMessage();
        expect(response.length).toBeGreaterThan(30);

        // Should reference the 80kg bench press
        const responseLower = response.toLowerCase();
        expect(responseLower).toMatch(/80.*kg|80.*kilo/);
      });
    });
  });

  test.describe('Performance and Quality Benchmarks', () => {
    test('Response time benchmarks', async () => {
      const agents = [
        'elite-training-strategist',
        'precision-nutrition-architect',
        'progress-tracker'
      ];

      const performanceResults = [];

      for (const agentId of agents) {
        await test.step(`Performance test: ${agentId}`, async () => {
          await chatPage.selectAgent(agentId);
          await chatPage.waitForAgentOnline(agentId);

          const timing = await chatPage.measureResponseTime('Quick test message for performance benchmark');

          // Performance expectations
          expect(timing.totalTime).toBeLessThan(30000); // 30s max
          expect(timing.receiveTime).toBeLessThan(25000); // 25s for actual AI processing

          performanceResults.push({
            agent: agentId,
            totalTime: timing.totalTime,
            receiveTime: timing.receiveTime
          });
        });
      }

      // Log performance results
      console.log('Agent Performance Benchmarks:', JSON.stringify(performanceResults, null, 2));
    });

    test('Response quality consistency', async () => {
      await chatPage.selectAgent('elite-training-strategist');
      await chatPage.waitForAgentOnline('elite-training-strategist');

      const testQuery = "I'm a beginner. Give me a simple workout routine.";
      const responses = [];

      // Test multiple responses to same query
      for (let i = 0; i < 3; i++) {
        await test.step(`Quality test iteration ${i + 1}`, async () => {
          await chatPage.startNewConversation();
          await chatPage.sendMessage(testQuery);
          const response = await chatPage.getLastAgentMessage();

          responses.push(response);

          // Each response should meet quality standards
          expect(response.length).toBeGreaterThan(100);

          const isValidResponse = await chatPage.validateAgentResponse(
            testQuery,
            response,
            'BLAZE',
            ['beginner', 'workout', 'routine']
          );
          expect(isValidResponse).toBe(true);
        });
      }

      // All responses should be reasonably consistent in quality
      const responseLengths = responses.map(r => r.length);
      const avgLength = responseLengths.reduce((a, b) => a + b, 0) / responseLengths.length;
      const variance = Math.max(...responseLengths) - Math.min(...responseLengths);

      // Variance shouldn't be too high (responses should be consistently good)
      expect(variance).toBeLessThan(avgLength * 0.8);
    });
  });
});
