import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ProfileSettings } from '../ProfileSettings';
import { useAuthStore } from '@/store/authStore';

jest.mock('@/store/authStore', () => ({
  useAuthStore: jest.fn()
}));

const mockUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>;
const mockUpdateProfile = jest.fn();

const mockUser = {
  id: '1',
  email: 'john.doe@example.com',
  name: 'John Doe',
  avatar: '/avatars/john.png',
  subscription: 'pro' as const,
  tokens: 150,
  createdAt: new Date('2024-01-01')
};

describe('ProfileSettings', () => {
  beforeEach(() => {
    mockUseAuthStore.mockReturnValue({
      user: mockUser,
      updateProfile: mockUpdateProfile,
      isAuthenticated: true,
      isLoading: false,
      setUser: jest.fn(),
      logout: jest.fn(),
      setLoading: jest.fn(),
      addTokens: jest.fn(),
      useTokens: jest.fn(),
      getTokens: jest.fn()
    });

    jest.clearAllMocks();
  });

  it('displays user information', () => {
    render(<ProfileSettings />);

    expect(screen.getByDisplayValue('John Doe')).toBeInTheDocument();
    expect(screen.getByDisplayValue('john.doe@example.com')).toBeInTheDocument();
  });

  it('allows editing profile information', async () => {
    const user = userEvent.setup();
    render(<ProfileSettings />);

    const nameInput = screen.getByDisplayValue('John Doe');
    await user.clear(nameInput);
    await user.type(nameInput, 'Jane Doe');

    const saveButton = screen.getByRole('button', { name: /save/i });
    await user.click(saveButton);

    expect(mockUpdateProfile).toHaveBeenCalledWith({ name: 'Jane Doe' });
  });

  it('shows subscription information', () => {
    render(<ProfileSettings />);

    expect(screen.getByText(/pro/i)).toBeInTheDocument();
  });

  it('validates form inputs', async () => {
    const user = userEvent.setup();
    render(<ProfileSettings />);

    const nameInput = screen.getByDisplayValue('John Doe');
    await user.clear(nameInput);

    const saveButton = screen.getByRole('button', { name: /save/i });
    await user.click(saveButton);

    expect(screen.getByText(/name is required/i)).toBeInTheDocument();
  });

  it('handles save errors', async () => {
    mockUpdateProfile.mockRejectedValueOnce(new Error('Update failed'));

    const user = userEvent.setup();
    render(<ProfileSettings />);

    const nameInput = screen.getByDisplayValue('John Doe');
    await user.type(nameInput, ' Updated');

    const saveButton = screen.getByRole('button', { name: /save/i });
    await user.click(saveButton);

    await waitFor(() => {
      expect(screen.getByText(/failed to update/i)).toBeInTheDocument();
    });
  });
});
