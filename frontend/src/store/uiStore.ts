
import { create } from 'zustand';

interface UIState {
  isDarkMode: boolean;
  sidebarCollapsed: boolean;
  activeModal: string | null;
  isLoading: boolean;
  notifications: Array<{
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
    timestamp: Date;
  }>;
  
  // Actions
  toggleDarkMode: () => void;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  openModal: (modalId: string) => void;
  closeModal: () => void;
  setLoading: (loading: boolean) => void;
  addNotification: (notification: Omit<UIState['notifications'][0], 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
}

export const useUIStore = create<UIState>((set) => ({
  isDarkMode: true,
  sidebarCollapsed: false,
  activeModal: null,
  isLoading: false,
  notifications: [],

  toggleDarkMode: () => {
    set((state) => ({ isDarkMode: !state.isDarkMode }));
  },

  toggleSidebar: () => {
    set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed }));
  },

  setSidebarCollapsed: (collapsed: boolean) => {
    set({ sidebarCollapsed: collapsed });
  },

  openModal: (modalId: string) => {
    set({ activeModal: modalId });
  },

  closeModal: () => {
    set({ activeModal: null });
  },

  setLoading: (loading: boolean) => {
    set({ isLoading: loading });
  },

  addNotification: (notification) => {
    const newNotification = {
      ...notification,
      id: crypto.randomUUID(),
      timestamp: new Date(),
    };
    set((state) => ({
      notifications: [newNotification, ...state.notifications.slice(0, 4)],
    }));
  },

  removeNotification: (id: string) => {
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    }));
  },
}));
