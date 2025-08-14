import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { VoiceInterface } from '../VoiceInterface';
import { useVoiceConversation } from '@/hooks/useVoiceConversation';

jest.mock('@/hooks/useVoiceConversation', () => ({
  useVoiceConversation: jest.fn()
}));

const mockUseVoiceConversation = useVoiceConversation as jest.MockedFunction<typeof useVoiceConversation>;

const mockVoiceHook = {
  isVoiceActive: false,
  conversationId: null,
  isSpeaking: false,
  status: 'idle',
  startVoiceConversation: jest.fn(),
  endVoiceConversation: jest.fn(),
  setVolume: jest.fn()
};

describe('VoiceInterface', () => {
  beforeEach(() => {
    mockUseVoiceConversation.mockReturnValue(mockVoiceHook);
    jest.clearAllMocks();
  });

  it('renders voice control buttons', () => {
    render(<VoiceInterface />);

    expect(screen.getByRole('button', { name: /start voice/i })).toBeInTheDocument();
  });

  it('starts voice conversation when button is clicked', async () => {
    const user = userEvent.setup();
    render(<VoiceInterface />);

    const startButton = screen.getByRole('button', { name: /start voice/i });
    await user.click(startButton);

    expect(mockVoiceHook.startVoiceConversation).toHaveBeenCalled();
  });

  it('shows stop button when voice is active', () => {
    mockUseVoiceConversation.mockReturnValue({
      ...mockVoiceHook,
      isVoiceActive: true
    });

    render(<VoiceInterface />);

    expect(screen.getByRole('button', { name: /stop voice/i })).toBeInTheDocument();
  });

  it('displays speaking indicator', () => {
    mockUseVoiceConversation.mockReturnValue({
      ...mockVoiceHook,
      isSpeaking: true
    });

    render(<VoiceInterface />);

    expect(screen.getByText(/speaking/i)).toBeInTheDocument();
  });

  it('shows volume control', () => {
    render(<VoiceInterface />);

    expect(screen.getByRole('slider', { name: /volume/i })).toBeInTheDocument();
  });

  it('adjusts volume when slider changes', async () => {
    const user = userEvent.setup();
    render(<VoiceInterface />);

    const volumeSlider = screen.getByRole('slider', { name: /volume/i });
    fireEvent.change(volumeSlider, { target: { value: 0.8 } });

    expect(mockVoiceHook.setVolume).toHaveBeenCalledWith(0.8);
  });

  it('displays connection status', () => {
    mockUseVoiceConversation.mockReturnValue({
      ...mockVoiceHook,
      status: 'connected'
    });

    render(<VoiceInterface />);

    expect(screen.getByText(/connected/i)).toBeInTheDocument();
  });
});
