import React from 'react';
import { render, screen } from '@testing-library/react';
import { ChatMessage } from '../ChatMessage';
import type { Message } from '@/store/chatStore';

const mockMessage: Message = {
  id: '1',
  content: 'Hello, this is a test message',
  role: 'user',
  timestamp: new Date('2024-01-01T12:00:00Z'),
  agentId: 'trainer'
};

const mockAssistantMessage: Message = {
  id: '2',
  content: 'Hello! How can I help you today?',
  role: 'assistant',
  timestamp: new Date('2024-01-01T12:01:00Z'),
  agentId: 'trainer',
  metadata: {
    confidence: 0.95,
    processingTime: 1200,
    tokens: 15,
    agentName: 'Personal Trainer',
    agentAvatar: '/avatars/trainer.png'
  }
};

describe('ChatMessage', () => {
  describe('user messages', () => {
    it('renders user message correctly', () => {
      render(<ChatMessage message={mockMessage} />);

      expect(screen.getByText('Hello, this is a test message')).toBeInTheDocument();
    });

    it('applies correct styling for user messages', () => {
      const { container } = render(<ChatMessage message={mockMessage} />);

      expect(container.firstChild).toHaveClass('user-message');
    });

    it('shows timestamp for user messages', () => {
      render(<ChatMessage message={mockMessage} />);

      expect(screen.getByText(/12:00/)).toBeInTheDocument();
    });
  });

  describe('assistant messages', () => {
    it('renders assistant message correctly', () => {
      render(<ChatMessage message={mockAssistantMessage} />);

      expect(screen.getByText('Hello! How can I help you today?')).toBeInTheDocument();
    });

    it('shows agent name when provided', () => {
      render(<ChatMessage message={mockAssistantMessage} />);

      expect(screen.getByText('Personal Trainer')).toBeInTheDocument();
    });

    it('shows confidence score when provided', () => {
      render(<ChatMessage message={mockAssistantMessage} />);

      expect(screen.getByText(/95%/)).toBeInTheDocument();
    });

    it('shows processing time when provided', () => {
      render(<ChatMessage message={mockAssistantMessage} />);

      expect(screen.getByText(/1.2s/)).toBeInTheDocument();
    });
  });

  describe('message with attachments', () => {
    const messageWithAttachments: Message = {
      ...mockMessage,
      attachments: [
        {
          id: 'att-1',
          name: 'image.jpg',
          type: 'image/jpeg',
          size: 1024,
          url: 'http://example.com/image.jpg'
        }
      ]
    };

    it('renders attachment information', () => {
      render(<ChatMessage message={messageWithAttachments} />);

      expect(screen.getByText('image.jpg')).toBeInTheDocument();
    });
  });

  describe('typing indicator', () => {
    const typingMessage: Message = {
      ...mockAssistantMessage,
      isTyping: true
    };

    it('shows typing indicator', () => {
      render(<ChatMessage message={typingMessage} />);

      expect(screen.getByTestId('typing-indicator')).toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('has proper ARIA labels', () => {
      render(<ChatMessage message={mockMessage} />);

      expect(screen.getByRole('article')).toHaveAccessibleName(/message from user/i);
    });
  });
});
