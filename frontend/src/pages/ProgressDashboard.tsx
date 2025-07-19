
import React from 'react';
import { ArrowLeft, Download, Share2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ProgressCharts } from '@/components/progress/ProgressCharts';
import { MetricsGrid } from '@/components/progress/MetricsGrid';
import { GoalTracker } from '@/components/progress/GoalTracker';
import { AchievementsBanner } from '@/components/progress/AchievementsBanner';
import { TimeframeSelector } from '@/components/progress/TimeframeSelector';
import { useProgressStore } from '@/store/progressStore';

const ProgressDashboard: React.FC = () => {
  const { achievements } = useProgressStore();
  
  const recentAchievements = achievements.slice(-3);

  return (
    <div className="min-h-screen bg-black grok-gradient relative overflow-hidden">
      {/* Floating orbs */}
      <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute top-3/4 right-1/4 w-96 h-96 bg-violet-700/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      
      {/* Header */}
      <div className="border-b border-violet-900/60 bg-black/50 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link to="/chat/progress-tracker">
                <Button variant="ghost" size="icon" className="text-white/60 hover:text-white/80 hover:bg-purple-500/10">
                  <ArrowLeft className="h-5 w-5" />
                </Button>
              </Link>
              <div>
                <h1 className="text-xl font-semibold text-white">Progress Dashboard</h1>
                <p className="text-sm text-white/60">Track your fitness journey with precision</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <TimeframeSelector />
              <Button variant="outline" size="sm" className="border-purple-500/20 text-white/80 hover:bg-purple-500/10 hover:border-purple-400/30">
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
              <Button variant="outline" size="sm" className="border-purple-500/20 text-white/80 hover:bg-purple-500/10 hover:border-purple-400/30">
                <Share2 className="h-4 w-4 mr-2" />
                Share
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {/* Recent Achievements Banner */}
        {recentAchievements.length > 0 && (
          <div className="mb-8">
            <AchievementsBanner achievements={recentAchievements} />
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Charts */}
          <div className="lg:col-span-2 space-y-8">
            <ProgressCharts />
          </div>

          {/* Right Column - Metrics & Goals */}
          <div className="space-y-8">
            <MetricsGrid />
            <GoalTracker />
          </div>
        </div>

        {/* Stats Footer */}
        <div className="mt-12 pt-8 border-t border-purple-500/20">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-white">{achievements.length}</div>
              <div className="text-sm text-white/60">Achievements</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">94%</div>
              <div className="text-sm text-white/60">Goal Progress</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">12</div>
              <div className="text-sm text-white/60">Weeks Tracked</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">-2.0kg</div>
              <div className="text-sm text-white/60">Total Progress</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressDashboard;
