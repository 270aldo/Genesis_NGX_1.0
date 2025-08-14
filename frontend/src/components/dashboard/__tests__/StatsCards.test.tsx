import React from 'react';
import { render, screen } from '@testing-library/react';
import { StatsCards } from '../StatsCards';

const mockStats = {
  totalConversations: 12,
  totalMessages: 48,
  tokensUsed: 1250,
  tokensLimit: 5000
};

describe('StatsCards', () => {
  describe('rendering', () => {
    it('displays total conversations', () => {
      render(<StatsCards stats={mockStats} />);

      expect(screen.getByText('12')).toBeInTheDocument();
      expect(screen.getByText(/conversations/i)).toBeInTheDocument();
    });

    it('displays total messages', () => {
      render(<StatsCards stats={mockStats} />);

      expect(screen.getByText('48')).toBeInTheDocument();
      expect(screen.getByText(/messages/i)).toBeInTheDocument();
    });

    it('displays tokens used and limit', () => {
      render(<StatsCards stats={mockStats} />);

      expect(screen.getByText('1,250')).toBeInTheDocument();
      expect(screen.getByText('5,000')).toBeInTheDocument();
      expect(screen.getByText(/tokens/i)).toBeInTheDocument();
    });
  });

  describe('token usage calculation', () => {
    it('calculates token usage percentage', () => {
      render(<StatsCards stats={mockStats} />);

      expect(screen.getByText('25%')).toBeInTheDocument(); // 1250/5000 * 100
    });

    it('shows warning when token usage is high', () => {
      const highUsageStats = {
        ...mockStats,
        tokensUsed: 4500 // 90% usage
      };

      render(<StatsCards stats={highUsageStats} />);

      expect(screen.getByText(/warning/i)).toBeInTheDocument();
    });
  });

  describe('zero values', () => {
    it('handles zero stats gracefully', () => {
      const zeroStats = {
        totalConversations: 0,
        totalMessages: 0,
        tokensUsed: 0,
        tokensLimit: 1000
      };

      render(<StatsCards stats={zeroStats} />);

      expect(screen.getByText('0')).toBeInTheDocument();
      expect(screen.getByText('0%')).toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('has proper ARIA labels for statistics', () => {
      render(<StatsCards stats={mockStats} />);

      expect(screen.getByLabelText(/conversations statistics/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/messages statistics/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/token usage statistics/i)).toBeInTheDocument();
    });
  });
});
