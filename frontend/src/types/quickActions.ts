
import { LucideIcon } from 'lucide-react';

export interface QuickAction {
  label: string;
  icon: LucideIcon;
  prompt: string;
}

export interface AgentActions {
  [key: string]: QuickAction[];
}
