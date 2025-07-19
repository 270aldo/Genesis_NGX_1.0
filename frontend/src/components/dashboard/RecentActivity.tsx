
import React from 'react';
import { Conversation } from '@/store/chatStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { MessageSquare, Clock, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

interface RecentActivityProps {
  conversations: Conversation[];
}

export const RecentActivity: React.FC<RecentActivityProps> = ({ conversations }) => {
  return (
    <Card className="glass-ultra border-white/10 bg-white/5">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-white">Recent Activity</CardTitle>
        <Link to="/chat">
          <Button variant="ghost" size="sm" className="text-blue-400 hover:text-blue-300">
            View All <ArrowRight className="w-4 h-4 ml-1" />
          </Button>
        </Link>
      </CardHeader>
      <CardContent>
        {conversations.length === 0 ? (
          <div className="text-center py-8">
            <MessageSquare className="w-12 h-12 text-white/20 mx-auto mb-4" />
            <p className="text-white/40">No conversations yet</p>
            <p className="text-white/30 text-sm">Start your first chat to see activity here</p>
          </div>
        ) : (
          <div className="space-y-4">
            {conversations.map((conversation) => (
              <div
                key={conversation.id}
                className="flex items-center justify-between p-4 rounded-lg glass-premium border border-white/5 hover:border-white/10 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-blue-400"></div>
                  <div>
                    <h4 className="text-white font-medium text-sm truncate max-w-xs">
                      {conversation.title}
                    </h4>
                    <div className="flex items-center gap-2 text-white/40 text-xs">
                      <Clock className="w-3 h-3" />
                      <span>{new Date(conversation.updatedAt).toLocaleDateString()}</span>
                      <span>•</span>
                      <span>{conversation.messages.length} messages</span>
                    </div>
                  </div>
                </div>
                <Link to="/chat">
                  <Button variant="ghost" size="icon" className="text-white/40 hover:text-white">
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
