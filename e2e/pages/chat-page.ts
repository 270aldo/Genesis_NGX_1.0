import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base-page';
import { TestHelpers, SemanticValidator } from '../utils/test-helpers';

/**
 * Chat Page Object Model for GENESIS AI Conversations
 *
 * Handles all chat-related interactions including:
 * - Agent selection and switching
 * - Message sending and receiving
 * - Voice interactions
 * - Streaming response handling
 * - Conversation management
 */
export class ChatPage extends BasePage {
  private readonly selectors = {
    // Chat Interface
    chatContainer: '[data-testid="chat-container"]',
    messageInput: '[data-testid="message-input"]',
    sendButton: '[data-testid="send-button"]',
    voiceButton: '[data-testid="voice-button"]',
    attachButton: '[data-testid="attach-button"]',

    // Messages
    messageList: '[data-testid="message-list"]',
    userMessage: '[data-testid="user-message"]',
    agentMessage: '[data-testid="agent-message"]',
    streamingMessage: '[data-testid="streaming-message"]',
    messageTimestamp: '[data-testid="message-timestamp"]',

    // Agent Selection
    agentSelector: '[data-testid="agent-selector"]',
    agentCard: '[data-testid="agent-card"]',
    currentAgent: '[data-testid="current-agent"]',
    agentStatus: '[data-testid="agent-status"]',

    // Conversation Management
    conversationList: '[data-testid="conversation-list"]',
    newConversationButton: '[data-testid="new-conversation-button"]',
    conversationTitle: '[data-testid="conversation-title"]',
    conversationMenu: '[data-testid="conversation-menu"]',

    // Loading and Status
    typingIndicator: '[data-testid="typing-indicator"]',
    aiLoadingIndicator: '[data-testid="ai-loading"]',
    connectionStatus: '[data-testid="connection-status"]',

    // Voice Interface
    voiceModal: '[data-testid="voice-modal"]',
    voiceWaveform: '[data-testid="voice-waveform"]',
    voicePlayButton: '[data-testid="voice-play-button"]',
    voiceStopButton: '[data-testid="voice-stop-button"]',

    // Quick Actions
    quickActions: '[data-testid="quick-actions"]',
    quickActionButton: '[data-testid="quick-action-button"]',
    suggestedQuestions: '[data-testid="suggested-questions"]',

    // Message Actions
    messageActions: '[data-testid="message-actions"]',
    copyButton: '[data-testid="copy-message-button"]',
    shareButton: '[data-testid="share-message-button"]',
    feedbackButton: '[data-testid="feedback-button"]',
  };

  constructor(page: Page) {
    super(page);
  }

  // Navigation and Setup

  async goToChat() {
    await this.goto('/chat');
    await this.waitForChatLoad();
  }

  async waitForChatLoad() {
    await this.page.waitForSelector(this.selectors.chatContainer, { state: 'visible' });
    await this.helpers.waitForNetworkIdle();

    // Wait for agent selector to be ready
    await this.page.waitForSelector(this.selectors.agentSelector, { state: 'visible' });
  }

  // Agent Selection and Management

  async selectAgent(agentName: string) {
    // Open agent selector if not visible
    const selector = this.page.locator(this.selectors.agentSelector);
    await selector.click();

    // Select specific agent
    const agentCard = this.page.locator(`${this.selectors.agentCard}[data-agent-name="${agentName}"]`);
    await agentCard.click();

    // Wait for agent to be selected
    await this.page.waitForSelector(
      `${this.selectors.currentAgent}[data-agent="${agentName}"]`,
      { state: 'visible' }
    );
  }

  async getCurrentAgent(): Promise<string | null> {
    const currentAgentElement = this.page.locator(this.selectors.currentAgent);
    return await currentAgentElement.getAttribute('data-agent');
  }

  async getAgentStatus(agentName?: string): Promise<string | null> {
    const agent = agentName || await this.getCurrentAgent();
    if (!agent) return null;

    const statusElement = this.page.locator(
      `${this.selectors.agentStatus}[data-agent="${agent}"]`
    );
    return await statusElement.textContent();
  }

  async waitForAgentOnline(agentName: string, timeout: number = 10000) {
    await this.page.waitForFunction(
      (agent) => {
        const statusElement = document.querySelector(`[data-testid="agent-status"][data-agent="${agent}"]`);
        return statusElement && statusElement.textContent === 'online';
      },
      agentName,
      { timeout }
    );
  }

