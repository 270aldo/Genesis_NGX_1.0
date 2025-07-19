
import React from 'react';
import { useSettingsStore } from '@/store/settingsStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { MessageSquare, Mic, Bot } from 'lucide-react';

export const ChatSettings: React.FC = () => {
  const { settings, updateSettings, updateNotifications } = useSettingsStore();

  const handleModelChange = (aiModel: 'gpt-4o' | 'gpt-4o-mini' | 'gpt-4.5-preview') => {
    updateSettings({ aiModel });
  };

  const modelOptions = [
    { value: 'gpt-4o-mini', label: 'GPT-4o Mini', description: 'Faster responses, lower cost' },
    { value: 'gpt-4o', label: 'GPT-4o', description: 'Balanced performance' },
    { value: 'gpt-4.5-preview', label: 'GPT-4.5 Preview', description: 'Latest features' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-light text-white mb-2">Chat Settings</h2>
        <p className="text-white/60">Configure your AI chat experience</p>
      </div>

      <Card className="glass-ultra border-white/10 bg-white/5">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Bot className="w-5 h-5" />
            AI Model
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-3">
            <Label className="text-white">AI Model</Label>
            <Select value={settings.aiModel} onValueChange={handleModelChange}>
              <SelectTrigger className="bg-white/5 border-white/10 text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-gray-900 border-white/10">
                {modelOptions.map((option) => (
                  <SelectItem
                    key={option.value}
                    value={option.value}
                    className="text-white hover:bg-white/5"
                  >
                    <div className="flex flex-col">
                      <span>{option.label}</span>
                      <span className="text-xs text-white/60">{option.description}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card className="glass-ultra border-white/10 bg-white/5">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <MessageSquare className="w-5 h-5" />
            Chat Features
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Voice Settings */}
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label className="text-white flex items-center gap-2">
                <Mic className="w-4 h-4" />
                Voice Messages
              </Label>
              <p className="text-sm text-white/60">Enable voice input and output</p>
            </div>
            <Switch
              checked={settings.voiceEnabled}
              onCheckedChange={(checked) => updateSettings({ voiceEnabled: checked })}
            />
          </div>

          {/* Notifications */}
          <div className="space-y-4">
            <Label className="text-white">Notifications</Label>
            
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label className="text-white text-sm">Desktop Notifications</Label>
                <p className="text-xs text-white/60">Get notified on your desktop</p>
              </div>
              <Switch
                checked={settings.notifications.desktop}
                onCheckedChange={(checked) => 
                  updateNotifications({ desktop: checked })
                }
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label className="text-white text-sm">Push Notifications</Label>
                <p className="text-xs text-white/60">Receive push notifications</p>
              </div>
              <Switch
                checked={settings.notifications.push}
                onCheckedChange={(checked) => 
                  updateNotifications({ push: checked })
                }
              />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
