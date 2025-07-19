
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { TrendingUp, TrendingDown, Activity, Target, Zap, Scale } from 'lucide-react';
import { useProgressStore } from '@/store/progressStore';
import { cn } from '@/lib/utils';

export const MetricsGrid: React.FC = () => {
  const { getFilteredData } = useProgressStore();
  const data = getFilteredData();
  
  if (data.length < 2) return null;

  const latest = data[data.length - 1];
  const previous = data[data.length - 2];

  const metrics = [
    {
      title: 'Current Weight',
      value: `${latest.weight}kg`,
      change: latest.weight - previous.weight,
      changeLabel: `${Math.abs(latest.weight - previous.weight).toFixed(1)}kg`,
      icon: Scale,
      color: 'purple'
    },
    {
      title: 'Body Fat',
      value: `${latest.bodyFat}%`,
      change: latest.bodyFat - previous.bodyFat,
      changeLabel: `${Math.abs(latest.bodyFat - previous.bodyFat).toFixed(1)}%`,
      icon: Activity,
      color: 'red'
    },
    {
      title: 'Muscle Mass',
      value: `${latest.muscleMass}kg`,
      change: latest.muscleMass - previous.muscleMass,
      changeLabel: `${Math.abs(latest.muscleMass - previous.muscleMass).toFixed(1)}kg`,
      icon: Zap,
      color: 'green'
    },
    {
      title: 'Waist',
      value: `${latest.waist}cm`,
      change: latest.waist - previous.waist,
      changeLabel: `${Math.abs(latest.waist - previous.waist).toFixed(1)}cm`,
      icon: Target,
      color: 'violet'
    }
  ];

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-white">Key Metrics</h3>
      <div className="grid grid-cols-1 gap-4">
        {metrics.map((metric, index) => {
          const Icon = metric.icon;
          const isPositive = metric.change > 0;
          const isNegative = metric.change < 0;
          
          // For weight and body fat, negative is good. For muscle mass, positive is good.
          const isGoodChange = (metric.title === 'Current Weight' || metric.title === 'Body Fat' || metric.title === 'Waist') 
            ? isNegative 
            : isPositive;

          return (
            <Card key={index} className="bg-white/5 border-purple-500/20 backdrop-blur-sm">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={cn(
                      "p-2 rounded-lg",
                      metric.color === 'purple' && "bg-purple-500/20 text-purple-400",
                      metric.color === 'red' && "bg-red-500/20 text-red-400",
                      metric.color === 'green' && "bg-green-500/20 text-green-400",
                      metric.color === 'violet' && "bg-violet-500/20 text-violet-400"
                    )}>
                      <Icon className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="text-sm text-white/60">{metric.title}</p>
                      <p className="text-lg font-semibold text-white">{metric.value}</p>
                    </div>
                  </div>
                  
                  {metric.change !== 0 && (
                    <div className={cn(
                      "flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full",
                      isGoodChange 
                        ? "bg-green-500/20 text-green-400" 
                        : "bg-red-500/20 text-red-400"
                    )}>
                      {isGoodChange ? (
                        <TrendingUp className="h-3 w-3" />
                      ) : (
                        <TrendingDown className="h-3 w-3" />
                      )}
                      {metric.changeLabel}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
};
