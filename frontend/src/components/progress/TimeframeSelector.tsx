
import React from 'react';
import { Button } from '@/components/ui/button';
import { useProgressStore } from '@/store/progressStore';
import { cn } from '@/lib/utils';

export const TimeframeSelector: React.FC = () => {
  const { selectedTimeframe, setTimeframe } = useProgressStore();

  const timeframes = [
    { value: '1W' as const, label: '1 Week' },
    { value: '1M' as const, label: '1 Month' },
    { value: '3M' as const, label: '3 Months' },
    { value: '1Y' as const, label: '1 Year' },
  ];

  return (
    <div className="flex items-center gap-1 p-1 bg-white/5 rounded-lg border border-white/10">
      {timeframes.map((timeframe) => (
        <Button
          key={timeframe.value}
          variant="ghost"
          size="sm"
          onClick={() => setTimeframe(timeframe.value)}
          className={cn(
            "text-xs px-3 py-1.5 h-auto transition-all",
            selectedTimeframe === timeframe.value
              ? "bg-white/10 text-white shadow-sm"
              : "text-white/60 hover:text-white/80 hover:bg-white/5"
          )}
        >
          {timeframe.label}
        </Button>
      ))}
    </div>
  );
};
