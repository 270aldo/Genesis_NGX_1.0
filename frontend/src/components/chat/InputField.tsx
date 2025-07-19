
import React from 'react';
import { Textarea } from '@/components/ui/textarea';
import { useIsMobile } from '@/hooks/use-mobile';
import { cn } from '@/lib/utils';

interface InputFieldProps {
  input: string;
  setInput: (value: string) => void;
  isFocused: boolean;
  setIsFocused: (focused: boolean) => void;
  textareaRef: React.RefObject<HTMLTextAreaElement>;
  handleKeyPress: (e: React.KeyboardEvent) => void;
  disabled?: boolean;
  isTyping: boolean;
}

export const InputField: React.FC<InputFieldProps> = ({
  input,
  setInput,
  setIsFocused,
  textareaRef,
  handleKeyPress,
  disabled,
  isTyping
}) => {
  const isMobile = useIsMobile();

  return (
    <div className="flex-1">
      <Textarea
        ref={textareaRef}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={handleKeyPress}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        placeholder={isTyping ? "NGX Agent is thinking..." : "Ask me anything..."}
        disabled={disabled || isTyping}
        className={cn(
          "resize-none border-0 bg-transparent shadow-none focus-visible:ring-0 focus-visible:ring-offset-0 px-2 text-white placeholder:text-gray-500",
          isMobile 
            ? "min-h-[44px] max-h-[100px] py-2.5 text-base" 
            : "min-h-[48px] max-h-[120px] py-2 text-lg"
        )}
        rows={1}
        style={{
          fontSize: isMobile ? '16px' : undefined, // Prevent zoom on iOS
        }}
      />
    </div>
  );
};
