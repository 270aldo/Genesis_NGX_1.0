/**
 * Biometric Updates WebSocket Service
 * Real-time bio-data updates for Layer 2 physiological modulation
 * Integrates with Hybrid Intelligence Engine for live personalization
 */

import { useHybridIntelligenceStore } from '@/store/hybridIntelligenceStore';
import { type UserBiometrics, type BiomarkerData } from '@/services/api/hybridIntelligence.service';

export interface BiometricUpdate {
  type: 'biometrics' | 'biomarkers' | 'device_connection';
  timestamp: string;
  source: 'manual' | 'device' | 'api' | 'wearable';
  data: Partial<UserBiometrics> | Partial<BiomarkerData>;
  deviceId?: string;
  reliability?: number; // 0-1 scale for data quality
}

export interface DeviceConnectionStatus {
  deviceId: string;
  deviceType: 'apple_health' | 'oura_ring' | 'whoop' | 'garmin' | 'fitbit' | 'manual';
  isConnected: boolean;
  lastSync?: string;
  batteryLevel?: number;
  signalStrength?: number;
}

export interface BiometricWebSocketMessage {
  type: 'biometric_update' | 'device_status' | 'sync_request' | 'error';
  userId: string;
  payload: BiometricUpdate | DeviceConnectionStatus | { error: string };
}

class BiometricUpdatesService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectInterval = 5000; // 5 seconds
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private isConnecting = false;
  private listeners: Map<string, Set<(data: any) => void>> = new Map();
  private deviceStatus: Map<string, DeviceConnectionStatus> = new Map();

  constructor() {
    this.setupEventListeners();
  }

  private setupEventListeners() {
    // Listen for Hybrid Intelligence store updates
    const unsubscribe = useHybridIntelligenceStore.subscribe(
      (state) => state.profile,
      (profile) => {
        if (profile && !this.ws) {
          this.connect();
        } else if (!profile && this.ws) {
          this.disconnect();
        }
      }
    );
  }

  async connect(): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      return;
    }

    this.isConnecting = true;

    try {
      const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:9000';
      const profile = useHybridIntelligenceStore.getState().profile;

      if (!profile) {
        throw new Error('No user profile available for biometric connection');
      }

      // Establish WebSocket connection with authentication
      this.ws = new WebSocket(`${wsUrl}/biometric-updates?userId=${profile.user_id}`);

      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
      this.ws.onerror = this.handleError.bind(this);

      // Set connection timeout
      setTimeout(() => {
        if (this.ws?.readyState === WebSocket.CONNECTING) {
          this.ws.close();
          this.isConnecting = false;
          this.handleReconnect();
        }
      }, 10000);

    } catch (error) {
      // Handle connection error gracefully
      this.isConnecting = false;
      this.handleReconnect();
    }
  }

  private handleOpen(): void {
    this.isConnecting = false;
    this.reconnectAttempts = 0;

    // Start heartbeat to keep connection alive
    this.startHeartbeat();

    // Request initial device status
    this.requestDeviceStatus();

    // Emit connection event
    this.emit('connected', { timestamp: new Date().toISOString() });
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const message: BiometricWebSocketMessage = JSON.parse(event.data);

      switch (message.type) {
        case 'biometric_update':
          this.handleBiometricUpdate(message.payload as BiometricUpdate);
          break;

        case 'device_status':
          this.handleDeviceStatus(message.payload as DeviceConnectionStatus);
          break;

        case 'sync_request':
          this.handleSyncRequest();
          break;

        case 'error':
          this.handleServerError(message.payload as { error: string });
          break;

        default:
          // Unknown message type - ignore
      }
    } catch (error) {
      // Message parsing error - ignore malformed messages
    }
  }

  private handleClose(event: CloseEvent): void {
    this.ws = null;
    this.stopHeartbeat();

    // Emit disconnection event
    this.emit('disconnected', {
      code: event.code,
      reason: event.reason,
      timestamp: new Date().toISOString()
    });

    // Attempt to reconnect if not intentionally closed
    if (event.code !== 1000) {
      this.handleReconnect();
    }
  }

  private handleError(error: Event): void {
    console.error('Biometric updates WebSocket error:', error);
    this.emit('error', { error: error.toString(), timestamp: new Date().toISOString() });
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached for biometric updates');
      this.emit('max_reconnect_reached', { attempts: this.reconnectAttempts });
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff

    setTimeout(() => {
      this.connect();
    }, delay);
  }

  private handleBiometricUpdate(update: BiometricUpdate): void {
    const { updateBiometrics, updateBiomarkers } = useHybridIntelligenceStore.getState();

    try {
      // Update the appropriate store based on update type
      if (update.type === 'biometrics') {
        updateBiometrics(update.data as UserBiometrics);
      } else if (update.type === 'biomarkers') {
        updateBiomarkers(update.data as BiomarkerData);
      }

      // Emit update event for components to listen
      this.emit('biometric_update', {
        ...update,
        processed: true,
        processedAt: new Date().toISOString(),
      });
    } catch (error) {
      console.error('Failed to process biometric update:', error);
      this.emit('update_error', { update, error: error.toString() });
    }
  }

  private handleDeviceStatus(status: DeviceConnectionStatus): void {
    this.deviceStatus.set(status.deviceId, status);

    this.emit('device_status', status);
  }

  private handleSyncRequest(): void {
    // Server is requesting a sync of current biometric data
    const { currentBiometrics, biomarkers } = useHybridIntelligenceStore.getState();

    if (currentBiometrics || biomarkers) {
      this.sendSyncResponse({
        biometrics: currentBiometrics,
        biomarkers,
        timestamp: new Date().toISOString(),
      });
    }
  }

  private handleServerError(error: { error: string }): void {
    console.error('Biometric server error:', error.error);
    this.emit('server_error', error);
  }

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({
          type: 'heartbeat',
          timestamp: new Date().toISOString(),
        });
      }
    }, 30000); // 30 seconds
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private send(data: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('Cannot send biometric data: WebSocket not open');
    }
  }

  private requestDeviceStatus(): void {
    this.send({
      type: 'get_device_status',
      timestamp: new Date().toISOString(),
    });
  }

  private sendSyncResponse(data: any): void {
    this.send({
      type: 'sync_response',
      payload: data,
      timestamp: new Date().toISOString(),
    });
  }

  // Public API

  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    this.stopHeartbeat();
    this.isConnecting = false;
  }

  // Manual biometric update (from UI inputs)
  updateBiometrics(biometrics: Partial<UserBiometrics>, source: string = 'manual'): void {
    const update: BiometricUpdate = {
      type: 'biometrics',
      timestamp: new Date().toISOString(),
      source: source as any,
      data: biometrics,
      reliability: source === 'manual' ? 0.8 : 1.0,
    };

    this.send({
      type: 'biometric_update',
      payload: update,
    });
  }

  // Manual biomarker update (from lab results)
  updateBiomarkers(biomarkers: Partial<BiomarkerData>, source: string = 'manual'): void {
    const update: BiometricUpdate = {
      type: 'biomarkers',
      timestamp: new Date().toISOString(),
      source: source as any,
      data: biomarkers,
      reliability: source === 'manual' ? 0.9 : 1.0,
    };

    this.send({
      type: 'biometric_update',
      payload: update,
    });
  }

  // Device connection management
  connectDevice(deviceType: DeviceConnectionStatus['deviceType'], deviceId: string): void {
    this.send({
      type: 'connect_device',
      payload: {
        deviceType,
        deviceId,
        timestamp: new Date().toISOString(),
      },
    });
  }

  disconnectDevice(deviceId: string): void {
    this.send({
      type: 'disconnect_device',
      payload: {
        deviceId,
        timestamp: new Date().toISOString(),
      },
    });
  }

  // Event listener management
  on(event: string, callback: (data: any) => void): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }

    this.listeners.get(event)!.add(callback);

    // Return unsubscribe function
    return () => {
      this.listeners.get(event)?.delete(callback);
    };
  }

  private emit(event: string, data: any): void {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }

  // Status getters
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  getDeviceStatus(deviceId?: string): DeviceConnectionStatus | DeviceConnectionStatus[] {
    if (deviceId) {
      return this.deviceStatus.get(deviceId) || {
        deviceId,
        deviceType: 'manual',
        isConnected: false,
      };
    }
    return Array.from(this.deviceStatus.values());
  }

  getConnectionInfo(): {
    isConnected: boolean;
    reconnectAttempts: number;
    connectedDevices: number;
    lastUpdate?: string;
  } {
    return {
      isConnected: this.isConnected(),
      reconnectAttempts: this.reconnectAttempts,
      connectedDevices: Array.from(this.deviceStatus.values()).filter(d => d.isConnected).length,
      lastUpdate: useHybridIntelligenceStore.getState().lastDataUpdate || undefined,
    };
  }
}

