
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Trophy, Calendar } from 'lucide-react';
import { Achievement } from '@/store/progressStore';
import { format, parseISO } from 'date-fns';
import { cn } from '@/lib/utils';

interface AchievementsBannerProps {
  achievements: Achievement[];
}

export const AchievementsBanner: React.FC<AchievementsBannerProps> = ({ achievements }) => {
  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'milestone':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'consistency':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'improvement':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  return (
    <Card className="bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-blue-500/10 border-blue-500/20 backdrop-blur-sm">
      <CardContent className="p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-yellow-500/20 rounded-full">
            <Trophy className="h-5 w-5 text-yellow-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Recent Achievements</h3>
            <p className="text-sm text-white/60">Your latest fitness milestones</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {achievements.map((achievement) => (
            <div key={achievement.id} className="flex items-start gap-3 p-3 bg-white/5 rounded-lg border border-white/10">
              <div className="text-2xl">{achievement.icon}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="font-medium text-white text-sm truncate">{achievement.title}</h4>
                  <Badge className={cn("text-xs", getCategoryColor(achievement.category))}>
                    {achievement.category}
                  </Badge>
                </div>
                <p className="text-xs text-white/60 mb-2">{achievement.description}</p>
                <div className="flex items-center gap-1 text-xs text-white/50">
                  <Calendar className="h-3 w-3" />
                  <span>{format(parseISO(achievement.unlockedAt), 'MMM dd')}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
