
import React from 'react';
import { useAgentStore } from '@/store/agentStore';
import { cn } from '@/lib/utils';

interface BiometricsToggleProps {
  showBiometrics: boolean;
  setShowBiometrics: (show: boolean) => void;
}

export const BiometricsToggle: React.FC<BiometricsToggleProps> = ({
  showBiometrics,
  setShowBiometrics
}) => {
  const { getActiveAgent } = useAgentStore();
  const activeAgent = getActiveAgent();

  if (activeAgent?.id !== 'biometrics-engine') {
    return null;
  }

  return (
    <button
      onClick={() => setShowBiometrics(!showBiometrics)}
      className={cn(
        "px-3 py-1 text-xs rounded-full transition-all duration-200",
        showBiometrics 
          ? "bg-purple-500/20 text-purple-400 border border-purple-500/30" 
          : "bg-white/10 text-white/60 border border-white/10 hover:bg-white/20"
      )}
    >
      {showBiometrics ? 'Hide' : 'Show'} Biometrics
    </button>
  );
};
