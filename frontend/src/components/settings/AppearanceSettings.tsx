
import React from 'react';
import { useSettingsStore } from '@/store/settingsStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Palette, Monitor, Sun, Moon, type LucideIcon } from 'lucide-react';

export const AppearanceSettings: React.FC = () => {
  const { settings, updateSettings } = useSettingsStore();

  type Theme = 'light' | 'dark' | 'system';

  const handleThemeChange = (theme: Theme) => {
    updateSettings({ theme });
  };

  type Language = 'en' | 'es' | 'fr' | 'de';

  const handleLanguageChange = (language: Language) => {
    updateSettings({ language });
  };

  const themeOptions: { value: Theme; label: string; icon: LucideIcon }[] = [
    { value: 'dark', label: 'Dark', icon: Moon },
    { value: 'light', label: 'Light', icon: Sun },
    { value: 'system', label: 'System', icon: Monitor },
  ];

  const languageOptions: { value: Language; label: string }[] = [
    { value: 'en', label: 'English' },
    { value: 'es', label: 'Español' },
    { value: 'fr', label: 'Français' },
    { value: 'de', label: 'Deutsch' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-light text-white mb-2">Appearance Settings</h2>
        <p className="text-white/60">Customize the look and feel of your experience</p>
      </div>

      <Card className="glass-ultra border-white/10 bg-white/5">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Palette className="w-5 h-5" />
            Theme & Display
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Theme Selection */}
          <div className="space-y-3">
            <Label className="text-white">Theme</Label>
            <div className="grid grid-cols-3 gap-3">
              {themeOptions.map((option) => {
                const Icon = option.icon;
                return (
                  <Button
                    key={option.value}
                    variant={settings.theme === option.value ? "default" : "outline"}
                    className={`flex flex-col items-center gap-2 h-20 ${
                      settings.theme === option.value
                        ? 'bg-gradient-to-r from-purple-500 to-violet-600 text-white'
                        : 'text-white border-white/20 hover:bg-white/5'
                    }`}
                    onClick={() => handleThemeChange(option.value)}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="text-sm">{option.label}</span>
                  </Button>
                );
              })}
            </div>
          </div>

          {/* Language Selection */}
          <div className="space-y-3">
            <Label className="text-white">Language</Label>
            <Select value={settings.language} onValueChange={handleLanguageChange}>
              <SelectTrigger className="bg-white/5 border-white/10 text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-gray-900 border-white/10">
                {languageOptions.map((option) => (
                  <SelectItem
                    key={option.value}
                    value={option.value}
                    className="text-white hover:bg-white/5"
                  >
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Auto-save Setting */}
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label className="text-white">Auto-save</Label>
              <p className="text-sm text-white/60">Automatically save your work</p>
            </div>
            <Switch
              checked={settings.autoSave}
              onCheckedChange={(checked) => updateSettings({ autoSave: checked })}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
