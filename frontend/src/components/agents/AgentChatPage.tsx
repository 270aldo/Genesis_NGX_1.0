
import React from 'react';
import { useParams, Navigate } from 'react-router-dom';
import { ChatLayout } from '@/components/layout/ChatLayout';
import { useAgentStore } from '@/store/agentStore';

export const AgentChatPage: React.FC = () => {
  const { agentId } = useParams<{ agentId: string }>();
  const { getAgent, setActiveAgent } = useAgentStore();

  React.useEffect(() => {
    if (agentId) {
      const agent = getAgent(agentId);
      if (agent) {
        setActiveAgent(agentId);
      }
    }
  }, [agentId, getAgent, setActiveAgent]);

  // Redirect to orchestrator if agent doesn't exist
  if (agentId && !getAgent(agentId)) {
    return <Navigate to="/chat/orchestrator" replace />;
  }

  return <ChatLayout />;
};
