
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { 
  Watch, 
  Smartphone, 
  Wifi, 
  WifiOff, 
  Battery, 
  RefreshCw,
  Apple,
  Activity,
  Heart
} from 'lucide-react';
import { useWearableSync } from '@/hooks/useWearableSync';
import { useWearablesStore } from '@/store/wearablesStore';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';

export const WearableSettings: React.FC = () => {
  const {
    isConnecting,
    connectedDevices,
    syncStatus,
    connectToAppleHealth,
    connectToGoogleFit,
    connectToAppleWatch,
    disconnect,
    manualSync
  } = useWearableSync();

  const { 
    autoSyncEnabled, 
    analysisEnabled, 
    lastSyncTime,
    setAutoSync, 
    setAnalysis 
  } = useWearablesStore();

  const getDeviceIcon = (type: string) => {
    switch (type) {
      case 'apple_watch':
        return <Watch className="h-5 w-5" />;
      case 'apple_health':
        return <Apple className="h-5 w-5" />;
      case 'google_fit':
        return <Activity className="h-5 w-5" />;
      default:
        return <Smartphone className="h-5 w-5" />;
    }
  };

  const getStatusColor = (isConnected: boolean) => {
    return isConnected ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400';
  };

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      <Card className="bg-white/5 border-purple-500/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Heart className="h-5 w-5" />
            Wearable Devices
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Connected Devices */}
          {connectedDevices.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-white/80">Connected Devices</h4>
              {connectedDevices.map((device) => (
                <div key={device.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="text-white/60">
                      {getDeviceIcon(device.type)}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">{device.name}</p>
                      <div className="flex items-center gap-2 text-xs text-white/60">
                        <Badge className={cn("text-xs", getStatusColor(device.isConnected))}>
                          {device.isConnected ? (
                            <>
                              <Wifi className="h-3 w-3 mr-1" />
                              Connected
                            </>
                          ) : (
                            <>
                              <WifiOff className="h-3 w-3 mr-1" />
                              Disconnected
                            </>
                          )}
                        </Badge>
                        {device.batteryLevel && (
                          <span className="flex items-center gap-1">
                            <Battery className="h-3 w-3" />
                            {device.batteryLevel}%
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => disconnect(device.id)}
                    className="border-red-500/20 text-red-400 hover:bg-red-500/10"
                  >
                    Disconnect
                  </Button>
                </div>
              ))}
            </div>
          )}

          {/* Add New Device */}
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-white/80">Add New Device</h4>
            <div className="grid grid-cols-1 gap-3">
              <Button
                onClick={connectToAppleHealth}
                disabled={!!isConnecting}
                className="justify-start h-auto p-4 bg-white/5 hover:bg-white/10 border border-white/10"
                variant="outline"
              >
                <Apple className="h-5 w-5 mr-3" />
                <div className="text-left">
                  <p className="font-medium text-white">Apple Health</p>
                  <p className="text-xs text-white/60">Connect to iPhone Health app</p>
                </div>
                {isConnecting === 'apple_health' && (
                  <RefreshCw className="h-4 w-4 ml-auto animate-spin" />
                )}
              </Button>

              <Button
                onClick={connectToGoogleFit}
                disabled={!!isConnecting}
                className="justify-start h-auto p-4 bg-white/5 hover:bg-white/10 border border-white/10"
                variant="outline"
              >
                <Activity className="h-5 w-5 mr-3" />
                <div className="text-left">
                  <p className="font-medium text-white">Google Fit</p>
                  <p className="text-xs text-white/60">Connect to Google Fit data</p>
                </div>
                {isConnecting === 'google_fit' && (
                  <RefreshCw className="h-4 w-4 ml-auto animate-spin" />
                )}
              </Button>

              <Button
                onClick={connectToAppleWatch}
                disabled={!!isConnecting}
                className="justify-start h-auto p-4 bg-white/5 hover:bg-white/10 border border-white/10"
                variant="outline"
              >
                <Watch className="h-5 w-5 mr-3" />
                <div className="text-left">
                  <p className="font-medium text-white">Apple Watch</p>
                  <p className="text-xs text-white/60">Direct watch connection</p>
                </div>
                {isConnecting === 'apple_watch' && (
                  <RefreshCw className="h-4 w-4 ml-auto animate-spin" />
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Sync Settings */}
      <Card className="bg-white/5 border-purple-500/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white">Sync Settings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-white">Auto Sync</p>
              <p className="text-xs text-white/60">Automatically sync data every 15 minutes</p>
            </div>
            <Switch
              checked={autoSyncEnabled}
              onCheckedChange={setAutoSync}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-white">Predictive Analysis</p>
              <p className="text-xs text-white/60">Enable AI-powered health insights</p>
            </div>
            <Switch
              checked={analysisEnabled}
              onCheckedChange={setAnalysis}
            />
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-white/10">
            <div>
              <p className="text-sm text-white/80">Last Sync</p>
              <p className="text-xs text-white/60">
                {lastSyncTime ? format(lastSyncTime, 'MMM dd, HH:mm') : 'Never'}
              </p>
            </div>
            <Button
              onClick={manualSync}
              disabled={syncStatus === 'syncing'}
              size="sm"
              className="bg-black border border-white/20 text-white hover:bg-black/80 hover:border-white/40"
            >
              {syncStatus === 'syncing' ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                'Sync Now'
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
