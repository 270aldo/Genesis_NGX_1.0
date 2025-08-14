
import React, { memo, useMemo } from 'react';
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

interface StatCard {
  title: string;
  value: string | number;
  icon: React.ComponentType<any>;
  description: string;
  tokenBalance?: boolean;
}

// Memoized individual card component
const StatCard = memo<{
  card: StatCard;
  currentTokens: number;
  index: number;
}>(({ card, currentTokens, index }) => {
  const Icon = card.icon;

  const tokenColor = useMemo(() => {
    if (!card.tokenBalance) return 'text-white';
    if (currentTokens < 10) return 'text-red-400';
    if (currentTokens < 50) return 'text-yellow-400';
    return 'text-green-400';
  }, [card.tokenBalance, currentTokens]);

  return (
    <Card className="glass-ultra border-white/10 bg-white/5">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-white/60">
          {card.title}
        </CardTitle>
        <Icon className={`h-4 w-4 ${card.tokenBalance ? 'text-yellow-400' : 'text-blue-400'}`} />
      </CardHeader>
      <CardContent>
        <div className={`text-2xl font-bold mb-1 ${tokenColor}`}>
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
});

StatCard.displayName = 'StatCard';

export const StatsCards: React.FC<StatsCardsProps> = memo(({ stats }) => {
  const { user } = useAuthStore();
  const currentTokens = user?.tokens ?? 0;

  // Memoize cards array to prevent unnecessary re-computations
  const cards = useMemo((): StatCard[] => [
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
  ], [stats.totalConversations, stats.totalMessages, currentTokens]);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, index) => (
        <StatCard
          key={`${card.title}-${index}`}
          card={card}
          currentTokens={currentTokens}
          index={index}
        />
      ))}
    </div>
  );
});

StatsCards.displayName = 'StatsCards';
