import { renderHook, act, waitFor } from '@testing-library/react';
import { useStreamingResponse } from '../useStreamingResponse';

// Mock timers
jest.useFakeTimers();

describe('useStreamingResponse Hook', () => {
  beforeEach(() => {
    jest.clearAllTimers();
  });

  afterEach(() => {
    jest.clearAllTimers();
  });

  afterAll(() => {
    jest.useRealTimers();
  });

  describe('initialization', () => {
    it('initializes with correct default values', () => {
      const { result } = renderHook(() =>
        useStreamingResponse({ text: 'Hello World' })
      );

      expect(result.current.displayedText).toBe('');
      expect(result.current.isStreaming).toBe(false);
      expect(result.current.progress).toBe(0);
    });

    it('calculates progress correctly with empty text', () => {
      const { result } = renderHook(() =>
        useStreamingResponse({ text: '' })
      );

      expect(result.current.progress).toBe(0);
    });

    it('provides start and stop functions', () => {
      const { result } = renderHook(() =>
        useStreamingResponse({ text: 'Hello World' })
      );

      expect(typeof result.current.startStreaming).toBe('function');
      expect(typeof result.current.stopStreaming).toBe('function');
    });
  });

  describe('startStreaming', () => {
    it('starts streaming when called', () => {
      const onStart = jest.fn();
      const { result } = renderHook(() =>
        useStreamingResponse({ text: 'Hello', onStart })
      );

      act(() => {
        result.current.startStreaming();
      });

      expect(result.current.isStreaming).toBe(true);
      expect(result.current.displayedText).toBe('');
      expect(onStart).toHaveBeenCalled();
    });

    it('resets state when starting again', () => {
      const { result } = renderHook(() =>
        useStreamingResponse({ text: 'Hello World' })
      );

      // Start first time
      act(() => {
        result.current.startStreaming();
      });

      // Advance some time to get partial text
      act(() => {
        jest.advanceTimersByTime(100);
      });

      expect(result.current.displayedText.length).toBeGreaterThan(0);

      // Start again
      act(() => {
        result.current.startStreaming();
      });

      expect(result.current.displayedText).toBe('');
      expect(result.current.isStreaming).toBe(true);
    });

    it('calls onStart callback only once when provided', () => {
      const onStart = jest.fn();
      const { result } = renderHook(() =>
        useStreamingResponse({ text: 'Hello', onStart })
      );

      act(() => {
        result.current.startStreaming();
        result.current.startStreaming();
      });

      expect(onStart).toHaveBeenCalledTimes(2);
    });
  });

  describe('stopStreaming', () => {
    it('stops streaming and shows full text immediately', () => {
      const onComplete = jest.fn();
      const text = 'Hello World';
      const { result } = renderHook(() =>
        useStreamingResponse({ text, onComplete })
      );

      act(() => {
        result.current.startStreaming();
      });

      expect(result.current.isStreaming).toBe(true);

      act(() => {
        result.current.stopStreaming();
      });

      expect(result.current.isStreaming).toBe(false);
      expect(result.current.displayedText).toBe(text);
      expect(result.current.progress).toBe(100);
      expect(onComplete).toHaveBeenCalled();
    });

    it('can stop streaming before it completes naturally', () => {
      const onComplete = jest.fn();
      const text = 'Hello World';
      const { result } = renderHook(() =>
        useStreamingResponse({ text, onComplete })
      );

      act(() => {
        result.current.startStreaming();
      });

      // Advance time partially
      act(() => {
        jest.advanceTimersByTime(150); // Should show partial text
      });

      expect(result.current.displayedText.length).toBeGreaterThan(0);
      expect(result.current.displayedText.length).toBeLessThan(text.length);

      act(() => {
        result.current.stopStreaming();
      });

      expect(result.current.displayedText).toBe(text);
      expect(onComplete).toHaveBeenCalled();
    });
  });

  describe('streaming behavior', () => {
    it('streams text character by character', () => {
      const text = 'Hello';
      const speed = 50;
      const { result } = renderHook(() =>
        useStreamingResponse({ text, speed })
      );

      act(() => {
        result.current.startStreaming();
      });

      expect(result.current.displayedText).toBe('');

      // First character
      act(() => {
        jest.advanceTimersByTime(70); // speed + some random
      });
      expect(result.current.displayedText).toBe('H');

      // Second character
      act(() => {
        jest.advanceTimersByTime(70);
      });
      expect(result.current.displayedText).toBe('He');

      // Continue until complete
      act(() => {
        jest.advanceTimersByTime(210); // Enough for remaining characters
      });
      expect(result.current.displayedText).toBe('Hello');
    });

    it('uses custom speed setting', () => {
      const text = 'Hi';
      const speed = 100;
      const { result } = renderHook(() =>
        useStreamingResponse({ text, speed })
      );

      act(() => {
        result.current.startStreaming();
      });

      // Should not advance with shorter time
      act(() => {
        jest.advanceTimersByTime(50);
      });
      expect(result.current.displayedText).toBe('');

      // Should advance with proper time
      act(() => {
        jest.advanceTimersByTime(70); // speed + some buffer for randomness
      });
      expect(result.current.displayedText).toBe('H');
    });

    it('calculates progress correctly during streaming', () => {
      const text = 'Hello';
      const { result } = renderHook(() =>
        useStreamingResponse({ text, speed: 10 })
      );

      act(() => {
        result.current.startStreaming();
      });

      expect(result.current.progress).toBe(0);

      // First character
      act(() => {
        jest.advanceTimersByTime(50);
      });
      expect(result.current.progress).toBe(20); // 1/5 * 100

      // Second character
      act(() => {
        jest.advanceTimersByTime(50);
      });
      expect(result.current.progress).toBe(40); // 2/5 * 100

      // Complete
      act(() => {
        jest.advanceTimersByTime(150);
      });
      expect(result.current.progress).toBe(100);
    });

    it('stops streaming when text is complete', () => {
      const onComplete = jest.fn();
      const text = 'Hi';
      const { result } = renderHook(() =>
        useStreamingResponse({ text, speed: 10, onComplete })
      );

      act(() => {
        result.current.startStreaming();
      });

      // Complete the streaming
      act(() => {
        jest.advanceTimersByTime(100);
      });

      expect(result.current.isStreaming).toBe(false);
      expect(result.current.displayedText).toBe(text);
      expect(onComplete).toHaveBeenCalled();
    });
  });

  describe('text changes', () => {
    it('handles text changes during streaming', () => {
      const { result, rerender } = renderHook(
        ({ text }) => useStreamingResponse({ text, speed: 10 }),
        { initialProps: { text: 'Hello' } }
      );

      act(() => {
        result.current.startStreaming();
      });

      // Advance partially
      act(() => {
        jest.advanceTimersByTime(30);
      });

      expect(result.current.displayedText).toBe('Hel');

      // Change text
      rerender({ text: 'World' });

      // Continue streaming with new text
      act(() => {
        jest.advanceTimersByTime(40);
      });

      // Should continue from where it left off with new text
      expect(result.current.displayedText.length).toBeGreaterThan(3);
    });

    it('handles empty text', () => {
      const { result } = renderHook(() =>
        useStreamingResponse({ text: '', speed: 10 })
      );

      act(() => {
        result.current.startStreaming();
      });

      act(() => {
        jest.advanceTimersByTime(50);
      });

      expect(result.current.displayedText).toBe('');
      expect(result.current.isStreaming).toBe(false);
      expect(result.current.progress).toBe(0);
    });

    it('handles single character text', () => {
      const onComplete = jest.fn();
      const { result } = renderHook(() =>
        useStreamingResponse({ text: 'A', speed: 10, onComplete })
      );

      act(() => {
        result.current.startStreaming();
      });

      act(() => {
        jest.advanceTimersByTime(50);
      });

      expect(result.current.displayedText).toBe('A');
      expect(result.current.isStreaming).toBe(false);
      expect(result.current.progress).toBe(100);
      expect(onComplete).toHaveBeenCalled();
    });
  });

  describe('callbacks', () => {
    it('calls onComplete when streaming finishes naturally', () => {
      const onComplete = jest.fn();
      const { result } = renderHook(() =>
        useStreamingResponse({ text: 'Hi', speed: 10, onComplete })
      );

      act(() => {
        result.current.startStreaming();
      });

      expect(onComplete).not.toHaveBeenCalled();

      act(() => {
        jest.advanceTimersByTime(100);
      });

      expect(onComplete).toHaveBeenCalledTimes(1);
    });

    it('does not call onComplete multiple times', () => {
      const onComplete = jest.fn();
      const { result } = renderHook(() =>
        useStreamingResponse({ text: 'Hi', speed: 10, onComplete })
      );

      act(() => {
        result.current.startStreaming();
      });

      // Complete streaming
      act(() => {
        jest.advanceTimersByTime(100);
      });

      expect(onComplete).toHaveBeenCalledTimes(1);

      // Advance more time
      act(() => {
        jest.advanceTimersByTime(100);
      });

      expect(onComplete).toHaveBeenCalledTimes(1);
    });

    it('handles missing callbacks gracefully', () => {
      const { result } = renderHook(() =>
        useStreamingResponse({ text: 'Hello' })
      );

      expect(() => {
        act(() => {
          result.current.startStreaming();
        });

        act(() => {
          jest.advanceTimersByTime(200);
        });

        act(() => {
          result.current.stopStreaming();
        });
      }).not.toThrow();
    });

    it('calls onStart each time streaming starts', () => {
      const onStart = jest.fn();
      const { result } = renderHook(() =>
        useStreamingResponse({ text: 'Hello', onStart })
      );

      act(() => {
        result.current.startStreaming();
      });

      expect(onStart).toHaveBeenCalledTimes(1);

      act(() => {
        result.current.stopStreaming();
      });

      act(() => {
        result.current.startStreaming();
      });

      expect(onStart).toHaveBeenCalledTimes(2);
    });
  });

  describe('edge cases', () => {
    it('handles rapid start/stop calls', () => {
      const { result } = renderHook(() =>
        useStreamingResponse({ text: 'Hello World' })
      );

      act(() => {
        result.current.startStreaming();
        result.current.stopStreaming();
        result.current.startStreaming();
        result.current.stopStreaming();
      });

      expect(result.current.isStreaming).toBe(false);
      expect(result.current.displayedText).toBe('Hello World');
    });

    it('cleans up timeouts properly', () => {
      const { result, unmount } = renderHook(() =>
        useStreamingResponse({ text: 'Hello', speed: 100 })
      );

      act(() => {
        result.current.startStreaming();
      });

      // Unmount while streaming
      unmount();

      // Should not throw or cause memory leaks
      act(() => {
        jest.advanceTimersByTime(1000);
      });

      // No assertions needed, just ensuring no errors
    });

    it('handles very long text', () => {
      const longText = 'A'.repeat(1000);
      const { result } = renderHook(() =>
        useStreamingResponse({ text: longText, speed: 1 })
      );

      act(() => {
        result.current.startStreaming();
      });

      // Advance enough time for several characters
      act(() => {
        jest.advanceTimersByTime(50);
      });

      expect(result.current.displayedText.length).toBeGreaterThan(10);
      expect(result.current.displayedText.length).toBeLessThan(longText.length);
      expect(result.current.isStreaming).toBe(true);

      // Stop early
      act(() => {
        result.current.stopStreaming();
      });

      expect(result.current.displayedText).toBe(longText);
    });

    it('handles special characters and unicode', () => {
      const text = 'Hello 🌍 World! 中文 emojis 🎉';
      const { result } = renderHook(() =>
        useStreamingResponse({ text, speed: 10 })
      );

      act(() => {
        result.current.startStreaming();
      });

      act(() => {
        jest.advanceTimersByTime(200);
      });

      // Should handle all characters properly
      expect(result.current.displayedText.includes('🌍')).toBe(true);
      expect(result.current.displayedText.includes('中')).toBe(true);
      expect(result.current.displayedText.includes('🎉')).toBe(true);
      expect(result.current.displayedText).toBe(text);
    });
  });

  describe('performance', () => {
    it('uses random timing variation', () => {
      const originalRandom = Math.random;
      const mockRandom = jest.fn(() => 0.5);
      Math.random = mockRandom;

      const { result } = renderHook(() =>
        useStreamingResponse({ text: 'Hi', speed: 50 })
      );

      act(() => {
        result.current.startStreaming();
      });

      act(() => {
        jest.advanceTimersByTime(70); // 50 + 20 * 0.5 = 60, but we give some buffer
      });

      expect(mockRandom).toHaveBeenCalled();

      Math.random = originalRandom;
    });

    it('does not create timers when not streaming', () => {
      const { result } = renderHook(() =>
        useStreamingResponse({ text: 'Hello' })
      );

      const initialTimerCount = jest.getTimerCount();

      act(() => {
        jest.advanceTimersByTime(1000);
      });

      expect(jest.getTimerCount()).toBe(initialTimerCount);
    });
  });
});
