
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Volume2, Mic, Settings } from 'lucide-react';

export const VoiceSettings: React.FC = () => {
  const [autoSpeech, setAutoSpeech] = useState(true);
  const [voiceSpeed, setVoiceSpeed] = useState([1.0]);
  const [selectedVoice, setSelectedVoice] = useState('aria');
  const [micSensitivity, setMicSensitivity] = useState([0.7]);

  // Top ElevenLabs voices
  const voices = [
    { id: 'aria', name: 'Aria - Natural & Warm', voiceId: '9BWtsMINqrJLrRacOk9x' },
    { id: 'sarah', name: 'Sarah - Professional', voiceId: 'EXAVITQu4vr4xnSDxMaL' },
    { id: 'laura', name: 'Laura - Friendly', voiceId: 'FGY2WhTYpPnrIDTdsKH5' },
    { id: 'charlotte', name: 'Charlotte - Elegant', voiceId: 'XB0fDUnXU5powFXDhCwa' },
    { id: 'alice', name: 'Alice - Youthful', voiceId: 'Xb7hH8MSUJpSbSDYk0k2' },
    { id: 'daniel', name: 'Daniel - Deep & Clear', voiceId: 'onwK4e9ZLuTAKqWW03F9' }
  ];

  return (
    <Card className="glass-ultra border-purple-500/20">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-white">
          <Settings className="w-5 h-5" />
          Voice Settings
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Auto Speech */}
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <Label className="text-white/90">Auto Speech</Label>
            <p className="text-sm text-white/60">
              Automatically speak AI responses
            </p>
          </div>
          <Switch
            checked={autoSpeech}
            onCheckedChange={setAutoSpeech}
          />
        </div>

        <Separator className="bg-white/10" />

        {/* Voice Selection */}
        <div className="space-y-3">
          <Label className="text-white/90">Voice Selection</Label>
          <Select value={selectedVoice} onValueChange={setSelectedVoice}>
            <SelectTrigger className="bg-black/40 border-white/20 text-white">
              <SelectValue placeholder="Select a voice" />
            </SelectTrigger>
            <SelectContent className="bg-black/90 border-purple-500/20">
              {voices.map((voice) => (
                <SelectItem 
                  key={voice.id} 
                  value={voice.id}
                  className="text-white hover:bg-purple-500/20"
                >
                  {voice.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Separator className="bg-white/10" />

        {/* Voice Speed */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label className="text-white/90">Speech Speed</Label>
            <span className="text-sm text-white/60">{voiceSpeed[0]}x</span>
          </div>
          <Slider
            value={voiceSpeed}
            onValueChange={setVoiceSpeed}
            max={2}
            min={0.5}
            step={0.1}
            className="w-full"
          />
        </div>

        <Separator className="bg-white/10" />

        {/* Microphone Sensitivity */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label className="flex items-center gap-2 text-white/90">
              <Mic className="w-4 h-4" />
              Mic Sensitivity
            </Label>
            <span className="text-sm text-white/60">
              {Math.round(micSensitivity[0] * 100)}%
            </span>
          </div>
          <Slider
            value={micSensitivity}
            onValueChange={setMicSensitivity}
            max={1}
            min={0.1}
            step={0.1}
            className="w-full"
          />
        </div>

        <Separator className="bg-white/10" />

        {/* Test Voice */}
        <div className="space-y-3">
          <Label className="text-white/90">Test Voice</Label>
          <Button 
            variant="outline" 
            className="w-full bg-transparent border-purple-500/30 text-white hover:bg-purple-500/20"
          >
            <Volume2 className="w-4 h-4 mr-2" />
            Test Selected Voice
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
