
import React from 'react';
import { Button } from '@/components/ui/button';
import { ArrowUp, ArrowDown } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ChatNavigationProps {
  onScrollToTop: () => void;
  onScrollToBottom: () => void;
  showTopButton?: boolean;
  showBottomButton?: boolean;
}

export const ChatNavigation: React.FC<ChatNavigationProps> = ({
  onScrollToTop,
  onScrollToBottom,
  showTopButton = true,
  showBottomButton = true
}) => {
  return (
    <div className="fixed right-6 bottom-24 z-20 flex flex-col gap-2">
      {showTopButton && (
        <Button
          onClick={onScrollToTop}
          size="sm"
          variant="outline"
          className={cn(
            "w-10 h-10 rounded-full p-0 shadow-lg",
            "bg-background/80 backdrop-blur-sm border-white/10",
            "hover:bg-background/90 hover:border-white/20",
            "transition-all duration-200 hover:scale-105"
          )}
        >
          <ArrowUp className="w-4 h-4" />
        </Button>
      )}
      
      {showBottomButton && (
        <Button
          onClick={onScrollToBottom}
          size="sm"
          variant="outline"
          className={cn(
            "w-10 h-10 rounded-full p-0 shadow-lg",
            "bg-background/80 backdrop-blur-sm border-white/10",
            "hover:bg-background/90 hover:border-white/20",
            "transition-all duration-200 hover:scale-105"
          )}
        >
          <ArrowDown className="w-4 h-4" />
        </Button>
      )}
    </div>
  );
};
