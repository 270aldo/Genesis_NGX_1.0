import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { Sidebar } from '../Sidebar';
import { useChatStore } from '@/store/chatStore';
import { useAuthStore } from '@/store/authStore';

jest.mock('@/store/chatStore', () => ({
  useChatStore: jest.fn()
}));

jest.mock('@/store/authStore', () => ({
  useAuthStore: jest.fn()
}));

const mockUseChatStore = useChatStore as jest.MockedFunction<typeof useChatStore>;
const mockUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>;

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Sidebar', () => {
  const mockConversations = [
    {
      id: '1',
      title: 'Workout Planning',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
      agentId: 'trainer'
    },
    {
      id: '2',
      title: 'Nutrition Questions',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
      agentId: 'nutritionist'
    }
  ];

  beforeEach(() => {
    mockUseChatStore.mockReturnValue({
      conversations: mockConversations,
      sidebarOpen: true,
      createConversation: jest.fn(),
      setActiveConversation: jest.fn(),
      toggleSidebar: jest.fn(),
      activeConversationId: null,
      isVoiceMode: false,
      isTyping: false,
      addMessage: jest.fn(),
      updateMessage: jest.fn(),
      deleteMessage: jest.fn(),
      deleteConversation: jest.fn(),
      getCurrentConversation: jest.fn(),
      getConversationsByAgent: jest.fn(),
      setSidebarOpen: jest.fn(),
      setVoiceMode: jest.fn(),
      setTyping: jest.fn(),
      updateConversationTitle: jest.fn(),
      currentConversationId: null,
      setCurrentConversation: jest.fn()
    });

    mockUseAuthStore.mockReturnValue({
      user: { id: '1', name: 'Test User', email: 'test@example.com' },
      isAuthenticated: true,
      isLoading: false,
      setUser: jest.fn(),
      logout: jest.fn(),
      updateProfile: jest.fn(),
      setLoading: jest.fn(),
      addTokens: jest.fn(),
      useTokens: jest.fn(),
      getTokens: jest.fn()
    });

    jest.clearAllMocks();
  });

  it('displays conversation list', () => {
    renderWithRouter(<Sidebar />);

    expect(screen.getByText('Workout Planning')).toBeInTheDocument();
    expect(screen.getByText('Nutrition Questions')).toBeInTheDocument();
  });

  it('shows new conversation button', () => {
    renderWithRouter(<Sidebar />);

    expect(screen.getByRole('button', { name: /new conversation/i })).toBeInTheDocument();
  });

  it('displays user information', () => {
    renderWithRouter(<Sidebar />);

    expect(screen.getByText('Test User')).toBeInTheDocument();
  });

  it('hides when sidebar is closed', () => {
    mockUseChatStore.mockReturnValue({
      ...mockUseChatStore(),
      sidebarOpen: false
    });

    const { container } = renderWithRouter(<Sidebar />);

    expect(container.firstChild).toHaveClass('hidden');
  });

  it('creates new conversation when button is clicked', async () => {
    const user = userEvent.setup();
    const mockCreateConversation = jest.fn();

    mockUseChatStore.mockReturnValue({
      ...mockUseChatStore(),
      createConversation: mockCreateConversation
    });

    renderWithRouter(<Sidebar />);

    const newConversationButton = screen.getByRole('button', { name: /new conversation/i });
    await user.click(newConversationButton);

    expect(mockCreateConversation).toHaveBeenCalled();
  });
});
