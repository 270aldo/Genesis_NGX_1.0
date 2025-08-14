import { renderHook, act } from '@testing-library/react';
import { useAuthStore, User } from '../authStore';

// Mock localStorage for persistence
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage
});

// Mock zustand persist middleware
jest.mock('zustand/middleware', () => ({
  persist: (config: any, options: any) => config
}));

describe('AuthStore', () => {
  const mockUser: User = {
    id: '1',
    email: 'test@example.com',
    name: 'Test User',
    avatar: 'http://example.com/avatar.jpg',
    createdAt: new Date('2024-01-01'),
    subscription: 'pro',
    tokens: 100
  };

  beforeEach(() => {
    // Reset store state before each test
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: false
    });

    jest.clearAllMocks();
  });

  describe('initial state', () => {
    it('has correct default values', () => {
      const { result } = renderHook(() => useAuthStore());

      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.isLoading).toBe(false);
    });

    it('provides all required actions', () => {
      const { result } = renderHook(() => useAuthStore());

      expect(typeof result.current.setUser).toBe('function');
      expect(typeof result.current.logout).toBe('function');
      expect(typeof result.current.updateProfile).toBe('function');
      expect(typeof result.current.setLoading).toBe('function');
      expect(typeof result.current.addTokens).toBe('function');
      expect(typeof result.current.useTokens).toBe('function');
      expect(typeof result.current.getTokens).toBe('function');
    });
  });

  describe('setUser', () => {
    it('sets user and authentication status', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setUser(mockUser);
      });

      expect(result.current.user).toEqual(mockUser);
      expect(result.current.isAuthenticated).toBe(true);
    });

    it('sets default tokens for user without tokens', () => {
      const userWithoutTokens = {
        ...mockUser,
        tokens: undefined as any
      };

      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setUser(userWithoutTokens);
      });

      expect(result.current.user?.tokens).toBe(100);
    });

    it('preserves existing tokens when provided', () => {
      const userWithTokens = {
        ...mockUser,
        tokens: 250
      };

      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setUser(userWithTokens);
      });

      expect(result.current.user?.tokens).toBe(250);
    });

    it('handles user with zero tokens', () => {
      const userWithZeroTokens = {
        ...mockUser,
        tokens: 0
      };

      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setUser(userWithZeroTokens);
      });

      expect(result.current.user?.tokens).toBe(0);
    });
  });

  describe('logout', () => {
    it('clears user and authentication status', () => {
      const { result } = renderHook(() => useAuthStore());

      // Set user first
      act(() => {
        result.current.setUser(mockUser);
      });

      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.user).not.toBeNull();

      // Then logout
      act(() => {
        result.current.logout();
      });

      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });

    it('can be called when already logged out', () => {
      const { result } = renderHook(() => useAuthStore());

      expect(() => {
        act(() => {
          result.current.logout();
        });
      }).not.toThrow();

      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });
  });

  describe('updateProfile', () => {
    it('updates user profile when authenticated', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setUser(mockUser);
      });

      const updates = {
        name: 'Updated Name',
        subscription: 'enterprise' as const
      };

      act(() => {
        result.current.updateProfile(updates);
      });

      expect(result.current.user?.name).toBe('Updated Name');
      expect(result.current.user?.subscription).toBe('enterprise');
      expect(result.current.user?.email).toBe(mockUser.email); // Unchanged
      expect(result.current.user?.id).toBe(mockUser.id); // Unchanged
    });

    it('does nothing when user is not authenticated', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.updateProfile({ name: 'New Name' });
      });

      expect(result.current.user).toBeNull();
    });

    it('can update partial fields', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setUser(mockUser);
      });

      act(() => {
        result.current.updateProfile({ avatar: 'new-avatar.jpg' });
      });

      expect(result.current.user?.avatar).toBe('new-avatar.jpg');
      expect(result.current.user?.name).toBe(mockUser.name); // Unchanged
    });

    it('can update tokens through profile update', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setUser(mockUser);
      });

      act(() => {
        result.current.updateProfile({ tokens: 500 });
      });

      expect(result.current.user?.tokens).toBe(500);
    });
  });

  describe('setLoading', () => {
    it('sets loading state to true', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setLoading(true);
      });

      expect(result.current.isLoading).toBe(true);
    });

    it('sets loading state to false', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setLoading(false);
      });

      expect(result.current.isLoading).toBe(false);
    });

    it('can toggle loading state', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setLoading(true);
      });
      expect(result.current.isLoading).toBe(true);

      act(() => {
        result.current.setLoading(false);
      });
      expect(result.current.isLoading).toBe(false);
    });
  });

  describe('token management', () => {
    beforeEach(() => {
      const { result } = renderHook(() => useAuthStore());
      act(() => {
        result.current.setUser(mockUser);
      });
    });

    describe('addTokens', () => {
      it('adds tokens to authenticated user', () => {
        const { result } = renderHook(() => useAuthStore());

        act(() => {
          result.current.addTokens(50);
        });

        expect(result.current.user?.tokens).toBe(150); // 100 + 50
      });

      it('handles adding zero tokens', () => {
        const { result } = renderHook(() => useAuthStore());

        act(() => {
          result.current.addTokens(0);
        });

        expect(result.current.user?.tokens).toBe(100); // Unchanged
      });

      it('handles adding negative tokens', () => {
        const { result } = renderHook(() => useAuthStore());

        act(() => {
          result.current.addTokens(-25);
        });

        expect(result.current.user?.tokens).toBe(75); // 100 - 25
      });

      it('does nothing when user is not authenticated', () => {
        const { result } = renderHook(() => useAuthStore());

        act(() => {
          result.current.logout();
        });

        act(() => {
          result.current.addTokens(50);
        });

        expect(result.current.user).toBeNull();
      });

      it('can add large amounts of tokens', () => {
        const { result } = renderHook(() => useAuthStore());

        act(() => {
          result.current.addTokens(1000);
        });

        expect(result.current.user?.tokens).toBe(1100);
      });
    });

    describe('useTokens', () => {
      it('deducts tokens when user has enough', () => {
        const { result } = renderHook(() => useAuthStore());

        let success: boolean;
        act(() => {
          success = result.current.useTokens(30);
        });

        expect(success!).toBe(true);
        expect(result.current.user?.tokens).toBe(70); // 100 - 30
      });

      it('returns false when user does not have enough tokens', () => {
        const { result } = renderHook(() => useAuthStore());

        let success: boolean;
        act(() => {
          success = result.current.useTokens(150);
        });

        expect(success!).toBe(false);
        expect(result.current.user?.tokens).toBe(100); // Unchanged
      });

      it('returns false when user is not authenticated', () => {
        const { result } = renderHook(() => useAuthStore());

        act(() => {
          result.current.logout();
        });

        let success: boolean;
        act(() => {
          success = result.current.useTokens(10);
        });

        expect(success!).toBe(false);
      });

      it('can use all available tokens', () => {
        const { result } = renderHook(() => useAuthStore());

        let success: boolean;
        act(() => {
          success = result.current.useTokens(100);
        });

        expect(success!).toBe(true);
        expect(result.current.user?.tokens).toBe(0);
      });

      it('handles using zero tokens', () => {
        const { result } = renderHook(() => useAuthStore());

        let success: boolean;
        act(() => {
          success = result.current.useTokens(0);
        });

        expect(success!).toBe(true);
        expect(result.current.user?.tokens).toBe(100); // Unchanged
      });

      it('returns false for negative token amounts', () => {
        const { result } = renderHook(() => useAuthStore());

        let success: boolean;
        act(() => {
          success = result.current.useTokens(-10);
        });

        expect(success!).toBe(false);
        expect(result.current.user?.tokens).toBe(100); // Unchanged
      });
    });

    describe('getTokens', () => {
      it('returns current token count for authenticated user', () => {
        const { result } = renderHook(() => useAuthStore());

        const tokens = result.current.getTokens();

        expect(tokens).toBe(100);
      });

      it('returns 0 when user is not authenticated', () => {
        const { result } = renderHook(() => useAuthStore());

        act(() => {
          result.current.logout();
        });

        const tokens = result.current.getTokens();

        expect(tokens).toBe(0);
      });

      it('returns updated token count after modifications', () => {
        const { result } = renderHook(() => useAuthStore());

        act(() => {
          result.current.addTokens(25);
        });

        expect(result.current.getTokens()).toBe(125);

        act(() => {
          result.current.useTokens(50);
        });

        expect(result.current.getTokens()).toBe(75);
      });
    });
  });

  describe('combined operations', () => {
    it('maintains consistency across multiple operations', () => {
      const { result } = renderHook(() => useAuthStore());

      // Set user
      act(() => {
        result.current.setUser(mockUser);
      });

      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.getTokens()).toBe(100);

      // Update profile
      act(() => {
        result.current.updateProfile({ name: 'New Name' });
      });

      expect(result.current.user?.name).toBe('New Name');
      expect(result.current.getTokens()).toBe(100); // Tokens unchanged

      // Use some tokens
      act(() => {
        result.current.useTokens(25);
      });

      expect(result.current.getTokens()).toBe(75);

      // Add tokens
      act(() => {
        result.current.addTokens(50);
      });

      expect(result.current.getTokens()).toBe(125);

      // Logout
      act(() => {
        result.current.logout();
      });

      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.user).toBeNull();
      expect(result.current.getTokens()).toBe(0);
    });

    it('handles rapid token operations', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setUser({ ...mockUser, tokens: 1000 });
      });

      // Perform multiple operations
      act(() => {
        result.current.useTokens(100);
        result.current.addTokens(50);
        result.current.useTokens(200);
        result.current.addTokens(25);
      });

      expect(result.current.getTokens()).toBe(775); // 1000 - 100 + 50 - 200 + 25
    });

    it('prevents token operations when not authenticated', () => {
      const { result } = renderHook(() => useAuthStore());

      // Try operations without authentication
      act(() => {
        result.current.addTokens(100);
        const success = result.current.useTokens(50);
        expect(success).toBe(false);
      });

      expect(result.current.getTokens()).toBe(0);
      expect(result.current.user).toBeNull();
    });
  });

  describe('edge cases', () => {
    it('handles user object with null/undefined fields', () => {
      const partialUser = {
        id: '1',
        email: 'test@example.com',
        name: 'Test',
        createdAt: new Date(),
        avatar: undefined,
        subscription: undefined,
        tokens: 50
      } as User;

      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setUser(partialUser);
      });

      expect(result.current.user?.avatar).toBeUndefined();
      expect(result.current.user?.subscription).toBeUndefined();
      expect(result.current.user?.tokens).toBe(50);
    });

    it('handles very large token amounts', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setUser({ ...mockUser, tokens: Number.MAX_SAFE_INTEGER });
      });

      expect(result.current.getTokens()).toBe(Number.MAX_SAFE_INTEGER);

      act(() => {
        result.current.useTokens(1000);
      });

      expect(result.current.getTokens()).toBe(Number.MAX_SAFE_INTEGER - 1000);
    });

    it('handles user with zero tokens initially', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setUser({ ...mockUser, tokens: 0 });
      });

      expect(result.current.getTokens()).toBe(0);

      const success = result.current.useTokens(1);
      expect(success).toBe(false);

      act(() => {
        result.current.addTokens(10);
      });

      expect(result.current.getTokens()).toBe(10);
    });
  });

  describe('type safety', () => {
    it('maintains proper typing for user object', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setUser(mockUser);
      });

      const user = result.current.user;
      if (user) {
        expect(typeof user.id).toBe('string');
        expect(typeof user.email).toBe('string');
        expect(typeof user.name).toBe('string');
        expect(typeof user.tokens).toBe('number');
        expect(user.createdAt).toBeInstanceOf(Date);
      }
    });

    it('properly handles subscription enum values', () => {
      const { result } = renderHook(() => useAuthStore());

      const freeUser = { ...mockUser, subscription: 'free' as const };
      const proUser = { ...mockUser, subscription: 'pro' as const };
      const enterpriseUser = { ...mockUser, subscription: 'enterprise' as const };

      act(() => {
        result.current.setUser(freeUser);
      });
      expect(result.current.user?.subscription).toBe('free');

      act(() => {
        result.current.setUser(proUser);
      });
      expect(result.current.user?.subscription).toBe('pro');

      act(() => {
        result.current.setUser(enterpriseUser);
      });
      expect(result.current.user?.subscription).toBe('enterprise');
    });
  });
});
