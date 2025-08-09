/**
 * Agent Activity Panel Component
 * Side panel showing which agents are active and their current tasks
 * Real-time updates of team activity coordinated by NEXUS
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';
import { FITNESS_AGENTS } from '@/data/agents';
import {
  Users,
  Eye,
  EyeOff,
  Minimize2,
  Maximize2,
  Clock,
  Brain,
  Pulse,
  TrendingUp,
  ChevronRight
} from 'lucide-react';

interface AgentActivity {
  id: string;
  name: string;
  avatar: string;
  status: 'active' | 'standby' | 'offline';
  currentTask?: string;
  lastActivity: Date;
  activityLevel: number; // 0-100
  contributions: number; // Number of contributions in current session
}

interface AgentActivityPanelProps {
  activities: AgentActivity[];
  isVisible?: boolean;
  isMinimized?: boolean;
  onToggleVisibility?: () => void;
  onToggleMinimize?: () => void;
  className?: string;
}

export const AgentActivityPanel: React.FC<AgentActivityPanelProps> = ({
  activities = [],
  isVisible = true,
  isMinimized = false,
  onToggleVisibility,
  onToggleMinimize,
  className
}) => {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  if (!isVisible) {
    return (
      <motion.div
        initial={{ x: 300 }}
        animate={{ x: 0 }}
        className="fixed right-4 top-1/2 -translate-y-1/2 z-50"
      >
        <Button
          variant="outline"
          size="sm"
          onClick={onToggleVisibility}
          className="bg-white shadow-lg border-purple-200 hover:bg-purple-50"
        >
          <Users className="w-4 h-4" />
        </Button>
      </motion.div>
    );
  }

  const getStatusColor = (status: AgentActivity['status']) => {
    switch (status) {
      case 'active':
        return 'text-green-600 bg-green-50';
      case 'standby':
        return 'text-yellow-600 bg-yellow-50';
      case 'offline':
        return 'text-gray-600 bg-gray-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusIcon = (status: AgentActivity['status'], activityLevel: number) => {
    if (status === 'active') {
      return <Pulse className="w-3 h-3 animate-pulse" />;
    } else if (status === 'standby') {
      return <Clock className="w-3 h-3" />;
    }
    return null;
  };

  const getAgentData = (agentId: string) => {
    return FITNESS_AGENTS.find(a => a.id === agentId);
  };

  const activeCount = activities.filter(a => a.status === 'active').length;
  const standbyCount = activities.filter(a => a.status === 'standby').length;

  const formatTimeAgo = (date: Date) => {
    const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000);

    if (seconds < 60) return 'ahora';
    if (seconds < 3600) return `hace ${Math.floor(seconds / 60)}m`;
    if (seconds < 86400) return `hace ${Math.floor(seconds / 3600)}h`;
    return `hace ${Math.floor(seconds / 86400)}d`;
  };

  return (
    <motion.div
      initial={{ x: 300, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 300, opacity: 0 }}
      className={cn(
        "fixed right-4 top-4 bottom-4 w-80 z-40",
        isMinimized && "bottom-auto h-auto",
        className
      )}
    >
      <Card className="h-full flex flex-col bg-white/95 backdrop-blur border-purple-200 shadow-xl">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-1 bg-purple-100 rounded-full">
                <Users className="w-4 h-4 text-purple-600" />
              </div>
              <div>
                <CardTitle className="text-lg text-purple-900">Tu Equipo NGX</CardTitle>
                <p className="text-xs text-purple-700">
                  {activeCount} activos • {standbyCount} en espera
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={onToggleMinimize}
                className="h-6 w-6 p-0"
              >
                {isMinimized ? <Maximize2 className="w-3 h-3" /> : <Minimize2 className="w-3 h-3" />}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={onToggleVisibility}
                className="h-6 w-6 p-0"
              >
                <EyeOff className="w-3 h-3" />
              </Button>
            </div>
          </div>

          {/* NEXUS Status */}
          <div className="mt-3 p-2 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg border border-purple-200">
            <div className="flex items-center gap-2">
              <div className="p-1 bg-purple-500 rounded-full">
                <Brain className="w-3 h-3 text-white" />
              </div>
              <div className="flex-1">
                <div className="font-medium text-purple-900 text-sm">NEXUS</div>
                <div className="text-xs text-purple-700">Director de Orquesta</div>
              </div>
              <Badge className="bg-green-100 text-green-800 text-xs">
                Coordinando
              </Badge>
            </div>
          </div>
        </CardHeader>

        {!isMinimized && (
          <CardContent className="flex-1 overflow-hidden p-0">
            <ScrollArea className="h-full px-4 pb-4">
              <div className="space-y-2">
                <AnimatePresence>
                  {activities
                    .sort((a, b) => {
                      // Sort by status (active first), then by activity level
                      if (a.status !== b.status) {
                        if (a.status === 'active') return -1;
                        if (b.status === 'active') return 1;
                        if (a.status === 'standby') return -1;
                        if (b.status === 'standby') return 1;
                      }
                      return b.activityLevel - a.activityLevel;
                    })
                    .map((activity) => {
                      const agentData = getAgentData(activity.id);
                      const isSelected = selectedAgent === activity.id;

                      return (
                        <motion.div
                          key={activity.id}
                          layout
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -20 }}
                          className={cn(
                            "p-3 rounded-lg border cursor-pointer transition-all duration-200",
                            isSelected
                              ? "bg-purple-50 border-purple-300"
                              : "bg-white border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                          )}
                          onClick={() => setSelectedAgent(isSelected ? null : activity.id)}
                        >
                          <div className="flex items-center gap-3">
                            {/* Agent Avatar */}
                            <div className="relative flex-shrink-0">
                              <div className={cn(
                                "w-8 h-8 rounded-full flex items-center justify-center text-sm",
                                agentData?.color ? `bg-gradient-to-r ${agentData.color}` : 'bg-gray-200',
                                'text-white font-medium'
                              )}>
                                {activity.avatar}
                              </div>

                              {/* Status Indicator */}
                              <div className={cn(
                                "absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white flex items-center justify-center",
                                activity.status === 'active' && "bg-green-500",
                                activity.status === 'standby' && "bg-yellow-500",
                                activity.status === 'offline' && "bg-gray-400"
                              )}>
                                {getStatusIcon(activity.status, activity.activityLevel) && (
                                  <div className="w-2 h-2 text-white">
                                    {getStatusIcon(activity.status, activity.activityLevel)}
                                  </div>
                                )}
                              </div>
                            </div>

                            {/* Agent Info */}
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1">
                                <span className="font-medium text-sm text-gray-900 truncate">
                                  {activity.name}
                                </span>
                                <Badge
                                  variant="outline"
                                  className={cn("text-xs", getStatusColor(activity.status))}
                                >
                                  {activity.status}
                                </Badge>
                              </div>

                              {activity.currentTask && (
                                <p className="text-xs text-gray-600 truncate mb-1">
                                  {activity.currentTask}
                                </p>
                              )}

                              <div className="flex items-center gap-3 text-xs text-gray-500">
                                <span>{formatTimeAgo(activity.lastActivity)}</span>
                                {activity.contributions > 0 && (
                                  <span className="flex items-center gap-1">
                                    <TrendingUp className="w-3 h-3" />
                                    {activity.contributions}
                                  </span>
                                )}
                              </div>
                            </div>

                            {/* Expand Indicator */}
                            <ChevronRight
                              className={cn(
                                "w-4 h-4 text-gray-400 transition-transform",
                                isSelected && "rotate-90"
                              )}
                            />
                          </div>

                          {/* Activity Level */}
                          {activity.status === 'active' && activity.activityLevel > 0 && (
                            <div className="mt-2 pt-2 border-t border-gray-100">
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-xs text-gray-600">Actividad</span>
                                <span className="text-xs text-gray-500">{activity.activityLevel}%</span>
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-1">
                                <motion.div
                                  className={cn(
                                    "h-1 rounded-full",
                                    agentData?.accentColor ? `bg-${agentData.accentColor}` : 'bg-purple-500'
                                  )}
                                  initial={{ width: 0 }}
                                  animate={{ width: `${activity.activityLevel}%` }}
                                  transition={{ duration: 0.3 }}
                                />
                              </div>
                            </div>
                          )}

                          {/* Expanded Details */}
                          <AnimatePresence>
                            {isSelected && agentData && (
                              <motion.div
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                                className="mt-3 pt-3 border-t border-gray-100"
                              >
                                <div className="space-y-2 text-xs">
                                  <div>
                                    <span className="font-medium text-gray-700">Especialidad:</span>
                                    <span className="ml-2 text-gray-600">{agentData.specialty}</span>
                                  </div>

                                  <div>
                                    <span className="font-medium text-gray-700">Capacidades:</span>
                                    <div className="flex flex-wrap gap-1 mt-1">
                                      {agentData.capabilities.slice(0, 3).map((cap, index) => (
                                        <Badge key={index} variant="outline" className="text-xs">
                                          {cap}
                                        </Badge>
                                      ))}
                                    </div>
                                  </div>
                                </div>
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </motion.div>
                      );
                    })}
                </AnimatePresence>
              </div>
            </ScrollArea>
          </CardContent>
        )}
      </Card>
    </motion.div>
  );
};

export default AgentActivityPanel;
