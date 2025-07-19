import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Card } from '@/components/ui/card';
import { Volume2, Phone, PhoneOff, Mic } from 'lucide-react';
import { useVoiceConversation } from '@/hooks/useVoiceConversation';
import { useAgentStore } from '@/store/agentStore';
import { VoiceEnergyBall } from './VoiceEnergyBall';
import { cn } from '@/lib/utils';

interface VoiceInterfaceProps {
  className?: string;
}

export const VoiceInterface: React.FC<VoiceInterfaceProps> = ({ className }) => {
  const [volume, setVolume] = useState([0.8]);
  const { getActiveAgent } = useAgentStore();
  const {
    isVoiceActive,
    isSpeaking,
    status,
    startVoiceConversation,
    endVoiceConversation,
    setVolume: setAudioVolume
  } = useVoiceConversation();

  const activeAgent = getActiveAgent();

  const handleVolumeChange = (value: number[]) => {
    setVolume(value);
    setAudioVolume(value[0]);
  };

  const handleToggleVoice = () => {
    if (isVoiceActive) {
      endVoiceConversation();
    } else {
      startVoiceConversation(activeAgent?.id);
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'connected': return 'text-green-400';
      case 'connecting': return 'text-yellow-400';
      case 'disconnected': return 'text-gray-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'connected': return 'Connected';
      case 'connecting': return 'Connecting...';
      case 'disconnected': return 'Disconnected';
      default: return 'Ready';
    }
  };

  return (
    <Card className={cn(
      "glass-ultra border-purple-500/20 p-8 space-y-8 bg-gradient-to-br from-black/40 via-black/30 to-black/20 backdrop-blur-xl",
      className
    )}>
      {/* Ultra-Modern Status Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="relative">
            <div className={cn(
              "w-4 h-4 rounded-full transition-all duration-500",
              status === 'connected' ? 'bg-green-400 animate-pulse shadow-green-400/50 shadow-lg' : 
              status === 'connecting' ? 'bg-yellow-400 animate-pulse shadow-yellow-400/50 shadow-lg' :
              'bg-gray-500 shadow-gray-500/30 shadow-md'
            )} />
            {status === 'connected' && (
              <div className="absolute inset-0 w-4 h-4 rounded-full bg-green-400/30 animate-ping" />
            )}
          </div>
          <div className="space-y-1">
            <span className={cn("text-sm font-semibold transition-colors", getStatusColor())}>
              Voice Chat {getStatusText()}
            </span>
            <p className="text-xs text-white/50">
              {activeAgent?.name || 'NGX Agent'} • Ultra AI Voice Interface
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          {isVoiceActive && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10">
              <Mic className="w-3 h-3 text-green-400" />
              <span className="text-xs text-white/70">Live</span>
            </div>
          )}
          
          <Button
            onClick={handleToggleVoice}
            size="sm"
            className={cn(
              "transition-all duration-500 px-6 py-2 font-medium",
              isVoiceActive 
                ? "bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white shadow-red-500/25 shadow-lg" 
                : "bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white shadow-purple-500/25 shadow-lg"
            )}
          >
            {isVoiceActive ? (
              <>
                <PhoneOff className="w-4 h-4 mr-2" />
                End Call
              </>
            ) : (
              <>
                <Phone className="w-4 h-4 mr-2" />
                Start Voice Chat
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Ultra-Modern Energy Ball Display */}
      <div className="flex flex-col items-center py-12 space-y-8">
        <VoiceEnergyBall 
          isActive={isVoiceActive}
          isSpeaking={isSpeaking}
          className="mb-4"
        />
        
        <div className="text-center space-y-3 max-w-md">
          <h3 className="text-xl font-bold text-white bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">
            {activeAgent?.name || 'NGX Agent'}
          </h3>
          <p className={cn(
            "text-sm transition-all duration-300 font-medium",
            !isVoiceActive ? "text-white/60" :
            isSpeaking ? "text-green-400" : "text-blue-400"
          )}>
            {!isVoiceActive ? (
              'Experience the future of AI voice interaction'
            ) : isSpeaking ? (
              `${activeAgent?.name} is speaking...`
            ) : (
              'Listening... Speak naturally'
            )}
          </p>
          
          {isVoiceActive && (
            <div className="flex items-center justify-center gap-2 mt-4">
              <div className="flex space-x-1">
                {[...Array(3)].map((_, i) => (
                  <div 
                    key={i}
                    className={cn(
                      "w-1 h-1 rounded-full transition-all duration-300",
                      isSpeaking ? "bg-green-400 animate-pulse" : "bg-white/30"
                    )}
                    style={{ animationDelay: `${i * 200}ms` }}
                  />
                ))}
              </div>
              <span className="text-xs text-white/40 ml-2">
                {isSpeaking ? 'AI Speaking' : 'Listening'}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Ultra-Modern Voice Controls */}
      {isVoiceActive && (
        <div className="space-y-6 p-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-sm">
          <div className="flex items-center gap-4">
            <Volume2 className="w-5 h-5 text-white/60" />
            <div className="flex-1 space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-white/70">Voice Volume</span>
                <span className="text-sm text-white/50 font-mono bg-white/10 px-2 py-1 rounded">
                  {Math.round(volume[0] * 100)}%
                </span>
              </div>
              <Slider
                value={volume}
                onValueChange={handleVolumeChange}
                max={1}
                min={0}
                step={0.1}
                className="flex-1"
              />
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4 pt-4 border-t border-white/10">
            <div className="text-center space-y-1">
              <p className="text-xs text-white/50">Status</p>
              <p className={cn("text-sm font-medium", getStatusColor())}>
                {getStatusText()}
              </p>
            </div>
            <div className="text-center space-y-1">
              <p className="text-xs text-white/50">Mode</p>
              <p className="text-sm font-medium text-white/70">
                {isSpeaking ? 'Speaking' : 'Listening'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Ultra-Modern Getting Started Info */}
      {!isVoiceActive && (
        <div className="text-center py-6 space-y-4 p-6 rounded-2xl bg-gradient-to-br from-white/5 to-white/10 border border-white/10">
          <div className="space-y-2">
            <p className="text-sm text-white/70 font-medium">
              Experience natural conversations with {activeAgent?.name}
            </p>
            <p className="text-xs text-white/50 leading-relaxed max-w-md mx-auto">
              Click "Start Voice Chat" to begin speaking with your AI agent. 
              Our advanced voice AI provides natural, real-time conversations.
            </p>
          </div>
          
          <div className="flex items-center justify-center gap-6 pt-4">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-400" />
              <span className="text-xs text-white/50">Real-time</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-blue-400" />
              <span className="text-xs text-white/50">Natural</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-purple-400" />
              <span className="text-xs text-white/50">Intelligent</span>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
};
