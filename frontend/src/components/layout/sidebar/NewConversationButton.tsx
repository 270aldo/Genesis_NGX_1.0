
import React from 'react';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { useChatStore } from '@/store/chatStore';
import { useIsMobile } from '@/hooks/use-mobile';
import { cn } from '@/lib/utils';
import { Plus } from 'lucide-react';

export const NewConversationButton: React.FC = () => {
  const { sidebarOpen, createConversation, toggleSidebar } = useChatStore();
  const isMobile = useIsMobile();

  const handleNewConversation = () => {
    createConversation();
    // Auto-close sidebar on mobile after creating conversation
    if (isMobile) {
      toggleSidebar();
    }
  };

  return (
    <TooltipProvider>
      <div className="p-4">
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              onClick={handleNewConversation}
              className={cn(
                "w-full bg-violet-600 text-white hover:bg-violet-700 transition-all duration-200 rounded-lg shadow-none",
                (sidebarOpen || isMobile) ? "justify-center gap-2 px-4 py-2.5" : "justify-center px-2 py-2"
              )}
            >
              <Plus className="h-5 w-5 flex-shrink-0" />
              {(sidebarOpen || isMobile) && (
                <span className="text-sm font-medium transition-opacity duration-200">
                  New Chat
                </span>
              )}
            </Button>
          </TooltipTrigger>
          {!sidebarOpen && !isMobile && (
            <TooltipContent side="right">
              <p>New Chat</p>
            </TooltipContent>
          )}
        </Tooltip>
      </div>
    </TooltipProvider>
  );
};
