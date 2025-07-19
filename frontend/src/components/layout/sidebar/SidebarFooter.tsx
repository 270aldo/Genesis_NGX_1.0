
import React from 'react';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { useChatStore } from '@/store/chatStore';
import { useIsMobile } from '@/hooks/use-mobile';
import { useAgentStore } from '@/store/agentStore';
import { cn } from '@/lib/utils';
import { Settings, Activity } from 'lucide-react';

interface SidebarFooterProps {
  showBiometrics: boolean;
  setShowBiometrics: (show: boolean) => void;
}

export const SidebarFooter: React.FC<SidebarFooterProps> = ({ showBiometrics, setShowBiometrics }) => {
  const { sidebarOpen } = useChatStore();
  const { getActiveAgent } = useAgentStore();
  const isMobile = useIsMobile();
  const activeAgent = getActiveAgent();

  return (
    <TooltipProvider>
      <div className={cn("border-t border-violet-800 transition-all duration-200", sidebarOpen || isMobile ? "p-4" : "p-2")}>
        {/* Collapsed view - only avatar */}
        {!sidebarOpen && !isMobile && (
          <div className="flex flex-col items-center space-y-2">
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="h-8 w-8 rounded-full bg-violet-900 flex items-center justify-center text-sm font-semibold text-violet-300 cursor-pointer hover:bg-violet-800 transition-colors">
                  JD
                </div>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>John Doe</p>
                {activeAgent?.id === 'biometrics-engine' && (
                  <p className="text-xs text-neutral-400">
                    Biometrics {showBiometrics ? 'Active' : 'Available'}
                  </p>
                )}
              </TooltipContent>
            </Tooltip>
            
            {/* Action buttons in collapsed state */}
            {activeAgent?.id === 'biometrics-engine' && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    onClick={() => setShowBiometrics(!showBiometrics)}
                    variant="ghost"
                    size="icon"
                    className={cn(
                      "h-6 w-6 rounded transition-colors",
                      showBiometrics 
                        ? "text-purple-400" 
                        : "text-neutral-400 hover:text-white"
                    )}
                  >
                    <Activity className="h-3 w-3" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="right">
                  <p>{showBiometrics ? 'Hide Biometrics' : 'Show Biometrics'}</p>
                </TooltipContent>
              </Tooltip>
            )}
          </div>
        )}

        {/* Expanded view - full content */}
        {(sidebarOpen || isMobile) && (
          <div className="flex w-full items-center justify-between rounded-md p-2 text-sm text-neutral-300 hover:bg-violet-800/50 cursor-pointer transition-all duration-200">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-full bg-violet-900 flex items-center justify-center text-sm font-semibold text-violet-300">
                JD
              </div>
              <div className="min-w-0">
                <span className="font-medium text-white">John Doe</span>
                {activeAgent?.id === 'biometrics-engine' && (
                  <div className={`text-xs transition-colors duration-200 ${showBiometrics ? 'text-purple-400' : 'text-white/60'}`}>
                    Biometrics {showBiometrics ? 'Active' : 'Available'}
                  </div>
                )}
              </div>
            </div>
            
            <div className="flex items-center gap-1">
              {activeAgent?.id === 'biometrics-engine' && (
                <Button
                  onClick={() => setShowBiometrics(!showBiometrics)}
                  variant="ghost"
                  size="icon"
                  className={cn(
                    "h-4 w-4 rounded transition-colors duration-200",
                    showBiometrics 
                      ? "text-purple-400" 
                      : "text-neutral-400 hover:text-white"
                  )}
                  title={showBiometrics ? 'Hide Biometrics' : 'Show Biometrics'}
                >
                  <Activity className="h-4 w-4" />
                </Button>
              )}
              <Button
                variant="ghost"
                size="icon"
                className="h-4 w-4 text-neutral-400 hover:text-white transition-colors duration-200"
                title="Settings"
              >
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </TooltipProvider>
  );
};
