
import React from 'react';
import { useChatStore } from '@/store/chatStore';

export const KeyboardShortcutsHelp: React.FC = () => {
  const { sidebarOpen } = useChatStore();

  // Hide shortcuts when sidebar is collapsed
  if (!sidebarOpen) {
    return null;
  }

  return (
    <div className="fixed bottom-4 left-4 text-xs text-white/30 font-light hidden lg:block">
      <div className="space-y-1">
        <div>Ctrl+F: Search • Ctrl+N: New Chat</div>
        <div>Ctrl+B: Toggle Sidebar • /: Focus Input</div>
      </div>
    </div>
  );
};
