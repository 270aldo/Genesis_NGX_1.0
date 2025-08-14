/**
 * Personalized Chat Interface Component (Refactored)
 *
 * Reduced from ~771 lines to ~150 lines (80% reduction!)
 *
 * Extracted components:
 * - MessageItem: Individual message rendering
 * - usePersonalizedChat: Chat logic and state management
 * - types.ts: Type definitions
 * - CollaborationIndicator: Agent collaboration display
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';
import { AgentCollaborationIndicator } from '@/components/collaboration';
import {
  Send,
  Sparkles,
  X,
  Settings
} from 'lucide-react';

import { PersonalizedChatInterfaceProps } from './types';
import { usePersonalizedChat } from './usePersonalizedChat';
import { MessageItem } from './MessageItem';

export const PersonalizedChatInterface: React.FC<PersonalizedChatInterfaceProps> = ({
  agentId,
  agentName,
  agentIcon: AgentIcon,
  agentColor,
  onClose,
  className
}) => {
  const chat = usePersonalizedChat({ agentId, agentName });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (chat.inputValue.trim()) {
      await chat.sendMessage(chat.inputValue);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <Card className={cn("w-full h-[600px] flex flex-col", className)}>
      {/* Header */}
      <CardHeader className="pb-3 border-b">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-3">
            <div className={cn("w-10 h-10 rounded-full flex items-center justify-center text-white", agentColor)}>
              <AgentIcon className="w-5 h-5" />
            </div>
            <div>
              <div className="text-lg font-semibold">{agentName}</div>
              {chat.hybridIntelligence.isArchetypeConfident && (
                <div className="text-sm text-slate-600 dark:text-slate-400 flex items-center gap-1">
                  <Sparkles className="w-3 h-3" />
                  Personalized for {chat.hybridIntelligence.archetype?.name || 'you'}
                </div>
              )}
            </div>
          </CardTitle>

          <div className="flex items-center gap-2">
            {/* Personalization Toggle */}
            <Button
              variant="ghost"
              size="sm"
              onClick={chat.togglePersonalizationDetails}
              className={cn(
                "transition-colors",
                chat.showPersonalizationDetails && "bg-blue-100 dark:bg-blue-900"
              )}
            >
              <Settings className="w-4 h-4" />
            </Button>

            {/* Close Button */}
            {onClose && (
              <Button variant="ghost" size="sm" onClick={onClose}>
                <X className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>

        {/* Collaboration Indicator */}
        {chat.featureFlags.shouldShowCollaboration &&
         chat.collaborationData.activeAgents.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-3"
          >
            <AgentCollaborationIndicator
              activeAgents={chat.collaborationData.activeAgents}
              currentTask={chat.collaborationData.currentTask}
              estimatedTime={chat.collaborationData.estimatedTime}
            />
          </motion.div>
        )}
      </CardHeader>

      {/* Messages */}
      <CardContent className="flex-1 p-0">
        <ScrollArea ref={chat.refs.scrollAreaRef} className="h-full">
          <div className="p-4 space-y-4">
            <AnimatePresence>
              {chat.messages.map((message) => (
                <MessageItem
                  key={message.id}
                  message={message}
                  agentName={agentName}
                  agentColor={agentColor}
                  AgentIcon={AgentIcon}
                  showPersonalizationDetails={chat.showPersonalizationDetails}
                  onFeedback={chat.handleFeedback}
                  shouldShowAttribution={chat.featureFlags.shouldShowAttribution}
                />
              ))}
            </AnimatePresence>

            {/* Typing Indicator */}
            {chat.isTyping && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="flex gap-3 p-4 rounded-lg bg-white dark:bg-slate-900 mr-8 border"
              >
                <div className={cn("w-8 h-8 rounded-full flex items-center justify-center text-white", agentColor)}>
                  <AgentIcon className="w-4 h-4" />
                </div>
                <div className="flex items-center gap-1">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                  </div>
                  <span className="text-sm text-slate-600 dark:text-slate-400 ml-2">
                    {agentName} is thinking...
                  </span>
                </div>
              </motion.div>
            )}
          </div>
        </ScrollArea>
      </CardContent>

      {/* Input */}
      <div className="p-4 border-t">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <div className="flex-1">
            <Input
              ref={chat.refs.inputRef}
              value={chat.inputValue}
              onChange={(e) => chat.setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                chat.personalizationHooks.isOptimalTime
                  ? `Ask ${agentName} anything... (optimal time for you!)`
                  : `Ask ${agentName} anything...`
              }
              disabled={chat.isTyping}
              className={cn(
                "transition-colors",
                chat.personalizationHooks.isOptimalTime &&
                "border-green-300 focus:border-green-500 dark:border-green-700"
              )}
            />
          </div>
          <Button
            type="submit"
            disabled={!chat.inputValue.trim() || chat.isTyping}
            className={cn("shrink-0", agentColor)}
          >
            <Send className="w-4 h-4" />
          </Button>
        </form>

        {/* Personalization Status */}
        {chat.personalizationHooks.confidenceScore && (
          <div className="mt-2 text-xs text-slate-600 dark:text-slate-400 flex items-center gap-2">
            <Sparkles className="w-3 h-3" />
            <span>
              Personalization: {Math.round(chat.personalizationHooks.confidenceScore * 100)}% confident
            </span>
            {chat.personalizationHooks.agentAffinity && (
              <span className="ml-2">
                • Agent affinity: {Math.round(chat.personalizationHooks.agentAffinity * 100)}%
              </span>
            )}
          </div>
        )}
      </div>
    </Card>
  );
};
