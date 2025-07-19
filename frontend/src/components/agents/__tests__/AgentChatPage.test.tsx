import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { AgentChatPage } from '../AgentChatPage';
import { useAgentStore } from '@/store/agentStore';
import { ChatLayout } from '@/components/layout/ChatLayout';

// Mock the store and components
jest.mock('@/store/agentStore');
jest.mock('@/components/layout/ChatLayout');

// Mock react-router-dom hooks
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  Navigate: ({ to, replace }: { to: string; replace?: boolean }) => {
    mockNavigate(to, { replace });
    return null;
  },
}));

describe('AgentChatPage Component', () => {
  const mockGetAgent = jest.fn();
  const mockSetActiveAgent = jest.fn();

  const mockAgent = {
    id: 'test-agent',
    name: 'Test Agent',
    role: 'Testing',
    description: 'Agent for testing',
    icon: 'Star',
    personality: 'Helpful',
    primaryColor: 'blue',
    isActive: true,
  };

  const mockStoreState = {
    agents: [mockAgent],
    activeAgentId: 'test-agent',
    orchestratorActive: false,
    agentHistory: [],
    getAgent: mockGetAgent,
    setActiveAgent: mockSetActiveAgent,
    toggleOrchestrator: jest.fn(),
    addAgentMessage: jest.fn(),
    getActiveAgent: jest.fn(),
    analyzeUserIntent: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (useAgentStore as unknown as jest.Mock).mockReturnValue(mockStoreState);
    (ChatLayout as jest.Mock).mockReturnValue(<div>Chat Layout</div>);
  });

  const renderWithRouter = (
    ui: React.ReactElement,
    { initialEntries = ['/chat/test-agent'] } = {}
  ) => {
    return render(
      <MemoryRouter initialEntries={initialEntries}>
        <Routes>
          <Route path="/chat/:agentId" element={ui} />
          <Route path="/chat/orchestrator" element={<div>Orchestrator</div>} />
        </Routes>
      </MemoryRouter>
    );
  };

  it('renders ChatLayout when agent exists', async () => {
    mockGetAgent.mockReturnValue(mockAgent);
    
    renderWithRouter(<AgentChatPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Chat Layout')).toBeInTheDocument();
    });
  });

  it('sets active agent on mount', async () => {
    mockGetAgent.mockReturnValue(mockAgent);
    
    renderWithRouter(<AgentChatPage />);
    
    await waitFor(() => {
      expect(mockGetAgent).toHaveBeenCalledWith('test-agent');
      expect(mockSetActiveAgent).toHaveBeenCalledWith('test-agent');
    });
  });

  it('redirects to orchestrator when agent does not exist', async () => {
    mockGetAgent.mockReturnValue(undefined);
    
    renderWithRouter(<AgentChatPage />);
    
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/chat/orchestrator', { replace: true });
    });
  });

  it('does not set active agent when agent does not exist', async () => {
    mockGetAgent.mockReturnValue(undefined);
    
    renderWithRouter(<AgentChatPage />);
    
    await waitFor(() => {
      expect(mockGetAgent).toHaveBeenCalledWith('test-agent');
      expect(mockSetActiveAgent).not.toHaveBeenCalled();
    });
  });

  it('handles undefined agentId parameter', async () => {
    renderWithRouter(<AgentChatPage />, { initialEntries: ['/chat/'] });
    
    // Should not crash and should render ChatLayout
    expect(screen.getByText('Chat Layout')).toBeInTheDocument();
    expect(mockGetAgent).not.toHaveBeenCalled();
    expect(mockSetActiveAgent).not.toHaveBeenCalled();
  });

  it('updates when agentId parameter changes', async () => {
    mockGetAgent.mockReturnValue(mockAgent);
    
    const { rerender } = render(
      <MemoryRouter initialEntries={['/chat/test-agent']}>
        <Routes>
          <Route path="/chat/:agentId" element={<AgentChatPage />} />
        </Routes>
      </MemoryRouter>
    );
    
    expect(mockSetActiveAgent).toHaveBeenCalledWith('test-agent');
    
    // Change to different agent
    const newAgent = { ...mockAgent, id: 'new-agent' };
    mockGetAgent.mockReturnValue(newAgent);
    
    rerender(
      <MemoryRouter initialEntries={['/chat/new-agent']}>
        <Routes>
          <Route path="/chat/:agentId" element={<AgentChatPage />} />
        </Routes>
      </MemoryRouter>
    );
    
    await waitFor(() => {
      expect(mockSetActiveAgent).toHaveBeenCalledWith('new-agent');
    });
  });

  it('calls getAgent and setActiveAgent in correct order', async () => {
    let getAgentCallOrder = 0;
    let setActiveAgentCallOrder = 0;
    let callOrder = 0;
    
    mockGetAgent.mockImplementation((id) => {
      getAgentCallOrder = ++callOrder;
      return id === 'test-agent' ? mockAgent : undefined;
    });
    
    mockSetActiveAgent.mockImplementation(() => {
      setActiveAgentCallOrder = ++callOrder;
    });
    
    renderWithRouter(<AgentChatPage />);
    
    await waitFor(() => {
      expect(getAgentCallOrder).toBeLessThan(setActiveAgentCallOrder);
    });
  });

  it('handles orchestrator agent correctly', async () => {
    const orchestratorAgent = {
      ...mockAgent,
      id: 'orchestrator',
      name: 'Orchestrator',
    };
    
    mockGetAgent.mockReturnValue(orchestratorAgent);
    
    renderWithRouter(<AgentChatPage />, { initialEntries: ['/chat/orchestrator'] });
    
    await waitFor(() => {
      expect(mockGetAgent).toHaveBeenCalledWith('orchestrator');
      expect(mockSetActiveAgent).toHaveBeenCalledWith('orchestrator');
      expect(screen.getByText('Chat Layout')).toBeInTheDocument();
    });
  });

  it('cleans up properly on unmount', async () => {
    mockGetAgent.mockReturnValue(mockAgent);
    
    const { unmount } = renderWithRouter(<AgentChatPage />);
    
    await waitFor(() => {
      expect(mockSetActiveAgent).toHaveBeenCalledWith('test-agent');
    });
    
    unmount();
    
    // Ensure no memory leaks or additional calls after unmount
    expect(mockSetActiveAgent).toHaveBeenCalledTimes(1);
  });

  it('handles rapid agent changes correctly', async () => {
    mockGetAgent.mockImplementation((id) => {
      if (id === 'agent1') return { ...mockAgent, id: 'agent1' };
      if (id === 'agent2') return { ...mockAgent, id: 'agent2' };
      if (id === 'agent3') return { ...mockAgent, id: 'agent3' };
      return undefined;
    });
    
    const { rerender } = render(
      <MemoryRouter initialEntries={['/chat/agent1']}>
        <Routes>
          <Route path="/chat/:agentId" element={<AgentChatPage />} />
        </Routes>
      </MemoryRouter>
    );
    
    // Rapid changes
    rerender(
      <MemoryRouter initialEntries={['/chat/agent2']}>
        <Routes>
          <Route path="/chat/:agentId" element={<AgentChatPage />} />
        </Routes>
      </MemoryRouter>
    );
    
    rerender(
      <MemoryRouter initialEntries={['/chat/agent3']}>
        <Routes>
          <Route path="/chat/:agentId" element={<AgentChatPage />} />
        </Routes>
      </MemoryRouter>
    );
    
    await waitFor(() => {
      // Should handle all changes correctly
      expect(mockSetActiveAgent).toHaveBeenCalledWith('agent1');
      expect(mockSetActiveAgent).toHaveBeenCalledWith('agent2');
      expect(mockSetActiveAgent).toHaveBeenCalledWith('agent3');
    });
  });

  it('handles special characters in agentId', async () => {
    const specialAgent = {
      ...mockAgent,
      id: 'agent-with-special_chars.123',
    };
    
    mockGetAgent.mockReturnValue(specialAgent);
    
    renderWithRouter(<AgentChatPage />, { 
      initialEntries: ['/chat/agent-with-special_chars.123'] 
    });
    
    await waitFor(() => {
      expect(mockGetAgent).toHaveBeenCalledWith('agent-with-special_chars.123');
      expect(mockSetActiveAgent).toHaveBeenCalledWith('agent-with-special_chars.123');
    });
  });

  it('handles case sensitivity in agentId', async () => {
    mockGetAgent.mockImplementation((id) => {
      // Simulate case-sensitive agent lookup
      return id === 'TestAgent' ? { ...mockAgent, id: 'TestAgent' } : undefined;
    });
    
    // Test with correct case
    renderWithRouter(<AgentChatPage />, { initialEntries: ['/chat/TestAgent'] });
    
    await waitFor(() => {
      expect(screen.getByText('Chat Layout')).toBeInTheDocument();
    });
    
    // Test with incorrect case
    mockGetAgent.mockClear();
    mockSetActiveAgent.mockClear();
    
    renderWithRouter(<AgentChatPage />, { initialEntries: ['/chat/testagent'] });
    
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/chat/orchestrator', { replace: true });
    });
  });

  it('handles empty string agentId', async () => {
    renderWithRouter(<AgentChatPage />, { initialEntries: ['/chat/'] });
    
    // Should render ChatLayout without errors
    expect(screen.getByText('Chat Layout')).toBeInTheDocument();
    expect(mockGetAgent).not.toHaveBeenCalled();
    expect(mockSetActiveAgent).not.toHaveBeenCalled();
  });

  it('handles very long agentId', async () => {
    const longId = 'a'.repeat(100);
    const longAgent = { ...mockAgent, id: longId };
    
    mockGetAgent.mockReturnValue(longAgent);
    
    renderWithRouter(<AgentChatPage />, { initialEntries: [`/chat/${longId}`] });
    
    await waitFor(() => {
      expect(mockGetAgent).toHaveBeenCalledWith(longId);
      expect(mockSetActiveAgent).toHaveBeenCalledWith(longId);
    });
  });

  it('maintains correct behavior when store state changes', async () => {
    mockGetAgent.mockReturnValue(mockAgent);
    
    const { rerender } = renderWithRouter(<AgentChatPage />);
    
    // Change store state
    const updatedStoreState = {
      ...mockStoreState,
      activeAgentId: 'different-agent',
      orchestratorActive: true,
    };
    
    (useAgentStore as unknown as jest.Mock).mockReturnValue(updatedStoreState);
    
    rerender(<AgentChatPage />);
    
    // Should still render correctly
    expect(screen.getByText('Chat Layout')).toBeInTheDocument();
  });
});