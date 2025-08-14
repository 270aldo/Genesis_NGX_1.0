import { renderHook, act } from '@testing-library/react';
import { useChatStore, Conversation, Message, FileAttachment } from '../chatStore';

// Mock localStorage for persistence
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage
});

// Mock zustand persist middleware
jest.mock('zustand/middleware', () => ({
  persist: (config: any, options: any) => config
}));

// Mock Date.now for consistent IDs
const originalDateNow = Date.now;
let mockTimestamp = 1000;

beforeAll(() => {
  Date.now = jest.fn(() => mockTimestamp++);
});

afterAll(() => {
  Date.now = originalDateNow;
});

describe('ChatStore', () => {
  const mockAttachment: FileAttachment = {
    id: 'att-1',
    name: 'test-image.jpg',
    type: 'image/jpeg',
    size: 1024,
    url: 'http://example.com/image.jpg',
    preview: 'http://example.com/preview.jpg'
  };

  beforeEach(() => {
    // Reset store state and mock timestamp before each test
    mockTimestamp = 1000;
    useChatStore.setState({
      conversations: [],
      activeConversationId: null,
      sidebarOpen: true,
      isVoiceMode: false,
      isTyping: false
    });

    jest.clearAllMocks();
  });

  describe('initial state', () => {
    it('has correct default values', () => {
      const { result } = renderHook(() => useChatStore());

      expect(result.current.conversations).toEqual([]);
      expect(result.current.activeConversationId).toBeNull();
      expect(result.current.sidebarOpen).toBe(true);
      expect(result.current.isVoiceMode).toBe(false);
      expect(result.current.isTyping).toBe(false);
      expect(result.current.currentConversationId).toBeNull();
    });

    it('provides all required actions', () => {
      const { result } = renderHook(() => useChatStore());

      expect(typeof result.current.createConversation).toBe('function');
      expect(typeof result.current.setActiveConversation).toBe('function');
      expect(typeof result.current.addMessage).toBe('function');
      expect(typeof result.current.updateMessage).toBe('function');
      expect(typeof result.current.deleteMessage).toBe('function');
      expect(typeof result.current.deleteConversation).toBe('function');
      expect(typeof result.current.getCurrentConversation).toBe('function');
      expect(typeof result.current.getConversationsByAgent).toBe('function');
      expect(typeof result.current.toggleSidebar).toBe('function');
      expect(typeof result.current.setSidebarOpen).toBe('function');
      expect(typeof result.current.setVoiceMode).toBe('function');
      expect(typeof result.current.setTyping).toBe('function');
      expect(typeof result.current.updateConversationTitle).toBe('function');
    });
  });

  describe('conversation management', () => {
    describe('createConversation', () => {
      it('creates a new conversation without agent', () => {
        const { result } = renderHook(() => useChatStore());

        let conversationId: string;
        act(() => {
          conversationId = result.current.createConversation();
        });

        expect(conversationId!).toBe('1000');
        expect(result.current.conversations).toHaveLength(1);
        expect(result.current.conversations[0]).toMatchObject({
          id: '1000',
          title: 'New Conversation',
          messages: [],
          agentId: undefined
        });
        expect(result.current.activeConversationId).toBe('1000');
      });

      it('creates a new conversation with agent', () => {
        const { result } = renderHook(() => useChatStore());

        let conversationId: string;
        act(() => {
          conversationId = result.current.createConversation('trainer');
        });

        expect(result.current.conversations[0].agentId).toBe('trainer');
        expect(result.current.conversations[0].id).toBe(conversationId!);
      });

      it('adds new conversation at the beginning of the list', () => {
        const { result } = renderHook(() => useChatStore());

        act(() => {
          result.current.createConversation('agent1');
          result.current.createConversation('agent2');
        });

        expect(result.current.conversations).toHaveLength(2);
        expect(result.current.conversations[0].agentId).toBe('agent2'); // Most recent first
        expect(result.current.conversations[1].agentId).toBe('agent1');
      });

      it('sets the new conversation as active', () => {
        const { result } = renderHook(() => useChatStore());

        let firstId: string, secondId: string;
        act(() => {
          firstId = result.current.createConversation();
          secondId = result.current.createConversation();
        });

        expect(result.current.activeConversationId).toBe(secondId!);
      });
    });

    describe('setActiveConversation', () => {
      it('sets the active conversation ID', () => {
        const { result } = renderHook(() => useChatStore());

        act(() => {
          result.current.createConversation();
          result.current.setActiveConversation('test-id');
        });

        expect(result.current.activeConversationId).toBe('test-id');
      });

      it('updates currentConversationId computed property', () => {
        const { result } = renderHook(() => useChatStore());

        act(() => {
          result.current.setActiveConversation('computed-test');
        });

        expect(result.current.currentConversationId).toBe('computed-test');
      });
    });

    describe('deleteConversation', () => {
      it('removes conversation from list', () => {
        const { result } = renderHook(() => useChatStore());

        let conversationId: string;
        act(() => {
          conversationId = result.current.createConversation();
        });

        expect(result.current.conversations).toHaveLength(1);

        act(() => {
          result.current.deleteConversation(conversationId!);
        });

        expect(result.current.conversations).toHaveLength(0);
      });

      it('clears active conversation if deleted conversation was active', () => {
        const { result } = renderHook(() => useChatStore());

        let conversationId: string;
        act(() => {
          conversationId = result.current.createConversation();
        });

        expect(result.current.activeConversationId).toBe(conversationId!);

        act(() => {
          result.current.deleteConversation(conversationId!);
        });

        expect(result.current.activeConversationId).toBeNull();
      });

      it('keeps active conversation if different conversation is deleted', () => {
        const { result } = renderHook(() => useChatStore());

        let firstId: string, secondId: string;
        act(() => {
          firstId = result.current.createConversation();
          secondId = result.current.createConversation();
          result.current.setActiveConversation(firstId!);
        });

        act(() => {
          result.current.deleteConversation(secondId!);
        });

        expect(result.current.activeConversationId).toBe(firstId!);
      });

      it('handles deleting non-existent conversation', () => {
        const { result } = renderHook(() => useChatStore());

        act(() => {
          result.current.createConversation();
        });

        expect(() => {
          act(() => {
            result.current.deleteConversation('non-existent');
          });
        }).not.toThrow();

        expect(result.current.conversations).toHaveLength(1);
      });
    });

    describe('getCurrentConversation', () => {
      it('returns current conversation when one is active', () => {
        const { result } = renderHook(() => useChatStore());

        let conversationId: string;
        act(() => {
          conversationId = result.current.createConversation('trainer');
        });

        const current = result.current.getCurrentConversation();

        expect(current).not.toBeNull();
        expect(current?.id).toBe(conversationId!);
        expect(current?.agentId).toBe('trainer');
      });

      it('returns null when no conversation is active', () => {
        const { result } = renderHook(() => useChatStore());

        const current = result.current.getCurrentConversation();

        expect(current).toBeNull();
      });

      it('returns null when active conversation does not exist', () => {
        const { result } = renderHook(() => useChatStore());

        act(() => {
          result.current.setActiveConversation('non-existent');
        });

        const current = result.current.getCurrentConversation();

        expect(current).toBeNull();
      });
    });

    describe('getConversationsByAgent', () => {
      it('returns conversations for specific agent', () => {
        const { result } = renderHook(() => useChatStore());

        act(() => {
          result.current.createConversation('trainer');
          result.current.createConversation('nutritionist');
          result.current.createConversation('trainer');
        });

        const trainerConversations = result.current.getConversationsByAgent('trainer');

        expect(trainerConversations).toHaveLength(2);
        expect(trainerConversations.every(conv => conv.agentId === 'trainer')).toBe(true);
      });

      it('returns empty array when no conversations exist for agent', () => {
        const { result } = renderHook(() => useChatStore());

        act(() => {
          result.current.createConversation('trainer');
        });

        const conversations = result.current.getConversationsByAgent('nutritionist');

        expect(conversations).toEqual([]);
      });

      it('returns empty array when no conversations exist at all', () => {
        const { result } = renderHook(() => useChatStore());

        const conversations = result.current.getConversationsByAgent('trainer');

        expect(conversations).toEqual([]);
      });
    });

    describe('updateConversationTitle', () => {
      it('updates conversation title', () => {
        const { result } = renderHook(() => useChatStore());

        let conversationId: string;
        act(() => {
          conversationId = result.current.createConversation();
        });

        act(() => {
          result.current.updateConversationTitle(conversationId!, 'Updated Title');
        });

        const conversation = result.current.conversations[0];
        expect(conversation.title).toBe('Updated Title');
        expect(conversation.updatedAt).toBeInstanceOf(Date);
      });

      it('does not affect other conversations', () => {
        const { result } = renderHook(() => useChatStore());

        let firstId: string, secondId: string;
        act(() => {
          firstId = result.current.createConversation();
          secondId = result.current.createConversation();
        });

        act(() => {
          result.current.updateConversationTitle(firstId!, 'First Title');
        });

        expect(result.current.conversations.find(c => c.id === firstId!)?.title).toBe('First Title');
        expect(result.current.conversations.find(c => c.id === secondId!)?.title).toBe('New Conversation');
      });
    });
  });

  describe('message management', () => {
    let conversationId: string;

    beforeEach(() => {
      const { result } = renderHook(() => useChatStore());
      act(() => {
        conversationId = result.current.createConversation();
      });
    });

    describe('addMessage', () => {
      it('adds message to conversation', () => {
        const { result } = renderHook(() => useChatStore());

        let messageId: string;
        act(() => {
          messageId = result.current.addMessage(conversationId, {
            content: 'Hello world',
            role: 'user'
          });
        });

        const conversation = result.current.conversations[0];
        expect(conversation.messages).toHaveLength(1);
        expect(conversation.messages[0]).toMatchObject({
          id: messageId!,
          content: 'Hello world',
          role: 'user',
          timestamp: expect.any(Date)
        });
      });

      it('updates conversation title with first message', () => {
        const { result } = renderHook(() => useChatStore());

        act(() => {
          result.current.addMessage(conversationId, {
            content: 'This is a long message that should be truncated for the title',
            role: 'user'
          });
        });

        const conversation = result.current.conversations[0];
        expect(conversation.title).toBe('This is a long message that should be truncated...');
      });

      it('does not update title for subsequent messages', () => {
        const { result } = renderHook(() => useChatStore());

        act(() => {
          result.current.addMessage(conversationId, {
            content: 'First message',
            role: 'user'
          });
          result.current.addMessage(conversationId, {
            content: 'Second message that should not become title',
            role: 'assistant'
          });
        });

        const conversation = result.current.conversations[0];
        expect(conversation.title).toBe('First message...');
      });

      it('adds message with attachments', () => {
        const { result } = renderHook(() => useChatStore());

        act(() => {
          result.current.addMessage(conversationId, {
            content: 'Check out this image',
            role: 'user',
            attachments: [mockAttachment]
          });
        });

        const message = result.current.conversations[0].messages[0];
        expect(message.attachments).toEqual([mockAttachment]);
      });

      it('adds message with metadata', () => {
        const { result } = renderHook(() => useChatStore());

        const metadata = {
          confidence: 0.95,
          processingTime: 1200,
          tokens: 25,
          agentName: 'Personal Trainer'
        };

        act(() => {
          result.current.addMessage(conversationId, {
            content: 'Response with metadata',
            role: 'assistant',
            metadata
          });
        });

        const message = result.current.conversations[0].messages[0];
        expect(message.metadata).toEqual(metadata);
      });

      it('updates conversation updatedAt timestamp', () => {
        const { result } = renderHook(() => useChatStore());

        const originalUpdatedAt = result.current.conversations[0].updatedAt;

        // Wait a bit to ensure timestamp difference
        setTimeout(() => {
          act(() => {
            result.current.addMessage(conversationId, {
              content: 'New message',
              role: 'user'
            });
          });

          const updatedConversation = result.current.conversations[0];
          expect(updatedConversation.updatedAt.getTime()).toBeGreaterThan(originalUpdatedAt.getTime());
        }, 1);
      });

      it('handles adding message to non-existent conversation', () => {
        const { result } = renderHook(() => useChatStore());

        act(() => {
          result.current.addMessage('non-existent', {
            content: 'Message to nowhere',
            role: 'user'
          });
        });

        // Should not crash and should not affect existing conversations
        expect(result.current.conversations[0].messages).toHaveLength(0);
      });
    });

    describe('updateMessage', () => {
      let messageId: string;

      beforeEach(() => {
        const { result } = renderHook(() => useChatStore());
        act(() => {
          messageId = result.current.addMessage(conversationId, {
            content: 'Original message',
            role: 'user'
          });
        });
      });

      it('updates message content', () => {
        const { result } = renderHook(() => useChatStore());

        act(() => {
          result.current.updateMessage(conversationId, messageId, {
            content: 'Updated message'
          });
        });

        const message = result.current.conversations[0].messages[0];
        expect(message.content).toBe('Updated message');
      });

      it('updates message typing status', () => {
        const { result } = renderHook(() => useChatStore());

        act(() => {
          result.current.updateMessage(conversationId, messageId, {
            isTyping: true
          });
        });

        const message = result.current.conversations[0].messages[0];
        expect(message.isTyping).toBe(true);
      });

      it('updates message metadata', () => {
        const { result } = renderHook(() => useChatStore());

        const newMetadata = {
          confidence: 0.88,
          processingTime: 1500
        };

        act(() => {
          result.current.updateMessage(conversationId, messageId, {
            metadata: newMetadata
          });
        });

        const message = result.current.conversations[0].messages[0];
        expect(message.metadata).toEqual(newMetadata);
      });

      it('updates conversation updatedAt timestamp', () => {
        const { result } = renderHook(() => useChatStore());

        const originalUpdatedAt = result.current.conversations[0].updatedAt;

        setTimeout(() => {
          act(() => {
            result.current.updateMessage(conversationId, messageId, {
              content: 'Updated'
            });
          });

          const conversation = result.current.conversations[0];
          expect(conversation.updatedAt.getTime()).toBeGreaterThan(originalUpdatedAt.getTime());
        }, 1);
      });

      it('handles updating non-existent message', () => {
        const { result } = renderHook(() => useChatStore());

        expect(() => {
          act(() => {
            result.current.updateMessage(conversationId, 'non-existent', {
              content: 'Updated'
            });
          });
        }).not.toThrow();

        // Original message should be unchanged
        const message = result.current.conversations[0].messages[0];
        expect(message.content).toBe('Original message');
      });
    });

    describe('deleteMessage', () => {
      let firstMessageId: string, secondMessageId: string;

      beforeEach(() => {
        const { result } = renderHook(() => useChatStore());
        act(() => {
          firstMessageId = result.current.addMessage(conversationId, {
            content: 'First message',
            role: 'user'
          });
          secondMessageId = result.current.addMessage(conversationId, {
            content: 'Second message',
            role: 'assistant'
          });
        });
      });

      it('removes message from conversation', () => {
        const { result } = renderHook(() => useChatStore());

        expect(result.current.conversations[0].messages).toHaveLength(2);

        act(() => {
          result.current.deleteMessage(conversationId, firstMessageId);
        });

        expect(result.current.conversations[0].messages).toHaveLength(1);
        expect(result.current.conversations[0].messages[0].id).toBe(secondMessageId);
      });

      it('updates conversation updatedAt timestamp', () => {
        const { result } = renderHook(() => useChatStore());

        const originalUpdatedAt = result.current.conversations[0].updatedAt;

        setTimeout(() => {
          act(() => {
            result.current.deleteMessage(conversationId, firstMessageId);
          });

          const conversation = result.current.conversations[0];
          expect(conversation.updatedAt.getTime()).toBeGreaterThan(originalUpdatedAt.getTime());
        }, 1);
      });

      it('handles deleting non-existent message', () => {
        const { result } = renderHook(() => useChatStore());

        expect(() => {
          act(() => {
            result.current.deleteMessage(conversationId, 'non-existent');
          });
        }).not.toThrow();

        expect(result.current.conversations[0].messages).toHaveLength(2);
      });
    });
  });

  describe('UI state management', () => {
    describe('sidebar', () => {
      it('toggles sidebar state', () => {
        const { result } = renderHook(() => useChatStore());

        expect(result.current.sidebarOpen).toBe(true);

        act(() => {
          result.current.toggleSidebar();
        });

        expect(result.current.sidebarOpen).toBe(false);

        act(() => {
          result.current.toggleSidebar();
        });

        expect(result.current.sidebarOpen).toBe(true);
      });

      it('sets sidebar open state directly', () => {
        const { result } = renderHook(() => useChatStore());

        act(() => {
          result.current.setSidebarOpen(false);
        });

        expect(result.current.sidebarOpen).toBe(false);

        act(() => {
          result.current.setSidebarOpen(true);
        });

        expect(result.current.sidebarOpen).toBe(true);
      });
    });

    describe('voice mode', () => {
      it('sets voice mode state', () => {
        const { result } = renderHook(() => useChatStore());

        expect(result.current.isVoiceMode).toBe(false);

        act(() => {
          result.current.setVoiceMode(true);
        });

        expect(result.current.isVoiceMode).toBe(true);

        act(() => {
          result.current.setVoiceMode(false);
        });

        expect(result.current.isVoiceMode).toBe(false);
      });
    });

    describe('typing indicator', () => {
      it('sets typing state', () => {
        const { result } = renderHook(() => useChatStore());

        expect(result.current.isTyping).toBe(false);

        act(() => {
          result.current.setTyping(true);
        });

        expect(result.current.isTyping).toBe(true);

        act(() => {
          result.current.setTyping(false);
        });

        expect(result.current.isTyping).toBe(false);
      });
    });
  });

  describe('computed properties', () => {
    it('currentConversationId reflects activeConversationId', () => {
      const { result } = renderHook(() => useChatStore());

      expect(result.current.currentConversationId).toBeNull();

      act(() => {
        result.current.setActiveConversation('test-id');
      });

      expect(result.current.currentConversationId).toBe('test-id');
    });

    it('setCurrentConversation updates activeConversationId', () => {
      const { result } = renderHook(() => useChatStore());

      act(() => {
        result.current.setCurrentConversation('new-id');
      });

      expect(result.current.activeConversationId).toBe('new-id');
      expect(result.current.currentConversationId).toBe('new-id');
    });
  });

  describe('complex scenarios', () => {
    it('handles full conversation lifecycle', () => {
      const { result } = renderHook(() => useChatStore());

      // Create conversation
      let conversationId: string;
      act(() => {
        conversationId = result.current.createConversation('trainer');
      });

      expect(result.current.conversations).toHaveLength(1);
      expect(result.current.activeConversationId).toBe(conversationId!);

      // Add messages
      let userMessageId: string, assistantMessageId: string;
      act(() => {
        userMessageId = result.current.addMessage(conversationId!, {
          content: 'Hello trainer',
          role: 'user'
        });
        assistantMessageId = result.current.addMessage(conversationId!, {
          content: 'Hello! How can I help you?',
          role: 'assistant',
          metadata: { confidence: 0.95 }
        });
      });

      expect(result.current.conversations[0].messages).toHaveLength(2);
      expect(result.current.conversations[0].title).toBe('Hello trainer...');

      // Update message
      act(() => {
        result.current.updateMessage(conversationId!, assistantMessageId!, {
          isTyping: false
        });
      });

      // Update title
      act(() => {
        result.current.updateConversationTitle(conversationId!, 'Fitness Discussion');
      });

      expect(result.current.conversations[0].title).toBe('Fitness Discussion');

      // Delete message
      act(() => {
        result.current.deleteMessage(conversationId!, userMessageId!);
      });

      expect(result.current.conversations[0].messages).toHaveLength(1);

      // Finally delete conversation
      act(() => {
        result.current.deleteConversation(conversationId!);
      });

      expect(result.current.conversations).toHaveLength(0);
      expect(result.current.activeConversationId).toBeNull();
    });

    it('handles multiple conversations with different agents', () => {
      const { result } = renderHook(() => useChatStore());

      let trainerId: string, nutritionistId: string;
      act(() => {
        trainerId = result.current.createConversation('trainer');
        nutritionistId = result.current.createConversation('nutritionist');
      });

      // Add messages to both conversations
      act(() => {
        result.current.addMessage(trainerId!, {
          content: 'Training question',
          role: 'user'
        });
        result.current.addMessage(nutritionistId!, {
          content: 'Nutrition question',
          role: 'user'
        });
      });

      // Check conversations by agent
      const trainerConversations = result.current.getConversationsByAgent('trainer');
      const nutritionistConversations = result.current.getConversationsByAgent('nutritionist');

      expect(trainerConversations).toHaveLength(1);
      expect(nutritionistConversations).toHaveLength(1);
      expect(trainerConversations[0].messages[0].content).toBe('Training question');
      expect(nutritionistConversations[0].messages[0].content).toBe('Nutrition question');
    });
  });

  describe('edge cases', () => {
    it('handles empty message content gracefully', () => {
      const { result } = renderHook(() => useChatStore());

      let conversationId: string;
      act(() => {
        conversationId = result.current.createConversation();
      });

      act(() => {
        result.current.addMessage(conversationId!, {
          content: '',
          role: 'user'
        });
      });

      const conversation = result.current.conversations[0];
      expect(conversation.messages[0].content).toBe('');
      expect(conversation.title).toBe('...');
    });

    it('handles very long message content in title', () => {
      const { result } = renderHook(() => useChatStore());

      let conversationId: string;
      act(() => {
        conversationId = result.current.createConversation();
      });

      const longMessage = 'A'.repeat(100);
      act(() => {
        result.current.addMessage(conversationId!, {
          content: longMessage,
          role: 'user'
        });
      });

      const conversation = result.current.conversations[0];
      expect(conversation.title).toBe(longMessage.slice(0, 50) + '...');
      expect(conversation.title.length).toBe(53); // 50 + '...'
    });
  });
});
