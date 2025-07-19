
import { useState, useEffect, useCallback } from 'react';

interface UseRealtimeTypingProps {
  text: string;
  speed?: number;
  onComplete?: () => void;
}

export const useRealtimeTyping = ({ 
  text, 
  speed = 50, 
  onComplete 
}: UseRealtimeTypingProps) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);

  const startTyping = useCallback(() => {
    setIsTyping(true);
    setDisplayedText('');
    setCurrentIndex(0);
  }, []);

  useEffect(() => {
    if (!isTyping || currentIndex >= text.length) {
      if (currentIndex >= text.length && isTyping) {
        setIsTyping(false);
        onComplete?.();
      }
      return;
    }

    const timeout = setTimeout(() => {
      setDisplayedText(prev => prev + text[currentIndex]);
      setCurrentIndex(prev => prev + 1);
    }, speed + Math.random() * 30); // Add slight randomness for more natural feel

    return () => clearTimeout(timeout);
  }, [currentIndex, text, speed, isTyping, onComplete]);

  return {
    displayedText,
    isTyping,
    startTyping,
    progress: text.length > 0 ? (currentIndex / text.length) * 100 : 0
  };
};
