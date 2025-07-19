
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { MessageSquare, BarChart3, Coins, TrendingUp } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';

interface StatsCardsProps {
  stats: {
    totalConversations: number;
    totalMessages: number;
    tokensUsed: number;
    tokensLimit: number;
  };
}

export const StatsCards: React.FC<StatsCardsProps> = ({ stats }) => {
  const { user } = useAuthStore();
  const currentTokens = user?.tokens ?? 0;

  const cards = [
    {
      title: 'Total Conversations',
      value: stats.totalConversations,
      icon: MessageSquare,
      description: 'Active chats',
    },
    {
      title: 'Messages Sent',
      value: stats.totalMessages,
      icon: BarChart3,
      description: 'This month',
    },
    {
      title: 'Available Tokens',
      value: `${currentTokens.toLocaleString()}`,
      icon: Coins,
      description: 'Ready to use',
      tokenBalance: true,
    },
    {
      title: 'Efficiency',
      value: '94%',
      icon: TrendingUp,
      description: 'Response accuracy',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, index) => {
        const Icon = card.icon;
        return (
          <Card key={index} className="glass-ultra border-white/10 bg-white/5">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white/60">
                {card.title}
              </CardTitle>
              <Icon className={`h-4 w-4 ${card.tokenBalance ? 'text-yellow-400' : 'text-blue-400'}`} />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold mb-1 ${
                card.tokenBalance 
                  ? currentTokens < 10 
                    ? 'text-red-400' 
                    : currentTokens < 50 
                    ? 'text-yellow-400' 
                    : 'text-green-400'
                  : 'text-white'
              }`}>
                {card.value}
              </div>
              <p className="text-xs text-white/40">{card.description}</p>
              {card.tokenBalance && currentTokens < 10 && (
                <div className="mt-2 text-xs text-red-400">
                  ⚠️ Low balance
                </div>
              )}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
};
