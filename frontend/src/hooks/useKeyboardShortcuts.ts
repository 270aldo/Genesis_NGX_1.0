import { useEffect } from 'react';
import { useChatStore } from '@/store/chatStore';

interface ShortcutCallbacks {
  onUploadFiles?: () => void;
  onOpenCamera?: () => void;
  onStartRecording?: () => void;
  onToggleSidebar?: () => void;
}

export const useKeyboardShortcuts = (callbacks: ShortcutCallbacks) => {
  const { toggleSidebar } = useChatStore();

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Check for modifier keys
      const isCtrl = event.ctrlKey || event.metaKey;
      
      if (isCtrl) {
        switch (event.key.toLowerCase()) {
          case 'u':
            if (event.shiftKey && callbacks.onUploadFiles) {
              event.preventDefault();
              callbacks.onUploadFiles();
            }
            break;
          case 'c':
            if (event.shiftKey && callbacks.onOpenCamera) {
              event.preventDefault();
              callbacks.onOpenCamera();
            }
            break;
          case 'm':
            if (event.shiftKey && callbacks.onStartRecording) {
              event.preventDefault();
              callbacks.onStartRecording();
            }
            break;
          case 'b':
            event.preventDefault();
            if (callbacks.onToggleSidebar) {
              callbacks.onToggleSidebar();
            } else {
              toggleSidebar();
            }
            break;
        }
      }

      // ESC key for closing modals
      if (event.key === 'Escape') {
        // This will be handled by individual components
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [callbacks, toggleSidebar]);
};