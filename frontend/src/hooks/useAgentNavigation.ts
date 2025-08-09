
/**
 * Agent Navigation Hook
 * Handles navigation between agents with NEXUS-only mode support
 * Routes all interactions through NEXUS when enabled
 */

import { useNavigate } from 'react-router-dom';
import { useAgentStore } from '@/store/agentStore';
import { useFeatureFlags } from '@/hooks/useFeatureFlags';
import { FITNESS_AGENTS } from '@/data/agents';

export const useAgentNavigation = () => {
  const navigate = useNavigate();
  const { setActiveAgent } = useAgentStore();
  const { isNexusOnlyMode } = useFeatureFlags();

  const navigateToAgent = (agentId: string, context?: { originalAgentId?: string }) => {
    console.log('Navigating to agent:', agentId, 'NEXUS-only mode:', isNexusOnlyMode);

    // In NEXUS-only mode, always navigate to NEXUS but preserve original agent context
    if (isNexusOnlyMode && agentId !== 'nexus') {
      const originalAgentId = context?.originalAgentId || agentId;
      setActiveAgent('nexus');
      navigate(`/chat/nexus`, {
        state: {
          originalAgentId,
          nexusCoordination: true,
          agentSpecialty: getAgentSpecialty(originalAgentId)
        }
      });
      console.log(`NEXUS coordination activated for ${originalAgentId} specialty`);
    } else {
      setActiveAgent(agentId);
      navigate(`/chat/${agentId}`);
    }
  };

  const navigateToAgentSpecialty = (agentId: string) => {
    console.log('Navigating to agent specialty:', agentId);

    if (isNexusOnlyMode) {
      // Show agent info but route to NEXUS for actual interaction
      setActiveAgent('nexus');
      navigate(`/chat/nexus`, {
        state: {
          originalAgentId: agentId,
          nexusCoordination: true,
          agentSpecialty: getAgentSpecialty(agentId),
          showSpecialtyInfo: true
        }
      });
    } else {
      navigateToAgent(agentId);
    }
  };

  const navigateToNexusWithContext = (originalAgentId: string, additionalContext?: Record<string, any>) => {
    console.log('Navigating to NEXUS with context:', originalAgentId, additionalContext);

    setActiveAgent('nexus');
    navigate('/chat/nexus', {
      state: {
        originalAgentId,
        nexusCoordination: true,
        agentSpecialty: getAgentSpecialty(originalAgentId),
        ...additionalContext
      }
    });
  };

  const getEffectiveAgentId = (requestedAgentId: string): string => {
    return isNexusOnlyMode && requestedAgentId !== 'nexus' ? 'nexus' : requestedAgentId;
  };

  const isNavigatingToNexus = (agentId: string): boolean => {
    return isNexusOnlyMode && agentId !== 'nexus';
  };

  return {
    navigateToAgent,
    navigateToAgentSpecialty,
    navigateToNexusWithContext,
    getEffectiveAgentId,
    isNavigatingToNexus,
    isNexusOnlyMode
  };
};

// Helper function to get agent specialty
function getAgentSpecialty(agentId: string): string {
  const agent = FITNESS_AGENTS.find(a => a.id === agentId);
  return agent?.specialty || 'General';
}
