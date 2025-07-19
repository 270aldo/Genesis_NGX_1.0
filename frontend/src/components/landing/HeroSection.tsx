
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Sparkles } from 'lucide-react';
import { EnergyLines } from './EnergyLines';
import { useIsMobile } from '@/hooks/use-mobile';

export const HeroSection: React.FC = () => {
  const [typedText, setTypedText] = useState('');
  const fullText = 'Advanced AI Agent System';
  const isMobile = useIsMobile();

  useEffect(() => {
    let index = 0;
    const timer = setInterval(() => {
      if (index <= fullText.length) {
        setTypedText(fullText.slice(0, index));
        index++;
      } else {
        clearInterval(timer);
      }
    }, 100);

    return () => clearInterval(timer);
  }, []);

  return (
    <section className="min-h-screen flex items-center justify-center relative pt-20 px-4">
      <EnergyLines />
      
      <div className="container mx-auto text-center relative z-10 max-w-6xl">
        <div className="floating-animation">
          <div className="inline-flex items-center gap-2 glass-premium px-3 sm:px-4 py-2 rounded-full border border-blue-500/20 mb-6 sm:mb-8">
            <Sparkles className="w-3 h-3 sm:w-4 sm:h-4 text-blue-400" />
            <span className="text-xs sm:text-sm text-white/80">Next-Generation Intelligence</span>
          </div>
        </div>

        <h1 className={`font-light mb-4 sm:mb-6 leading-tight ${
          isMobile ? 'text-4xl' : 'text-6xl md:text-8xl'
        }`}>
          <span className="bg-gradient-to-r from-white via-blue-100 to-purple-100 bg-clip-text text-transparent">
            NGX
          </span>
          <br />
          <span className={`text-white/90 ${
            isMobile ? 'text-2xl' : 'text-4xl md:text-6xl'
          }`}>
            {typedText}
            <span className="animate-pulse">|</span>
          </span>
        </h1>

        <p className={`text-white/60 mb-8 sm:mb-12 max-w-3xl mx-auto leading-relaxed font-light ${
          isMobile ? 'text-base px-2' : 'text-xl md:text-2xl'
        }`}>
          Experience the future of conversational AI with our sophisticated multi-agent system. 
          Premium interface meets cutting-edge intelligence.
        </p>

        <div className={`flex items-center justify-center gap-4 sm:gap-6 ${
          isMobile ? 'flex-col px-4' : 'flex-col sm:flex-row'
        }`}>
          <Link to="/chat" className={isMobile ? 'w-full' : ''}>
            <button className={`premium-glow-button ${isMobile ? 'w-full' : ''}`}>
              <span>Start Conversation</span>
            </button>
          </Link>
          
          <button 
            className={`rainbow-button ${isMobile ? 'w-full' : ''}`}
            onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
          >
            <span>Explore Features</span>
          </button>
        </div>
      </div>

      {/* Responsive gradient orbs */}
      <div className={`absolute bg-blue-500/20 rounded-full blur-3xl animate-pulse ${
        isMobile ? 'top-1/3 left-4 w-20 h-20' : 'top-1/4 left-10 w-32 h-32'
      }`}></div>
      <div className={`absolute bg-purple-500/10 rounded-full blur-3xl animate-pulse ${
        isMobile ? 'bottom-1/3 right-4 w-24 h-24' : 'bottom-1/4 right-10 w-48 h-48'
      }`} style={{ animationDelay: '1s' }}></div>
    </section>
  );
};
