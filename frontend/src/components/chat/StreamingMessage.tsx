
import React, { useEffect, useState } from 'react';
import { useStreamingResponse } from '@/hooks/useStreamingResponse';
import { MarkdownRenderer } from './MarkdownRenderer';
import { Sparkles } from 'lucide-react';

interface StreamingMessageProps {
  content: string;
  isStreaming?: boolean;
  onStreamingComplete?: () => void;
  className?: string;
}

export const StreamingMessage: React.FC<StreamingMessageProps> = ({
  content,
  isStreaming = false,
  onStreamingComplete,
  className
}) => {
  const [shouldStream, setShouldStream] = useState(isStreaming);

  const {
    displayedText,
    isStreaming: streamingActive,
    startStreaming,
    progress
  } = useStreamingResponse({
    text: content,
    speed: 25,
    onComplete: () => {
      setShouldStream(false);
      onStreamingComplete?.();
    }
  });

  useEffect(() => {
    if (isStreaming && content) {
      setShouldStream(true);
      startStreaming();
    }
  }, [isStreaming, content, startStreaming]);

  if (!shouldStream && !streamingActive) {
    return (
      <div className={className}>
        <MarkdownRenderer content={content} />
      </div>
    );
  }

  return (
    <div className={className}>
      <MarkdownRenderer content={displayedText} />
      
      {streamingActive && (
        <div className="flex items-center gap-2 mt-2 text-xs text-white/40">
          <Sparkles className="w-3 h-3 text-blue-400 animate-pulse" />
          <div className="flex-1 bg-white/10 rounded-full h-1 overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-blue-400 to-purple-400 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <span className="font-light">Generating...</span>
        </div>
      )}
    </div>
  );
};
