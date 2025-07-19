
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface FileAttachment {
  id: string;
  name: string;
  type: string;
  size: number;
  url: string;
  preview?: string;
}

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  agentId?: string;
  isTyping?: boolean;
  attachments?: FileAttachment[];
  metadata?: {
    confidence?: number;
    processingTime?: number;
    tokens?: number;
    agentName?: string;
    agentAvatar?: string;
  };
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
  agentId?: string;
}

interface ChatState {
  conversations: Conversation[];
  activeConversationId: string | null;
  sidebarOpen: boolean;
  isVoiceMode: boolean;
  isTyping: boolean;

  // Actions
  createConversation: (agentId?: string) => string;
  setActiveConversation: (id: string) => void;
  addMessage: (conversationId: string, message: Omit<Message, 'id' | 'timestamp'>) => string;
  updateMessage: (conversationId: string, messageId: string, updates: Partial<Message>) => void;
  deleteMessage: (conversationId: string, messageId: string) => void;
  deleteConversation: (id: string) => void;
  getCurrentConversation: () => Conversation | null;
  getConversationsByAgent: (agentId: string) => Conversation[];
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setVoiceMode: (enabled: boolean) => void;
  setTyping: (typing: boolean) => void;
  updateConversationTitle: (id: string, title: string) => void;
  
  // Computed properties
  currentConversationId: string | null;
  setCurrentConversation: (id: string) => void;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      conversations: [],
      activeConversationId: null,
      sidebarOpen: true,
      isVoiceMode: false,
      isTyping: false,

      get currentConversationId() {
        return get().activeConversationId;
      },

      setCurrentConversation: (id: string) => {
        set({ activeConversationId: id });
      },

      createConversation: (agentId?: string) => {
        const id = Date.now().toString();
        const newConversation: Conversation = {
          id,
          title: 'New Conversation',
          messages: [],
          createdAt: new Date(),
          updatedAt: new Date(),
          agentId,
        };

        set((state) => ({
          conversations: [newConversation, ...state.conversations],
          activeConversationId: id,
        }));

        return id;
      },

      setActiveConversation: (id: string) => {
        set({ activeConversationId: id });
      },

      addMessage: (conversationId: string, message: Omit<Message, 'id' | 'timestamp'>) => {
        const messageId = Date.now().toString();
        const newMessage: Message = {
          ...message,
          id: messageId,
          timestamp: new Date(),
        };

        set((state) => ({
          conversations: state.conversations.map((conv) =>
            conv.id === conversationId
              ? {
                  ...conv,
                  messages: [...conv.messages, newMessage],
                  updatedAt: new Date(),
                  title: conv.messages.length === 0 ? message.content.slice(0, 50) + '...' : conv.title,
                }
              : conv
          ),
        }));

        return messageId;
      },

      updateMessage: (conversationId: string, messageId: string, updates: Partial<Message>) => {
        set((state) => ({
          conversations: state.conversations.map((conv) =>
            conv.id === conversationId
              ? {
                  ...conv,
                  messages: conv.messages.map((msg) =>
                    msg.id === messageId
                      ? { ...msg, ...updates }
                      : msg
                  ),
                  updatedAt: new Date(),
                }
              : conv
          ),
        }));
      },

      deleteMessage: (conversationId: string, messageId: string) => {
        set((state) => ({
          conversations: state.conversations.map((conv) =>
            conv.id === conversationId
              ? {
                  ...conv,
                  messages: conv.messages.filter((msg) => msg.id !== messageId),
                  updatedAt: new Date(),
                }
              : conv
          ),
        }));
      },

      deleteConversation: (id: string) => {
        set((state) => ({
          conversations: state.conversations.filter((conv) => conv.id !== id),
          activeConversationId: state.activeConversationId === id ? null : state.activeConversationId,
        }));
      },

      getCurrentConversation: () => {
        const state = get();
        return state.conversations.find((conv) => conv.id === state.activeConversationId) || null;
      },

      getConversationsByAgent: (agentId: string) => {
        const state = get();
        return state.conversations.filter((conv) => conv.agentId === agentId);
      },

      toggleSidebar: () => {
        set((state) => ({ sidebarOpen: !state.sidebarOpen }));
      },

      setSidebarOpen: (open: boolean) => {
        set({ sidebarOpen: open });
      },

      setVoiceMode: (enabled: boolean) => {
        set({ isVoiceMode: enabled });
      },

      setTyping: (typing: boolean) => {
        set({ isTyping: typing });
      },

      updateConversationTitle: (id: string, title: string) => {
        set((state) => ({
          conversations: state.conversations.map((conv) =>
            conv.id === id
              ? { ...conv, title, updatedAt: new Date() }
              : conv
          ),
        }));
      },
    }),
    {
      name: 'ngx-agents-chat',
      partialize: (state) => ({
        conversations: state.conversations,
        activeConversationId: state.activeConversationId,
        sidebarOpen: state.sidebarOpen,
      }),
    }
  )
);
