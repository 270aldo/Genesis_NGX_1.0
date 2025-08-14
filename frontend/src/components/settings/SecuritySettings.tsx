
import React from 'react';
import { useSettingsStore } from '@/store/settingsStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Key, Database, AlertTriangle } from 'lucide-react';

export const SecuritySettings: React.FC = () => {
  const { settings, updatePrivacy } = useSettingsStore();

  const handleExportData = () => {
    // TODO: Implement data export
  };

  const handleDeleteAccount = () => {
    // TODO: Implement account deletion with confirmation
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-light text-white mb-2">Security & Privacy</h2>
        <p className="text-white/60">Manage your security preferences and data</p>
      </div>

      <Card className="glass-ultra border-white/10 bg-white/5">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Database className="w-5 h-5" />
            Privacy Settings
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label className="text-white">Data Collection</Label>
              <p className="text-sm text-white/60">Allow collection of usage data to improve service</p>
            </div>
            <Switch
              checked={settings.privacy.dataCollection}
              onCheckedChange={(checked) =>
                updatePrivacy({ dataCollection: checked })
              }
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label className="text-white">Analytics</Label>
              <p className="text-sm text-white/60">Help us understand how you use the app</p>
            </div>
            <Switch
              checked={settings.privacy.analytics}
              onCheckedChange={(checked) =>
                updatePrivacy({ analytics: checked })
              }
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label className="text-white">Share Usage Data</Label>
              <p className="text-sm text-white/60">Share anonymized usage patterns</p>
            </div>
            <Switch
              checked={settings.privacy.shareUsage}
              onCheckedChange={(checked) =>
                updatePrivacy({ shareUsage: checked })
              }
            />
          </div>
        </CardContent>
      </Card>

      <Card className="glass-ultra border-white/10 bg-white/5">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Key className="w-5 h-5" />
            Account Security
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-3">
            <Button
              variant="outline"
              className="w-full text-white border-white/20 hover:bg-white/5"
            >
              Change Password
            </Button>
            <Button
              variant="outline"
              className="w-full text-white border-white/20 hover:bg-white/5"
            >
              Enable Two-Factor Authentication
            </Button>
            <Button
              variant="outline"
              className="w-full text-white border-white/20 hover:bg-white/5"
              onClick={handleExportData}
            >
              Export My Data
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="glass-ultra border-white/10 bg-red-500/5 border-red-500/20">
        <CardHeader>
          <CardTitle className="text-red-400 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            Danger Zone
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <p className="text-white/60 text-sm">
              Once you delete your account, there is no going back. Please be certain.
            </p>
            <Button
              variant="destructive"
              className="bg-red-600 hover:bg-red-700"
              onClick={handleDeleteAccount}
            >
              Delete Account
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
