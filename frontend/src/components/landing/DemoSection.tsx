import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Bot, User, ArrowUp } from 'lucide-react';

const demoMessages = [
  { role: 'user', content: 'Hello, can you help me with data analysis?' },
  { role: 'assistant', content: 'Absolutely! I can assist you with comprehensive data analysis using advanced statistical methods and machine learning techniques.' },
  { role: 'user', content: 'What makes NGX Agents different?' },
  { role: 'assistant', content: 'NGX Agents combines multiple specialized AI agents with a premium interface, offering unparalleled accuracy and user experience.' },
];

export const DemoSection: React.FC = () => {
  const [visibleMessages, setVisibleMessages] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setVisibleMessages(prev => {
        if (prev < demoMessages.length) {
          return prev + 1;
        } else {
          // Reset after showing all messages
          setTimeout(() => setVisibleMessages(0), 2000);
          return prev;
        }
      });
    }, 2500);

    return () => clearInterval(timer);
  }, []);

  return (
    <section id="demo" className="py-32 relative">
      <div className="container mx-auto px-6">
        <div className="text-center mb-20">
          <h2 className="text-4xl md:text-6xl font-light mb-6 text-white">
            See It In
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent"> Action</span>
          </h2>
          <p className="text-xl text-white/60 max-w-2xl mx-auto">
            Experience the smooth and intelligent conversation flow of NGX Agents
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          {/* Demo Chat Window */}
          <div className="glass-ultra border border-white/10 rounded-3xl p-8 relative overflow-hidden">
            <div className="flex items-center gap-3 mb-8 pb-6 border-b border-white/10">
              <div className="w-3 h-3 rounded-full bg-red-400"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
              <div className="w-3 h-3 rounded-full bg-green-400"></div>
              <span className="ml-4 text-white/60 text-sm">NGX Agents Chat</span>
            </div>

            <div className="space-y-6 min-h-[400px]">
              {demoMessages.slice(0, visibleMessages).map((message, index) => (
                <div
                  key={index}
                  className={`flex gap-4 message-fade-in ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
                >
                  <div className={`w-10 h-10 rounded-2xl flex items-center justify-center ${
                    message.role === 'user' 
                      ? 'glass-premium border border-white/10' 
                      : 'glass-premium border border-blue-500/20 glow-subtle'
                  }`}>
                    {message.role === 'user' ? (
                      <User className="w-5 h-5 text-white/80" />
                    ) : (
                      <Bot className="w-5 h-5 text-blue-400" />
                    )}
                  </div>
                  <div className={`flex-1 max-w-2xl ${message.role === 'user' ? 'text-right' : ''}`}>
                    <div className={`inline-block glass-premium border rounded-2xl px-6 py-4 ${
                      message.role === 'user' 
                        ? 'border-white/10' 
                        : 'border-blue-500/10'
                    }`}>
                      <p className="text-white/90 leading-relaxed">{message.content}</p>
                    </div>
                  </div>
                </div>
              ))}
              
              {visibleMessages === demoMessages.length && (
                <div className="text-center pt-8">
                  <div className="inline-flex items-center gap-2 text-white/50 text-sm">
                    <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></div>
                    Demo will restart...
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="text-center mt-12">
            <Link to="/chat">
              <button className="premium-glow-button">
                <span>Try NGX Agents Now</span>
                <ArrowUp className="w-5 h-5 ml-2 rotate-45" />
              </button>
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
};
