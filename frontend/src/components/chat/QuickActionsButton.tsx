
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Badge } from '@/components/ui/badge';
import { useAgentStore } from '@/store/agentStore';
import { useChatStore } from '@/store/chatStore';
import { useIsMobile } from '@/hooks/use-mobile';
import { cn } from '@/lib/utils';
import { Sparkles, Zap } from 'lucide-react';
import { agentActions } from '@/data/quickActions';
import { QuickActionButton } from './QuickActionButton';

export const QuickActionsButton: React.FC = () => {
  const { getActiveAgent } = useAgentStore();
  const { addMessage, getCurrentConversation, createConversation } = useChatStore();
  const isMobile = useIsMobile();
  const [open, setOpen] = useState(false);
  
  const activeAgent = getActiveAgent();
  const actions = activeAgent ? agentActions[activeAgent.id as keyof typeof agentActions] || [] : [];
  
  const handleQuickAction = (prompt: string) => {
    let conversationId = getCurrentConversation()?.id;
    if (!conversationId) {
      conversationId = createConversation();
    }
    addMessage(conversationId, {
      content: prompt,
      role: 'user',
      agentId: activeAgent?.id
    });
    setOpen(false);
  };

  if (actions.length === 0) return null;

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="ghost"
          size={isMobile ? "sm" : "default"}
          className="relative text-white/70 hover:text-white hover:bg-white/10 rounded-lg border border-transparent hover:border-purple-500/30 transition-all duration-200"
        >
          <Zap className="w-4 h-4" />
          {!isMobile && (
            <>
              <span className="ml-2 text-sm">Quick Actions</span>
              <Badge variant="secondary" className="ml-2 bg-purple-500/20 text-purple-300 text-xs border border-purple-500/30">
                {actions.length}
              </Badge>
            </>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent 
        className={cn(
          "p-4 bg-black/90 backdrop-blur-xl border border-purple-500/20",
          isMobile ? "w-72" : "w-80"
        )} 
        align="end" 
        side={isMobile ? "bottom" : "bottom"} 
        sideOffset={8}
      >
        <div className="space-y-3">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles className="w-4 h-4 text-purple-400" />
            <h3 className="font-medium text-white">Quick Actions</h3>
            <Badge variant="secondary" className="bg-purple-500/20 text-purple-300 text-xs border border-purple-500/30">
              {activeAgent?.name}
            </Badge>
          </div>
          
          <div className={cn("grid gap-2", isMobile ? "grid-cols-1" : "grid-cols-2")}>
            {actions.slice(0, isMobile ? 4 : 6).map((action, index) => (
              <QuickActionButton
                key={index}
                action={action}
                index={index}
                onClick={handleQuickAction}
              />
            ))}
          </div>

          {actions.length > (isMobile ? 4 : 6) && (
            <div className="text-center pt-2 border-t border-white/10">
              <span className="text-xs text-white/50">
                +{actions.length - (isMobile ? 4 : 6)} more available
              </span>
            </div>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
};
