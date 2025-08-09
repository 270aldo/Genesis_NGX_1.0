/**
 * Agent Collaboration Indicator Component
 * Shows when NEXUS is collaborating with other agents
 * Real-time indicators of agent activity and coordination
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import { FITNESS_AGENTS } from '@/data/agents';
import {
  Brain,
  Zap,
  Users,
  Clock,
  CheckCircle,
  ArrowRight,
  Loader2
} from 'lucide-react';

interface ActiveAgent {
  id: string;
  name: string;
  avatar: string;
  status: 'consulting' | 'analyzing' | 'responding' | 'completed';
  progress: number;
  task: string;
  startTime: Date;
}

interface AgentCollaborationIndicatorProps {
  activeAgents: ActiveAgent[];
  currentTask?: string;
  estimatedTime?: number;
  className?: string;
}

export const AgentCollaborationIndicator: React.FC<AgentCollaborationIndicatorProps> = ({
  activeAgents = [],
  currentTask = '',
  estimatedTime = 0,
  className
}) => {
  const [elapsedTime, setElapsedTime] = useState(0);

  // Update elapsed time
  useEffect(() => {
    if (activeAgents.length === 0) {
      setElapsedTime(0);
      return;
    }

    const interval = setInterval(() => {
      const startTime = Math.min(...activeAgents.map(a => a.startTime.getTime()));
      setElapsedTime(Date.now() - startTime);
    }, 1000);

    return () => clearInterval(interval);
  }, [activeAgents]);

  if (activeAgents.length === 0) {
    return null;
  }

  const getStatusIcon = (status: ActiveAgent['status']) => {
    switch (status) {
      case 'consulting':
        return <Brain className="w-3 h-3" />;
      case 'analyzing':
        return <Zap className="w-3 h-3" />;
      case 'responding':
        return <ArrowRight className="w-3 h-3" />;
      case 'completed':
        return <CheckCircle className="w-3 h-3" />;
      default:
        return <Loader2 className="w-3 h-3 animate-spin" />;
    }
  };

  const getStatusColor = (status: ActiveAgent['status']) => {
    switch (status) {
      case 'consulting':
        return 'text-blue-600 bg-blue-50';
      case 'analyzing':
        return 'text-yellow-600 bg-yellow-50';
      case 'responding':
        return 'text-purple-600 bg-purple-50';
      case 'completed':
        return 'text-green-600 bg-green-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusText = (status: ActiveAgent['status']) => {
    switch (status) {
      case 'consulting':
        return 'Consultando';
      case 'analyzing':
        return 'Analizando';
      case 'responding':
        return 'Respondiendo';
      case 'completed':
        return 'Completado';
      default:
        return 'Procesando';
    }
  };

  const getAgentData = (agentId: string) => {
    return FITNESS_AGENTS.find(a => a.id === agentId);
  };

  const overallProgress = activeAgents.length > 0
    ? activeAgents.reduce((sum, agent) => sum + agent.progress, 0) / activeAgents.length
    : 0;

  const completedCount = activeAgents.filter(a => a.status === 'completed').length;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className={cn("w-full", className)}
    >
      <Card className="border-purple-200 bg-gradient-to-r from-purple-50 to-indigo-50">
        <CardContent className="p-4">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="p-1 bg-purple-100 rounded-full">
                <Users className="w-4 h-4 text-purple-600" />
              </div>
              <div>
                <h3 className="font-medium text-purple-900">Tu Equipo NGX Trabajando</h3>
                <p className="text-xs text-purple-700">
                  {currentTask || 'Coordinando especialistas'}
                </p>
              </div>
            </div>

            <div className="text-right">
              <div className="text-sm font-medium text-purple-800">
                {completedCount}/{activeAgents.length}
              </div>
              <div className="text-xs text-purple-600 flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {Math.round(elapsedTime / 1000)}s
              </div>
            </div>
          </div>

          {/* Overall Progress */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-medium text-purple-800">Progreso General</span>
              <span className="text-xs text-purple-600">{Math.round(overallProgress)}%</span>
            </div>
            <Progress value={overallProgress} className="h-2 bg-purple-100" />
          </div>

          {/* Active Agents */}
          <div className="space-y-2">
            <AnimatePresence>
              {activeAgents.map((activeAgent) => {
                const agentData = getAgentData(activeAgent.id);

                return (
                  <motion.div
                    key={activeAgent.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    className="flex items-center gap-3 p-2 bg-white/70 rounded-lg border border-purple-100"
                  >
                    {/* Agent Avatar */}
                    <div className="flex-shrink-0">
                      <div className={cn(
                        "w-8 h-8 rounded-full flex items-center justify-center text-lg",
                        agentData?.color ? `bg-gradient-to-r ${agentData.color}` : 'bg-gray-200',
                        'text-white font-medium'
                      )}>
                        {activeAgent.avatar}
                      </div>
                    </div>

                    {/* Agent Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-sm text-gray-900 truncate">
                          {activeAgent.name}
                        </span>
                        <Badge
                          variant="outline"
                          className={cn("text-xs", getStatusColor(activeAgent.status))}
                        >
                          {getStatusIcon(activeAgent.status)}
                          <span className="ml-1">{getStatusText(activeAgent.status)}</span>
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-600 truncate">
                        {activeAgent.task}
                      </p>
                    </div>

                    {/* Progress */}
                    <div className="flex-shrink-0 w-12">
                      <div className="text-right">
                        <div className="text-xs font-medium text-gray-700">
                          {Math.round(activeAgent.progress)}%
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-1 mt-1">
                          <motion.div
                            className={cn(
                              "h-1 rounded-full transition-all duration-300",
                              agentData?.accentColor ? `bg-${agentData.accentColor}` : 'bg-purple-500'
                            )}
                            style={{ width: `${activeAgent.progress}%` }}
                            initial={{ width: 0 }}
                            animate={{ width: `${activeAgent.progress}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>

          {/* Footer */}
          <div className="mt-3 pt-3 border-t border-purple-200">
            <div className="flex items-center justify-between text-xs text-purple-700">
              <span>🧠 NEXUS coordinando tu equipo personal</span>
              {estimatedTime > 0 && (
                <span>~{Math.round(estimatedTime / 1000)}s estimado</span>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default AgentCollaborationIndicator;
