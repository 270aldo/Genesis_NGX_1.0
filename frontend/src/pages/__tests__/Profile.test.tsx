import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Profile from '../Profile';
import { useAuthStore } from '@/store/authStore';

jest.mock('@/store/authStore', () => ({
  useAuthStore: jest.fn()
}));

const mockUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>;

const mockUser = {
  id: '1',
  email: 'john.doe@example.com',
  name: 'John Doe',
  avatar: '/avatars/john.png',
  subscription: 'pro' as const,
  tokens: 450,
  createdAt: new Date('2024-01-01')
};

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Profile', () => {
  beforeEach(() => {
    mockUseAuthStore.mockReturnValue({
      user: mockUser,
      isAuthenticated: true,
      isLoading: false,
      setUser: jest.fn(),
      logout: jest.fn(),
      updateProfile: jest.fn(),
      setLoading: jest.fn(),
      addTokens: jest.fn(),
      useTokens: jest.fn(),
      getTokens: jest.fn()
    });

    jest.clearAllMocks();
  });

  it('displays user profile information', () => {
    renderWithRouter(<Profile />);

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john.doe@example.com')).toBeInTheDocument();
    expect(screen.getByText(/pro/i)).toBeInTheDocument();
  });

  it('shows user avatar', () => {
    renderWithRouter(<Profile />);

    const avatar = screen.getByRole('img', { name: /profile avatar/i });
    expect(avatar).toHaveAttribute('src', '/avatars/john.png');
  });

  it('displays token balance', () => {
    renderWithRouter(<Profile />);

    expect(screen.getByText('450')).toBeInTheDocument();
    expect(screen.getByText(/tokens/i)).toBeInTheDocument();
  });

  it('shows account creation date', () => {
    renderWithRouter(<Profile />);

    expect(screen.getByText(/member since/i)).toBeInTheDocument();
    expect(screen.getByText(/jan 1, 2024/i)).toBeInTheDocument();
  });

  it('has edit profile button', () => {
    renderWithRouter(<Profile />);

    expect(screen.getByRole('button', { name: /edit profile/i })).toBeInTheDocument();
  });

  it('shows subscription benefits', () => {
    renderWithRouter(<Profile />);

    expect(screen.getByText(/pro benefits/i)).toBeInTheDocument();
  });

  it('displays account settings link', () => {
    renderWithRouter(<Profile />);

    const settingsLink = screen.getByRole('link', { name: /settings/i });
    expect(settingsLink).toHaveAttribute('href', '/settings');
  });

  it('redirects unauthenticated users', () => {
    mockUseAuthStore.mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      setUser: jest.fn(),
      logout: jest.fn(),
      updateProfile: jest.fn(),
      setLoading: jest.fn(),
      addTokens: jest.fn(),
      useTokens: jest.fn(),
      getTokens: jest.fn()
    });

    renderWithRouter(<Profile />);

    // Should redirect or show sign in prompt
    expect(screen.getByText(/please sign in/i)).toBeInTheDocument();
  });

  it('handles user without avatar', () => {
    mockUseAuthStore.mockReturnValue({
      ...mockUseAuthStore(),
      user: { ...mockUser, avatar: undefined }
    });

    renderWithRouter(<Profile />);

    const avatar = screen.getByRole('img', { name: /profile avatar/i });
    expect(avatar).toHaveAttribute('src', '/default-avatar.png');
  });

  it('displays free subscription differently', () => {
    mockUseAuthStore.mockReturnValue({
      ...mockUseAuthStore(),
      user: { ...mockUser, subscription: 'free' as const }
    });

    renderWithRouter(<Profile />);

    expect(screen.getByText(/free/i)).toBeInTheDocument();
    expect(screen.getByText(/upgrade/i)).toBeInTheDocument();
  });
});
