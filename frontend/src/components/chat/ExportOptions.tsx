
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { useChatStore } from '@/store/chatStore';
import { useAgentStore } from '@/store/agentStore';
import { Download, FileText, Share, Copy, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

export const ExportOptions: React.FC = () => {
  const { getCurrentConversation } = useChatStore();
  const { getAgent, getActiveAgent } = useAgentStore();
  const { toast } = useToast();
  const [isOpen, setIsOpen] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  const conversation = getCurrentConversation();
  const activeAgent = getActiveAgent();
  const messageCount = conversation?.messages?.length || 0;

  // Get agent color for dynamic styling
  const getAgentGradient = () => {
    if (!activeAgent) return 'from-purple-500 to-violet-600';

    const colorMap: Record<string, string> = {
      'nexus': 'from-purple-500 to-violet-600',
      'blaze': 'from-orange-500 to-red-600',
      'sage': 'from-emerald-500 to-green-600',
      'wave': 'from-cyan-500 to-blue-600',
      'luna': 'from-pink-500 to-rose-600',
      'spark': 'from-yellow-500 to-orange-600',
      'stella': 'from-indigo-500 to-purple-600',
      'nova': 'from-violet-500 to-purple-600',
      'codex': 'from-blue-500 to-indigo-600'
    };

    return colorMap[activeAgent.id] || 'from-purple-500 to-violet-600';
  };

  const generateConversationText = () => {
    if (!conversation) return '';

    let text = `NGX Agents - Conversación\n`;
    text += `Título: ${conversation.title}\n`;
    text += `Fecha: ${conversation.createdAt.toLocaleDateString()}\n`;
    text += `\n${'='.repeat(50)}\n\n`;

    conversation.messages.forEach((message, index) => {
      const agent = message.agentId ? getAgent(message.agentId) : null;
      const speaker = message.role === 'user' ? 'Tú' : (agent?.name || 'NGX Agent');

      text += `${speaker} [${message.timestamp.toLocaleTimeString()}]:\n`;
      text += `${message.content}\n\n`;

      if (index < conversation.messages.length - 1) {
        text += `${'-'.repeat(30)}\n\n`;
      }
    });

    return text;
  };

  const generateConversationHTML = () => {
    if (!conversation) return '';

    let html = `
<!DOCTYPE html>
<html>
<head>
    <title>NGX Agents - ${conversation.title}</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { border-bottom: 2px solid #e5e7eb; padding-bottom: 20px; margin-bottom: 30px; }
        .message { margin-bottom: 20px; padding: 15px; border-radius: 8px; }
        .user { background-color: #f3f4f6; margin-left: 60px; }
        .assistant { background-color: #eff6ff; margin-right: 60px; }
        .speaker { font-weight: bold; margin-bottom: 8px; }
        .timestamp { font-size: 12px; color: #6b7280; margin-top: 8px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>NGX Agents - Conversación</h1>
        <p><strong>Título:</strong> ${conversation.title}</p>
        <p><strong>Fecha:</strong> ${conversation.createdAt.toLocaleDateString()}</p>
    </div>
`;

    conversation.messages.forEach((message) => {
      const agent = message.agentId ? getAgent(message.agentId) : null;
      const speaker = message.role === 'user' ? 'Tú' : (agent?.name || 'NGX Agent');
      const messageClass = message.role === 'user' ? 'user' : 'assistant';

      html += `
    <div class="message ${messageClass}">
        <div class="speaker">${speaker}</div>
        <div>${message.content.replace(/\n/g, '<br>')}</div>
        <div class="timestamp">${message.timestamp.toLocaleTimeString()}</div>
    </div>`;
    });

    html += `
</body>
</html>`;

    return html;
  };

  const handleExport = async (type: 'txt' | 'html') => {
    setIsExporting(true);

    // Simulate export delay for better UX
    await new Promise(resolve => setTimeout(resolve, 800));

    try {
      if (type === 'txt') {
        const text = generateConversationText();
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ngx-agents-${conversation?.title.replace(/[^a-z0-9]/gi, '-')}-${Date.now()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        toast({
          title: "Conversación exportada",
          description: "La conversación se ha descargado como archivo de texto.",
        });
      } else {
        const html = generateConversationHTML();
        const blob = new Blob([html], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ngx-agents-${conversation?.title.replace(/[^a-z0-9]/gi, '-')}-${Date.now()}.html`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        toast({
          title: "Conversación exportada",
          description: "La conversación se ha descargado como archivo HTML.",
        });
      }
    } catch (error) {
      toast({
        title: "Error al exportar",
        description: "No se pudo exportar la conversación.",
      });
    }

    setIsExporting(false);
    setIsOpen(false);
  };

  const copyToClipboard = async () => {
    const text = generateConversationText();
    try {
      await navigator.clipboard.writeText(text);
      toast({
        title: "Copiado al portapapeles",
        description: "La conversación se ha copiado al portapapeles.",
      });
    } catch (err) {
      toast({
        title: "Error al copiar",
        description: "No se pudo copiar la conversación.",
      });
    }
    setIsOpen(false);
  };

  const shareConversation = async () => {
    const text = generateConversationText();
    if (navigator.share) {
      try {
        await navigator.share({
          title: `NGX Agents - ${conversation?.title}`,
          text: text,
        });
      } catch (err) {
        // Fallback to copy if sharing fails
        copyToClipboard();
      }
    } else {
      copyToClipboard();
    }
    setIsOpen(false);
  };

  if (!conversation || conversation.messages.length === 0) {
    return null;
  }

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          className={cn(
            "relative overflow-hidden group transition-all duration-300",
            "glass-premium border border-white/10 hover:border-white/20",
            `bg-gradient-to-r ${getAgentGradient()}/10 hover:${getAgentGradient()}/20`,
            "text-white hover:text-white shadow-lg hover:shadow-xl",
            "h-9 px-4 rounded-xl backdrop-blur-xl",
            isExporting && "animate-pulse"
          )}
          disabled={isExporting}
        >
          {/* Background glow effect */}
          <div className={cn(
            "absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300",
            `bg-gradient-to-r ${getAgentGradient()}/5 blur-lg`
          )} />

          {/* Content */}
          <div className="relative flex items-center gap-2">
            {isExporting ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span className="text-sm font-medium">Exportando...</span>
              </>
            ) : (
              <>
                <Download className="w-4 h-4 transition-transform group-hover:scale-110" />
                <span className="text-sm font-medium">Exportar</span>
                {messageCount > 0 && (
                  <Badge
                    className={cn(
                      "ml-1 h-5 px-1.5 text-xs font-semibold border-0",
                      `bg-gradient-to-r ${getAgentGradient()}/20 text-white`
                    )}
                  >
                    {messageCount}
                  </Badge>
                )}
                <Sparkles className="w-3 h-3 text-white/60" />
              </>
            )}
          </div>
        </Button>
      </DropdownMenuTrigger>

      <DropdownMenuContent
        align="end"
        className="w-56 glass-ultra border-white/10 bg-black/80 backdrop-blur-xl"
      >
        <DropdownMenuItem
          onClick={() => handleExport('txt')}
          className="hover:bg-white/5 text-white/90 hover:text-white"
        >
          <FileText className="h-4 w-4 mr-2" />
          Exportar como TXT
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={() => handleExport('html')}
          className="hover:bg-white/5 text-white/90 hover:text-white"
        >
          <Download className="h-4 w-4 mr-2" />
          Exportar como HTML
        </DropdownMenuItem>
        <DropdownMenuSeparator className="bg-white/10" />
        <DropdownMenuItem
          onClick={copyToClipboard}
          className="hover:bg-white/5 text-white/90 hover:text-white"
        >
          <Copy className="h-4 w-4 mr-2" />
          Copiar al portapapeles
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={shareConversation}
          className="hover:bg-white/5 text-white/90 hover:text-white"
        >
          <Share className="h-4 w-4 mr-2" />
          Compartir
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
