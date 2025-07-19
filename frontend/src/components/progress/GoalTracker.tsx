
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Calendar, Trophy } from 'lucide-react';
import { useProgressStore } from '@/store/progressStore';
import { format, parseISO, differenceInDays } from 'date-fns';
import { cn } from '@/lib/utils';

export const GoalTracker: React.FC = () => {
  const { goals } = useProgressStore();

  const getProgressPercentage = (current: number, target: number, isReverse = false) => {
    if (isReverse) {
      // For goals where lower is better (like weight loss or body fat reduction)
      return Math.max(0, Math.min(100, ((target - current) / target) * 100));
    }
    return Math.max(0, Math.min(100, (current / target) * 100));
  };

  const getDaysRemaining = (deadline: string) => {
    const days = differenceInDays(parseISO(deadline), new Date());
    return Math.max(0, days);
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'weight':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'strength':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'endurance':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'body_composition':
        return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Trophy className="h-5 w-5 text-white" />
        <h3 className="text-lg font-semibold text-white">Goals</h3>
      </div>
      
      <div className="space-y-4">
        {goals.map((goal) => {
          const isReverse = goal.category === 'weight' || goal.title.includes('Body Fat');
          const progress = getProgressPercentage(goal.current, goal.target, isReverse);
          const daysRemaining = getDaysRemaining(goal.deadline);
          const isNearDeadline = daysRemaining <= 30;
          const isOverdue = daysRemaining === 0;

          return (
            <Card key={goal.id} className="bg-white/5 border-white/10 backdrop-blur-sm">
              <CardContent className="p-4">
                <div className="space-y-3">
                  {/* Header */}
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-white">{goal.title}</h4>
                    <Badge className={cn("text-xs", getCategoryColor(goal.category))}>
                      {goal.category.replace('_', ' ')}
                    </Badge>
                  </div>

                  {/* Progress Bar */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-white/60">
                        {goal.current}{goal.unit} / {goal.target}{goal.unit}
                      </span>
                      <span className="text-white font-medium">
                        {progress.toFixed(0)}%
                      </span>
                    </div>
                    <Progress 
                      value={progress} 
                      className="h-2 bg-white/10"
                    />
                  </div>

                  {/* Deadline */}
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-1 text-white/60">
                      <Calendar className="h-3 w-3" />
                      <span>Due {format(parseISO(goal.deadline), 'MMM dd, yyyy')}</span>
                    </div>
                    <div className={cn(
                      "font-medium",
                      isOverdue && "text-red-400",
                      isNearDeadline && !isOverdue && "text-orange-400",
                      !isNearDeadline && "text-white/60"
                    )}>
                      {isOverdue ? 'Overdue' : `${daysRemaining} days left`}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
};
