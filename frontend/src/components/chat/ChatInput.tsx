
import React, { useState, useRef, useEffect } from 'react';
import { useChatStore, FileAttachment } from '@/store/chatStore';
import { useAgentStore } from '@/store/agentStore';
import { useQuickMessageListener } from '@/hooks/useQuickMessageListener';
import { useIsMobile } from '@/hooks/use-mobile';
import { Button } from '@/components/ui/button';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { ArrowUp, Paperclip, ChevronUp, Bot } from 'lucide-react';
import { cn } from '@/lib/utils';
import { FileAttachmentComponent } from './FileAttachment';
import { CameraCapture } from './CameraCapture';
import { VoiceRecorder } from './VoiceRecorder';
import { useVoiceConversation } from '@/hooks/useVoiceConversation';
import { VoiceInterface } from '../voice/VoiceInterface';
import { Dialog, DialogContent, DialogTrigger } from '@/components/ui/dialog';
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';

interface ChatInputProps {
  onSendMessage: (content: string, attachments?: FileAttachment[]) => void;
  disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, disabled }) => {
  const [input, setInput] = useState('');
  const [agentDropdownOpen, setAgentDropdownOpen] = useState(false);
  const [attachments, setAttachments] = useState<FileAttachment[]>([]);
  const [showVoiceDialog, setShowVoiceDialog] = useState(false);
  const { isTyping } = useChatStore();
  const { agents, activeAgentId, setActiveAgent, getActiveAgent } = useAgentStore();
  const { isVoiceActive } = useVoiceConversation();
  const isMobile = useIsMobile();
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const activeAgent = getActiveAgent();

  useQuickMessageListener(onSendMessage);

  // Keyboard shortcuts
  useKeyboardShortcuts({
    onUploadFiles: () => fileInputRef.current?.click(),
    onOpenCamera: () => {}, // Camera has its own trigger
    onStartRecording: () => setShowVoiceDialog(true),
  });

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  const handleSubmit = () => {
    if ((input.trim() || attachments.length > 0) && !disabled) {
      onSendMessage(input.trim(), attachments.length > 0 ? attachments : undefined);
      setInput('');
      setAttachments([]);
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleFilesAdded = (newFiles: FileAttachment[]) => {
    setAttachments(prev => [...prev, ...newFiles].slice(0, 5)); // Max 5 files
  };

  const handleFileRemoved = (fileId: string) => {
    setAttachments(prev => prev.filter(file => file.id !== fileId));
  };

  const handleCameraCapture = (file: FileAttachment) => {
    handleFilesAdded([file]);
  };

  const handleVoiceRecording = (audioBlob: Blob) => {
    // Convert audio blob to file attachment
    const id = Date.now().toString();
    const url = URL.createObjectURL(audioBlob);
    const audioFile: FileAttachment = {
      id,
      name: `voice-recording-${Date.now()}.wav`,
      type: 'audio/wav',
      size: audioBlob.size,
      url
    };
    handleFilesAdded([audioFile]);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className={cn("w-full max-w-3xl mx-auto", isMobile && "px-3")}>
      <div className="bg-black border border-violet-800 rounded-2xl shadow-lg shadow-violet-800/10">
        {/* File Attachments Area */}
        <FileAttachmentComponent
          files={attachments}
          onFilesAdded={handleFilesAdded}
          onFileRemoved={handleFileRemoved}
          disabled={disabled}
        />
        
        <div className={cn("p-2", isMobile ? "md:p-2" : "md:p-4")}>
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={isTyping ? "NGX Agent is thinking..." : "Ask me anything..."}
            disabled={disabled || isTyping}
            className="w-full text-base md:text-lg placeholder-gray-400 bg-transparent outline-none resize-none p-2 text-white"
            rows={2}
          />
        </div>
        <div className="flex items-center justify-between mt-2 px-4 pb-3 border-t border-violet-800 pt-3">
          <div className="flex items-center gap-2">
            {/* File Upload Button */}
            <Button
              variant="ghost"
              size="icon"
              className="p-2 hover:bg-violet-900/50 rounded-lg transition-all duration-200 touch-manipulation min-h-[44px] min-w-[44px]"
              disabled={disabled}
              onClick={() => fileInputRef.current?.click()}
              aria-label="Upload files (Ctrl+U)"
              title="Upload files (Ctrl+U)"
            >
              <Paperclip className="w-5 h-5 text-violet-500" />
            </Button>

            {/* Camera Capture */}
            <CameraCapture
              onCapture={handleCameraCapture}
              disabled={disabled}
            />

            {/* Voice Recording */}
            <VoiceRecorder
              onRecordingComplete={handleVoiceRecording}
              disabled={disabled}
            />

            {/* Voice Conversation */}
            <Dialog open={showVoiceDialog} onOpenChange={setShowVoiceDialog}>
              <DialogTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className={cn(
                    "p-2 rounded-lg transition-all duration-200 touch-manipulation min-h-[44px] min-w-[44px]",
                    isVoiceActive 
                      ? "bg-violet-500/20 hover:bg-violet-500/30 text-violet-400" 
                      : "hover:bg-violet-900/50 text-violet-500"
                  )}
                  disabled={disabled}
                  aria-label="Start voice conversation (Ctrl+Shift+M)"
                  title="Start voice conversation (Ctrl+Shift+M)"
                >
                  <Bot className="w-5 h-5" />
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-md bg-black/90 border-violet-500/20">
                <VoiceInterface />
              </DialogContent>
            </Dialog>
          </div>
          <div className="flex items-center gap-3">
            <Popover open={agentDropdownOpen} onOpenChange={setAgentDropdownOpen}>
              <PopoverTrigger asChild>
                <div className="flex items-center gap-1 cursor-pointer group px-2 py-1 rounded-lg hover:bg-violet-900/30 transition-colors">
                  <span className="text-sm font-medium text-gray-300 group-hover:text-white transition-colors">
                    {activeAgent?.name || 'Select Agent'}
                  </span>
                  <ChevronUp className="w-3 h-3 text-gray-400 group-hover:text-white transition-colors" />
                </div>
              </PopoverTrigger>
              <PopoverContent 
                className="w-80 p-0 bg-black border border-violet-800 shadow-lg shadow-violet-800/20" 
                align="end"
                side="top"
                sideOffset={8}
              >
                <div className="p-3">
                  <div className="text-xs font-medium text-gray-400 mb-3 uppercase tracking-wider">Select Agent</div>
                  <div className="space-y-1 max-h-60 overflow-y-auto">
                    {agents.map((agent) => (
                      <div
                        key={agent.id}
                        onClick={() => {
                          setActiveAgent(agent.id);
                          setAgentDropdownOpen(false);
                        }}
                        className={cn(
                          "flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors",
                          activeAgentId === agent.id 
                            ? "bg-violet-900/50 border border-violet-700" 
                            : "hover:bg-violet-900/30"
                        )}
                      >
                        <div 
                          className="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-semibold"
                          style={{ backgroundColor: agent.accentColor, color: 'white' }}
                        >
                          {agent.name.charAt(0)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium text-white">{agent.name}</div>
                          <div className="text-xs text-gray-400 truncate">{agent.specialty}</div>
                        </div>
                        {activeAgentId === agent.id && (
                          <div className="w-2 h-2 rounded-full bg-violet-400"></div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </PopoverContent>
            </Popover>
            <Button
              onClick={handleSubmit}
              disabled={((!input.trim() && attachments.length === 0) && !isTyping) || disabled}
              className="p-2.5 rounded-lg bg-violet-500 text-white hover:bg-violet-600 transition-all duration-200 disabled:opacity-50 touch-manipulation min-h-[44px] min-w-[44px] active:scale-95"
              aria-label="Send message"
            >
              <ArrowUp className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </div>

      {/* Hidden file input for keyboard shortcut */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={(e) => {
          const files = Array.from(e.target.files || []);
          if (files.length > 0) {
            const fileAttachments = files.map(file => ({
              id: Date.now().toString() + Math.random(),
              name: file.name,
              type: file.type,
              size: file.size,
              url: URL.createObjectURL(file),
              preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined
            }));
            handleFilesAdded(fileAttachments);
          }
        }}
        multiple
        accept="image/*,.pdf,.doc,.docx,.txt"
        className="hidden"
        disabled={disabled}
      />
    </div>
  );
};
