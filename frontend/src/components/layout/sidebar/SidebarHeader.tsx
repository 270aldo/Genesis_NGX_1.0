
import React from 'react';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { useIsMobile } from '@/hooks/use-mobile';
import { useChatStore } from '@/store/chatStore';
import { cn } from '@/lib/utils';
import { ChevronLeft, Sparkles, Menu } from 'lucide-react';

export const SidebarHeader: React.FC = () => {
  const { sidebarOpen, toggleSidebar } = useChatStore();
  const isMobile = useIsMobile();

  return (
    <TooltipProvider>
      <div className="flex h-16 items-center justify-between border-b border-violet-800 px-4">
        {/* Logo area - show icon always, text only when expanded */}
        <div className="flex items-center gap-2">
          <Tooltip>
            <TooltipTrigger asChild>
              <div className="w-7 h-7 flex items-center justify-center rounded-lg bg-violet-600">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
            </TooltipTrigger>
            {!sidebarOpen && !isMobile && (
              <TooltipContent side="right">
                <p>Assistant</p>
              </TooltipContent>
            )}
          </Tooltip>
          {(sidebarOpen || isMobile) && (
            <span className="text-base font-semibold text-neutral-100 transition-opacity duration-200">
              Assistant
            </span>
          )}
        </div>
        
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleSidebar}
          className="flex items-center justify-center h-8 w-8 rounded-md hover:bg-violet-800/50 transition-colors"
        >
          {isMobile ? (
            <Menu className="w-4 h-4 text-neutral-400" />
          ) : (
            <ChevronLeft className={cn("w-4 h-4 text-neutral-400 transition-transform duration-200", !sidebarOpen && "rotate-180")} />
          )}
        </Button>
      </div>
    </TooltipProvider>
  );
};
