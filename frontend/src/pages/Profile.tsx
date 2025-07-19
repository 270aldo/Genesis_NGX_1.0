
import React from 'react';
import { useAuthStore } from '@/store/authStore';
import { ProfileSettings } from '@/components/settings/ProfileSettings';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useIsMobile } from '@/hooks/use-mobile';

const Profile: React.FC = () => {
  const { user } = useAuthStore();
  const isMobile = useIsMobile();

  if (!user) {
    return (
      <div className="min-h-screen bg-black grok-gradient flex items-center justify-center">
        <div className="text-white text-center">
          <h1 className="text-2xl font-light mb-4">No user found</h1>
          <Link to="/dashboard">
            <Button variant="outline" className="text-white border-white/20 hover:bg-white/5">
              Return to Dashboard
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black grok-gradient relative overflow-hidden">
      {/* Floating orbs */}
      <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute top-3/4 right-1/4 w-96 h-96 bg-violet-700/10 rounded-full blur-3xl animate-pulse delay-1000"></div>

      <div className="relative z-10 p-4 sm:p-6 lg:p-8 max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6 sm:mb-8 flex items-center gap-4">
          <Link to="/dashboard">
            <Button variant="ghost" size="icon" className="text-white/60 hover:text-white hover:bg-purple-500/10">
              <ArrowLeft className="w-5 h-5" />
            </Button>
          </Link>
          <div>
            <h1 className={`font-light text-white mb-2 ${
              isMobile ? 'text-2xl sm:text-3xl' : 'text-4xl'
            }`}>Profile</h1>
            <p className={`text-white/60 ${
              isMobile ? 'text-sm' : 'text-base'
            }`}>Manage your personal information</p>
          </div>
        </div>

        {/* Profile Content */}
        <ProfileSettings />
      </div>
    </div>
  );
};

export default Profile;
