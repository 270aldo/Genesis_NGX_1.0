
import React from 'react';
import { ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { NutritionOverview } from '@/components/nutrition/NutritionOverview';

const NutritionDashboard: React.FC = () => {
  return (
    <div className="min-h-screen bg-black grok-gradient relative overflow-hidden">
      {/* Floating orbs */}
      <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute top-3/4 right-1/4 w-96 h-96 bg-violet-700/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      
      {/* Header with back button */}
      <div className="border-b border-violet-900/60 bg-black/50 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link to="/chat/nutrition-architect">
                <Button variant="ghost" size="icon" className="text-white/60 hover:text-white/80 hover:bg-purple-500/10">
                  <ArrowLeft className="h-5 w-5" />
                </Button>
              </Link>
              <div>
                <h1 className="text-xl font-semibold text-white">Nutrition Dashboard</h1>
                <p className="text-sm text-white/60">Manage your nutrition plans and track progress</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="relative z-10 p-6">
        <div className="max-w-7xl mx-auto">
          <NutritionOverview />
        </div>
      </div>
    </div>
  );
};

export default NutritionDashboard;
