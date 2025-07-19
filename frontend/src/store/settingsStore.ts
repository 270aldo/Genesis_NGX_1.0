
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface UserSettings {
  theme: 'light' | 'dark' | 'system';
  language: 'en' | 'es' | 'fr' | 'de';
  aiModel: 'gpt-4o' | 'gpt-4o-mini' | 'gpt-4.5-preview';
  voiceEnabled: boolean;
  autoSave: boolean;
  notifications: {
    email: boolean;
    push: boolean;
    desktop: boolean;
  };
  privacy: {
    dataCollection: boolean;
    analytics: boolean;
    shareUsage: boolean;
  };
}

interface SettingsState {
  settings: UserSettings;
  
  // Actions
  updateSettings: (updates: Partial<UserSettings>) => void;
  resetSettings: () => void;
  updateNotifications: (notifications: Partial<UserSettings['notifications']>) => void;
  updatePrivacy: (privacy: Partial<UserSettings['privacy']>) => void;
}

const defaultSettings: UserSettings = {
  theme: 'dark',
  language: 'en',
  aiModel: 'gpt-4o-mini',
  voiceEnabled: true,
  autoSave: true,
  notifications: {
    email: true,
    push: true,
    desktop: false,
  },
  privacy: {
    dataCollection: true,
    analytics: false,
    shareUsage: false,
  },
};

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      settings: defaultSettings,

      updateSettings: (updates: Partial<UserSettings>) => {
        set((state) => ({
          settings: { ...state.settings, ...updates },
        }));
      },

      resetSettings: () => {
        set({ settings: defaultSettings });
      },

      updateNotifications: (notifications: Partial<UserSettings['notifications']>) => {
        set((state) => ({
          settings: {
            ...state.settings,
            notifications: { ...state.settings.notifications, ...notifications },
          },
        }));
      },

      updatePrivacy: (privacy: Partial<UserSettings['privacy']>) => {
        set((state) => ({
          settings: {
            ...state.settings,
            privacy: { ...state.settings.privacy, ...privacy },
          },
        }));
      },
    }),
    {
      name: 'ngx-agents-settings',
    }
  )
);
