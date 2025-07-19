
import React, { useRef, useEffect, useState } from 'react';
import { ChatMessage } from './ChatMessage';
import { ChatNavigation } from './ChatNavigation';
import type { Conversation } from '@/store/chatStore';

interface MessageListProps {
  conversation: Conversation;
  onEditMessage: (messageId: string) => void;
  onDeleteMessage: (messageId: string) => void;
}

export const MessageList: React.FC<MessageListProps> = ({
  conversation,
  onEditMessage,
  onDeleteMessage
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const [showScrollButtons, setShowScrollButtons] = useState(false);
  const [isNearBottom, setIsNearBottom] = useState(true);

  const scrollToBottom = React.useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  const scrollToTop = React.useCallback(() => {
    scrollAreaRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  const handleScroll = React.useCallback(() => {
    if (!scrollAreaRef.current) return;
    
    const { scrollTop, scrollHeight, clientHeight } = scrollAreaRef.current;
    const isAtBottom = scrollTop + clientHeight >= scrollHeight - 100;
    const hasScroll = scrollHeight > clientHeight;
    
    setIsNearBottom(isAtBottom);
    setShowScrollButtons(hasScroll && conversation.messages.length > 3);
  }, [conversation.messages.length]);

  useEffect(() => {
    scrollToBottom();
  }, [conversation.messages, scrollToBottom]);

  useEffect(() => {
    const scrollElement = scrollAreaRef.current;
    if (scrollElement) {
      scrollElement.addEventListener('scroll', handleScroll);
      handleScroll(); // Check initial state

      return () => scrollElement.removeEventListener('scroll', handleScroll);
    }
  }, [conversation.messages.length, handleScroll]);

  return (
    <>
      <div 
        ref={scrollAreaRef}
        className="flex-1 overflow-y-auto relative chat-scroll-area"
        onScroll={handleScroll}
      >
        {/* Improved padding to prevent header interference */}
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <div className="space-y-6 py-6">
            {conversation.messages.map((message, index) => (
              <ChatMessage
                key={message.id}
                message={message}
                isLast={index === conversation.messages.length - 1}
                onEditMessage={onEditMessage}
                onDeleteMessage={onDeleteMessage}
              />
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {showScrollButtons && (
        <ChatNavigation
          onScrollToTop={scrollToTop}
          onScrollToBottom={scrollToBottom}
          showTopButton={true}
          showBottomButton={!isNearBottom}
        />
      )}
    </>
  );
};
