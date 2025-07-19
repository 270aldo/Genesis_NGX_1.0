
import React from 'react';
import { useAuthStore } from '@/store/authStore';
import { useChatStore } from '@/store/chatStore';
import { ProfileSection } from '@/components/dashboard/ProfileSection';
import { StatsCards } from '@/components/dashboard/StatsCards';
import { RecentActivity } from '@/components/dashboard/RecentActivity';
import { QuickActions } from '@/components/dashboard/QuickActions';
import { TokenBalance } from '@/components/tokens/TokenBalance';
import { AgentInsights } from '@/components/dashboard/AgentInsights';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Calendar, Download, Share2, Settings, TrendingUp, Activity } from 'lucide-react';
import { Link } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const { user } = useAuthStore();
  const { conversations } = useChatStore();

  // Mock stats for now - will be real data when Supabase is connected
  const stats = {
    totalConversations: conversations.length,
    totalMessages: conversations.reduce((acc, conv) => acc + conv.messages.length, 0),
    tokensUsed: 12500,
    tokensLimit: 50000,
  };

  return (
    <div className="min-h-screen bg-black grok-gradient relative overflow-hidden">
      {/* Floating orbs */}
      <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute top-3/4 right-1/4 w-96 h-96 bg-violet-700/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      
      {/* Enhanced Header */}
      <div className="border-b border-violet-900/60 bg-black/50 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link to="/chat">
                <Button variant="ghost" size="icon" className="text-white/60 hover:text-white/80 hover:bg-purple-500/10">
                  <ArrowLeft className="h-5 w-5" />
                </Button>
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-white">Dashboard</h1>
                <p className="text-sm text-white/60">Welcome back, {user?.name || 'User'}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Link to="/dashboard/progress">
                <Button variant="outline" size="sm" className="border-purple-500/20 text-white/80 hover:bg-purple-500/10 hover:border-purple-400/30">
                  <TrendingUp className="h-4 w-4 mr-2" />
                  Progress
                </Button>
              </Link>
              <Button variant="outline" size="sm" className="border-purple-500/20 text-white/80 hover:bg-purple-500/10 hover:border-purple-400/30">
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
              <Link to="/settings">
                <Button variant="outline" size="sm" className="border-purple-500/20 text-white/80 hover:bg-purple-500/10 hover:border-purple-400/30">
                  <Settings className="h-4 w-4 mr-2" />
                  Settings
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {/* Welcome Section */}
        <div className="mb-8">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-white mb-2">Your Fitness Command Center</h2>
            <p className="text-white/60 max-w-2xl mx-auto">
              Track your progress, monitor your health, and get AI-powered insights to optimize your fitness journey.
            </p>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="mb-8">
          <StatsCards stats={stats} />
        </div>

        {/* Main Content Grid - Enhanced Layout */}
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
          {/* Left Section - Main Content (3 columns) */}
          <div className="xl:col-span-3 space-y-8">
            {/* AI Insights - Prominent placement */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="lg:col-span-2">
                <AgentInsights />
              </div>
            </div>

            {/* Recent Activity */}
            <RecentActivity conversations={conversations.slice(0, 5)} />
          </div>

          {/* Right Sidebar (1 column) */}
          <div className="xl:col-span-1 space-y-6">
            <TokenBalance />
            <ProfileSection user={user} />
            <QuickActions />
          </div>
        </div>

        {/* Enhanced Stats Footer */}
        <div className="mt-16 pt-8 border-t border-purple-500/20">
          <div className="text-center mb-6">
            <h3 className="text-xl font-semibold text-white mb-2">Performance Overview</h3>
            <p className="text-white/60">Your fitness journey at a glance</p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center p-4 rounded-xl bg-white/5 border border-purple-500/20">
              <div className="flex items-center justify-center mb-2">
                <Activity className="h-5 w-5 text-purple-400 mr-2" />
                <div className="text-2xl font-bold text-white">{conversations.length}</div>
              </div>
              <div className="text-sm text-white/60">Total Chats</div>
              <div className="text-xs text-green-400 mt-1">+15% this week</div>
            </div>
            
            <div className="text-center p-4 rounded-xl bg-white/5 border border-purple-500/20">
              <div className="flex items-center justify-center mb-2">
                <TrendingUp className="h-5 w-5 text-green-400 mr-2" />
                <div className="text-2xl font-bold text-white">{user?.tokens || 0}</div>
              </div>
              <div className="text-sm text-white/60">Available Tokens</div>
              <div className="text-xs text-yellow-400 mt-1">Use wisely</div>
            </div>
            
            <div className="text-center p-4 rounded-xl bg-white/5 border border-purple-500/20">
              <div className="flex items-center justify-center mb-2">
                <Calendar className="h-5 w-5 text-purple-400 mr-2" />
                <div className="text-2xl font-bold text-white">12</div>
              </div>
              <div className="text-sm text-white/60">Days Active</div>
              <div className="text-xs text-purple-400 mt-1">Great streak!</div>
            </div>
            
            <div className="text-center p-4 rounded-xl bg-white/5 border border-purple-500/20">
              <div className="flex items-center justify-center mb-2">
                <Share2 className="h-5 w-5 text-violet-400 mr-2" />
                <div className="text-2xl font-bold text-white">94%</div>
              </div>
              <div className="text-sm text-white/60">Satisfaction</div>
              <div className="text-xs text-violet-400 mt-1">Excellent!</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
