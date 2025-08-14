import { renderHook } from '@testing-library/react';
import { useKeyboardShortcuts } from '../useKeyboardShortcuts';
import { useChatStore } from '@/store/chatStore';

// Mock the store
jest.mock('@/store/chatStore', () => ({
  useChatStore: jest.fn()
}));

const mockUseChatStore = useChatStore as jest.MockedFunction<typeof useChatStore>;
const mockToggleSidebar = jest.fn();

describe('useKeyboardShortcuts Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    mockUseChatStore.mockReturnValue({
      toggleSidebar: mockToggleSidebar,
      conversations: [],
      currentConversation: null,
      currentConversationId: null,
      isLoading: false,
      error: null,
      addMessage: jest.fn(),
      createConversation: jest.fn(),
      setCurrentConversationId: jest.fn(),
      updateMessage: jest.fn(),
      removeMessage: jest.fn(),
      clearConversation: jest.fn(),
      removeConversation: jest.fn(),
      setLoading: jest.fn(),
      setError: jest.fn(),
      clearError: jest.fn()
    });
  });

  // Helper function to simulate keyboard events
  const simulateKeyDown = (key: string, options: {
    ctrlKey?: boolean;
    metaKey?: boolean;
    shiftKey?: boolean;
    preventDefault?: jest.Mock;
  } = {}) => {
    const preventDefault = options.preventDefault || jest.fn();
    const event = new KeyboardEvent('keydown', {
      key,
      ctrlKey: options.ctrlKey || false,
      metaKey: options.metaKey || false,
      shiftKey: options.shiftKey || false,
      bubbles: true
    });

    // Mock preventDefault
    Object.defineProperty(event, 'preventDefault', {
      value: preventDefault,
      writable: false
    });

    document.dispatchEvent(event);
    return { preventDefault };
  };

  describe('initialization', () => {
    it('attaches keyboard event listener on mount', () => {
      const addEventListenerSpy = jest.spyOn(document, 'addEventListener');
      const callbacks = {};

      renderHook(() => useKeyboardShortcuts(callbacks));

      expect(addEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function));

      addEventListenerSpy.mockRestore();
    });

    it('removes event listener on unmount', () => {
      const removeEventListenerSpy = jest.spyOn(document, 'removeEventListener');
      const callbacks = {};

      const { unmount } = renderHook(() => useKeyboardShortcuts(callbacks));

      unmount();

      expect(removeEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function));

      removeEventListenerSpy.mockRestore();
    });
  });

  describe('upload files shortcut (Ctrl+Shift+U)', () => {
    it('calls onUploadFiles when Ctrl+Shift+U is pressed', () => {
      const onUploadFiles = jest.fn();
      const callbacks = { onUploadFiles };

      renderHook(() => useKeyboardShortcuts(callbacks));

      const { preventDefault } = simulateKeyDown('u', { ctrlKey: true, shiftKey: true });

      expect(onUploadFiles).toHaveBeenCalled();
      expect(preventDefault).toHaveBeenCalled();
    });

    it('calls onUploadFiles when Meta+Shift+U is pressed (Mac)', () => {
      const onUploadFiles = jest.fn();
      const callbacks = { onUploadFiles };

      renderHook(() => useKeyboardShortcuts(callbacks));

      const { preventDefault } = simulateKeyDown('u', { metaKey: true, shiftKey: true });

      expect(onUploadFiles).toHaveBeenCalled();
      expect(preventDefault).toHaveBeenCalled();
    });

    it('does not call onUploadFiles when only Ctrl+U is pressed (no Shift)', () => {
      const onUploadFiles = jest.fn();
      const callbacks = { onUploadFiles };

      renderHook(() => useKeyboardShortcuts(callbacks));

      const { preventDefault } = simulateKeyDown('u', { ctrlKey: true });

      expect(onUploadFiles).not.toHaveBeenCalled();
      expect(preventDefault).not.toHaveBeenCalled();
    });

    it('does not call onUploadFiles when callback is not provided', () => {
      const callbacks = {};

      renderHook(() => useKeyboardShortcuts(callbacks));

      // Should not throw an error
      expect(() => {
        simulateKeyDown('u', { ctrlKey: true, shiftKey: true });
      }).not.toThrow();
    });

    it('handles uppercase U key', () => {
      const onUploadFiles = jest.fn();
      const callbacks = { onUploadFiles };

      renderHook(() => useKeyboardShortcuts(callbacks));

      simulateKeyDown('U', { ctrlKey: true, shiftKey: true });

      expect(onUploadFiles).toHaveBeenCalled();
    });
  });

  describe('camera shortcut (Ctrl+Shift+C)', () => {
    it('calls onOpenCamera when Ctrl+Shift+C is pressed', () => {
      const onOpenCamera = jest.fn();
      const callbacks = { onOpenCamera };

      renderHook(() => useKeyboardShortcuts(callbacks));

      const { preventDefault } = simulateKeyDown('c', { ctrlKey: true, shiftKey: true });

      expect(onOpenCamera).toHaveBeenCalled();
      expect(preventDefault).toHaveBeenCalled();
    });

    it('calls onOpenCamera when Meta+Shift+C is pressed (Mac)', () => {
      const onOpenCamera = jest.fn();
      const callbacks = { onOpenCamera };

      renderHook(() => useKeyboardShortcuts(callbacks));

      const { preventDefault } = simulateKeyDown('c', { metaKey: true, shiftKey: true });

      expect(onOpenCamera).toHaveBeenCalled();
      expect(preventDefault).toHaveBeenCalled();
    });

    it('does not call onOpenCamera when only Ctrl+C is pressed (copy)', () => {
      const onOpenCamera = jest.fn();
      const callbacks = { onOpenCamera };

      renderHook(() => useKeyboardShortcuts(callbacks));

      const { preventDefault } = simulateKeyDown('c', { ctrlKey: true });

      expect(onOpenCamera).not.toHaveBeenCalled();
      expect(preventDefault).not.toHaveBeenCalled();
    });

    it('does not call onOpenCamera when callback is not provided', () => {
      const callbacks = {};

      renderHook(() => useKeyboardShortcuts(callbacks));

      expect(() => {
        simulateKeyDown('c', { ctrlKey: true, shiftKey: true });
      }).not.toThrow();
    });
  });

  describe('recording shortcut (Ctrl+Shift+M)', () => {
    it('calls onStartRecording when Ctrl+Shift+M is pressed', () => {
      const onStartRecording = jest.fn();
      const callbacks = { onStartRecording };

      renderHook(() => useKeyboardShortcuts(callbacks));

      const { preventDefault } = simulateKeyDown('m', { ctrlKey: true, shiftKey: true });

      expect(onStartRecording).toHaveBeenCalled();
      expect(preventDefault).toHaveBeenCalled();
    });

    it('calls onStartRecording when Meta+Shift+M is pressed (Mac)', () => {
      const onStartRecording = jest.fn();
      const callbacks = { onStartRecording };

      renderHook(() => useKeyboardShortcuts(callbacks));

      const { preventDefault } = simulateKeyDown('m', { metaKey: true, shiftKey: true });

      expect(onStartRecording).toHaveBeenCalled();
      expect(preventDefault).toHaveBeenCalled();
    });

    it('does not call onStartRecording when only Ctrl+M is pressed', () => {
      const onStartRecording = jest.fn();
      const callbacks = { onStartRecording };

      renderHook(() => useKeyboardShortcuts(callbacks));

      const { preventDefault } = simulateKeyDown('m', { ctrlKey: true });

      expect(onStartRecording).not.toHaveBeenCalled();
      expect(preventDefault).not.toHaveBeenCalled();
    });

    it('does not call onStartRecording when callback is not provided', () => {
      const callbacks = {};

      renderHook(() => useKeyboardShortcuts(callbacks));

      expect(() => {
        simulateKeyDown('m', { ctrlKey: true, shiftKey: true });
      }).not.toThrow();
    });
  });

  describe('sidebar toggle shortcut (Ctrl+B)', () => {
    it('calls custom onToggleSidebar when provided', () => {
      const onToggleSidebar = jest.fn();
      const callbacks = { onToggleSidebar };

      renderHook(() => useKeyboardShortcuts(callbacks));

      const { preventDefault } = simulateKeyDown('b', { ctrlKey: true });

      expect(onToggleSidebar).toHaveBeenCalled();
      expect(mockToggleSidebar).not.toHaveBeenCalled();
      expect(preventDefault).toHaveBeenCalled();
    });

    it('calls store toggleSidebar when custom callback is not provided', () => {
      const callbacks = {};

      renderHook(() => useKeyboardShortcuts(callbacks));

      const { preventDefault } = simulateKeyDown('b', { ctrlKey: true });

      expect(mockToggleSidebar).toHaveBeenCalled();
      expect(preventDefault).toHaveBeenCalled();
    });

    it('works with Meta key (Mac)', () => {
      const onToggleSidebar = jest.fn();
      const callbacks = { onToggleSidebar };

      renderHook(() => useKeyboardShortcuts(callbacks));

      const { preventDefault } = simulateKeyDown('b', { metaKey: true });

      expect(onToggleSidebar).toHaveBeenCalled();
      expect(preventDefault).toHaveBeenCalled();
    });

    it('does not require Shift key for sidebar toggle', () => {
      const onToggleSidebar = jest.fn();
      const callbacks = { onToggleSidebar };

      renderHook(() => useKeyboardShortcuts(callbacks));

      simulateKeyDown('b', { ctrlKey: true, shiftKey: true });

      expect(onToggleSidebar).toHaveBeenCalled();
    });
  });

  describe('escape key handling', () => {
    it('does not crash when Escape is pressed', () => {
      const callbacks = {};

      renderHook(() => useKeyboardShortcuts(callbacks));

      expect(() => {
        simulateKeyDown('Escape');
      }).not.toThrow();
    });

    it('does not prevent default for Escape key', () => {
      const callbacks = {};

      renderHook(() => useKeyboardShortcuts(callbacks));

      const { preventDefault } = simulateKeyDown('Escape');

      expect(preventDefault).not.toHaveBeenCalled();
    });
  });

  describe('multiple shortcuts', () => {
    it('handles all shortcuts in one hook instance', () => {
      const onUploadFiles = jest.fn();
      const onOpenCamera = jest.fn();
      const onStartRecording = jest.fn();
      const onToggleSidebar = jest.fn();

      const callbacks = {
        onUploadFiles,
        onOpenCamera,
        onStartRecording,
        onToggleSidebar
      };

      renderHook(() => useKeyboardShortcuts(callbacks));

      simulateKeyDown('u', { ctrlKey: true, shiftKey: true });
      simulateKeyDown('c', { ctrlKey: true, shiftKey: true });
      simulateKeyDown('m', { ctrlKey: true, shiftKey: true });
      simulateKeyDown('b', { ctrlKey: true });

      expect(onUploadFiles).toHaveBeenCalledTimes(1);
      expect(onOpenCamera).toHaveBeenCalledTimes(1);
      expect(onStartRecording).toHaveBeenCalledTimes(1);
      expect(onToggleSidebar).toHaveBeenCalledTimes(1);
    });

    it('handles rapid key presses', () => {
      const onUploadFiles = jest.fn();
      const callbacks = { onUploadFiles };

      renderHook(() => useKeyboardShortcuts(callbacks));

      // Rapid fire the same shortcut
      for (let i = 0; i < 5; i++) {
        simulateKeyDown('u', { ctrlKey: true, shiftKey: true });
      }

      expect(onUploadFiles).toHaveBeenCalledTimes(5);
    });
  });

  describe('callback changes', () => {
    it('uses updated callbacks when they change', () => {
      const originalCallback = jest.fn();
      const updatedCallback = jest.fn();

      const { rerender } = renderHook(
        ({ callbacks }) => useKeyboardShortcuts(callbacks),
        { initialProps: { callbacks: { onUploadFiles: originalCallback } } }
      );

      simulateKeyDown('u', { ctrlKey: true, shiftKey: true });
      expect(originalCallback).toHaveBeenCalledTimes(1);
      expect(updatedCallback).not.toHaveBeenCalled();

      // Update callbacks
      rerender({ callbacks: { onUploadFiles: updatedCallback } });

      simulateKeyDown('u', { ctrlKey: true, shiftKey: true });
      expect(originalCallback).toHaveBeenCalledTimes(1);
      expect(updatedCallback).toHaveBeenCalledTimes(1);
    });

    it('handles callback removal', () => {
      const onUploadFiles = jest.fn();

      const { rerender } = renderHook(
        ({ callbacks }) => useKeyboardShortcuts(callbacks),
        { initialProps: { callbacks: { onUploadFiles } } }
      );

      simulateKeyDown('u', { ctrlKey: true, shiftKey: true });
      expect(onUploadFiles).toHaveBeenCalledTimes(1);

      // Remove callback
      rerender({ callbacks: {} });

      // Should not throw error
      expect(() => {
        simulateKeyDown('u', { ctrlKey: true, shiftKey: true });
      }).not.toThrow();

      expect(onUploadFiles).toHaveBeenCalledTimes(1);
    });
  });

  describe('edge cases', () => {
    it('ignores keys without modifiers', () => {
      const onUploadFiles = jest.fn();
      const onOpenCamera = jest.fn();
      const onStartRecording = jest.fn();
      const onToggleSidebar = jest.fn();

      const callbacks = {
        onUploadFiles,
        onOpenCamera,
        onStartRecording,
        onToggleSidebar
      };

      renderHook(() => useKeyboardShortcuts(callbacks));

      simulateKeyDown('u');
      simulateKeyDown('c');
      simulateKeyDown('m');
      simulateKeyDown('b');

      expect(onUploadFiles).not.toHaveBeenCalled();
      expect(onOpenCamera).not.toHaveBeenCalled();
      expect(onStartRecording).not.toHaveBeenCalled();
      expect(onToggleSidebar).not.toHaveBeenCalled();
      expect(mockToggleSidebar).not.toHaveBeenCalled();
    });

    it('handles other keys without errors', () => {
      const callbacks = {};

      renderHook(() => useKeyboardShortcuts(callbacks));

      expect(() => {
        simulateKeyDown('a', { ctrlKey: true });
        simulateKeyDown('z', { ctrlKey: true, shiftKey: true });
        simulateKeyDown('Enter');
        simulateKeyDown('Space');
        simulateKeyDown('ArrowUp');
      }).not.toThrow();
    });

    it('handles special keys', () => {
      const callbacks = {};

      renderHook(() => useKeyboardShortcuts(callbacks));

      expect(() => {
        simulateKeyDown('F1');
        simulateKeyDown('Tab');
        simulateKeyDown('Shift');
        simulateKeyDown('Control');
        simulateKeyDown('Alt');
      }).not.toThrow();
    });

    it('handles multiple modifier keys', () => {
      const onUploadFiles = jest.fn();
      const callbacks = { onUploadFiles };

      renderHook(() => useKeyboardShortcuts(callbacks));

      // Should still work with additional modifiers
      simulateKeyDown('u', { ctrlKey: true, shiftKey: true, altKey: true });

      expect(onUploadFiles).toHaveBeenCalled();
    });
  });

  describe('cross-platform compatibility', () => {
    it('works with both Ctrl and Meta keys', () => {
      const onToggleSidebar = jest.fn();
      const callbacks = { onToggleSidebar };

      renderHook(() => useKeyboardShortcuts(callbacks));

      // Windows/Linux (Ctrl)
      simulateKeyDown('b', { ctrlKey: true });
      expect(onToggleSidebar).toHaveBeenCalledTimes(1);

      // Mac (Meta/Cmd)
      simulateKeyDown('b', { metaKey: true });
      expect(onToggleSidebar).toHaveBeenCalledTimes(2);
    });

    it('prioritizes Meta over Ctrl when both are pressed', () => {
      const onToggleSidebar = jest.fn();
      const callbacks = { onToggleSidebar };

      renderHook(() => useKeyboardShortcuts(callbacks));

      simulateKeyDown('b', { ctrlKey: true, metaKey: true });

      expect(onToggleSidebar).toHaveBeenCalledTimes(1);
    });
  });
});
