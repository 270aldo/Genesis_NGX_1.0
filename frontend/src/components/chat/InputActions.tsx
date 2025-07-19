
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Send, Mic, Plus, Bot } from 'lucide-react';
import { useVoiceConversation } from '@/hooks/useVoiceConversation';
import { VoiceInterface } from '../voice/VoiceInterface';
import { Dialog, DialogContent, DialogTrigger } from '@/components/ui/dialog';
import { useIsMobile } from '@/hooks/use-mobile';
import { cn } from '@/lib/utils';

interface InputActionsProps {
  disabled?: boolean;
  isRecording: boolean;
  toggleRecording: () => void;
  isTyping: boolean;
  input: string;
  handleSubmit: () => void;
}

export const InputActions: React.FC<InputActionsProps> = ({
  disabled,
  isRecording,
  toggleRecording,
  isTyping,
  input,
  handleSubmit
}) => {
  const [showVoiceDialog, setShowVoiceDialog] = useState(false);
  const { isVoiceActive } = useVoiceConversation();
  const isMobile = useIsMobile();

  const buttonSize = isMobile ? "sm" : "icon";
  const iconSize = isMobile ? "w-4 h-4" : "w-4 h-4";

  return (
    <div className={cn("flex items-center", isMobile ? "gap-1.5" : "gap-2")}>
      <Button
        variant="ghost"
        size={buttonSize}
        className={cn(
          "text-white/60 hover:text-white hover:bg-white/10",
          isMobile ? "h-9 w-9 p-0" : "h-8 w-8"
        )}
        disabled={disabled}
      >
        <Plus className={iconSize} />
      </Button>

      <Dialog open={showVoiceDialog} onOpenChange={setShowVoiceDialog}>
        <DialogTrigger asChild>
          <Button
            variant="ghost"
            size={buttonSize}
            className={cn(
              isVoiceActive 
                ? 'text-purple-400 bg-purple-500/20 hover:bg-purple-500/30' 
                : 'text-white/60 hover:text-white hover:bg-white/10',
              isMobile ? "h-9 w-9 p-0" : "h-8 w-8"
            )}
            disabled={disabled}
          >
            <Bot className={iconSize} />
          </Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-md bg-black/90 border-purple-500/20">
          <VoiceInterface />
        </DialogContent>
      </Dialog>

      <Button
        variant="ghost"
        size={buttonSize}
        onClick={toggleRecording}
        disabled={disabled}
        className={cn(
          isRecording 
            ? 'text-red-400 bg-red-500/20 hover:bg-red-500/30' 
            : 'text-white/60 hover:text-white hover:bg-white/10',
          isMobile ? "h-9 w-9 p-0" : "h-8 w-8"
        )}
      >
        <Mic className={iconSize} />
      </Button>

      <Button
        onClick={handleSubmit}
        disabled={(!input.trim() && !isTyping) || disabled}
        size={buttonSize}
        className={cn(
          "bg-purple-600 hover:bg-purple-700 text-white disabled:opacity-50 shrink-0",
          isMobile ? "h-9 w-9 p-0" : "h-8 w-8"
        )}
      >
        <Send className={iconSize} />
      </Button>
    </div>
  );
};
