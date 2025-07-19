
import React from 'react';
import { Sparkles, Shield, ArrowUp } from 'lucide-react';
import { useIsMobile } from '@/hooks/use-mobile';

const features = [
  {
    icon: Sparkles,
    title: 'Advanced AI Agents',
    description: 'Multi-agent system with specialized capabilities for complex reasoning and task execution.',
    gradient: 'from-purple-500/20 to-violet-600/20',
  },
  {
    icon: ArrowUp,
    title: 'Real-time Processing',
    description: 'Lightning-fast response times with streaming capabilities and instant feedback.',
    gradient: 'from-purple-500/20 to-purple-700/20',
  },
  {
    icon: Shield,
    title: 'Premium Interface',
    description: 'Sophisticated user experience with glassmorphism design and fluid animations.',
    gradient: 'from-purple-500/20 to-purple-800/20',
  },
];

export const FeatureCards: React.FC = () => {
  const isMobile = useIsMobile();

  return (
    <section id="features" className="py-16 sm:py-24 lg:py-32 relative px-4">
      <div className="container mx-auto">
        <div className="text-center mb-12 sm:mb-16 lg:mb-20">
          <h2 className={`font-light mb-4 sm:mb-6 text-white ${
            isMobile ? 'text-3xl' : 'text-4xl md:text-6xl'
          }`}>
            Cutting-Edge
            <span className="bg-gradient-to-r from-purple-400 to-violet-400 bg-clip-text text-transparent"> Features</span>
          </h2>
          <p className={`text-white/60 max-w-2xl mx-auto px-4 ${
            isMobile ? 'text-base' : 'text-xl'
          }`}>
            Experience the next generation of AI interaction with our premium feature set
          </p>
        </div>

        <div className={`grid gap-6 sm:gap-8 max-w-6xl mx-auto ${
          isMobile ? 'grid-cols-1' : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
        }`}>
          {features.map((feature, index) => (
            <div
              key={feature.title}
              className="group relative"
              style={{ animationDelay: `${index * 200}ms` }}
            >
              <div className={`glass-ultra border border-white/10 rounded-2xl sm:rounded-3xl hover:border-purple-500/30 transition-all duration-500 hover:scale-105 relative overflow-hidden ${
                isMobile ? 'p-6' : 'p-8'
              }`}>
                {/* Gradient background */}
                <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`}></div>
                
                {/* Content */}
                <div className="relative z-10">
                  <div className={`glass-premium border border-purple-500/20 rounded-xl sm:rounded-2xl flex items-center justify-center mb-4 sm:mb-6 glow-subtle group-hover:glow-primary transition-all duration-300 ${
                    isMobile ? 'w-12 h-12' : 'w-16 h-16'
                  }`}>
                    <feature.icon className={`text-purple-400 ${
                      isMobile ? 'w-6 h-6' : 'w-8 h-8'
                    }`} />
                  </div>
                  
                  <h3 className={`font-semibold mb-3 sm:mb-4 text-white ${
                    isMobile ? 'text-xl' : 'text-2xl'
                  }`}>{feature.title}</h3>
                  <p className={`text-white/70 leading-relaxed ${
                    isMobile ? 'text-sm' : 'text-base'
                  }`}>{feature.description}</p>
                </div>

                {/* Shimmer effect */}
                <div className="absolute inset-0 shimmer-premium opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
