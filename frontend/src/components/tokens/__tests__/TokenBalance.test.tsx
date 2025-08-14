import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TokenBalance } from '../TokenBalance';
import { useAuthStore } from '@/store/authStore';

jest.mock('@/store/authStore', () => ({
  useAuthStore: jest.fn()
}));

const mockUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>;

const mockUser = {
  id: '1',
  email: 'test@example.com',
  name: 'Test User',
  tokens: 500,
  subscription: 'pro' as const,
  createdAt: new Date()
};

describe('TokenBalance', () => {
  beforeEach(() => {
    mockUseAuthStore.mockReturnValue({
      user: mockUser,
      getTokens: jest.fn(() => 500),
      isAuthenticated: true,
      isLoading: false,
      setUser: jest.fn(),
      logout: jest.fn(),
      updateProfile: jest.fn(),
      setLoading: jest.fn(),
      addTokens: jest.fn(),
      useTokens: jest.fn()
    });

    jest.clearAllMocks();
  });

  it('displays current token balance', () => {
    render(<TokenBalance />);

    expect(screen.getByText('500')).toBeInTheDocument();
    expect(screen.getByText(/tokens/i)).toBeInTheDocument();
  });

  it('shows subscription type', () => {
    render(<TokenBalance />);

    expect(screen.getByText(/pro/i)).toBeInTheDocument();
  });

  it('displays token usage progress', () => {
    render(<TokenBalance />);

    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toBeInTheDocument();
  });

  it('shows low token warning', () => {
    mockUseAuthStore.mockReturnValue({
      ...mockUseAuthStore(),
      user: { ...mockUser, tokens: 10 },
      getTokens: jest.fn(() => 10)
    });

    render(<TokenBalance />);

    expect(screen.getByText(/low token/i)).toBeInTheDocument();
  });

  it('provides purchase tokens button', () => {
    render(<TokenBalance />);

    expect(screen.getByRole('button', { name: /purchase/i })).toBeInTheDocument();
  });

  it('handles zero tokens', () => {
    mockUseAuthStore.mockReturnValue({
      ...mockUseAuthStore(),
      user: { ...mockUser, tokens: 0 },
      getTokens: jest.fn(() => 0)
    });

    render(<TokenBalance />);

    expect(screen.getByText('0')).toBeInTheDocument();
    expect(screen.getByText(/out of tokens/i)).toBeInTheDocument();
  });

  it('shows estimated usage time', () => {
    render(<TokenBalance />);

    expect(screen.getByText(/estimated/i)).toBeInTheDocument();
  });
});
