import React from 'react';
import { render, screen } from '@testing-library/react';
import { AgentCollaborationIndicator } from '../AgentCollaborationIndicator';

const mockCollaborationData = {
  activeAgents: [
    { id: 'trainer', name: 'Personal Trainer', status: 'active' },
    { id: 'nutritionist', name: 'Nutritionist', status: 'consulting' },
    { id: 'progress', name: 'Progress Tracker', status: 'standby' }
  ],
  collaborationMode: 'multi-agent' as const
};

describe('AgentCollaborationIndicator', () => {
  it('displays active agents', () => {
    render(<AgentCollaborationIndicator data={mockCollaborationData} />);

    expect(screen.getByText('Personal Trainer')).toBeInTheDocument();
    expect(screen.getByText('Nutritionist')).toBeInTheDocument();
    expect(screen.getByText('Progress Tracker')).toBeInTheDocument();
  });

  it('shows agent status indicators', () => {
    render(<AgentCollaborationIndicator data={mockCollaborationData} />);

    expect(screen.getByText(/active/i)).toBeInTheDocument();
    expect(screen.getByText(/consulting/i)).toBeInTheDocument();
    expect(screen.getByText(/standby/i)).toBeInTheDocument();
  });

  it('displays collaboration mode', () => {
    render(<AgentCollaborationIndicator data={mockCollaborationData} />);

    expect(screen.getByText(/multi-agent/i)).toBeInTheDocument();
  });

  it('shows agent count', () => {
    render(<AgentCollaborationIndicator data={mockCollaborationData} />);

    expect(screen.getByText('3 agents')).toBeInTheDocument();
  });

  it('handles single agent mode', () => {
    const singleAgentData = {
      ...mockCollaborationData,
      activeAgents: [mockCollaborationData.activeAgents[0]],
      collaborationMode: 'single-agent' as const
    };

    render(<AgentCollaborationIndicator data={singleAgentData} />);

    expect(screen.getByText(/single-agent/i)).toBeInTheDocument();
    expect(screen.getByText('1 agent')).toBeInTheDocument();
  });

  it('displays no agents when empty', () => {
    const emptyData = {
      activeAgents: [],
      collaborationMode: 'single-agent' as const
    };

    render(<AgentCollaborationIndicator data={emptyData} />);

    expect(screen.getByText(/no active agents/i)).toBeInTheDocument();
  });
});
