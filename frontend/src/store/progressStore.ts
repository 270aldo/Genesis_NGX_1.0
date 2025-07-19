
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface ProgressData {
  date: string;
  weight: number;
  bodyFat: number;
  muscleMass: number;
  waist: number;
  chest: number;
  arms: number;
  thighs: number;
}

export interface Goal {
  id: string;
  title: string;
  target: number;
  current: number;
  unit: string;
  deadline: string;
  category: 'weight' | 'strength' | 'endurance' | 'body_composition';
}

export interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  unlockedAt: string;
  category: 'milestone' | 'consistency' | 'improvement';
}

interface ProgressState {
  progressData: ProgressData[];
  goals: Goal[];
  achievements: Achievement[];
  selectedTimeframe: '1W' | '1M' | '3M' | '1Y';
  
  // Actions
  setTimeframe: (timeframe: '1W' | '1M' | '3M' | '1Y') => void;
  addProgressEntry: (entry: ProgressData) => void;
  updateGoal: (goalId: string, updates: Partial<Goal>) => void;
  unlockAchievement: (achievement: Achievement) => void;
  getFilteredData: () => ProgressData[];
}

// Mock data for demonstration
const mockProgressData: ProgressData[] = [
  { date: '2024-01-01', weight: 75, bodyFat: 18, muscleMass: 62, waist: 85, chest: 95, arms: 35, thighs: 60 },
  { date: '2024-01-15', weight: 74.5, bodyFat: 17.5, muscleMass: 62.5, waist: 84, chest: 96, arms: 35.5, thighs: 60.5 },
  { date: '2024-02-01', weight: 74, bodyFat: 17, muscleMass: 63, waist: 83, chest: 97, arms: 36, thighs: 61 },
  { date: '2024-02-15', weight: 73.5, bodyFat: 16.5, muscleMass: 63.5, waist: 82, chest: 98, arms: 36.5, thighs: 61.5 },
  { date: '2024-03-01', weight: 73, bodyFat: 16, muscleMass: 64, waist: 81, chest: 99, arms: 37, thighs: 62 },
];

const mockGoals: Goal[] = [
  { id: '1', title: 'Target Weight', target: 72, current: 73, unit: 'kg', deadline: '2024-06-01', category: 'weight' },
  { id: '2', title: 'Body Fat %', target: 15, current: 16, unit: '%', deadline: '2024-06-01', category: 'body_composition' },
  { id: '3', title: 'Muscle Mass', target: 65, current: 64, unit: 'kg', deadline: '2024-06-01', category: 'body_composition' },
  { id: '4', title: 'Bench Press', target: 100, current: 85, unit: 'kg', deadline: '2024-05-01', category: 'strength' },
];

const mockAchievements: Achievement[] = [
  { id: '1', title: 'First Milestone', description: 'Completed your first week of training', icon: '🎯', unlockedAt: '2024-01-07', category: 'milestone' },
  { id: '2', title: 'Consistency King', description: '30 days of consistent tracking', icon: '👑', unlockedAt: '2024-01-30', category: 'consistency' },
  { id: '3', title: 'Body Recomposition', description: 'Lost fat while gaining muscle', icon: '💪', unlockedAt: '2024-02-15', category: 'improvement' },
];

export const useProgressStore = create<ProgressState>()(
  persist(
    (set, get) => ({
      progressData: mockProgressData,
      goals: mockGoals,
      achievements: mockAchievements,
      selectedTimeframe: '3M',

      setTimeframe: (timeframe) => set({ selectedTimeframe: timeframe }),

      addProgressEntry: (entry) => set((state) => ({
        progressData: [...state.progressData, entry].sort((a, b) => 
          new Date(a.date).getTime() - new Date(b.date).getTime()
        )
      })),

      updateGoal: (goalId, updates) => set((state) => ({
        goals: state.goals.map(goal => 
          goal.id === goalId ? { ...goal, ...updates } : goal
        )
      })),

      unlockAchievement: (achievement) => set((state) => ({
        achievements: [...state.achievements, achievement]
      })),

      getFilteredData: () => {
        const { progressData, selectedTimeframe } = get();
        const now = new Date();
        const startDate = new Date();

        switch (selectedTimeframe) {
          case '1W':
            startDate.setDate(now.getDate() - 7);
            break;
          case '1M':
            startDate.setMonth(now.getMonth() - 1);
            break;
          case '3M':
            startDate.setMonth(now.getMonth() - 3);
            break;
          case '1Y':
            startDate.setFullYear(now.getFullYear() - 1);
            break;
        }

        return progressData.filter(entry => new Date(entry.date) >= startDate);
      }
    }),
    {
      name: 'ngx-progress-store',
      partialize: (state) => ({
        progressData: state.progressData,
        goals: state.goals,
        achievements: state.achievements,
        selectedTimeframe: state.selectedTimeframe
      })
    }
  )
);
