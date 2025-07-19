
import React from 'react';
import { ChatArea } from '../chat/ChatArea';
import { BiometricsOverview } from '../biometrics/BiometricsOverview';

interface ChatMainContentProps {
  showBiometrics: boolean;
}

export const ChatMainContent: React.FC<ChatMainContentProps> = ({ showBiometrics }) => {
  // Show biometrics dashboard only when explicitly requested from sidebar
  if (showBiometrics) {
    return <BiometricsOverview />;
  }
  
  // Always show ChatArea for all agents (including biometrics-engine)
  return <ChatArea />;
};
