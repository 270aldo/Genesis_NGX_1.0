/**
 * Message Item Component
 * Individual message component extracted from PersonalizedChatInterface
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import {
  User,
  Bot,
  Star,
  ThumbsUp,
  ThumbsDown,
  Brain,
  TrendingUp,
  Clock,
  Target
} from 'lucide-react';
import { Message } from './types';

interface MessageItemProps {
  message: Message;
  agentName: string;
  agentColor: string;
  AgentIcon: React.ComponentType<{ className?: string }>;
  showPersonalizationDetails: boolean;
  onFeedback: (messageId: string, rating: number, helpful: boolean) => void;
  shouldShowAttribution: boolean;
}

export const MessageItem: React.FC<MessageItemProps> = ({
  message,
  agentName,
  agentColor,
  AgentIcon,
  showPersonalizationDetails,
  onFeedback,
  shouldShowAttribution
}) => {
  const isUser = message.type === 'user';
  const isAgent = message.type === 'agent';
  const isSystem = message.type === 'system';

  const getMessageIcon = () => {
    if (isUser) return <User className="w-4 h-4" />;
    if (isAgent) return <AgentIcon className="w-4 h-4" />;
    return <Bot className="w-4 h-4" />;
  };

  const getMessageHeader = () => {
    if (isUser) return 'You';
    if (isAgent) return agentName;
    return 'System';
  };

  const getPersonalizationBadges = () => {
    if (!isAgent || !message.personalizationData) return null;

    const { confidence, archetypeAlignment, physiologicalFactors, adaptations } = message.personalizationData;

    return (
      <div className="flex flex-wrap gap-1 mt-2">
        <Badge variant="secondary" className="text-xs">
          <Brain className="w-3 h-3 mr-1" />
          {Math.round(confidence * 100)}% confident
        </Badge>
        <Badge variant="outline" className="text-xs">
          <Target className="w-3 h-3 mr-1" />
          {archetypeAlignment}
        </Badge>
        {physiologicalFactors.length > 0 && (
          <Badge variant="outline" className="text-xs">
            <TrendingUp className="w-3 h-3 mr-1" />
            {physiologicalFactors.length} factors
          </Badge>
        )}
        {adaptations.length > 0 && (
          <Badge variant="outline" className="text-xs">
            <Star className="w-3 h-3 mr-1" />
            {adaptations.length} adaptations
          </Badge>
        )}
      </div>
    );
  };

  const getPersonalizationDetails = () => {
    if (!showPersonalizationDetails || !isAgent || !message.personalizationData) {
      return null;
    }

    const { confidence, archetypeAlignment, physiologicalFactors, adaptations } = message.personalizationData;

    return (
      <motion.div
        initial={{ opacity: 0, height: 0 }}
        animate={{ opacity: 1, height: 'auto' }}
        exit={{ opacity: 0, height: 0 }}
        className="mt-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg border"
      >
        <div className="text-sm font-medium mb-2 flex items-center">
          <Brain className="w-4 h-4 mr-2" />
          Personalization Details
        </div>

        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <div className="font-medium">Confidence</div>
            <div className="text-slate-600 dark:text-slate-400">
              {Math.round(confidence * 100)}%
            </div>
          </div>

          <div>
            <div className="font-medium">Archetype</div>
            <div className="text-slate-600 dark:text-slate-400 capitalize">
              {archetypeAlignment}
            </div>
          </div>

          {physiologicalFactors.length > 0 && (
            <div className="col-span-2">
              <div className="font-medium mb-1">Physiological Factors</div>
              <div className="flex flex-wrap gap-1">
                {physiologicalFactors.map((factor, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {factor}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {adaptations.length > 0 && (
            <div className="col-span-2">
              <div className="font-medium mb-1">Adaptations Applied</div>
              <div className="flex flex-wrap gap-1">
                {adaptations.map((adaptation, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    {adaptation}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      </motion.div>
    );
  };

  const getFeedbackButtons = () => {
    if (!isAgent || message.feedback) return null;

    return (
      <div className="flex items-center gap-2 mt-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onFeedback(message.id, 5, true)}
          className="h-8 px-2 text-green-600 hover:text-green-700 hover:bg-green-50"
        >
          <ThumbsUp className="w-4 h-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onFeedback(message.id, 1, false)}
          className="h-8 px-2 text-red-600 hover:text-red-700 hover:bg-red-50"
        >
          <ThumbsDown className="w-4 h-4" />
        </Button>
      </div>
    );
  };

  const getFeedbackDisplay = () => {
    if (!message.feedback) return null;

    return (
      <div className="flex items-center gap-2 mt-2 text-sm text-slate-600 dark:text-slate-400">
        {message.feedback.helpful ? (
          <ThumbsUp className="w-4 h-4 text-green-600" />
        ) : (
          <ThumbsDown className="w-4 h-4 text-red-600" />
        )}
        <span>Feedback provided</span>
      </div>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className={cn(
        "flex gap-3 p-4 rounded-lg transition-colors",
        isUser && "bg-slate-50 dark:bg-slate-800 ml-8",
        isAgent && "bg-white dark:bg-slate-900 mr-8 border",
        isSystem && "bg-blue-50 dark:bg-blue-900/20 mx-8 border-blue-200 dark:border-blue-800"
      )}
    >
      <div
        className={cn(
          "w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium",
          isUser && "bg-slate-600",
          isAgent && agentColor,
          isSystem && "bg-blue-600"
        )}
      >
        {getMessageIcon()}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center gap-2">
            <span className="font-medium text-sm">
              {getMessageHeader()}
            </span>
            {shouldShowAttribution && isAgent && (
              <Badge variant="outline" className="text-xs">
                <Clock className="w-3 h-3 mr-1" />
                {new Date(message.timestamp).toLocaleTimeString()}
              </Badge>
            )}
          </div>
        </div>

        <div className="prose prose-sm max-w-none dark:prose-invert">
          <p className="text-slate-900 dark:text-slate-100 leading-relaxed">
            {message.content}
          </p>
        </div>

        {getPersonalizationBadges()}
        {getPersonalizationDetails()}
        {getFeedbackButtons()}
        {getFeedbackDisplay()}
      </div>
    </motion.div>
  );
};
