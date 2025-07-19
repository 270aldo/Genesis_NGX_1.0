
import React, { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Search, X, ChevronUp, ChevronDown } from 'lucide-react';
import { useChatStore } from '@/store/chatStore';
import { cn } from '@/lib/utils';

interface ChatSearchProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ChatSearch: React.FC<ChatSearchProps> = ({ isOpen, onClose }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [currentMatch, setCurrentMatch] = useState(0);
  const [searchResults, setSearchResults] = useState<Array<{ messageId: string; conversationId: string; content: string; index: number }>>([]);
  const { getCurrentConversation, conversations } = useChatStore();

  useEffect(() => {
    if (!searchTerm.trim()) {
      setSearchResults([]);
      setCurrentMatch(0);
      return;
    }

    const results: Array<{ messageId: string; conversationId: string; content: string; index: number }> = [];
    
    // Search in current conversation first
    const currentConversation = getCurrentConversation();
    if (currentConversation) {
      currentConversation.messages.forEach((message, index) => {
        if (message.content.toLowerCase().includes(searchTerm.toLowerCase())) {
          results.push({
            messageId: message.id,
            conversationId: currentConversation.id,
            content: message.content,
            index
          });
        }
      });
    }

    // Search in other conversations
    conversations.forEach(conversation => {
      if (conversation.id !== currentConversation?.id) {
        conversation.messages.forEach((message, index) => {
          if (message.content.toLowerCase().includes(searchTerm.toLowerCase())) {
            results.push({
              messageId: message.id,
              conversationId: conversation.id,
              content: message.content,
              index
            });
          }
        });
      }
    });

    setSearchResults(results);
    setCurrentMatch(0);
  }, [searchTerm, conversations, getCurrentConversation]);

  const handlePrevious = () => {
    setCurrentMatch((prev) => prev > 0 ? prev - 1 : searchResults.length - 1);
  };

  const handleNext = () => {
    setCurrentMatch((prev) => prev < searchResults.length - 1 ? prev + 1 : 0);
  };

  const highlightText = (text: string, term: string) => {
    if (!term) return text;
    
    const regex = new RegExp(`(${term})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <mark key={index} className="bg-yellow-400/30 text-yellow-200 rounded px-1">
          {part}
        </mark>
      ) : part
    );
  };

  if (!isOpen) return null;

  return (
    <div className="border-b border-white/10 bg-background/95 backdrop-blur-xl p-4">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-white/40" />
            <Input
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search in conversations..."
              className="pl-10 pr-4 bg-white/5 border-white/10 focus:border-blue-500/30"
              autoFocus
            />
          </div>
          
          {searchResults.length > 0 && (
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="bg-white/10 text-white/70">
                {currentMatch + 1} of {searchResults.length}
              </Badge>
              <Button
                variant="ghost"
                size="icon"
                onClick={handlePrevious}
                className="h-8 w-8 text-white/60 hover:text-white/80"
              >
                <ChevronUp className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleNext}
                className="h-8 w-8 text-white/60 hover:text-white/80"
              >
                <ChevronDown className="h-4 w-4" />
              </Button>
            </div>
          )}
          
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="h-8 w-8 text-white/60 hover:text-white/80"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        {searchTerm && searchResults.length > 0 && (
          <div className="mt-4 max-h-48 overflow-y-auto space-y-2">
            {searchResults.slice(0, 5).map((result, index) => (
              <div
                key={result.messageId}
                className={cn(
                  "p-3 rounded-lg border cursor-pointer transition-all",
                  index === currentMatch
                    ? "bg-blue-500/20 border-blue-500/30"
                    : "bg-white/5 border-white/10 hover:bg-white/10"
                )}
              >
                <div className="text-sm text-white/90 line-clamp-2">
                  {highlightText(result.content, searchTerm)}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
