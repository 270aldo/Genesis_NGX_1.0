import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Settings from '../Settings';
import { useAuthStore } from '@/store/authStore';

jest.mock('@/store/authStore', () => ({
  useAuthStore: jest.fn()
}));

const mockUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>;

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Settings', () => {
  beforeEach(() => {
    mockUseAuthStore.mockReturnValue({
      user: {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        subscription: 'pro',
        tokens: 250,
        createdAt: new Date()
      },
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

  it('renders settings navigation', () => {
    renderWithRouter(<Settings />);

    expect(screen.getByRole('navigation')).toBeInTheDocument();
    expect(screen.getByText(/profile/i)).toBeInTheDocument();
    expect(screen.getByText(/security/i)).toBeInTheDocument();
    expect(screen.getByText(/notifications/i)).toBeInTheDocument();
  });

  it('displays settings sections', () => {
    renderWithRouter(<Settings />);

    expect(screen.getByText(/account settings/i)).toBeInTheDocument();
    expect(screen.getByText(/privacy settings/i)).toBeInTheDocument();
    expect(screen.getByText(/chat preferences/i)).toBeInTheDocument();
  });

  it('allows navigation between settings tabs', async () => {
    const user = userEvent.setup();
    renderWithRouter(<Settings />);

    const securityTab = screen.getByText(/security/i);
    await user.click(securityTab);

    expect(screen.getByText(/change password/i)).toBeInTheDocument();
  });

  it('shows current user information', () => {
    renderWithRouter(<Settings />);

    expect(screen.getByDisplayValue('Test User')).toBeInTheDocument();
    expect(screen.getByDisplayValue('test@example.com')).toBeInTheDocument();
  });

  it('has save changes button', () => {
    renderWithRouter(<Settings />);

    expect(screen.getByRole('button', { name: /save changes/i })).toBeInTheDocument();
  });

  it('includes danger zone for account deletion', () => {
    renderWithRouter(<Settings />);

    expect(screen.getByText(/danger zone/i)).toBeInTheDocument();
    expect(screen.getByText(/delete account/i)).toBeInTheDocument();
  });

  it('displays subscription information', () => {
    renderWithRouter(<Settings />);

    expect(screen.getByText(/pro subscription/i)).toBeInTheDocument();
  });

  it('shows theme preferences', () => {
    renderWithRouter(<Settings />);

    expect(screen.getByText(/theme/i)).toBeInTheDocument();
    expect(screen.getByRole('combobox', { name: /theme/i })).toBeInTheDocument();
  });
});
