
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  AlertTriangle, 
  CheckCircle, 
  Brain, 
  X,
  Clock
} from 'lucide-react';
import { useWearablesStore } from '@/store/wearablesStore';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';

export const PredictiveAlerts: React.FC = () => {
  const { predictiveAlerts, markAlertAsRead } = useWearablesStore();

  const unreadAlerts = predictiveAlerts.filter(alert => !alert.isRead);
  const recentAlerts = predictiveAlerts.slice(0, 5);

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'fatigue':
      case 'overtraining':
        return <AlertTriangle className="h-4 w-4" />;
      case 'recovery':
      case 'optimal_training':
        return <CheckCircle className="h-4 w-4" />;
      case 'illness':
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Brain className="h-4 w-4" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'medium':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'low':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'fatigue':
      case 'overtraining':
        return 'text-red-400';
      case 'recovery':
      case 'optimal_training':
        return 'text-green-400';
      case 'illness':
        return 'text-orange-400';
      default:
        return 'text-purple-400';
    }
  };

  if (recentAlerts.length === 0) {
    return (
      <Card className="bg-white/5 border-purple-500/20 backdrop-blur-sm">
        <CardContent className="p-6 text-center">
          <Brain className="h-12 w-12 text-white/40 mx-auto mb-3" />
          <p className="text-white/60">No predictive insights available yet</p>
          <p className="text-sm text-white/40 mt-1">
            Connect a wearable device to start receiving AI-powered health insights
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Unread Alerts Count */}
      {unreadAlerts.length > 0 && (
        <div className="flex items-center gap-2 mb-4">
          <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30">
            <Brain className="h-3 w-3 mr-1" />
            {unreadAlerts.length} New Insight{unreadAlerts.length > 1 ? 's' : ''}
          </Badge>
        </div>
      )}

      {/* Alerts List */}
      <div className="space-y-3">
        {recentAlerts.map((alert) => (
          <Card 
            key={alert.id} 
            className={cn(
              "bg-white/5 border backdrop-blur-sm transition-all duration-200",
              alert.isRead ? "border-white/10" : "border-purple-500/30 shadow-lg shadow-purple-500/10"
            )}
          >
            <CardContent className="p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className={cn("p-2 rounded-lg bg-white/10", getTypeColor(alert.type))}>
                    {getAlertIcon(alert.type)}
                  </div>
                  <div>
                    <h4 className="font-medium text-white text-sm">{alert.title}</h4>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge className={cn("text-xs", getSeverityColor(alert.severity))}>
                        {alert.severity} priority
                      </Badge>
                      <span className="text-xs text-white/60 flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {format(alert.timestamp, 'HH:mm')}
                      </span>
                    </div>
                  </div>
                </div>
                
                {!alert.isRead && (
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 text-white/40 hover:text-white/80"
                    onClick={() => markAlertAsRead(alert.id)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>

              <p className="text-sm text-white/80 mb-3">{alert.description}</p>

              {/* Recommendations */}
              <div className="space-y-2">
                <p className="text-xs font-medium text-white/60">Recommendations:</p>
                <ul className="space-y-1">
                  {alert.recommendations.map((rec, index) => (
                    <li key={index} className="text-xs text-white/70 flex items-center gap-2">
                      <div className="w-1 h-1 bg-purple-400 rounded-full flex-shrink-0" />
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Confidence */}
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/10">
                <span className="text-xs text-white/60">AI Confidence</span>
                <div className="flex items-center gap-2">
                  <div className="w-16 h-1 bg-white/20 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-purple-400 rounded-full transition-all duration-300"
                      style={{ width: `${alert.confidence * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-white/80">
                    {Math.round(alert.confidence * 100)}%
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};
