import { useState, useCallback, useEffect } from 'react';
import { useWearablesStore } from '@/store/wearablesStore';
import { toastSuccess, toastError, toastAI } from '@/components/ui/enhanced-toast';

export const useWearableSync = () => {
  const [isConnecting, setIsConnecting] = useState<string | null>(null);
  const {
    connectedDevices,
    syncStatus,
    autoSyncEnabled,
    connectDevice,
    disconnectDevice,
    syncAllDevices
  } = useWearablesStore();

  // Auto-sync every 15 minutes if enabled
  useEffect(() => {
    if (!autoSyncEnabled) return;

    const interval = setInterval(() => {
      if (connectedDevices.some(d => d.isConnected)) {
        syncAllDevices();
      }
    }, 15 * 60 * 1000); // 15 minutes

    return () => clearInterval(interval);
  }, [autoSyncEnabled, connectedDevices, syncAllDevices]);

  const connectToAppleHealth = useCallback(async () => {
    setIsConnecting('apple_health');
    
    try {
      // In a real implementation, you would:
      // 1. Check if running on iOS
      // 2. Use HealthKit APIs or a Capacitor plugin
      // 3. Request permissions for specific data types
      
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate connection process
      
      const device = {
        id: 'apple-health-' + Date.now(),
        name: 'Apple Health',
        type: 'apple_health' as const,
        isConnected: true,
        lastSync: new Date(),
        capabilities: ['heart_rate', 'hrv', 'sleep', 'steps', 'calories']
      };
      
      connectDevice(device);
      toastSuccess('Apple Health connected successfully');
      
    } catch (error) {
      toastError('Failed to connect to Apple Health', 'Please check your permissions and try again');
    } finally {
      setIsConnecting(null);
    }
  }, [connectDevice]);

  const connectToGoogleFit = useCallback(async () => {
    setIsConnecting('google_fit');
    
    try {
      // In a real implementation, you would:
      // 1. Use Google Fit APIs
      // 2. Handle OAuth authentication
      // 3. Request appropriate scopes
      
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const device = {
        id: 'google-fit-' + Date.now(),
        name: 'Google Fit',
        type: 'google_fit' as const,
        isConnected: true,
        lastSync: new Date(),
        capabilities: ['heart_rate', 'steps', 'calories', 'sleep']
      };
      
      connectDevice(device);
      toastSuccess('Google Fit connected successfully');
      
    } catch (error) {
      toastError('Failed to connect to Google Fit', 'Please check your permissions and try again');
    } finally {
      setIsConnecting(null);
    }
  }, [connectDevice]);

  const connectToAppleWatch = useCallback(async () => {
    setIsConnecting('apple_watch');
    
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const device = {
        id: 'apple-watch-' + Date.now(),
        name: 'Apple Watch',
        type: 'apple_watch' as const,
        isConnected: true,
        lastSync: new Date(),
        batteryLevel: 85,
        capabilities: ['heart_rate', 'hrv', 'temperature', 'blood_oxygen', 'sleep']
      };
      
      connectDevice(device);
      toastSuccess('Apple Watch connected successfully');
      
    } catch (error) {
      toastError('Failed to connect to Apple Watch', 'Make sure your watch is nearby and unlocked');
    } finally {
      setIsConnecting(null);
    }
  }, [connectDevice]);

  const disconnect = useCallback(async (deviceId: string) => {
    try {
      disconnectDevice(deviceId);
      toastAI('Device disconnected', 'Wearable sync has been disabled for this device');
    } catch (error) {
      toastError('Failed to disconnect device');
    }
  }, [disconnectDevice]);

  const manualSync = useCallback(async () => {
    if (connectedDevices.length === 0) {
      toastError('No devices connected', 'Please connect a wearable device first');
      return;
    }

    toastAI('Syncing wearables...', 'Fetching latest health data');
    await syncAllDevices();
    
    if (syncStatus === 'success') {
      toastSuccess('Sync completed', 'All wearable data has been updated');
    }
  }, [connectedDevices, syncAllDevices, syncStatus]);

  return {
    isConnecting,
    connectedDevices,
    syncStatus,
    connectToAppleHealth,
    connectToGoogleFit,
    connectToAppleWatch,
    disconnect,
    manualSync
  };
};
