
import React from 'react';
import { useAgentStore } from '@/store/agentStore';
import { Circle, Target, Leaf, BarChart3, Lightbulb, TrendingUp, RotateCcw, Zap, Users, Heart, Dna } from 'lucide-react';

const iconMap = {
  Circle,
  Target,
  Leaf,
  BarChart3,
  Lightbulb,
  TrendingUp,
  RotateCcw,
  Zap,
  Users,
  Heart,
  Dna
};

const getGreeting = () => {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 18) return 'Good afternoon';
  return 'Good evening';
};

export const WelcomeState: React.FC = () => {
  const { getActiveAgent } = useAgentStore();
  const activeAgent = getActiveAgent();
  
  const getIcon = (iconName: string) => {
    const IconComponent = iconMap[iconName as keyof typeof iconMap] || Circle;
    return IconComponent;
  };

  if (!activeAgent) {
    return (
      <div className="flex items-center justify-center min-h-full py-12">
        <div className="text-center space-y-6 p-8">
          <h1 className="text-3xl md:text-5xl font-semibold tracking-tight text-white">
            {getGreeting()}.
          </h1>
          <p className="text-lg md:text-xl text-gray-300 mt-2">
            How can I help you today?
          </p>
        </div>
      </div>
    );
  }

  const Icon = getIcon(activeAgent.icon);

  return (
    <div className="flex items-center justify-center min-h-full py-12">
      <div className="w-full max-w-3xl mx-auto flex flex-col items-center">
        <div className="text-center mb-8">
          <h1 className="animate-fade-in text-3xl md:text-5xl font-semibold tracking-tight text-white" style={{animationDelay: '100ms'}}>
            {getGreeting()}.
          </h1>
          {activeAgent && (
            <div className="space-y-2 mt-4">
              <h2 className="animate-fade-in text-xl md:text-2xl font-medium text-white" style={{animationDelay: '150ms'}}>
                I'm {activeAgent.name}
              </h2>
              <p className="animate-fade-in text-lg text-gray-300" style={{animationDelay: '200ms'}}>
                {activeAgent.description}
              </p>
            </div>
          )}
        </div>

        {/* Quick Actions */}
        {activeAgent?.actions && activeAgent.actions.length > 0 && (
          <div className="animate-fade-in flex flex-wrap justify-center gap-3 mt-8 max-w-2xl" style={{animationDelay: '400ms'}}>
            {activeAgent.actions.slice(0, 3).map((action) => (
              <button
                key={action.id}
                className="group flex items-center gap-2 px-4 py-2 rounded-full border border-violet-800 bg-black/50 text-sm font-medium text-white hover:bg-violet-500 hover:border-violet-500 transition-colors"
                onClick={() => {
                  const textarea = document.querySelector('textarea');
                  if (textarea) {
                    textarea.value = action.label;
                    textarea.focus();
                  }
                }}
              >
                <Icon className="w-4 h-4 text-violet-500 group-hover:text-white transition-colors" />
                <span>{action.label}</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
