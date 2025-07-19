
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Exercise {
  id: string;
  name: string;
  sets: number;
  reps: string;
  weight?: string;
  rest?: string;
  notes?: string;
}

export interface WorkoutDay {
  id: string;
  name: string;
  exercises: Exercise[];
  completed?: boolean;
  completedAt?: Date;
}

export interface TrainingPlan {
  id: string;
  name: string;
  file: File | null;
  content: string;
  uploadDate: Date;
  duration: number; // weeks
  workoutDays: WorkoutDay[];
  totalWorkouts: number;
  completedWorkouts: number;
}

interface TrainingState {
  currentPlan: TrainingPlan | null;
  planHistory: TrainingPlan[];
  isUploading: boolean;
  uploadProgress: number;
  workoutLogs: Record<string, Record<string, unknown>[]>;

  // Actions
  setCurrentPlan: (plan: TrainingPlan) => void;
  addPlanToHistory: (plan: TrainingPlan) => void;
  setUploading: (uploading: boolean) => void;
  setUploadProgress: (progress: number) => void;
  clearCurrentPlan: () => void;
  completeWorkout: (workoutId: string) => void;
  logExercise: (
    workoutId: string,
    exerciseId: string,
    data: Record<string, unknown>
  ) => void;
}

export const useTrainingStore = create<TrainingState>()(
  persist(
    (set, get) => ({
      currentPlan: null,
      planHistory: [],
      isUploading: false,
      uploadProgress: 0,
      workoutLogs: {},

      setCurrentPlan: (plan: TrainingPlan) => {
        set({ currentPlan: plan });
        get().addPlanToHistory(plan);
      },

      addPlanToHistory: (plan: TrainingPlan) => {
        set((state) => ({
          planHistory: [plan, ...state.planHistory.filter(p => p.id !== plan.id)].slice(0, 10)
        }));
      },

      setUploading: (uploading: boolean) => set({ isUploading: uploading }),
      setUploadProgress: (progress: number) => set({ uploadProgress: progress }),
      clearCurrentPlan: () => set({ currentPlan: null }),

      completeWorkout: (workoutId: string) => {
        set((state) => {
          if (!state.currentPlan) return state;
          
          const updatedPlan = {
            ...state.currentPlan,
            workoutDays: state.currentPlan.workoutDays.map(day =>
              day.id === workoutId
                ? { ...day, completed: true, completedAt: new Date() }
                : day
            ),
            completedWorkouts: state.currentPlan.completedWorkouts + 1
          };

          return { currentPlan: updatedPlan };
        });
      },

      logExercise: (
        workoutId: string,
        exerciseId: string,
        data: Record<string, unknown>
      ) => {
        set((state) => ({
          workoutLogs: {
            ...state.workoutLogs,
            [`${workoutId}-${exerciseId}`]: [
              ...(state.workoutLogs[`${workoutId}-${exerciseId}`] || []),
              { ...data, timestamp: new Date() }
            ]
          }
        }));
      },
    }),
    {
      name: 'ngx-training-store',
      partialize: (state) => ({
        currentPlan: state.currentPlan,
        planHistory: state.planHistory.slice(0, 5),
        workoutLogs: state.workoutLogs
      })
    }
  )
);
