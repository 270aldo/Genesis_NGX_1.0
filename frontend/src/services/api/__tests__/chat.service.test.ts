import { ChatService, chatService } from '../chat.service';
import { apiClient, API_ENDPOINTS } from '../client';
import { useChatStore } from '../../../store/chatStore';
import { useAuthStore } from '../../../store/authStore';
import type { SendMessageRequest, SendMessageResponse, ChatHistoryRequest } from '../chat.service';

// Mock dependencies
jest.mock('../client', () => ({
  apiClient: {
    post: jest.fn(),
    get: jest.fn(),
    delete: jest.fn(),
    defaults: {
      baseURL: 'http://localhost:8000'
    }
  },
  API_ENDPOINTS: {
    CHAT: {
      SEND: '/api/v1/chat/send',
      STREAM: '/api/v1/chat/stream',
      HISTORY: '/api/v1/chat/history',
      SEARCH: '/api/v1/chat/search',
      EXPORT: '/api/v1/chat/export'
    }
  }
}));

jest.mock('../../../store/chatStore', () => ({
  useChatStore: {
    getState: jest.fn()
  }
}));

jest.mock('../../../store/authStore', () => ({
  useAuthStore: {
    getState: jest.fn()
  }
}));

const mockApiClient = apiClient as jest.Mocked<typeof apiClient>;
const mockUseChatStore = useChatStore as jest.Mocked<typeof useChatStore>;
const mockUseAuthStore = useAuthStore as jest.Mocked<typeof useAuthStore>;

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn()
};

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage
});

// Mock EventSource
class MockEventSource {
  public onmessage: ((event: MessageEvent) => void) | null = null;
  public onerror: ((event: Event) => void) | null = null;
  public close: jest.Mock = jest.fn();
  public addEventListener: jest.Mock = jest.fn();
  public url: string;

  constructor(url: string) {
    this.url = url;
  }

  // Helper methods for testing
  simulateMessage(data: any) {
    if (this.onmessage) {
      this.onmessage({ data: JSON.stringify(data) } as MessageEvent);
    }
  }

  simulateError(error: any) {
    if (this.onerror) {
      this.onerror(error as Event);
    }
  }

  simulateComplete() {
    const completeHandler = this.addEventListener.mock.calls.find(
      call => call[0] === 'complete'
    )?.[1];
    if (completeHandler) {
      completeHandler();
    }
  }
}

(global as any).EventSource = MockEventSource;

// Mock console methods
const originalConsoleError = console.error;
const originalConsoleWarn = console.warn;

beforeAll(() => {
  console.error = jest.fn();
  console.warn = jest.fn();
});

afterAll(() => {
  console.error = originalConsoleError;
  console.warn = originalConsoleWarn;
});

