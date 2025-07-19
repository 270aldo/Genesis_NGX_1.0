import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Agent, AgentMessage } from '@/types/agent';
import { FITNESS_AGENTS } from '@/data/agents';
import { analyzeUserIntent } from '@/utils/intentAnalysis';

interface AgentState {
  agents: Agent[];
  activeAgentId: string;
  orchestratorActive: boolean;
  agentHistory: AgentMessage[];
  
  // Actions
  setActiveAgent: (agentId: string) => void;
  toggleOrchestrator: () => void;
  addAgentMessage: (message: AgentMessage) => void;
  getAgent: (id: string) => Agent | undefined;
  getActiveAgent: () => Agent | undefined;
  analyzeUserIntent: (message: string) => string[];
}

export const useAgentStore = create<AgentState>()(
  persist(
    (set, get) => ({
      agents: FITNESS_AGENTS,
      activeAgentId: 'nexus',
      orchestratorActive: true,
      agentHistory: [],

      setActiveAgent: (agentId: string) => {
        set({ activeAgentId: agentId, orchestratorActive: agentId === 'nexus' });
      },

      toggleOrchestrator: () => {
        set((state) => ({ orchestratorActive: !state.orchestratorActive }));
      },

      addAgentMessage: (message: AgentMessage) => {
        set((state) => ({
          agentHistory: [...state.agentHistory, message].slice(-100) // Keep last 100 messages
        }));
      },

      getAgent: (id: string) => {
        const state = get();
        return state.agents.find(agent => agent.id === id);
      },

      getActiveAgent: () => {
        const state = get();
        return state.agents.find(agent => agent.id === state.activeAgentId);
      },

      analyzeUserIntent: (message: string) => {
        return analyzeUserIntent(message);
      }
    }),
    {
      name: 'ngx-agents-store',
      partialize: (state) => ({
        activeAgentId: state.activeAgentId,
        orchestratorActive: state.orchestratorActive,
        agentHistory: state.agentHistory.slice(-50) // Persist last 50 messages
      })
    }
  )
);
