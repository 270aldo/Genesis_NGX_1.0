
import React from 'react';
import { HeroSection } from '@/components/landing/HeroSection';
import { FeatureCards } from '@/components/landing/FeatureCards';
import { DemoSection } from '@/components/landing/DemoSection';
import { ParticleBackground } from '@/components/landing/ParticleBackground';
import { LandingHeader } from '@/components/landing/LandingHeader';
import { LandingFooter } from '@/components/landing/LandingFooter';

const Landing: React.FC = () => {
  return (
    <div className="min-h-screen bg-black grok-gradient relative overflow-hidden">
      {/* Floating orbs */}
      <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute top-3/4 right-1/4 w-96 h-96 bg-violet-700/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      
      <ParticleBackground />
      <LandingHeader />
      <main>
        <HeroSection />
        <FeatureCards />
        <DemoSection />
      </main>
      <LandingFooter />
    </div>
  );
};

export default Landing;