// Singleton instance
export const biometricUpdatesService = new BiometricUpdatesService();

// React hook for easy integration
export const useBiometricUpdates = () => {
  const [connectionInfo, setConnectionInfo] = React.useState(biometricUpdatesService.getConnectionInfo());
  const [devices, setDevices] = React.useState<DeviceConnectionStatus[]>([]);

  React.useEffect(() => {
    // Subscribe to connection events
    const unsubscribeConnected = biometricUpdatesService.on('connected', () => {
      setConnectionInfo(biometricUpdatesService.getConnectionInfo());
    });

    const unsubscribeDisconnected = biometricUpdatesService.on('disconnected', () => {
      setConnectionInfo(biometricUpdatesService.getConnectionInfo());
    });

    const unsubscribeDeviceStatus = biometricUpdatesService.on('device_status', (status) => {
      setDevices(prev => {
        const updated = [...prev];
        const index = updated.findIndex(d => d.deviceId === status.deviceId);
        if (index >= 0) {
          updated[index] = status;
        } else {
          updated.push(status);
        }
        return updated;
      });
    });

    const unsubscribeBiometricUpdate = biometricUpdatesService.on('biometric_update', () => {
      setConnectionInfo(biometricUpdatesService.getConnectionInfo());
    });

    // Initialize devices
    setDevices(biometricUpdatesService.getDeviceStatus() as DeviceConnectionStatus[]);

    return () => {
      unsubscribeConnected();
      unsubscribeDisconnected();
      unsubscribeDeviceStatus();
      unsubscribeBiometricUpdate();
    };
  }, []);

  return {
    ...connectionInfo,
    devices,
    connect: () => biometricUpdatesService.connect(),
    disconnect: () => biometricUpdatesService.disconnect(),
    updateBiometrics: biometricUpdatesService.updateBiometrics.bind(biometricUpdatesService),
    updateBiomarkers: biometricUpdatesService.updateBiomarkers.bind(biometricUpdatesService),
    connectDevice: biometricUpdatesService.connectDevice.bind(biometricUpdatesService),
    disconnectDevice: biometricUpdatesService.disconnectDevice.bind(biometricUpdatesService),
  };
};