  // Message Sending and Receiving

  async sendMessage(message: string, options: {
    waitForResponse?: boolean;
    timeout?: number;
    expectStream?: boolean;
  } = {}) {
    const { waitForResponse = true, timeout = 30000, expectStream = false } = options;

    // Type message
    await this.helpers.humanType(this.selectors.messageInput, message);

    // Send message
    await this.helpers.humanClick(this.selectors.sendButton);

    // Wait for user message to appear
    await this.page.waitForSelector(this.selectors.userMessage + ':last-child', {
      state: 'visible',
      timeout: 5000
    });

    if (waitForResponse) {
      if (expectStream) {
        await this.waitForStreamingResponse(timeout);
      } else {
        await this.waitForAgentResponse(timeout);
      }
    }
  }

  async waitForAgentResponse(timeout: number = 30000): Promise<string> {
    // Wait for typing indicator
    await this.page.waitForSelector(this.selectors.typingIndicator, {
      state: 'visible',
      timeout: 5000
    }).catch(() => {
      // Typing indicator might not appear for cached responses
    });

    // Wait for response to appear
    const responseSelector = this.selectors.agentMessage + ':last-child';
    await this.page.waitForSelector(responseSelector, {
      state: 'visible',
      timeout
    });

    // Wait for typing indicator to disappear
    await this.page.waitForSelector(this.selectors.typingIndicator, {
      state: 'hidden',
      timeout: 5000
    }).catch(() => {
      // Indicator might already be hidden
    });

    // Get response text
    const responseElement = this.page.locator(responseSelector);
    const responseText = await responseElement.textContent();

    return responseText || '';
  }

  async waitForStreamingResponse(timeout: number = 60000): Promise<string> {
    // Wait for streaming message container
    await this.page.waitForSelector(this.selectors.streamingMessage, {
      state: 'visible',
      timeout: 10000
    });

    // Wait for streaming to complete
    await this.page.waitForFunction(
      () => {
        const streamingElement = document.querySelector('[data-testid="streaming-message"]:last-child');
        if (!streamingElement) return false;

        // Check if streaming cursor is gone (indicates completion)
        const hasCursor = streamingElement.querySelector('.streaming-cursor') !== null;
        const hasContent = streamingElement.textContent && streamingElement.textContent.length > 10;

        return !hasCursor && hasContent;
      },
      { timeout }
    );

    // Get final streamed content
    const streamingElement = this.page.locator(this.selectors.streamingMessage + ':last-child');
    return (await streamingElement.textContent()) || '';
  }

  async getLastUserMessage(): Promise<string> {
    const messageElement = this.page.locator(this.selectors.userMessage + ':last-child');
    return (await messageElement.textContent()) || '';
  }

  async getLastAgentMessage(): Promise<string> {
    const messageElement = this.page.locator(this.selectors.agentMessage + ':last-child');
    return (await messageElement.textContent()) || '';
  }

  async getAllMessages(): Promise<Array<{ type: 'user' | 'agent', content: string, timestamp?: string }>> {
    const messages = [];

    // Get all message elements
    const messageElements = await this.page.locator('[data-testid*="message"]:not([data-testid*="message-"])').all();

    for (const element of messageElements) {
      const testId = await element.getAttribute('data-testid');
      const content = await element.textContent();
      const timestamp = await element.locator(this.selectors.messageTimestamp).textContent().catch(() => null);

      if (testId?.includes('user-message')) {
        messages.push({ type: 'user' as const, content: content || '', timestamp: timestamp || undefined });
      } else if (testId?.includes('agent-message')) {
        messages.push({ type: 'agent' as const, content: content || '', timestamp: timestamp || undefined });
      }
    }

    return messages;
  }

  // Voice Interactions

  async startVoiceRecording() {
    await this.helpers.humanClick(this.selectors.voiceButton);

    // Wait for voice modal to appear
    await this.page.waitForSelector(this.selectors.voiceModal, { state: 'visible' });

    // Wait for recording to start (waveform appears)
    await this.page.waitForSelector(this.selectors.voiceWaveform, { state: 'visible' });
  }

  async stopVoiceRecording() {
    const stopButton = this.page.locator(this.selectors.voiceStopButton);
    await stopButton.click();

    // Wait for processing
    await this.page.waitForSelector(this.selectors.voiceModal, { state: 'hidden' });
  }

