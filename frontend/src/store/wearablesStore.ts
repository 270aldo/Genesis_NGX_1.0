
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface WearableDevice {
  id: string;
  name: string;
  type: 'apple_watch' | 'fitbit' | 'garmin' | 'samsung' | 'google_fit' | 'apple_health';
  isConnected: boolean;
  lastSync: Date | null;
  batteryLevel?: number;
  capabilities: string[];
}

export interface BiometricReading {
  id: string;
  type: 'heart_rate' | 'hrv' | 'sleep' | 'steps' | 'calories' | 'temperature' | 'blood_oxygen' | 'stress';
  value: number;
  unit: string;
  timestamp: Date;
  deviceId: string;
  quality: 'high' | 'medium' | 'low';
}

export interface PredictiveAlert {
  id: string;
  type: 'fatigue' | 'overtraining' | 'recovery' | 'illness' | 'optimal_training';
  severity: 'low' | 'medium' | 'high';
  title: string;
  description: string;
  recommendations: string[];
  confidence: number;
  timestamp: Date;
  isRead: boolean;
}

interface WearablesState {
  connectedDevices: WearableDevice[];
  biometricReadings: BiometricReading[];
  predictiveAlerts: PredictiveAlert[];
  syncStatus: 'idle' | 'syncing' | 'success' | 'error';
  lastSyncTime: Date | null;
  autoSyncEnabled: boolean;
  analysisEnabled: boolean;

  // Actions
  connectDevice: (device: WearableDevice) => void;
  disconnectDevice: (deviceId: string) => void;
  addBiometricReading: (reading: BiometricReading) => void;
  addPredictiveAlert: (alert: PredictiveAlert) => void;
  markAlertAsRead: (alertId: string) => void;
  setSyncStatus: (status: 'idle' | 'syncing' | 'success' | 'error') => void;
  setAutoSync: (enabled: boolean) => void;
  setAnalysis: (enabled: boolean) => void;
  syncAllDevices: () => Promise<void>;
  analyzePatterns: () => PredictiveAlert[];
}

// Mock data for demonstration
const mockReadings: BiometricReading[] = [
  {
    id: '1',
    type: 'heart_rate',
    value: 72,
    unit: 'bpm',
    timestamp: new Date(Date.now() - 1000 * 60 * 30),
    deviceId: 'apple-watch-1',
    quality: 'high'
  },
  {
    id: '2',
    type: 'hrv',
    value: 45,
    unit: 'ms',
    timestamp: new Date(Date.now() - 1000 * 60 * 60),
    deviceId: 'apple-watch-1',
    quality: 'high'
  },
  {
    id: '3',
    type: 'sleep',
    value: 7.5,
    unit: 'hours',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 8),
    deviceId: 'apple-watch-1',
    quality: 'medium'
  }
];

export const useWearablesStore = create<WearablesState>()(
  persist(
    (set, get) => ({
      connectedDevices: [],
      biometricReadings: mockReadings,
      predictiveAlerts: [],
      syncStatus: 'idle',
      lastSyncTime: null,
      autoSyncEnabled: true,
      analysisEnabled: true,

      connectDevice: (device) => {
        set((state) => ({
          connectedDevices: [...state.connectedDevices, { ...device, isConnected: true }]
        }));
      },

      disconnectDevice: (deviceId) => {
        set((state) => ({
          connectedDevices: state.connectedDevices.map(device =>
            device.id === deviceId ? { ...device, isConnected: false } : device
          )
        }));
      },

      addBiometricReading: (reading) => {
        set((state) => ({
          biometricReadings: [...state.biometricReadings, reading].slice(-1000) // Keep last 1000 readings
        }));
      },

      addPredictiveAlert: (alert) => {
        set((state) => ({
          predictiveAlerts: [alert, ...state.predictiveAlerts].slice(0, 50) // Keep last 50 alerts
        }));
      },

      markAlertAsRead: (alertId) => {
        set((state) => ({
          predictiveAlerts: state.predictiveAlerts.map(alert =>
            alert.id === alertId ? { ...alert, isRead: true } : alert
          )
        }));
      },

      setSyncStatus: (status) => set({ syncStatus: status }),
      setAutoSync: (enabled) => set({ autoSyncEnabled: enabled }),
      setAnalysis: (enabled) => set({ analysisEnabled: enabled }),

      syncAllDevices: async () => {
        const { connectedDevices, setSyncStatus, addBiometricReading } = get();
        
        setSyncStatus('syncing');
        
        try {
          // Simulate API calls to different wearable services
          for (const device of connectedDevices.filter(d => d.isConnected)) {
            await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate network delay
            
            // Generate mock readings
            const newReading: BiometricReading = {
              id: Date.now().toString(),
              type: 'heart_rate',
              value: 65 + Math.random() * 20,
              unit: 'bpm',
              timestamp: new Date(),
              deviceId: device.id,
              quality: 'high'
            };
            
            addBiometricReading(newReading);
          }
          
          set({ lastSyncTime: new Date() });
          setSyncStatus('success');
          
          // Run analysis after sync
          const alerts = get().analyzePatterns();
          alerts.forEach(alert => get().addPredictiveAlert(alert));
          
        } catch (error) {
          setSyncStatus('error');
        }
      },

      analyzePatterns: () => {
        const { biometricReadings, analysisEnabled } = get();
        
        if (!analysisEnabled) return [];
        
        const alerts: PredictiveAlert[] = [];
        const recentReadings = biometricReadings.filter(
          r => new Date().getTime() - r.timestamp.getTime() < 24 * 60 * 60 * 1000
        );
        
        // Analyze heart rate patterns
        const hrReadings = recentReadings.filter(r => r.type === 'heart_rate');
        if (hrReadings.length > 5) {
          const avgHR = hrReadings.reduce((sum, r) => sum + r.value, 0) / hrReadings.length;
          
          if (avgHR > 80) {
            alerts.push({
              id: Date.now().toString(),
              type: 'fatigue',
              severity: 'medium',
              title: 'Elevated Resting Heart Rate Detected',
              description: 'Your average heart rate has been higher than usual, which may indicate fatigue or overtraining.',
              recommendations: [
                'Consider taking a rest day',
                'Focus on recovery activities like stretching',
                'Ensure adequate hydration and sleep'
              ],
              confidence: 0.75,
              timestamp: new Date(),
              isRead: false
            });
          }
        }
        
        // Analyze HRV patterns
        const hrvReadings = recentReadings.filter(r => r.type === 'hrv');
        if (hrvReadings.length > 3) {
          const avgHRV = hrvReadings.reduce((sum, r) => sum + r.value, 0) / hrvReadings.length;
          
          if (avgHRV > 50) {
            alerts.push({
              id: (Date.now() + 1).toString(),
              type: 'optimal_training',
              severity: 'low',
              title: 'Optimal Recovery State',
              description: 'Your HRV indicates excellent recovery. This is a great time for intensive training.',
              recommendations: [
                'Consider a challenging workout today',
                'Your body is well-recovered and ready',
                'Take advantage of this optimal state'
              ],
              confidence: 0.85,
              timestamp: new Date(),
              isRead: false
            });
          }
        }
        
        return alerts;
      }
    }),
    {
      name: 'wearables-store',
      partialize: (state) => ({
        connectedDevices: state.connectedDevices,
        biometricReadings: state.biometricReadings.slice(-100),
        predictiveAlerts: state.predictiveAlerts.slice(0, 20),
        autoSyncEnabled: state.autoSyncEnabled,
        analysisEnabled: state.analysisEnabled
      })
    }
  )
);
