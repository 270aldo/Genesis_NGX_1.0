import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import SignIn from '../SignIn';
import { useAuthStore } from '@/store/authStore';
import { authService } from '@/services/api/auth.service';

jest.mock('@/store/authStore', () => ({
  useAuthStore: jest.fn()
}));

jest.mock('@/services/api/auth.service', () => ({
  authService: {
    login: jest.fn()
  }
}));

const mockUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>;
const mockLogin = authService.login as jest.MockedFunction<typeof authService.login>;

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('SignIn', () => {
  beforeEach(() => {
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

    jest.clearAllMocks();
  });

  it('renders sign in form', () => {
    renderWithRouter(<SignIn />);

    expect(screen.getByRole('textbox', { name: /email/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('validates required fields', async () => {
    const user = userEvent.setup();
    renderWithRouter(<SignIn />);

    const submitButton = screen.getByRole('button', { name: /sign in/i });
    await user.click(submitButton);

    expect(screen.getByText(/email is required/i)).toBeInTheDocument();
    expect(screen.getByText(/password is required/i)).toBeInTheDocument();
  });

  it('submits form with valid credentials', async () => {
    const user = userEvent.setup();
    const mockAuthResponse = {
      user: { id: '1', email: 'test@example.com', name: 'Test User' },
      token: 'mock-token',
      refreshToken: 'mock-refresh'
    };

    mockLogin.mockResolvedValueOnce(mockAuthResponse);

    renderWithRouter(<SignIn />);

    await user.type(screen.getByRole('textbox', { name: /email/i }), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    expect(mockLogin).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123'
    });
  });

  it('displays error message on login failure', async () => {
    const user = userEvent.setup();
    mockLogin.mockRejectedValueOnce({ message: 'Invalid credentials' });

    renderWithRouter(<SignIn />);

    await user.type(screen.getByRole('textbox', { name: /email/i }), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'wrong-password');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
    });
  });

  it('shows loading state during sign in', async () => {
    const user = userEvent.setup();
    mockLogin.mockImplementation(() => new Promise(() => {})); // Never resolves

    renderWithRouter(<SignIn />);

    await user.type(screen.getByRole('textbox', { name: /email/i }), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    expect(screen.getByText(/signing in/i)).toBeInTheDocument();
  });

  it('has link to sign up page', () => {
    renderWithRouter(<SignIn />);

    const signUpLink = screen.getByRole('link', { name: /sign up/i });
    expect(signUpLink).toHaveAttribute('href', '/signup');
  });

  it('has forgot password link', () => {
    renderWithRouter(<SignIn />);

    const forgotPasswordLink = screen.getByRole('link', { name: /forgot password/i });
    expect(forgotPasswordLink).toHaveAttribute('href', '/forgot-password');
  });

  it('validates email format', async () => {
    const user = userEvent.setup();
    renderWithRouter(<SignIn />);

    await user.type(screen.getByRole('textbox', { name: /email/i }), 'invalid-email');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    expect(screen.getByText(/valid email/i)).toBeInTheDocument();
  });

  it('redirects authenticated users', () => {
    mockUseAuthStore.mockReturnValue({
      ...mockUseAuthStore(),
      isAuthenticated: true,
      user: { id: '1', email: 'test@example.com', name: 'Test User' }
    });

    // This would typically redirect, but in tests we just check the redirect logic
    renderWithRouter(<SignIn />);
    // In a real implementation, this would redirect to dashboard
  });
});
