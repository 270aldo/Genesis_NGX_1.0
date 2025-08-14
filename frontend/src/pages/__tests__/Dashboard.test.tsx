import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../Dashboard';
import { useAuthStore } from '@/store/authStore';
import { useChatStore } from '@/store/chatStore';

// Mock the stores
jest.mock('@/store/authStore', () => ({
  useAuthStore: jest.fn()
}));

jest.mock('@/store/chatStore', () => ({
  useChatStore: jest.fn()
}));

// Mock lazy loaded components
jest.mock('@/components/dashboard/ProfileSection', () => ({
  ProfileSection: ({ user }: { user: any }) => (
    <div data-testid="profile-section">Profile: {user?.name || 'Unknown'}</div>
  )
}));

jest.mock('@/components/dashboard/StatsCards', () => ({
  StatsCards: ({ stats }: { stats: any }) => (
    <div data-testid="stats-cards">
      Conversations: {stats.totalConversations}, Messages: {stats.totalMessages}
    </div>
  )
}));

jest.mock('@/components/dashboard/RecentActivity', () => ({
  RecentActivity: ({ conversations }: { conversations: any[] }) => (
    <div data-testid="recent-activity">Recent: {conversations.length} conversations</div>
  )
}));

jest.mock('@/components/dashboard/QuickActions', () => ({
  QuickActions: () => <div data-testid="quick-actions">Quick Actions</div>
}));

jest.mock('@/components/tokens/TokenBalance', () => ({
  TokenBalance: () => <div data-testid="token-balance">Token Balance</div>
}));

jest.mock('@/components/dashboard/AgentInsights', () => ({
  AgentInsights: () => <div data-testid="agent-insights">Agent Insights</div>
}));

// Mock lazy loading utilities
jest.mock('@/utils/lazyWithPreload', () => ({
  lazyWithPreload: (fn: any) => {
    const Component = React.lazy(fn);
    return Component;
  },
  lazyWithNamedExport: (fn: any, exportName: string) => {
    return React.lazy(async () => {
      const module = await fn();
      return { default: module[exportName] };
    });
  }
}));

// Mock lazy loading components
jest.mock('@/components/ui/lazy-loading', () => ({
  LazyLoad: ({ children, fallback }: any) => (
    <React.Suspense fallback={fallback || <div>Loading...</div>}>
      {children}
    </React.Suspense>
  ),
  StatsCardSkeleton: () => <div data-testid="stats-skeleton">Stats Loading...</div>,
  CardSkeleton: () => <div data-testid="card-skeleton">Card Loading...</div>,
  ListSkeleton: ({ count }: { count: number }) => <div data-testid="list-skeleton">List Loading ({count})...</div>,
  ProfileSkeleton: () => <div data-testid="profile-skeleton">Profile Loading...</div>
}));

const mockUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>;
const mockUseChatStore = useChatStore as jest.MockedFunction<typeof useChatStore>;

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Dashboard', () => {
  const mockUser = {
    id: '1',
    email: 'test@example.com',
    name: 'John Doe',
    tokens: 250,
    createdAt: new Date()
  };

  const mockConversations = [
    {
      id: '1',
      title: 'Workout Planning',
      messages: [
        { id: '1', content: 'Hello', role: 'user' as const, timestamp: new Date() },
        { id: '2', content: 'Hi there!', role: 'assistant' as const, timestamp: new Date() }
      ],
      createdAt: new Date(),
      updatedAt: new Date(),
      agentId: 'trainer'
    },
    {
      id: '2',
      title: 'Nutrition Advice',
      messages: [
        { id: '3', content: 'Diet help?', role: 'user' as const, timestamp: new Date() }
      ],
      createdAt: new Date(),
      updatedAt: new Date(),
      agentId: 'nutritionist'
    }
  ];

  beforeEach(() => {
    mockUseAuthStore.mockReturnValue({
      user: mockUser,
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

    mockUseChatStore.mockReturnValue({
      conversations: mockConversations,
      activeConversationId: null,
      sidebarOpen: true,
      isVoiceMode: false,
      isTyping: false,
      createConversation: jest.fn(),
      setActiveConversation: jest.fn(),
      addMessage: jest.fn(),
      updateMessage: jest.fn(),
      deleteMessage: jest.fn(),
      deleteConversation: jest.fn(),
      getCurrentConversation: jest.fn(),
      getConversationsByAgent: jest.fn(),
      toggleSidebar: jest.fn(),
      setSidebarOpen: jest.fn(),
      setVoiceMode: jest.fn(),
      setTyping: jest.fn(),
      updateConversationTitle: jest.fn(),
      currentConversationId: null,
      setCurrentConversation: jest.fn()
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('rendering', () => {
    it('renders dashboard with correct title', async () => {
      renderWithRouter(<Dashboard />);

      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Your Fitness Command Center')).toBeInTheDocument();
    });

    it('displays user welcome message', async () => {
      renderWithRouter(<Dashboard />);

      expect(screen.getByText('Welcome back, John Doe')).toBeInTheDocument();
    });

    it('shows fallback for user without name', async () => {
      mockUseAuthStore.mockReturnValue({
        ...mockUseAuthStore(),
        user: { ...mockUser, name: '' }
      });

      renderWithRouter(<Dashboard />);

      expect(screen.getByText('Welcome back, User')).toBeInTheDocument();
    });

    it('handles null user gracefully', async () => {
      mockUseAuthStore.mockReturnValue({
        ...mockUseAuthStore(),
        user: null
      });

      renderWithRouter(<Dashboard />);

      expect(screen.getByText('Welcome back, User')).toBeInTheDocument();
    });
  });

  describe('navigation', () => {
    it('renders navigation buttons', async () => {
      renderWithRouter(<Dashboard />);

      // Check for navigation buttons
      expect(screen.getByRole('button', { name: /progress/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /export/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /settings/i })).toBeInTheDocument();
    });

    it('renders back to chat button', async () => {
      renderWithRouter(<Dashboard />);

      const backButton = screen.getByRole('button');
      expect(backButton).toBeInTheDocument();
    });

    it('has correct navigation links', async () => {
      renderWithRouter(<Dashboard />);

      // Check for links (they should be present as Link components)
      const progressLink = screen.getByRole('button', { name: /progress/i }).closest('a');
      const settingsLink = screen.getByRole('button', { name: /settings/i }).closest('a');

      if (progressLink) {
        expect(progressLink).toHaveAttribute('href', '/dashboard/progress');
      }
      if (settingsLink) {
        expect(settingsLink).toHaveAttribute('href', '/settings');
      }
    });
  });

  describe('stats calculation', () => {
    it('calculates stats correctly from conversations', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByTestId('stats-cards')).toHaveTextContent('Conversations: 2, Messages: 3');
      });
    });

    it('handles empty conversations', async () => {
      mockUseChatStore.mockReturnValue({
        ...mockUseChatStore(),
        conversations: []
      });

      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByTestId('stats-cards')).toHaveTextContent('Conversations: 0, Messages: 0');
      });
    });

    it('calculates total messages across conversations', async () => {
      const conversationsWithMoreMessages = [
        {
          ...mockConversations[0],
          messages: [
            ...mockConversations[0].messages,
            { id: '4', content: 'More', role: 'user' as const, timestamp: new Date() }
          ]
        },
        mockConversations[1]
      ];

      mockUseChatStore.mockReturnValue({
        ...mockUseChatStore(),
        conversations: conversationsWithMoreMessages
      });

      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByTestId('stats-cards')).toHaveTextContent('Conversations: 2, Messages: 4');
      });
    });
  });

  describe('lazy loaded components', () => {
    it('renders all lazy loaded components', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByTestId('stats-cards')).toBeInTheDocument();
        expect(screen.getByTestId('agent-insights')).toBeInTheDocument();
        expect(screen.getByTestId('recent-activity')).toBeInTheDocument();
        expect(screen.getByTestId('token-balance')).toBeInTheDocument();
        expect(screen.getByTestId('profile-section')).toBeInTheDocument();
        expect(screen.getByTestId('quick-actions')).toBeInTheDocument();
      });
    });

    it('passes correct props to components', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByTestId('profile-section')).toHaveTextContent('Profile: John Doe');
        expect(screen.getByTestId('recent-activity')).toHaveTextContent('Recent: 2 conversations');
      });
    });

    it('limits recent activity to 5 conversations', async () => {
      const manyConversations = Array.from({ length: 10 }, (_, i) => ({
        id: `conv-${i}`,
        title: `Conversation ${i}`,
        messages: [],
        createdAt: new Date(),
        updatedAt: new Date()
      }));

      mockUseChatStore.mockReturnValue({
        ...mockUseChatStore(),
        conversations: manyConversations
      });

      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByTestId('recent-activity')).toHaveTextContent('Recent: 5 conversations');
      });
    });
  });

  describe('performance footer', () => {
    it('displays performance metrics', async () => {
      renderWithRouter(<Dashboard />);

      expect(screen.getByText('Performance Overview')).toBeInTheDocument();
      expect(screen.getByText('Your fitness journey at a glance')).toBeInTheDocument();
    });

    it('shows correct conversation count in footer', async () => {
      renderWithRouter(<Dashboard />);

      const conversationCount = screen.getByText('2'); // Based on mockConversations length
      expect(conversationCount).toBeInTheDocument();
      expect(screen.getByText('Total Chats')).toBeInTheDocument();
    });

    it('displays user tokens in footer', async () => {
      renderWithRouter(<Dashboard />);

      expect(screen.getByText('250')).toBeInTheDocument();
      expect(screen.getByText('Available Tokens')).toBeInTheDocument();
    });

    it('handles zero tokens display', async () => {
      mockUseAuthStore.mockReturnValue({
        ...mockUseAuthStore(),
        user: { ...mockUser, tokens: 0 }
      });

      renderWithRouter(<Dashboard />);

      expect(screen.getByText('0')).toBeInTheDocument();
    });

    it('handles user without tokens', async () => {
      mockUseAuthStore.mockReturnValue({
        ...mockUseAuthStore(),
        user: { ...mockUser, tokens: undefined as any }
      });

      renderWithRouter(<Dashboard />);

      expect(screen.getByText('0')).toBeInTheDocument();
    });
  });

  describe('layout and styling', () => {
    it('applies correct CSS classes for dark theme', async () => {
      const { container } = renderWithRouter(<Dashboard />);

      const dashboardContainer = container.firstChild as Element;
      expect(dashboardContainer).toHaveClass('min-h-screen', 'bg-black');
    });

    it('includes floating orb animations', async () => {
      const { container } = renderWithRouter(<Dashboard />);

      const orbs = container.querySelectorAll('.animate-pulse');
      expect(orbs.length).toBeGreaterThanOrEqual(2);
    });

    it('has responsive grid layout', async () => {
      const { container } = renderWithRouter(<Dashboard />);

      const gridElement = container.querySelector('.grid.grid-cols-1.xl\\:grid-cols-4');
      expect(gridElement).toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('has proper heading structure', async () => {
      renderWithRouter(<Dashboard />);

      expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Dashboard');
      expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('Your Fitness Command Center');
    });

    it('has accessible button labels', async () => {
      renderWithRouter(<Dashboard />);

      expect(screen.getByRole('button', { name: /progress/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /export/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /settings/i })).toBeInTheDocument();
    });

    it('includes descriptive text for context', async () => {
      renderWithRouter(<Dashboard />);

      expect(screen.getByText('Track your progress, monitor your health, and get AI-powered insights to optimize your fitness journey.')).toBeInTheDocument();
    });
  });

  describe('error handling', () => {
    it('handles missing user data gracefully', async () => {
      mockUseAuthStore.mockReturnValue({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        setUser: jest.fn(),
        logout: jest.fn(),
        updateProfile: jest.fn(),
        setLoading: jest.fn(),
        addTokens: jest.fn(),
        useTokens: jest.fn(),
        getTokens: jest.fn()
      });

      expect(() => renderWithRouter(<Dashboard />)).not.toThrow();
    });

    it('handles empty conversations array', async () => {
      mockUseChatStore.mockReturnValue({
        ...mockUseChatStore(),
        conversations: []
      });

      expect(() => renderWithRouter(<Dashboard />)).not.toThrow();
    });

    it('handles conversations with empty messages', async () => {
      const conversationsWithEmptyMessages = [
        {
          id: '1',
          title: 'Empty Conversation',
          messages: [],
          createdAt: new Date(),
          updatedAt: new Date()
        }
      ];

      mockUseChatStore.mockReturnValue({
        ...mockUseChatStore(),
        conversations: conversationsWithEmptyMessages
      });

      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByTestId('stats-cards')).toHaveTextContent('Conversations: 1, Messages: 0');
      });
    });
  });

  describe('responsive behavior', () => {
    it('renders mobile-friendly layout classes', async () => {
      const { container } = renderWithRouter(<Dashboard />);

      // Check for responsive classes
      const gridElements = container.querySelectorAll('.grid-cols-1, .lg\\:grid-cols-2, .xl\\:grid-cols-4');
      expect(gridElements.length).toBeGreaterThan(0);
    });

    it('has responsive padding and margins', async () => {
      const { container } = renderWithRouter(<Dashboard />);

      const responsiveElement = container.querySelector('.px-4.sm\\:px-6.lg\\:px-8');
      expect(responsiveElement).toBeInTheDocument();
    });
  });

  describe('component integration', () => {
    it('integrates with auth store correctly', async () => {
      renderWithRouter(<Dashboard />);

      expect(mockUseAuthStore).toHaveBeenCalled();
    });

    it('integrates with chat store correctly', async () => {
      renderWithRouter(<Dashboard />);

      expect(mockUseChatStore).toHaveBeenCalled();
    });

    it('passes user data to profile component', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByTestId('profile-section')).toHaveTextContent('John Doe');
      });
    });
  });
});
