
import { useState, useEffect, useCallback } from 'react';

interface UseStreamingResponseProps {
  text: string;
  speed?: number;
  onComplete?: () => void;
  onStart?: () => void;
}

export const useStreamingResponse = ({ 
  text, 
  speed = 30, 
  onComplete,
  onStart 
}: UseStreamingResponseProps) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);

  const startStreaming = useCallback(() => {
    setIsStreaming(true);
    setDisplayedText('');
    setCurrentIndex(0);
    onStart?.();
  }, [onStart]);

  const stopStreaming = useCallback(() => {
    setIsStreaming(false);
    setDisplayedText(text);
    setCurrentIndex(text.length);
    onComplete?.();
  }, [text, onComplete]);

  useEffect(() => {
    if (!isStreaming || currentIndex >= text.length) {
      if (currentIndex >= text.length && isStreaming) {
        setIsStreaming(false);
        onComplete?.();
      }
      return;
    }

    const timeout = setTimeout(() => {
      setDisplayedText(prev => prev + text[currentIndex]);
      setCurrentIndex(prev => prev + 1);
    }, speed + Math.random() * 20); // Slight randomness for natural feel

    return () => clearTimeout(timeout);
  }, [currentIndex, text, speed, isStreaming, onComplete]);

  return {
    displayedText,
    isStreaming,
    startStreaming,
    stopStreaming,
    progress: text.length > 0 ? (currentIndex / text.length) * 100 : 0
  };
};
