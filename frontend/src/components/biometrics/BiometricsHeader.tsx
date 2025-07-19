
import React from 'react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogTrigger, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Settings, RefreshCw } from 'lucide-react';
import { useWearablesStore } from '@/store/wearablesStore';
import { WearableSettings } from '../wearables/WearableSettings';
import { useWearableSync } from '@/hooks/useWearableSync';
import { format } from 'date-fns';

export const BiometricsHeader: React.FC = () => {
  const { 
    connectedDevices, 
    syncStatus,
    lastSyncTime 
  } = useWearablesStore();
  
  const { manualSync } = useWearableSync();

  const hasConnectedDevices = connectedDevices.some(d => d.isConnected);

  return (
    <div className="space-y-4">
      {/* Header with Wearables Status */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-white/60 text-sm">
            {hasConnectedDevices 
              ? `Live data from ${connectedDevices.filter(d => d.isConnected).length} connected device(s)`
              : 'Connect wearables for live health tracking'
            }
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          {hasConnectedDevices && (
            <Button
              onClick={manualSync}
              disabled={syncStatus === 'syncing'}
              size="sm"
              variant="outline"
              className="border-purple-500/20 text-white/80 hover:bg-purple-500/10"
            >
              {syncStatus === 'syncing' ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4" />
              )}
              Sync
            </Button>
          )}
          
          <Dialog>
            <DialogTrigger asChild>
              <Button size="sm" className="bg-black border border-white/20 text-white hover:bg-black/80 hover:border-white/40">
                <Settings className="h-4 w-4 mr-2" />
                Wearables
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-2xl bg-black/90 border-purple-500/20 max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle className="text-white">Wearable Settings</DialogTitle>
              </DialogHeader>
              <WearableSettings />
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Sync Status */}
      {lastSyncTime && (
        <div className="text-xs text-white/60 text-center">
          Last sync: {format(lastSyncTime, 'MMM dd, HH:mm')}
        </div>
      )}
    </div>
  );
};
