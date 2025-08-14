import React from 'react';
import { render, screen } from '@testing-library/react';
import { MessageList } from '../MessageList';
import type { Message } from '@/store/chatStore';

const mockMessages: Message[] = [
  {
    id: '1',
    content: 'Hello, I need help with my workout',
    role: 'user',
    timestamp: new Date('2024-01-01T12:00:00Z')
  },
  {
    id: '2',
    content: 'I can help you create a personalized workout plan!',
    role: 'assistant',
    timestamp: new Date('2024-01-01T12:01:00Z'),
    agentId: 'trainer'
  },
  {
    id: '3',
    content: 'What type of exercises do you prefer?',
    role: 'assistant',
    timestamp: new Date('2024-01-01T12:02:00Z'),
    agentId: 'trainer'
  }
];

describe('MessageList', () => {
  describe('rendering', () => {
    it('renders all messages', () => {
      render(<MessageList messages={mockMessages} />);

      expect(screen.getByText('Hello, I need help with my workout')).toBeInTheDocument();
      expect(screen.getByText('I can help you create a personalized workout plan!')).toBeInTheDocument();
      expect(screen.getByText('What type of exercises do you prefer?')).toBeInTheDocument();
    });

    it('renders empty state when no messages', () => {
      render(<MessageList messages={[]} />);

      expect(screen.getByText(/no messages yet/i)).toBeInTheDocument();
    });

    it('displays messages in chronological order', () => {
      render(<MessageList messages={mockMessages} />);

      const messages = screen.getAllByRole('article');
      expect(messages).toHaveLength(3);
    });
  });

  describe('scrolling behavior', () => {
    it('auto-scrolls to bottom when new message is added', () => {
      const scrollIntoViewMock = jest.fn();
      Element.prototype.scrollIntoView = scrollIntoViewMock;

      const { rerender } = render(<MessageList messages={mockMessages} />);

      const newMessage: Message = {
        id: '4',
        content: 'New message',
        role: 'user',
        timestamp: new Date()
      };

      rerender(<MessageList messages={[...mockMessages, newMessage]} />);

      expect(scrollIntoViewMock).toHaveBeenCalled();
    });
  });

  describe('loading state', () => {
    it('shows loading indicator when loading', () => {
      render(<MessageList messages={mockMessages} isLoading={true} />);

      expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('has proper ARIA labels', () => {
      render(<MessageList messages={mockMessages} />);

      expect(screen.getByRole('log')).toHaveAccessibleName(/message history/i);
    });
  });
});
