
import React from 'react';
import { Button } from '@/components/ui/button';
import { useIsMobile } from '@/hooks/use-mobile';
import { cn } from '@/lib/utils';
import type { QuickAction } from '@/types/quickActions';

interface QuickActionButtonProps {
  action: QuickAction;
  index: number;
  onClick: (prompt: string) => void;
}

export const QuickActionButton: React.FC<QuickActionButtonProps> = ({
  action,
  index,
  onClick
}) => {
  const isMobile = useIsMobile();
  const ActionIcon = action.icon;

  return (
    <Button 
      key={index} 
      variant="ghost" 
      size="sm" 
      onClick={() => onClick(action.prompt)} 
      className={cn(
        "group relative overflow-hidden",
        "flex items-center gap-3 text-left",
        "text-white/70 hover:text-white rounded-xl",
        "border border-transparent hover:border-purple-500/30",
        "transition-all duration-300 ease-out",
        "hover:bg-purple-500/10 hover:scale-[1.02]",
        "active:scale-[0.98] active:transition-transform active:duration-100",
        isMobile ? "h-12 py-2 px-3 justify-start" : "h-auto py-3 px-3 flex-col"
      )}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-violet-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 ease-out" />
      
      {isMobile ? (
        <>
          <ActionIcon className="w-4 h-4 flex-shrink-0 relative z-10 transition-transform duration-300 ease-out group-hover:scale-110" />
          <span className="text-sm font-medium relative z-10 transition-all duration-300 ease-out">
            {action.label}
          </span>
        </>
      ) : (
        <>
          <ActionIcon className="w-4 h-4 flex-shrink-0 relative z-10 transition-transform duration-300 ease-out group-hover:scale-110" />
          <span className="leading-tight text-center font-medium relative z-10 transition-all duration-300 ease-out text-xs">
            {action.label}
          </span>
        </>
      )}
    </Button>
  );
};