  async simulateVoiceInput(text: string) {
    await this.startVoiceRecording();

    // Simulate voice input recognition
    await this.page.evaluate((voiceText) => {
      // Trigger voice recognition result
      const event = new CustomEvent('voice-recognition-result', {
        detail: { text: voiceText, confidence: 0.95 }
      });
      window.dispatchEvent(event);
    }, text);

    await this.stopVoiceRecording();
  }

  async playVoiceResponse() {
    const playButton = this.page.locator(this.selectors.voicePlayButton + ':last-child');
    await playButton.click();

    // Wait for audio to start playing
    await this.page.waitForTimeout(1000);
  }

  // Quick Actions and Suggestions

  async useQuickAction(actionText: string) {
    const quickAction = this.page.locator(`${this.selectors.quickActionButton}:has-text("${actionText}")`);
    await quickAction.click();

    // Wait for action to be processed
    await this.helpers.waitForNetworkIdle();
  }

  async clickSuggestedQuestion(questionText: string) {
    const suggestion = this.page.locator(
      `${this.selectors.suggestedQuestions} button:has-text("${questionText}")`
    );
    await suggestion.click();

    // Wait for message to be sent
    await this.waitForAgentResponse();
  }

  async getAvailableQuickActions(): Promise<string[]> {
    const actionElements = await this.page.locator(this.selectors.quickActionButton).all();
    const actions = [];

    for (const element of actionElements) {
      const text = await element.textContent();
      if (text) actions.push(text);
    }

    return actions;
  }

  // Conversation Management

  async startNewConversation() {
    await this.helpers.humanClick(this.selectors.newConversationButton);

    // Wait for new conversation to be initialized
    await this.page.waitForTimeout(1000);
    await this.helpers.waitForNetworkIdle();
  }

  async getConversationTitle(): Promise<string> {
    const titleElement = this.page.locator(this.selectors.conversationTitle);
    return (await titleElement.textContent()) || '';
  }

  async switchToConversation(conversationTitle: string) {
    const conversationElement = this.page.locator(
      `${this.selectors.conversationList} [data-testid="conversation-item"]:has-text("${conversationTitle}")`
    );
    await conversationElement.click();

    // Wait for conversation to load
    await this.waitForChatLoad();
  }

  async deleteConversation(conversationTitle?: string) {
    if (conversationTitle) {
      await this.switchToConversation(conversationTitle);
    }

    // Open conversation menu
    await this.helpers.humanClick(this.selectors.conversationMenu);

    // Click delete option
    const deleteButton = this.page.locator('[data-testid="delete-conversation"]');
    await deleteButton.click();

    // Confirm deletion
    const confirmButton = this.page.locator('[data-testid="confirm-delete"]');
    await confirmButton.click();

    // Wait for deletion to complete
    await this.helpers.waitForNetworkIdle();
  }

  // Message Actions and Feedback

  async copyMessage(messageIndex: number = -1) {
    const messageElement = messageIndex === -1
      ? this.page.locator(this.selectors.agentMessage).last()
      : this.page.locator(this.selectors.agentMessage).nth(messageIndex);

    // Hover to show actions
    await messageElement.hover();

    // Click copy button
    const copyButton = messageElement.locator(this.selectors.copyButton);
    await copyButton.click();

    // Verify copy success (toast notification)
    await this.page.waitForSelector('[data-testid="copy-success-toast"]', {
      state: 'visible',
      timeout: 3000
    });
  }

  async provideFeedback(messageIndex: number = -1, rating: 'positive' | 'negative', comment?: string) {
    const messageElement = messageIndex === -1
      ? this.page.locator(this.selectors.agentMessage).last()
      : this.page.locator(this.selectors.agentMessage).nth(messageIndex);

    // Hover to show actions
    await messageElement.hover();

    // Click feedback button
    const feedbackButton = messageElement.locator(this.selectors.feedbackButton);
    await feedbackButton.click();

    // Select rating
    const ratingButton = this.page.locator(`[data-testid="${rating}-feedback"]`);
    await ratingButton.click();

    // Add comment if provided
    if (comment) {
      const commentInput = this.page.locator('[data-testid="feedback-comment"]');
      await commentInput.fill(comment);
    }

    // Submit feedback
    const submitButton = this.page.locator('[data-testid="submit-feedback"]');
    await submitButton.click();

    // Wait for feedback confirmation
    await this.page.waitForSelector('[data-testid="feedback-success"]', {
      state: 'visible',
      timeout: 5000
    });
  }

