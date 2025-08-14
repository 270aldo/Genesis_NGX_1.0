import { renderHook, act, waitFor } from '@testing-library/react';
import { useDebounce } from '../useDebounce';

// Mock timers
jest.useFakeTimers();

describe('useDebounce Hook', () => {
  afterEach(() => {
    jest.clearAllTimers();
  });

  afterAll(() => {
    jest.useRealTimers();
  });

  it('returns initial value immediately', () => {
    const { result } = renderHook(() => useDebounce('initial', 500));

    expect(result.current).toBe('initial');
  });

  it('updates debounced value after delay', async () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      {
        initialProps: { value: 'initial', delay: 500 }
      }
    );

    expect(result.current).toBe('initial');

    // Update the value
    rerender({ value: 'updated', delay: 500 });

    // Value should still be initial immediately after update
    expect(result.current).toBe('initial');

    // Fast-forward time by 500ms
    act(() => {
      jest.advanceTimersByTime(500);
    });

    // Now the value should be updated
    expect(result.current).toBe('updated');
  });

  it('resets timer when value changes before delay', async () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      {
        initialProps: { value: 'initial', delay: 1000 }
      }
    );

    expect(result.current).toBe('initial');

    // First update
    rerender({ value: 'first-update', delay: 1000 });
    expect(result.current).toBe('initial');

    // Fast-forward 500ms (not enough to trigger debounce)
    act(() => {
      jest.advanceTimersByTime(500);
    });
    expect(result.current).toBe('initial');

    // Second update (should reset the timer)
    rerender({ value: 'second-update', delay: 1000 });
    expect(result.current).toBe('initial');

    // Fast-forward another 500ms (total 1000ms from first update, but only 500ms from second)
    act(() => {
      jest.advanceTimersByTime(500);
    });
    expect(result.current).toBe('initial'); // Still should be initial

    // Fast-forward another 500ms (now 1000ms from second update)
    act(() => {
      jest.advanceTimersByTime(500);
    });
    expect(result.current).toBe('second-update');
  });

  it('handles delay change', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      {
        initialProps: { value: 'initial', delay: 500 }
      }
    );

    rerender({ value: 'updated', delay: 500 });
    expect(result.current).toBe('initial');

    // Change delay
    rerender({ value: 'updated', delay: 1000 });

    // Fast-forward by original delay (500ms)
    act(() => {
      jest.advanceTimersByTime(500);
    });
    expect(result.current).toBe('initial'); // Should still be initial due to new delay

    // Fast-forward by remaining time (500ms more)
    act(() => {
      jest.advanceTimersByTime(500);
    });
    expect(result.current).toBe('updated');
  });

  it('works with different data types', () => {
    // Test with number
    const { result: numberResult } = renderHook(() => useDebounce(42, 100));
    expect(numberResult.current).toBe(42);

    // Test with boolean
    const { result: boolResult } = renderHook(() => useDebounce(true, 100));
    expect(boolResult.current).toBe(true);

    // Test with object
    const testObject = { name: 'test', value: 123 };
    const { result: objectResult } = renderHook(() => useDebounce(testObject, 100));
    expect(objectResult.current).toBe(testObject);

    // Test with array
    const testArray = [1, 2, 3];
    const { result: arrayResult } = renderHook(() => useDebounce(testArray, 100));
    expect(arrayResult.current).toBe(testArray);
  });

  it('works with zero delay', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      {
        initialProps: { value: 'initial', delay: 0 }
      }
    );

    expect(result.current).toBe('initial');

    rerender({ value: 'updated', delay: 0 });

    // With zero delay, it should update on the next tick
    act(() => {
      jest.advanceTimersByTime(0);
    });

    expect(result.current).toBe('updated');
  });

  it('handles rapid value changes', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      {
        initialProps: { value: 'initial', delay: 500 }
      }
    );

    expect(result.current).toBe('initial');

    // Rapid updates
    const updates = ['update1', 'update2', 'update3', 'update4', 'final'];

    updates.forEach((update, index) => {
      rerender({ value: update, delay: 500 });

      // Advance time by less than the delay
      act(() => {
        jest.advanceTimersByTime(100);
      });

      // Should still be initial value
      expect(result.current).toBe('initial');
    });

    // Now advance by the full delay
    act(() => {
      jest.advanceTimersByTime(500);
    });

    // Should have the final value
    expect(result.current).toBe('final');
  });

  it('cleans up timeout on unmount', () => {
    const clearTimeoutSpy = jest.spyOn(global, 'clearTimeout');

    const { rerender, unmount } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      {
        initialProps: { value: 'initial', delay: 500 }
      }
    );

    rerender({ value: 'updated', delay: 500 });

    // Unmount before timeout
    unmount();

    // Should have called clearTimeout
    expect(clearTimeoutSpy).toHaveBeenCalled();

    clearTimeoutSpy.mockRestore();
  });

  it('handles undefined and null values', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      {
        initialProps: { value: undefined as any, delay: 500 }
      }
    );

    expect(result.current).toBeUndefined();

    rerender({ value: null as any, delay: 500 });

    act(() => {
      jest.advanceTimersByTime(500);
    });

    expect(result.current).toBeNull();

    rerender({ value: 'defined', delay: 500 });

    act(() => {
      jest.advanceTimersByTime(500);
    });

    expect(result.current).toBe('defined');
  });

  it('works with complex objects and maintains reference equality when appropriate', () => {
    const initialObject = { id: 1, name: 'initial' };
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      {
        initialProps: { value: initialObject, delay: 500 }
      }
    );

    expect(result.current).toBe(initialObject);

    const updatedObject = { id: 2, name: 'updated' };
    rerender({ value: updatedObject, delay: 500 });

    // Before timeout
    expect(result.current).toBe(initialObject);

    act(() => {
      jest.advanceTimersByTime(500);
    });

    // After timeout
    expect(result.current).toBe(updatedObject);
    expect(result.current.id).toBe(2);
    expect(result.current.name).toBe('updated');
  });

  describe('Real-world use cases', () => {
    it('works for search input debouncing', () => {
      const { result, rerender } = renderHook(
        ({ searchTerm }) => useDebounce(searchTerm, 300),
        { initialProps: { searchTerm: '' } }
      );

      expect(result.current).toBe('');

      // User starts typing
      rerender({ searchTerm: 'r' });
      expect(result.current).toBe('');

      rerender({ searchTerm: 're' });
      expect(result.current).toBe('');

      rerender({ searchTerm: 'rea' });
      expect(result.current).toBe('');

      rerender({ searchTerm: 'reac' });
      expect(result.current).toBe('');

      rerender({ searchTerm: 'react' });
      expect(result.current).toBe('');

      // User stops typing, wait for debounce
      act(() => {
        jest.advanceTimersByTime(300);
      });

      expect(result.current).toBe('react');
    });

    it('works for API call optimization', () => {
      const { result, rerender } = renderHook(
        ({ filters }) => useDebounce(filters, 500),
        {
          initialProps: {
            filters: { category: '', priceMin: 0, priceMax: 1000 }
          }
        }
      );

      const initialFilters = { category: '', priceMin: 0, priceMax: 1000 };
      expect(result.current).toEqual(initialFilters);

      // User changes filters rapidly
      rerender({ filters: { category: 'electronics', priceMin: 0, priceMax: 1000 } });
      rerender({ filters: { category: 'electronics', priceMin: 100, priceMax: 1000 } });
      rerender({ filters: { category: 'electronics', priceMin: 100, priceMax: 500 } });

      // Should still have initial filters
      expect(result.current).toEqual(initialFilters);

      // After debounce delay
      act(() => {
        jest.advanceTimersByTime(500);
      });

      expect(result.current).toEqual({
        category: 'electronics',
        priceMin: 100,
        priceMax: 500
      });
    });

    it('works for resize event handling', () => {
      const { result, rerender } = renderHook(
        ({ windowSize }) => useDebounce(windowSize, 250),
        {
          initialProps: {
            windowSize: { width: 1920, height: 1080 }
          }
        }
      );

      expect(result.current).toEqual({ width: 1920, height: 1080 });

      // Simulate rapid resize events
      const sizes = [
        { width: 1900, height: 1080 },
        { width: 1850, height: 1050 },
        { width: 1800, height: 1000 },
        { width: 1600, height: 900 }
      ];

      sizes.forEach((size, index) => {
        rerender({ windowSize: size });

        // Advance by small amount (simulating rapid events)
        act(() => {
          jest.advanceTimersByTime(50);
        });

        // Should still have original size
        expect(result.current).toEqual({ width: 1920, height: 1080 });
      });

      // After full debounce delay
      act(() => {
        jest.advanceTimersByTime(250);
      });

      expect(result.current).toEqual({ width: 1600, height: 900 });
    });
  });

  describe('Performance considerations', () => {
    it('does not cause unnecessary re-renders', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        {
          initialProps: { value: 'same-value', delay: 500 }
        }
      );

      const initialResult = result.current;

      // Update with same value
      rerender({ value: 'same-value', delay: 500 });

      // Should maintain reference equality
      expect(result.current).toBe(initialResult);

      // Even after timeout
      act(() => {
        jest.advanceTimersByTime(500);
      });

      expect(result.current).toBe(initialResult);
    });

    it('handles high-frequency updates efficiently', () => {
      const setTimeoutSpy = jest.spyOn(global, 'setTimeout');
      const clearTimeoutSpy = jest.spyOn(global, 'clearTimeout');

      const { rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        {
          initialProps: { value: 'initial', delay: 500 }
        }
      );

      // Make 100 rapid updates
      for (let i = 0; i < 100; i++) {
        rerender({ value: `update-${i}`, delay: 500 });
      }

      // Should have called setTimeout 100 times (once per update)
      expect(setTimeoutSpy).toHaveBeenCalledTimes(100);

      // Should have called clearTimeout 99 times (all but the last)
      expect(clearTimeoutSpy).toHaveBeenCalledTimes(99);

      setTimeoutSpy.mockRestore();
      clearTimeoutSpy.mockRestore();
    });
  });
});
