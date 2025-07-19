
import React from 'react';
import { Message } from '@/store/chatStore';
import { useAgentStore } from '@/store/agentStore';
import { cn } from '@/lib/utils';
import { User, Sparkles } from 'lucide-react';
import { MarkdownRenderer } from './MarkdownRenderer';
import { MessageActions } from './MessageActions';

interface ChatMessageProps {
  message: Message;
  isLast?: boolean;
  onEditMessage?: (messageId: string) => void;
  onDeleteMessage?: (messageId: string) => void;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ 
  message, 
  onEditMessage,
  onDeleteMessage
}) => {
  const { getAgent } = useAgentStore();
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';
  
  // Get agent information for this message
  const agent = message.agentId ? getAgent(message.agentId) : null;
  const agentAvatar = agent?.avatar || '🤖';
  const agentName = agent?.name || 'NGX Agent';
  // Updated to use violet color scheme
  const agentColor = 'from-purple-500 to-violet-600';

  return (
    <div
        className={cn(
          'flex gap-3 sm:gap-6 group message-fade-in px-4 sm:px-0',
          isUser && 'flex-row-reverse',
          'hover:bg-violet-900/10 transition-all duration-300 rounded-xl sm:rounded-2xl p-2 sm:p-4 -mx-2 sm:-mx-4'
        )}
    >
      {/* Avatar */}
      <div
        className={cn(
          'flex-shrink-0 w-8 h-8 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl flex items-center justify-center relative',
          isUser
            ? 'glass-premium border border-white/10'
            : `glass-premium border border-purple-500/20 bg-gradient-to-br ${agentColor} shadow-lg shadow-purple-500/10`
        )}
      >
        {isUser ? (
          <User className="w-3 h-3 sm:w-5 sm:h-5 text-white/80" />
        ) : (
          <>
            <span className="text-sm sm:text-lg">{agentAvatar}</span>
            <Sparkles className="w-2 h-2 sm:w-3 sm:h-3 text-purple-400 absolute -top-0.5 -right-0.5 sm:-top-1 sm:-right-1" />
          </>
        )}
      </div>

      {/* Message Content */}
      <div className={cn('flex-1 space-y-2 sm:space-y-3 max-w-full sm:max-w-4xl', isUser && 'flex flex-col items-end')}>
        {/* Agent Name (for assistant messages) */}
        {isAssistant && agent && (
          <div className="flex items-center gap-2">
            <span className="text-xs sm:text-sm font-medium text-white/80">{agentName}</span>
            <span className="text-xs text-purple-400/60">{agent.specialty}</span>
          </div>
        )}
        
        {/* Message Bubble */}
        <div
          className={cn(
            'inline-block max-w-full rounded-xl sm:rounded-2xl relative overflow-hidden',
            isUser
              ? 'bg-black/50 border border-violet-800 px-3 py-2 sm:px-6 sm:py-4'
              : 'bg-black/20 border border-violet-900/60 px-3 py-2 sm:px-6 sm:py-4',
            'backdrop-blur-xl'
          )}
        >
          {message.isTyping ? (
            <div className="flex items-center gap-2 py-1 sm:py-2">
              <div className="flex gap-1">
                <div className="typing-dot-premium"></div>
                <div className="typing-dot-premium"></div>
                <div className="typing-dot-premium"></div>
              </div>
              <span className="text-xs sm:text-sm text-muted-foreground ml-2">{agentName} is thinking...</span>
            </div>
          ) : (
            <div className="relative">
              {isAssistant ? (
                <MarkdownRenderer content={message.content} className="text-sm sm:text-base" />
              ) : (
                <div className="text-xs sm:text-sm leading-relaxed whitespace-pre-wrap font-light text-white/90">
                  {message.content}
                </div>
              )}
              
              {/* Message Actions - Hidden on mobile unless menu is opened */}
              <div className={cn(
                'absolute top-1 sm:top-2 opacity-0 group-hover:opacity-100 transition-opacity hidden sm:block',
                isUser ? 'left-1 sm:left-2' : 'right-1 sm:right-2'
              )}>
                <MessageActions
                  message={message}
                  onEdit={onEditMessage}
                  onDelete={onDeleteMessage}
                />
              </div>
            </div>
          )}

          {/* Subtle shimmer effect */}
          {!message.isTyping && (
            <div className="absolute inset-0 shimmer-premium opacity-20 pointer-events-none"></div>
          )}
        </div>

        {/* Mobile Message Actions */}
        <div className={cn(
          'flex sm:hidden',
          isUser ? 'justify-end' : 'justify-start'
        )}>
          <MessageActions
            message={message}
            onEdit={onEditMessage}
            onDelete={onDeleteMessage}
          />
        </div>

        {/* Metadata */}
        {message.metadata && !message.isTyping && (
          <div className={cn('text-xs text-muted-foreground/50 space-x-2 sm:space-x-4', isUser && 'text-right')}>
            {message.metadata.confidence && (
              <span className="inline-flex items-center gap-1">
                <div className="w-1 h-1 rounded-full bg-purple-400"></div>
                {Math.round(message.metadata.confidence * 100)}% confidence
              </span>
            )}
            {message.metadata.processingTime && (
              <span className="inline-flex items-center gap-1">
                <div className="w-1 h-1 rounded-full bg-violet-400"></div>
                {message.metadata.processingTime}ms
              </span>
            )}
          </div>
        )}

        {/* Timestamp */}
        <div className={cn('text-xs text-muted-foreground/40 font-light', isUser && 'text-right')}>
          {message.timestamp.toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </div>
      </div>
    </div>
  );
};
