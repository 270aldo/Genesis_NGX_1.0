
import React from 'react';
import { ChatInput } from '../chat/ChatInput';

interface ChatFooterProps {
  onSendMessage: (content: string) => void;
}

export const ChatFooter: React.FC<ChatFooterProps> = ({ onSendMessage }) => {
  return (
    <div className="px-4 pb-4 sm:px-6 sm:pb-6">
      <ChatInput onSendMessage={onSendMessage} />
    </div>
  );
};
