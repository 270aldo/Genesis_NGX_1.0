
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface NutritionPlan {
  id: string;
  name: string;
  file: File | null;
  content: string;
  uploadDate: Date;
  duration: number; // days
  macros: {
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
  };
  meals: {
    id: string;
    name: string;
    time: string;
    calories: number;
    ingredients: string[];
  }[];
}

interface NutritionState {
  currentPlan: NutritionPlan | null;
  planHistory: NutritionPlan[];
  isUploading: boolean;
  uploadProgress: number;

  // Actions
  setCurrentPlan: (plan: NutritionPlan) => void;
  addPlanToHistory: (plan: NutritionPlan) => void;
  setUploading: (uploading: boolean) => void;
  setUploadProgress: (progress: number) => void;
  clearCurrentPlan: () => void;
}

export const useNutritionStore = create<NutritionState>()(
  persist(
    (set, get) => ({
      currentPlan: null,
      planHistory: [],
      isUploading: false,
      uploadProgress: 0,

      setCurrentPlan: (plan: NutritionPlan) => {
        set({ currentPlan: plan });
        get().addPlanToHistory(plan);
      },

      addPlanToHistory: (plan: NutritionPlan) => {
        set((state) => ({
          planHistory: [plan, ...state.planHistory.filter(p => p.id !== plan.id)].slice(0, 10)
        }));
      },

      setUploading: (uploading: boolean) => set({ isUploading: uploading }),
      setUploadProgress: (progress: number) => set({ uploadProgress: progress }),
      clearCurrentPlan: () => set({ currentPlan: null }),
    }),
    {
      name: 'ngx-nutrition-store',
      partialize: (state) => ({
        currentPlan: state.currentPlan,
        planHistory: state.planHistory.slice(0, 5)
      })
    }
  )
);