describe('ChatService', () => {
  let mockAuthStore: any;
  let mockChatStore: any;

  beforeEach(() => {
    jest.clearAllMocks();

    mockAuthStore = {
      user: {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        tokens: 100
      },
      useTokens: jest.fn().mockReturnValue(true),
      addTokens: jest.fn()
    };

    mockChatStore = {
      deleteConversation: jest.fn()
    };

    mockUseAuthStore.getState.mockReturnValue(mockAuthStore);
    mockUseChatStore.getState.mockReturnValue(mockChatStore);

    mockLocalStorage.getItem.mockReturnValue(JSON.stringify({
      state: {
        token: 'mock-token',
        user: mockAuthStore.user
      }
    }));
  });

  describe('singleton pattern', () => {
    it('returns the same instance', () => {
      const instance1 = ChatService.getInstance();
      const instance2 = ChatService.getInstance();

      expect(instance1).toBe(instance2);
      expect(instance1).toBe(chatService);
    });
  });

  describe('sendMessage', () => {
    const mockRequest: SendMessageRequest = {
      message: 'Hello, how are you?',
      agentId: 'trainer',
      conversationId: 'conv-123'
    };

    const mockResponse: SendMessageResponse = {
      id: 'msg-456',
      content: 'I am doing great, thank you!',
      agentId: 'trainer',
      agentName: 'Personal Trainer',
      metadata: {
        confidence: 0.95,
        processingTime: 1200,
        tokens: 25
      }
    };

    it('successfully sends a message', async () => {
      mockApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await chatService.sendMessage(mockRequest);

      expect(mockAuthStore.useTokens).toHaveBeenCalledWith(6); // ~6 tokens for "Hello, how are you?"
      expect(mockApiClient.post).toHaveBeenCalledWith(
        API_ENDPOINTS.CHAT.SEND,
        {
          message: mockRequest.message,
          agent_id: mockRequest.agentId,
          conversation_id: mockRequest.conversationId,
          attachments: undefined,
          context: {
            previous_messages: 5,
            include_profile: true,
            include_progress: true
          }
        }
      );
      expect(result).toEqual(mockResponse);
    });

    it('handles unauthenticated user', async () => {
      mockAuthStore.user = null;
      mockUseAuthStore.getState.mockReturnValue(mockAuthStore);

      await expect(chatService.sendMessage(mockRequest)).rejects.toEqual({
        message: 'User not authenticated',
        code: 401
      });

      expect(mockApiClient.post).not.toHaveBeenCalled();
    });

    it('handles insufficient tokens', async () => {
      mockAuthStore.useTokens.mockReturnValue(false);

      await expect(chatService.sendMessage(mockRequest)).rejects.toEqual({
        message: 'Insufficient tokens',
        code: 402
      });

      expect(mockApiClient.post).not.toHaveBeenCalled();
    });

    it('refunds tokens on API error', async () => {
      const apiError = {
        response: {
          data: { message: 'Server error' },
          status: 500
        }
      };

      mockApiClient.post.mockRejectedValueOnce(apiError);

      await expect(chatService.sendMessage(mockRequest)).rejects.toEqual({
        message: 'Server error',
        code: 500
      });

      expect(mockAuthStore.addTokens).toHaveBeenCalledWith(6);
    });

    it('does not refund tokens on insufficient token error', async () => {
      const tokenError = { code: 402 };
      mockApiClient.post.mockRejectedValueOnce(tokenError);

      await expect(chatService.sendMessage(mockRequest)).rejects.toThrow();

      expect(mockAuthStore.addTokens).not.toHaveBeenCalled();
    });

    it('includes attachments and custom context', async () => {
      const requestWithAttachments = {
        ...mockRequest,
        attachments: [{
          id: 'att-1',
          name: 'image.jpg',
          type: 'image/jpeg',
          size: 1024,
          url: 'http://example.com/image.jpg'
        }],
        context: {
          previousMessages: 10,
          includeProfile: false,
          includeProgress: true
        }
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      await chatService.sendMessage(requestWithAttachments);

      expect(mockAuthStore.useTokens).toHaveBeenCalledWith(16); // message + 1 attachment (10 tokens)
      expect(mockApiClient.post).toHaveBeenCalledWith(
        API_ENDPOINTS.CHAT.SEND,
        {
          message: requestWithAttachments.message,
          agent_id: requestWithAttachments.agentId,
          conversation_id: requestWithAttachments.conversationId,
          attachments: requestWithAttachments.attachments,
          context: {
            previous_messages: 10,
            include_profile: false,
            include_progress: true
          }
        }
      );
    });
  });

  describe('sendMessageStream', () => {
    const mockRequest: SendMessageRequest = {
      message: 'Tell me about fitness',
      agentId: 'trainer'
    };

    let mockEventSource: MockEventSource;

    beforeEach(() => {
      // Clear any existing event source
      (chatService as any).eventSource = null;
    });

    it('sets up streaming message successfully', async () => {
      const onMessage = jest.fn();
      const onError = jest.fn();
      const onComplete = jest.fn();

      await chatService.sendMessageStream(mockRequest, onMessage, onError, onComplete);

      // Check that EventSource was created
      expect(MockEventSource).toHaveBeenCalled();

      // Get the created instance
      mockEventSource = (chatService as any).eventSource as MockEventSource;
      expect(mockEventSource).toBeDefined();
      expect(mockEventSource.url).toContain(API_ENDPOINTS.CHAT.STREAM);
      expect(mockEventSource.url).toContain('message=Tell%20me%20about%20fitness');
      expect(mockEventSource.url).toContain('agent_id=trainer');
      expect(mockEventSource.url).toContain('token=mock-token');
    });

    it('handles streaming messages', async () => {
      const onMessage = jest.fn();

      await chatService.sendMessageStream(mockRequest, onMessage);

      mockEventSource = (chatService as any).eventSource as MockEventSource;

      const streamMessage = {
        id: 'stream-1',
        content: 'Fitness is important',
        finished: false
      };

      mockEventSource.simulateMessage(streamMessage);

      expect(onMessage).toHaveBeenCalledWith(streamMessage);
    });

    it('handles stream completion', async () => {
      const onComplete = jest.fn();

      await chatService.sendMessageStream(mockRequest, jest.fn(), undefined, onComplete);

      mockEventSource = (chatService as any).eventSource as MockEventSource;
      mockEventSource.simulateComplete();

      expect(onComplete).toHaveBeenCalled();
      expect(mockEventSource.close).toHaveBeenCalled();
    });

    it('handles stream errors and refunds tokens', async () => {
      const onError = jest.fn();

      await chatService.sendMessageStream(mockRequest, jest.fn(), onError);

      mockEventSource = (chatService as any).eventSource as MockEventSource;
      mockEventSource.simulateError(new Error('Stream error'));

      expect(onError).toHaveBeenCalled();
      expect(mockAuthStore.addTokens).toHaveBeenCalled();
      expect(mockEventSource.close).toHaveBeenCalled();
    });

    it('closes existing stream before creating new one', async () => {
      const oldMockEventSource = new MockEventSource('old-url');
      (chatService as any).eventSource = oldMockEventSource;

      await chatService.sendMessageStream(mockRequest, jest.fn());

      expect(oldMockEventSource.close).toHaveBeenCalled();
    });

    it('handles authentication errors', async () => {
      mockAuthStore.user = null;
      mockUseAuthStore.getState.mockReturnValue(mockAuthStore);

      await expect(
        chatService.sendMessageStream(mockRequest, jest.fn())
      ).rejects.toEqual({
        message: 'User not authenticated',
        code: 401
      });
    });

    it('handles insufficient tokens', async () => {
      mockAuthStore.useTokens.mockReturnValue(false);

      await expect(
        chatService.sendMessageStream(mockRequest, jest.fn())
      ).rejects.toEqual({
        message: 'Insufficient tokens',
        code: 402
      });
    });
  });

  describe('closeStream', () => {
    it('closes existing event source', () => {
      const mockEventSource = new MockEventSource('test-url');
      (chatService as any).eventSource = mockEventSource;

      chatService.closeStream();

      expect(mockEventSource.close).toHaveBeenCalled();
      expect((chatService as any).eventSource).toBeNull();
    });

    it('does nothing when no event source exists', () => {
      (chatService as any).eventSource = null;

      expect(() => chatService.closeStream()).not.toThrow();
    });
  });

  describe('getChatHistory', () => {
    const mockRequest: ChatHistoryRequest = {
      conversationId: 'conv-123',
      limit: 10,
      offset: 0
    };

    const mockResponse = {
      conversations: [
        {
          id: 'conv-123',
          title: 'Fitness Discussion',
          agentId: 'trainer',
          createdAt: '2024-01-01T00:00:00Z',
          updatedAt: '2024-01-01T01:00:00Z',
          messageCount: 5
        }
      ],
      total: 1,
      hasMore: false
    };

    it('successfully gets chat history', async () => {
      mockApiClient.get.mockResolvedValueOnce({ data: mockResponse });

      const result = await chatService.getChatHistory(mockRequest);

      expect(mockApiClient.get).toHaveBeenCalledWith(API_ENDPOINTS.CHAT.HISTORY, {
        params: {
          conversation_id: 'conv-123',
          agent_id: undefined,
          limit: 10,
          offset: 0,
          start_date: undefined,
          end_date: undefined
        }
      });
      expect(result).toEqual(mockResponse);
    });

    it('uses default parameters', async () => {
      mockApiClient.get.mockResolvedValueOnce({ data: mockResponse });

      await chatService.getChatHistory({});

      expect(mockApiClient.get).toHaveBeenCalledWith(API_ENDPOINTS.CHAT.HISTORY, {
        params: {
          conversation_id: undefined,
          agent_id: undefined,
          limit: 20,
          offset: 0,
          start_date: undefined,
          end_date: undefined
        }
      });
    });

    it('handles API errors', async () => {
      const apiError = {
        response: {
          data: { message: 'Access denied' },
          status: 403
        }
      };

      mockApiClient.get.mockRejectedValueOnce(apiError);

      await expect(chatService.getChatHistory(mockRequest)).rejects.toEqual({
        message: 'Access denied',
        code: 403
      });
    });
  });

  describe('searchChats', () => {
    const mockRequest = {
      query: 'fitness tips',
      limit: 5
    };

    const mockResponse = {
      results: [
        {
          conversationId: 'conv-123',
          messageId: 'msg-456',
          content: 'Here are some fitness tips...',
          agentName: 'Personal Trainer',
          timestamp: '2024-01-01T00:00:00Z',
          relevanceScore: 0.95
        }
      ],
      total: 1
    };

    it('successfully searches chats', async () => {
      mockApiClient.get.mockResolvedValueOnce({ data: mockResponse });

      const result = await chatService.searchChats(mockRequest);

      expect(mockApiClient.get).toHaveBeenCalledWith(API_ENDPOINTS.CHAT.SEARCH, {
        params: {
          query: 'fitness tips',
          conversation_id: undefined,
          agent_id: undefined,
          limit: 5
        }
      });
      expect(result).toEqual(mockResponse);
    });

    it('handles search errors', async () => {
      const apiError = {
        response: {
          data: { message: 'Search failed' },
          status: 500
        }
      };

      mockApiClient.get.mockRejectedValueOnce(apiError);

      await expect(chatService.searchChats(mockRequest)).rejects.toEqual({
        message: 'Search failed',
        code: 500
      });
    });
  });

  describe('exportConversation', () => {
    it('successfully exports conversation', async () => {
      const mockBlob = new Blob(['PDF content'], { type: 'application/pdf' });
      mockApiClient.get.mockResolvedValueOnce({ data: mockBlob });

      const result = await chatService.exportConversation('conv-123', 'pdf');

      expect(mockApiClient.get).toHaveBeenCalledWith(API_ENDPOINTS.CHAT.EXPORT, {
        params: {
          conversation_id: 'conv-123',
          format: 'pdf'
        },
        responseType: 'blob'
      });
      expect(result).toBe(mockBlob);
    });

    it('uses default format', async () => {
      const mockBlob = new Blob(['PDF content'], { type: 'application/pdf' });
      mockApiClient.get.mockResolvedValueOnce({ data: mockBlob });

      await chatService.exportConversation('conv-123');

      expect(mockApiClient.get).toHaveBeenCalledWith(API_ENDPOINTS.CHAT.EXPORT, {
        params: {
          conversation_id: 'conv-123',
          format: 'pdf'
        },
        responseType: 'blob'
      });
    });
  });

  describe('deleteConversation', () => {
    it('successfully deletes conversation', async () => {
      mockApiClient.delete.mockResolvedValueOnce({ data: {} });

      await chatService.deleteConversation('conv-123');

      expect(mockApiClient.delete).toHaveBeenCalledWith('/api/v1/chat/history/conv-123');
      expect(mockChatStore.deleteConversation).toHaveBeenCalledWith('conv-123');
    });

    it('handles delete errors', async () => {
      const apiError = {
        response: {
          data: { message: 'Not found' },
          status: 404
        }
      };

      mockApiClient.delete.mockRejectedValueOnce(apiError);

      await expect(chatService.deleteConversation('conv-123')).rejects.toEqual({
        message: 'Not found',
        code: 404
      });
    });
  });

  describe('uploadAttachment', () => {
    it('successfully uploads attachment', async () => {
      const mockFile = new File(['content'], 'test.txt', { type: 'text/plain' });
      const mockResponse = {
        id: 'att-123',
        url: 'http://example.com/file.txt',
        preview: 'http://example.com/preview.jpg'
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await chatService.uploadAttachment(mockFile);

      expect(mockApiClient.post).toHaveBeenCalledWith(
        '/api/v1/chat/upload',
        expect.any(FormData),
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      expect(result).toEqual({
        id: 'att-123',
        name: 'test.txt',
        type: 'text/plain',
        size: mockFile.size,
        url: 'http://example.com/file.txt',
        preview: 'http://example.com/preview.jpg'
      });
    });
  });

  describe('getConversationAnalytics', () => {
    it('successfully gets analytics', async () => {
      const mockAnalytics = {
        messageCount: 10,
        tokensUsed: 250,
        averageResponseTime: 1500,
        agentsUsed: ['trainer', 'nutritionist'],
        timeSpent: 3600,
        topTopics: [
          { topic: 'fitness', frequency: 5 },
          { topic: 'nutrition', frequency: 3 }
        ]
      };

      mockApiClient.get.mockResolvedValueOnce({ data: mockAnalytics });

      const result = await chatService.getConversationAnalytics('conv-123');

      expect(mockApiClient.get).toHaveBeenCalledWith('/api/v1/chat/analytics/conv-123');
      expect(result).toEqual(mockAnalytics);
    });
  });

  describe('calculateTokensRequired', () => {
    it('calculates tokens for text only', () => {
      const service = chatService as any;
      const tokens = service.calculateTokensRequired('Hello world');

      expect(tokens).toBe(3); // Math.ceil(11/4) = 3
    });

    it('calculates tokens with attachments', () => {
      const service = chatService as any;
      const attachments = [{ id: '1' }, { id: '2' }];
      const tokens = service.calculateTokensRequired('Hi', attachments);

      expect(tokens).toBe(21); // Math.ceil(2/4) + (2 * 10) = 1 + 20 = 21
    });

    it('returns minimum of 1 token', () => {
      const service = chatService as any;
      const tokens = service.calculateTokensRequired('');

      expect(tokens).toBe(1);
    });
  });

  describe('error handling', () => {
    it('handles errors without response data', async () => {
      const networkError = new Error('Network error');
      mockApiClient.post.mockRejectedValueOnce(networkError);

      await expect(
        chatService.sendMessage({ message: 'test' })
      ).rejects.toEqual({
        message: 'Failed to send message',
        code: 500
      });
    });

    it('parses stream message errors gracefully', async () => {
      const onMessage = jest.fn();

      await chatService.sendMessageStream(
        { message: 'test' },
        onMessage
      );

      const mockEventSource = (chatService as any).eventSource as MockEventSource;

      // Simulate invalid JSON
      if (mockEventSource.onmessage) {
        mockEventSource.onmessage({ data: 'invalid json' } as MessageEvent);
      }

      expect(onMessage).not.toHaveBeenCalled();
      expect(console.error).toHaveBeenCalledWith(
        'Error parsing stream message:',
        expect.any(Error)
      );
    });
  });
});
