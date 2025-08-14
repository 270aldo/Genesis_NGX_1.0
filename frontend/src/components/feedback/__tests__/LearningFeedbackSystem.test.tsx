import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LearningFeedbackSystem } from '../LearningFeedbackSystem';

const mockFeedbackData = {
  messageId: 'msg-123',
  agentId: 'trainer',
  userSatisfaction: null,
  feedbackText: ''
};

describe('LearningFeedbackSystem', () => {
  const mockOnFeedback = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders feedback interface', () => {
    render(<LearningFeedbackSystem data={mockFeedbackData} onFeedback={mockOnFeedback} />);

    expect(screen.getByText(/rate this response/i)).toBeInTheDocument();
  });

  it('shows rating buttons', () => {
    render(<LearningFeedbackSystem data={mockFeedbackData} onFeedback={mockOnFeedback} />);

    expect(screen.getByRole('button', { name: /thumbs up/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /thumbs down/i })).toBeInTheDocument();
  });

  it('allows text feedback input', () => {
    render(<LearningFeedbackSystem data={mockFeedbackData} onFeedback={mockOnFeedback} />);

    expect(screen.getByPlaceholderText(/additional feedback/i)).toBeInTheDocument();
  });

  it('submits positive feedback', async () => {
    const user = userEvent.setup();
    render(<LearningFeedbackSystem data={mockFeedbackData} onFeedback={mockOnFeedback} />);

    await user.click(screen.getByRole('button', { name: /thumbs up/i }));

    expect(mockOnFeedback).toHaveBeenCalledWith({
      messageId: 'msg-123',
      agentId: 'trainer',
      rating: 'positive',
      feedback: ''
    });
  });

  it('submits negative feedback with text', async () => {
    const user = userEvent.setup();
    render(<LearningFeedbackSystem data={mockFeedbackData} onFeedback={mockOnFeedback} />);

    await user.click(screen.getByRole('button', { name: /thumbs down/i }));
    await user.type(screen.getByPlaceholderText(/additional feedback/i), 'Not helpful');

    expect(mockOnFeedback).toHaveBeenLastCalledWith({
      messageId: 'msg-123',
      agentId: 'trainer',
      rating: 'negative',
      feedback: 'Not helpful'
    });
  });

  it('shows feedback submitted state', async () => {
    const submittedData = { ...mockFeedbackData, userSatisfaction: 'positive' };
    render(<LearningFeedbackSystem data={submittedData} onFeedback={mockOnFeedback} />);

    expect(screen.getByText(/thank you for your feedback/i)).toBeInTheDocument();
  });
});
