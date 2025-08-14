import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatInput } from '../ChatInput';

// Mock the UI components
jest.mock('@/components/ui/button', () => ({
  Button: ({ children, onClick, disabled, ...props }: any) => (
    <button onClick={onClick} disabled={disabled} {...props}>
      {children}
    </button>
  )
}));

jest.mock('@/components/ui/textarea', () => ({
  Textarea: ({ value, onChange, onKeyDown, placeholder, ...props }: any) => (
    <textarea
      value={value}
      onChange={onChange}
      onKeyDown={onKeyDown}
      placeholder={placeholder}
      {...props}
    />
  )
}));

const mockOnSend = jest.fn();
const mockOnFileUpload = jest.fn();
const mockOnVoiceToggle = jest.fn();

const defaultProps = {
  onSend: mockOnSend,
  onFileUpload: mockOnFileUpload,
  onVoiceToggle: mockOnVoiceToggle,
  disabled: false,
  isVoiceMode: false,
  isTyping: false
};

describe('ChatInput', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('rendering', () => {
    it('renders input field and send button', () => {
      render(<ChatInput {...defaultProps} />);

      expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
    });

    it('renders file upload button', () => {
      render(<ChatInput {...defaultProps} />);

      expect(screen.getByRole('button', { name: /attach file/i })).toBeInTheDocument();
    });

    it('renders voice toggle button', () => {
      render(<ChatInput {...defaultProps} />);

      expect(screen.getByRole('button', { name: /voice/i })).toBeInTheDocument();
    });
  });

  describe('text input functionality', () => {
    it('updates input value when typing', async () => {
      const user = userEvent.setup();
      render(<ChatInput {...defaultProps} />);

      const textarea = screen.getByPlaceholderText(/type your message/i);
      await user.type(textarea, 'Hello world');

      expect(textarea).toHaveValue('Hello world');
    });

    it('calls onSend when send button is clicked', async () => {
      const user = userEvent.setup();
      render(<ChatInput {...defaultProps} />);

      const textarea = screen.getByPlaceholderText(/type your message/i);
      const sendButton = screen.getByRole('button', { name: /send/i });

      await user.type(textarea, 'Test message');
      await user.click(sendButton);

      expect(mockOnSend).toHaveBeenCalledWith('Test message');
    });

    it('calls onSend when Enter is pressed', async () => {
      const user = userEvent.setup();
      render(<ChatInput {...defaultProps} />);

      const textarea = screen.getByPlaceholderText(/type your message/i);
      await user.type(textarea, 'Test message');
      await user.keyboard('{Enter}');

      expect(mockOnSend).toHaveBeenCalledWith('Test message');
    });

    it('does not send empty messages', async () => {
      const user = userEvent.setup();
      render(<ChatInput {...defaultProps} />);

      const sendButton = screen.getByRole('button', { name: /send/i });
      await user.click(sendButton);

      expect(mockOnSend).not.toHaveBeenCalled();
    });

    it('trims whitespace from messages', async () => {
      const user = userEvent.setup();
      render(<ChatInput {...defaultProps} />);

      const textarea = screen.getByPlaceholderText(/type your message/i);
      const sendButton = screen.getByRole('button', { name: /send/i });

      await user.type(textarea, '  Test message  ');
      await user.click(sendButton);

      expect(mockOnSend).toHaveBeenCalledWith('Test message');
    });

    it('clears input after sending message', async () => {
      const user = userEvent.setup();
      render(<ChatInput {...defaultProps} />);

      const textarea = screen.getByPlaceholderText(/type your message/i);
      const sendButton = screen.getByRole('button', { name: /send/i });

      await user.type(textarea, 'Test message');
      await user.click(sendButton);

      expect(textarea).toHaveValue('');
    });
  });

  describe('disabled state', () => {
    it('disables input and buttons when disabled prop is true', () => {
      render(<ChatInput {...defaultProps} disabled={true} />);

      expect(screen.getByPlaceholderText(/type your message/i)).toBeDisabled();
      expect(screen.getByRole('button', { name: /send/i })).toBeDisabled();
      expect(screen.getByRole('button', { name: /attach file/i })).toBeDisabled();
      expect(screen.getByRole('button', { name: /voice/i })).toBeDisabled();
    });

    it('shows loading state when typing', () => {
      render(<ChatInput {...defaultProps} isTyping={true} />);

      expect(screen.getByText(/typing/i)).toBeInTheDocument();
    });
  });

  describe('voice mode', () => {
    it('shows voice mode indicator when active', () => {
      render(<ChatInput {...defaultProps} isVoiceMode={true} />);

      expect(screen.getByText(/voice mode active/i)).toBeInTheDocument();
    });

    it('calls onVoiceToggle when voice button is clicked', async () => {
      const user = userEvent.setup();
      render(<ChatInput {...defaultProps} />);

      const voiceButton = screen.getByRole('button', { name: /voice/i });
      await user.click(voiceButton);

      expect(mockOnVoiceToggle).toHaveBeenCalled();
    });
  });

  describe('file upload', () => {
    it('calls onFileUpload when file upload button is clicked', async () => {
      const user = userEvent.setup();
      render(<ChatInput {...defaultProps} />);

      const fileButton = screen.getByRole('button', { name: /attach file/i });
      await user.click(fileButton);

      expect(mockOnFileUpload).toHaveBeenCalled();
    });
  });

  describe('keyboard shortcuts', () => {
    it('allows Shift+Enter for new line', async () => {
      const user = userEvent.setup();
      render(<ChatInput {...defaultProps} />);

      const textarea = screen.getByPlaceholderText(/type your message/i);
      await user.type(textarea, 'Line 1');
      await user.keyboard('{Shift>}{Enter}{/Shift}');
      await user.type(textarea, 'Line 2');

      expect(textarea).toHaveValue('Line 1\nLine 2');
      expect(mockOnSend).not.toHaveBeenCalled();
    });

    it('prevents sending with Ctrl+Enter when input is empty', async () => {
      const user = userEvent.setup();
      render(<ChatInput {...defaultProps} />);

      const textarea = screen.getByPlaceholderText(/type your message/i);
      await user.keyboard('{Control>}{Enter}{/Control}');

      expect(mockOnSend).not.toHaveBeenCalled();
    });
  });

  describe('accessibility', () => {
    it('has proper ARIA labels', () => {
      render(<ChatInput {...defaultProps} />);

      expect(screen.getByRole('textbox')).toHaveAccessibleName(/message input/i);
      expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /attach file/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /voice/i })).toBeInTheDocument();
    });

    it('maintains focus on input after sending', async () => {
      const user = userEvent.setup();
      render(<ChatInput {...defaultProps} />);

      const textarea = screen.getByPlaceholderText(/type your message/i);
      await user.type(textarea, 'Test message');
      await user.keyboard('{Enter}');

      expect(textarea).toHaveFocus();
    });
  });

  describe('edge cases', () => {
    it('handles very long messages', async () => {
      const user = userEvent.setup();
      render(<ChatInput {...defaultProps} />);

      const longMessage = 'a'.repeat(1000);
      const textarea = screen.getByPlaceholderText(/type your message/i);

      await user.type(textarea, longMessage);
      await user.keyboard('{Enter}');

      expect(mockOnSend).toHaveBeenCalledWith(longMessage);
    });

    it('handles special characters', async () => {
      const user = userEvent.setup();
      render(<ChatInput {...defaultProps} />);

      const specialMessage = '!@#$%^&*()_+{}[]|;:,.<>?';
      const textarea = screen.getByPlaceholderText(/type your message/i);

      await user.type(textarea, specialMessage);
      await user.keyboard('{Enter}');

      expect(mockOnSend).toHaveBeenCalledWith(specialMessage);
    });

    it('handles unicode characters', async () => {
      const user = userEvent.setup();
      render(<ChatInput {...defaultProps} />);

      const unicodeMessage = 'Hello 🌍 World!';
      const textarea = screen.getByPlaceholderText(/type your message/i);

      await user.type(textarea, unicodeMessage);
      await user.keyboard('{Enter}');

      expect(mockOnSend).toHaveBeenCalledWith(unicodeMessage);
    });
  });

  describe('component lifecycle', () => {
    it('maintains state across re-renders', async () => {
      const user = userEvent.setup();
      const { rerender } = render(<ChatInput {...defaultProps} />);

      const textarea = screen.getByPlaceholderText(/type your message/i);
      await user.type(textarea, 'Persistent message');

      rerender(<ChatInput {...defaultProps} disabled={true} />);

      expect(textarea).toHaveValue('Persistent message');
    });
  });
});
