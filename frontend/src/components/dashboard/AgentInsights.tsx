import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { TrendingUp, AlertTriangle, CheckCircle, ArrowRight, Brain, Target, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

export const AgentInsights: React.FC = () => {

  // Enhanced insights data for new NGX agents
  const insights = [
    {
      agentId: 'blaze',
      title: 'Alerta de Progreso en Fuerza',
      insight: 'Tu fuerza ha mejorado 18% este mes. Listo para sobrecarga progresiva avanzada.',
      priority: 'high' as const,
      action: 'Incrementar cargas 5-10% próxima semana',
      type: 'success' as const,
      icon: TrendingUp,
      color: 'orange'
    },
    {
      agentId: 'sage',
      title: 'Optimización Nutrigenómica',
      insight: 'Detecté polimorfismo MTHFR. Ajustar protocolo de folatos.',
      priority: 'medium' as const,
      action: 'Incorporar folato metilado en suplementación',
      type: 'warning' as const,
      icon: AlertTriangle,
      color: 'emerald'
    },
    {
      agentId: 'wave',
      title: 'Análisis HRV Profundo',
      insight: 'HRV descendente 3 días. Activar protocolo de recuperación avanzada.',
      priority: 'high' as const,
      action: 'Implementar sesión de respiración + crioterapia',
      type: 'alert' as const,
      icon: Brain,
      color: 'cyan'
    },
    {
      agentId: 'luna',
      title: 'Optimización Hormonal Femenina',
      insight: 'Fase lútea detectada. Ajustar intensidad de entrenamiento.',
      priority: 'medium' as const,
      action: 'Reducir volumen 15%, enfoque en técnica',
      type: 'warning' as const,
      icon: CheckCircle,
      color: 'pink'
    }
  ];

  const getPriorityStyle = (type: string) => {
    if (type === 'success') return 'border-green-500/30 bg-green-500/10';
    if (type === 'warning') return 'border-yellow-500/30 bg-yellow-500/10';
    if (type === 'alert') return 'border-red-500/30 bg-red-500/10';
    return 'border-purple-500/30 bg-purple-500/10';
  };

  const getIconColor = (color: string) => {
    switch (color) {
      case 'green': return 'text-green-400';
      case 'yellow': return 'text-yellow-400';
      case 'red': return 'text-red-400';
      default: return 'text-purple-400';
    }
  };

  return (
    <Card className="glass-ultra border-white/10 bg-white/5">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-purple-500/20">
              <Zap className="h-5 w-5 text-purple-400" />
            </div>
            <div>
              <CardTitle className="text-white text-xl">AI Insights</CardTitle>
              <p className="text-white/60 text-sm">Personalized recommendations from your agents</p>
            </div>
          </div>
          <Badge variant="secondary" className="bg-purple-500/20 text-purple-300 border-purple-500/30">
            {insights.length} Active
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {insights.map((insight, index) => {
          const Icon = insight.icon;
          
          return (
            <div
              key={index}
              className={cn(
                "p-4 rounded-xl border backdrop-blur-sm transition-all hover:bg-white/5",
                getPriorityStyle(insight.type)
              )}
            >
              <div className="flex items-start gap-4">
                <div className={cn(
                  "p-2 rounded-lg bg-white/10",
                  getIconColor(insight.color)
                )}>
                  <Icon className="h-4 w-4" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <h4 className="text-white font-medium text-sm">{insight.title}</h4>
                    <Badge 
                      variant={insight.priority === 'high' ? 'destructive' : 'secondary'}
                      className="text-xs"
                    >
                      {insight.priority}
                    </Badge>
                  </div>
                  
                  <p className="text-white/70 text-sm mb-3 leading-relaxed">
                    {insight.insight}
                  </p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Target className="h-3 w-3 text-white/40" />
                      <span className="text-white/60 text-xs">{insight.action}</span>
                    </div>
                    
                    <Button
                      size="sm"
                      variant="ghost"
                      className="h-7 px-2 text-white/60 hover:text-white hover:bg-white/10"
                    >
                      View Details
                      <ArrowRight className="h-3 w-3 ml-1" />
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
        
        {/* Summary footer */}
        <div className="pt-4 border-t border-white/10">
          <div className="flex items-center justify-between text-sm">
            <span className="text-white/60">Last updated: 2 minutes ago</span>
            <Button variant="ghost" size="sm" className="text-purple-400 hover:text-purple-300">
              View All Insights
              <ArrowRight className="h-3 w-3 ml-1" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
