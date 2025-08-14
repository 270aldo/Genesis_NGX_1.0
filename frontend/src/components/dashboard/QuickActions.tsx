
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, Settings, Download, HelpCircle, Utensils, Dumbbell } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useChatStore } from '@/store/chatStore';
import { TokenPurchase } from '@/components/tokens/TokenPurchase';

export const QuickActions: React.FC = () => {
  const { createConversation } = useChatStore();

  const handleNewChat = () => {
    createConversation();
  };

  const actions = [
    {
      label: 'New Chat',
      icon: Plus,
      onClick: handleNewChat,
      href: '/chat',
      primary: true,
    },
    {
      label: 'Training',
      icon: Dumbbell,
      href: '/dashboard/training',
    },
    {
      label: 'Nutrition',
      icon: Utensils,
      href: '/dashboard/nutrition',
    },
    {
      label: 'Settings',
      icon: Settings,
      href: '/settings',
    },
    {
      label: 'Export Data',
      icon: Download,
      onClick: () => {/* TODO: Implement export functionality */},
    },
    {
      label: 'Help & Support',
      icon: HelpCircle,
      onClick: () => {/* TODO: Implement help functionality */},
    },
  ];

  return (
    <Card className="glass-ultra border-white/10 bg-white/5">
      <CardHeader>
        <CardTitle className="text-white">Quick Actions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {actions.map((action, index) => {
          const Icon = action.icon;
          const content = (
            <Button
              key={index}
              variant={action.primary ? "default" : "ghost"}
              className={`w-full justify-start gap-3 ${
                action.primary
                  ? 'bg-gradient-to-r from-purple-500 to-violet-600 hover:from-purple-600 hover:to-violet-700 text-white'
                  : 'text-white/60 hover:text-white hover:bg-white/5'
              }`}
              onClick={action.onClick}
            >
              <Icon className="w-4 h-4" />
              {action.label}
            </Button>
          );

          return action.href ? (
            <Link key={index} to={action.href}>
              {content}
            </Link>
          ) : (
            content
          );
        })}

        {/* Token Purchase Button */}
        <TokenPurchase />
      </CardContent>
    </Card>
  );
};
