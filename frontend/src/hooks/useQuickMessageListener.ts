
import { useEffect } from 'react';

export const useQuickMessageListener = (onSendMessage: (content: string) => void) => {
  useEffect(() => {
    const handleQuickMessage = (event: CustomEvent) => {
      const message = event.detail.message;
      onSendMessage(message);
    };

    window.addEventListener('quickMessageSelected', handleQuickMessage as EventListener);
    return () => {
      window.removeEventListener('quickMessageSelected', handleQuickMessage as EventListener);
    };
  }, [onSendMessage]);
};
