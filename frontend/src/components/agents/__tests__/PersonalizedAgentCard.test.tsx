import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PersonalizedAgentCard } from '../PersonalizedAgentCard';
import { useHybridIntelligencePersonalization } from '@/hooks/useHybridIntelligencePersonalization';
import { useHybridIntelligenceStore } from '@/store/hybridIntelligenceStore';
import { Zap } from 'lucide-react';

// Mock the hooks
jest.mock('@/hooks/useHybridIntelligencePersonalization');
jest.mock('@/store/hybridIntelligenceStore');

const mockUseHybridIntelligencePersonalization = useHybridIntelligencePersonalization as jest.MockedFunction<typeof useHybridIntelligencePersonalization>;
const mockUseHybridIntelligenceStore = useHybridIntelligenceStore as jest.MockedFunction<typeof useHybridIntelligenceStore>;

describe('PersonalizedAgentCard Component', () => {
  const defaultProps = {
    agentId: 'blaze',
    agentName: 'Blaze',
    agentDescription: 'High-intensity trainer',
    agentIcon: Zap,
    agentColor: 'orange',
  };

  const mockPersonalizationHook = {
    personalizeContent: jest.fn().mockResolvedValue({
      archetype_considerations: {
        strategic_alignment: 'performance_optimization',
        communication_style: 'direct',
        intensity_preference: 'high',
      },
    }),
    getPersonalizedGreeting: jest.fn().mockReturnValue('Ready to push your limits?'),
    checkAgentCompatibility: jest.fn().mockReturnValue({ compatible: true }),
    agentAffinity: {},
  };

  const mockStoreHook = {
    archetype: 'PRIME',
    currentBiometrics: {
      energy_level: 0.8,
      recovery_status: 0.7,
    },
    getAgentAffinity: jest.fn().mockReturnValue(0.85),
    isArchetypeConfident: true,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseHybridIntelligencePersonalization.mockReturnValue(mockPersonalizationHook);
    mockUseHybridIntelligenceStore.mockReturnValue(mockStoreHook);
  });

  describe('Basic rendering', () => {
    it('renders agent card with basic information', () => {
      render(<PersonalizedAgentCard {...defaultProps} />);
      
      expect(screen.getByText('Blaze')).toBeInTheDocument();
      expect(screen.getByText('High-intensity trainer')).toBeInTheDocument();
    });

    it('renders agent icon', () => {
      render(<PersonalizedAgentCard {...defaultProps} />);
      
      const icon = screen.getByRole('img', { hidden: true }).parentElement;
      expect(icon).toHaveClass('bg-orange-100');
    });

    it('applies custom className', () => {
      render(<PersonalizedAgentCard {...defaultProps} className="custom-card-class" />);
      
      const card = screen.getByText('Blaze').closest('.custom-card-class');
      expect(card).toBeInTheDocument();
    });

    it('shows active state when isActive is true', () => {
      render(<PersonalizedAgentCard {...defaultProps} isActive={true} />);
      
      const card = screen.getByText('Blaze').closest('[class*="ring-2"]');
      expect(card).toHaveClass('ring-2', 'ring-blue-500', 'shadow-lg');
    });
  });

  describe('Personalized content', () => {
    it('displays personalized greeting', async () => {
      render(<PersonalizedAgentCard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('"Ready to push your limits?"')).toBeInTheDocument();
      });
    });

    it('shows affinity score', async () => {
      render(<PersonalizedAgentCard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('85%')).toBeInTheDocument();
        expect(screen.getByText('Excelente')).toBeInTheDocument();
      });
    });

    it('displays compatibility status', async () => {
      render(<PersonalizedAgentCard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Compatible con tu perfil')).toBeInTheDocument();
      });
    });

    it('shows incompatibility warning', async () => {
      mockPersonalizationHook.checkAgentCompatibility.mockReturnValue({
        compatible: false,
        reason: 'Not suitable for your current fitness level',
      });
      
      render(<PersonalizedAgentCard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Not suitable for your current fitness level')).toBeInTheDocument();
      });
    });

    it('displays archetype alignment for PRIME archetype', async () => {
      render(<PersonalizedAgentCard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Alineado con tu arquetipo')).toBeInTheDocument();
      });
    });

    it('displays complementary archetype for misaligned agents', async () => {
      mockStoreHook.archetype = 'LONGEVITY';
      mockUseHybridIntelligenceStore.mockReturnValue(mockStoreHook);
      
      render(<PersonalizedAgentCard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Arquetipo complementario')).toBeInTheDocument();
      });
    });
  });

  describe('Biometric insights', () => {
    it('displays energy level when available', async () => {
      render(<PersonalizedAgentCard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Energía: 80%')).toBeInTheDocument();
      });
    });

    it('displays recovery status when available', async () => {
      render(<PersonalizedAgentCard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Recuperación: 70%')).toBeInTheDocument();
      });
    });

    it('handles missing biometric data', async () => {
      mockStoreHook.currentBiometrics = undefined;
      mockUseHybridIntelligenceStore.mockReturnValue(mockStoreHook);
      
      render(<PersonalizedAgentCard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.queryByText(/Energía:/)).not.toBeInTheDocument();
        expect(screen.queryByText(/Recuperación:/)).not.toBeInTheDocument();
      });
    });
  });

  describe('Recommendations', () => {
    it('displays personalized recommendations', async () => {
      render(<PersonalizedAgentCard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Enfoque en optimización de rendimiento')).toBeInTheDocument();
        expect(screen.getByText('Comunicación directa y eficiente')).toBeInTheDocument();
      });
    });

    it('limits recommendations to 2 items', async () => {
      mockPersonalizationHook.personalizeContent.mockResolvedValue({
        archetype_considerations: {
          strategic_alignment: 'performance_optimization',
          communication_style: 'direct',
          intensity_preference: 'high',
          additional_preference: 'extra',
        },
      });
      
      render(<PersonalizedAgentCard {...defaultProps} />);
      
      await waitFor(() => {
        const recommendations = screen.getAllByText(/Enfoque|Comunicación|Entrenamientos/);
        expect(recommendations).toHaveLength(2);
      });
    });
  });

  describe('Optimal timing', () => {
    it('shows optimal timing indicator when appropriate', async () => {
      // Mock current hour to be 7 AM (optimal for Blaze)
      jest.spyOn(Date.prototype, 'getHours').mockReturnValue(7);
      
      render(<PersonalizedAgentCard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Momento óptimo para interactuar')).toBeInTheDocument();
      });
    });

    it('does not show optimal timing indicator outside optimal hours', async () => {
      // Mock current hour to be 2 PM (not optimal for Blaze)
      jest.spyOn(Date.prototype, 'getHours').mockReturnValue(14);
      
      render(<PersonalizedAgentCard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.queryByText('Momento óptimo para interactuar')).not.toBeInTheDocument();
      });
    });
  });

  describe('User interactions', () => {
    it('calls onSelect when card is clicked', async () => {
      const handleSelect = jest.fn();
      const user = userEvent.setup();
      
      render(<PersonalizedAgentCard {...defaultProps} onSelect={handleSelect} />);
      
      const card = screen.getByText('Blaze').closest('.cursor-pointer');
      await user.click(card!);
      
      expect(handleSelect).toHaveBeenCalledWith('blaze');
    });

    it('calls onStartChat when chat button is clicked', async () => {
      const handleStartChat = jest.fn();
      const user = userEvent.setup();
      
      render(<PersonalizedAgentCard {...defaultProps} onStartChat={handleStartChat} />);
      
      await waitFor(() => {
        const chatButton = screen.getByRole('button', { name: /Chatear/i });
        expect(chatButton).toBeInTheDocument();
      });
      
      const chatButton = screen.getByRole('button', { name: /Chatear/i });
      await user.click(chatButton);
      
      expect(handleStartChat).toHaveBeenCalledWith('blaze');
    });

    it('prevents event propagation when chat button is clicked', async () => {
      const handleSelect = jest.fn();
      const handleStartChat = jest.fn();
      const user = userEvent.setup();
      
      render(
        <PersonalizedAgentCard 
          {...defaultProps} 
          onSelect={handleSelect}
          onStartChat={handleStartChat}
        />
      );
      
      await waitFor(() => {
        const chatButton = screen.getByRole('button', { name: /Chatear/i });
        expect(chatButton).toBeInTheDocument();
      });
      
      const chatButton = screen.getByRole('button', { name: /Chatear/i });
      await user.click(chatButton);
      
      expect(handleStartChat).toHaveBeenCalled();
      expect(handleSelect).not.toHaveBeenCalled();
    });

    it('disables chat button when agent is not compatible', async () => {
      mockPersonalizationHook.checkAgentCompatibility.mockReturnValue({
        compatible: false,
        reason: 'Not compatible',
      });
      
      render(<PersonalizedAgentCard {...defaultProps} />);
      
      await waitFor(() => {
        const chatButton = screen.getByRole('button', { name: /Chatear/i });
        expect(chatButton).toBeDisabled();
      });
    });
  });

  describe('Loading state', () => {
    it('shows loading animation while personalizing', async () => {
      // Delay the personalization response
      mockPersonalizationHook.personalizeContent.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({
          archetype_considerations: {},
        }), 100))
      );
      
      render(<PersonalizedAgentCard {...defaultProps} />);
      
      // Check for loading indicator
      const loadingButton = screen.getByRole('button', { name: '' });
      expect(loadingButton).toBeDisabled();
      
      // Wait for loading to complete
      await waitFor(() => {
        expect(screen.getByText('Ready to push your limits?')).toBeInTheDocument();
      });
    });
  });

  describe('Error handling', () => {
    it('handles personalization errors gracefully', async () => {
      mockPersonalizationHook.personalizeContent.mockRejectedValue(new Error('Personalization failed'));
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
      render(<PersonalizedAgentCard {...defaultProps} />);
      
      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Failed to load personalized data:', expect.any(Error));
      });
      
      // Card should still render basic information
      expect(screen.getByText('Blaze')).toBeInTheDocument();
      
      consoleSpy.mockRestore();
    });
  });

  describe('Affinity color coding', () => {
    it.each([
      [0.85, 'text-green-600'],
      [0.6, 'text-blue-600'],
      [0.4, 'text-yellow-600'],
      [0.2, 'text-red-600'],
    ])('shows correct color for affinity %s', async (affinity, expectedClass) => {
      mockStoreHook.getAgentAffinity.mockReturnValue(affinity);
      
      render(<PersonalizedAgentCard {...defaultProps} />);
      
      await waitFor(() => {
        const affinityElement = screen.getByText(`${Math.round(affinity * 100)}%`);
        expect(affinityElement).toHaveClass(expectedClass);
      });
    });
  });

  describe('Progress bar', () => {
    it('displays affinity progress bar', async () => {
      render(<PersonalizedAgentCard {...defaultProps} />);
      
      await waitFor(() => {
        const progressBar = screen.getByRole('progressbar');
        expect(progressBar).toBeInTheDocument();
        expect(progressBar).toHaveAttribute('aria-valuenow', '85');
      });
    });
  });

  describe('Without archetype', () => {
    it('does not load personalized data when archetype is not set', () => {
      mockStoreHook.archetype = null;
      mockUseHybridIntelligenceStore.mockReturnValue(mockStoreHook);
      
      render(<PersonalizedAgentCard {...defaultProps} />);
      
      expect(mockPersonalizationHook.personalizeContent).not.toHaveBeenCalled();
    });
  });
});