
import React, { useState } from 'react';
import { Sidebar } from './Sidebar';
import { ChatHeader } from './ChatHeader';
import { ChatMainContent } from './ChatMainContent';
import { ChatFooter } from './ChatFooter';
import { KeyboardShortcutsHelp } from './KeyboardShortcutsHelp';
import { useChatMessageHandlers } from './ChatMessageHandlers';
import { useChatStore } from '@/store/chatStore';
import { useAgentStore } from '@/store/agentStore';
import { useIsMobile } from '@/hooks/use-mobile';
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';
import { cn } from '@/lib/utils';

export const ChatLayout: React.FC = () => {
  const {
    sidebarOpen,
    toggleSidebar,
  } = useChatStore();
  
  const { activeAgentId } = useAgentStore();
  const isMobile = useIsMobile();
  const [showBiometrics, setShowBiometrics] = useState(false);
  const { handleSendMessage } = useChatMessageHandlers();

  // Hide biometrics dashboard when agent changes (unless it's biometrics-engine)
  React.useEffect(() => {
    if (activeAgentId && activeAgentId !== 'biometrics-engine') {
      setShowBiometrics(false);
    }
  }, [activeAgentId]);

  // Keyboard shortcuts
  useKeyboardShortcuts({
    onToggleSidebar: () => toggleSidebar()
  });

  // Auto-collapse sidebar on mobile
  React.useEffect(() => {
    if (isMobile && sidebarOpen) {
      toggleSidebar();
    }
  }, [isMobile, sidebarOpen, toggleSidebar]);

  const onSendMessage = async (content: string) => {
    const shouldShowBiometrics = await handleSendMessage(content);
    if (shouldShowBiometrics) {
      setShowBiometrics(true);
    }
  };

  return (
    <div className="min-h-screen bg-black grok-gradient relative">
      {/* GROK-style background */}
      
      <div className="min-h-screen flex relative z-10 overflow-hidden">
        {/* Mobile Overlay for Sidebar */}
        {isMobile && sidebarOpen && (
          <div 
            className="absolute inset-0 bg-black/50 z-40 lg:hidden"
            onClick={toggleSidebar}
          />
        )}
        
        {/* Sidebar */}
        <div className={cn(
          "relative z-50",
          isMobile && !sidebarOpen && "hidden"
        )}>
          <Sidebar 
            showBiometrics={showBiometrics}
            setShowBiometrics={setShowBiometrics}
          />
        </div>
        
        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col min-w-0 relative">
          <ChatHeader 
            showBiometrics={showBiometrics}
            setShowBiometrics={setShowBiometrics}
          />
          
          {/* Chat Content Area */}
          <div className="flex-1 flex flex-col min-h-0 overflow-y-auto">
            <ChatMainContent showBiometrics={showBiometrics} />
            {!showBiometrics && <ChatFooter onSendMessage={onSendMessage} />}
          </div>
        </div>

        <KeyboardShortcutsHelp />
      </div>
    </div>
  );
};