  // Test Helper Methods

  async validateAgentResponse(
    query: string,
    response: string,
    agentName: string,
    expectedKeywords: string[] = []
  ): Promise<boolean> {
    // Basic validation
    if (response.length < 10) {
      console.warn(`Agent response too short: "${response}"`);
      return false;
    }

    // Check for error patterns
    const errorPatterns = [
      /error/i, /sorry, i (can't|cannot)/i, /something went wrong/i
    ];

    if (errorPatterns.some(pattern => pattern.test(response))) {
      console.warn(`Agent response contains error: "${response}"`);
      return false;
    }

    // Check expected keywords
    if (expectedKeywords.length > 0) {
      const responseLower = response.toLowerCase();
      const foundKeywords = expectedKeywords.filter(keyword =>
        responseLower.includes(keyword.toLowerCase())
      );

      if (foundKeywords.length < expectedKeywords.length * 0.5) {
        console.warn(`Response missing keywords: ${expectedKeywords.join(', ')}`);
        return false;
      }
    }

    // Agent-specific validation
    return this.validateAgentSpecificResponse(response, agentName);
  }

  private validateAgentSpecificResponse(response: string, agentName: string): boolean {
    const responseLower = response.toLowerCase();

    switch (agentName.toLowerCase()) {
      case 'blaze':
      case 'elite-training-strategist':
        const trainingKeywords = ['workout', 'exercise', 'training', 'muscle', 'rep', 'set'];
        return trainingKeywords.some(keyword => responseLower.includes(keyword));

      case 'sage':
      case 'precision-nutrition-architect':
        const nutritionKeywords = ['nutrition', 'diet', 'meal', 'calories', 'protein'];
        return nutritionKeywords.some(keyword => responseLower.includes(keyword));

      case 'stella':
      case 'progress-tracker':
        const progressKeywords = ['progress', 'goal', 'tracking', 'metric'];
        return progressKeywords.some(keyword => responseLower.includes(keyword));

      default:
        return true; // Accept any response for unknown agents
    }
  }

  async measureResponseTime(message: string): Promise<{
    sendTime: number,
    receiveTime: number,
    totalTime: number
  }> {
    const startTime = Date.now();

    // Send message
    await this.helpers.humanType(this.selectors.messageInput, message);
    const sendTime = Date.now() - startTime;

    await this.helpers.humanClick(this.selectors.sendButton);
    const postSendTime = Date.now();

    // Wait for response
    await this.waitForAgentResponse();
    const endTime = Date.now();

    return {
      sendTime,
      receiveTime: endTime - postSendTime,
      totalTime: endTime - startTime
    };
  }

  async checkConnectionStatus(): Promise<'connected' | 'disconnected' | 'reconnecting'> {
    const statusElement = this.page.locator(this.selectors.connectionStatus);
    const status = await statusElement.getAttribute('data-status');

    return (status as 'connected' | 'disconnected' | 'reconnecting') || 'connected';
  }

  async waitForConnection(timeout: number = 10000) {
    await this.page.waitForFunction(
      () => {
        const statusElement = document.querySelector('[data-testid="connection-status"]');
        return statusElement?.getAttribute('data-status') === 'connected';
      },
      { timeout }
    );
  }

  // Visual Validation

  async takeConversationScreenshot(name?: string): Promise<string> {
    const screenshotName = name || `conversation-${Date.now()}`;
    return await this.helpers.takeContextualScreenshot(screenshotName, false);
  }

  async validateChatLayout(): Promise<{ issues: string[] }> {
    const issues = [];

    // Check that essential elements are visible
    const essentialElements = [
      { selector: this.selectors.chatContainer, name: 'Chat container' },
      { selector: this.selectors.messageInput, name: 'Message input' },
      { selector: this.selectors.sendButton, name: 'Send button' },
      { selector: this.selectors.agentSelector, name: 'Agent selector' }
    ];

    for (const element of essentialElements) {
      const isVisible = await this.page.locator(element.selector).isVisible();
      if (!isVisible) {
        issues.push(`${element.name} not visible`);
      }
    }

    // Check layout responsiveness
    const viewport = this.page.viewportSize();
    if (viewport && viewport.width < 768) {
      // Mobile layout checks
      const isMobileOptimized = await this.page.locator('[data-mobile-optimized="true"]').isVisible();
      if (!isMobileOptimized) {
        issues.push('Mobile layout not optimized');
      }
    }

    return { issues };
  }
}
