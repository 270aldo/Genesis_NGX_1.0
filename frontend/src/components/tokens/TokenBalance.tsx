
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Coins } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';

export const TokenBalance: React.FC = () => {
  const { user } = useAuthStore();
  const tokens = user?.tokens ?? 0;

  const getBalanceColor = () => {
    if (tokens < 10) return 'text-red-400';
    if (tokens < 50) return 'text-yellow-400';
    return 'text-green-400';
  };

  return (
    <Card className="glass-ultra border-white/10 bg-white/5">
      <CardContent className="p-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-yellow-500 to-orange-600 flex items-center justify-center">
            <Coins className="w-4 h-4 text-white" />
          </div>
          <div>
            <p className="text-white/60 text-xs">Token Balance</p>
            <p className={`text-lg font-semibold ${getBalanceColor()}`}>
              {tokens.toLocaleString()}
            </p>
          </div>
        </div>
        {tokens < 10 && (
          <div className="mt-2 text-xs text-red-400">
            ⚠️ Low token balance
          </div>
        )}
      </CardContent>
    </Card>
  );
};
