
import React from 'react';
import { Sparkles } from 'lucide-react';

export const LandingFooter: React.FC = () => {
  return (
    <footer className="py-16 border-t border-white/10 relative">
      <div className="container mx-auto px-6">
        <div className="flex flex-col md:flex-row items-center justify-between">
          <div className="flex items-center gap-3 mb-6 md:mb-0">
            <div className="w-8 h-8 rounded-xl glass-premium border border-blue-500/20 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-blue-400" />
            </div>
            <span className="text-lg font-semibold text-white">NGX Agents</span>
          </div>
          
          <div className="flex flex-col md:flex-row items-center gap-6 text-sm text-white/60">
            <span>© 2024 NGX Agents. All rights reserved.</span>
            <div className="flex gap-6">
              <a href="#privacy" className="hover:text-white transition-colors">Privacy</a>
              <a href="#terms" className="hover:text-white transition-colors">Terms</a>
              <a href="#contact" className="hover:text-white transition-colors">Contact</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};
