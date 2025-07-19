
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  createdAt: Date;
  subscription?: 'free' | 'pro' | 'enterprise';
  tokens: number;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  setUser: (user: User) => void;
  logout: () => void;
  updateProfile: (updates: Partial<User>) => void;
  setLoading: (loading: boolean) => void;
  addTokens: (amount: number) => void;
  useTokens: (amount: number) => boolean;
  getTokens: () => number;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,

      setUser: (user: User) => {
        // Ensure tokens field exists, default to 100 for new users
        const userWithTokens = {
          ...user,
          tokens: user.tokens ?? 100
        };
        set({ user: userWithTokens, isAuthenticated: true });
      },

      logout: () => {
        set({ user: null, isAuthenticated: false });
      },

      updateProfile: (updates: Partial<User>) => {
        const currentUser = get().user;
        if (currentUser) {
          set({ user: { ...currentUser, ...updates } });
        }
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      addTokens: (amount: number) => {
        const currentUser = get().user;
        if (currentUser) {
          const updatedUser = {
            ...currentUser,
            tokens: currentUser.tokens + amount
          };
          set({ user: updatedUser });
        }
      },

      useTokens: (amount: number) => {
        const currentUser = get().user;
        if (currentUser && currentUser.tokens >= amount) {
          const updatedUser = {
            ...currentUser,
            tokens: currentUser.tokens - amount
          };
          set({ user: updatedUser });
          return true;
        }
        return false;
      },

      getTokens: () => {
        const currentUser = get().user;
        return currentUser?.tokens ?? 0;
      },
    }),
    {
      name: 'ngx-agents-auth',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
