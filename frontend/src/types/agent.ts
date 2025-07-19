
export interface Agent {
  id: string;
  name: string;
  title: string;
  specialty: string;
  description: string;
  avatar: string;
  color: string;
  accentColor: string;
  icon: string;
  capabilities: string[];
  personality: 'motivational' | 'analytical' | 'empathetic' | 'technical' | 'supportive';
  actions?: AgentAction[];
}

export interface AgentAction {
  id: string;
  label: string;
  description: string;
  icon: string;
  category: 'assessment' | 'plan' | 'analysis' | 'guidance' | 'tracking';
}

export interface AgentMessage {
  agentId: string;
  content: string;
  timestamp: Date;
  type: 'analysis' | 'recommendation' | 'insight' | 'plan' | 'alert';
  data?: Record<string, unknown>;
}
