
import { 
  Dumbbell, 
  Calendar, 
  Camera, 
  Utensils, 
  BarChart3, 
  Moon, 
  Activity, 
  Heart, 
  Target, 
  Clock, 
  Shield, 
  Snowflake, 
  Wind, 
  Apple, 
  Sun, 
  CheckCircle, 
  Trophy,
  Map
} from 'lucide-react';
import type { AgentActions } from '@/types/quickActions';

export const agentActions: AgentActions = {
  'training-strategist': [{
    label: 'Create Workout Plan',
    icon: Dumbbell,
    prompt: 'Create a personalized workout plan for me'
  }, {
    label: 'Schedule Training',
    icon: Calendar,
    prompt: 'Help me schedule my training sessions'
  }, {
    label: 'Form Check',
    icon: Camera,
    prompt: 'I want to check my exercise form'
  }],
  'nutrition-architect': [{
    label: 'Meal Plan',
    icon: Utensils,
    prompt: 'Create a meal plan for my goals'
  }, {
    label: 'Food Analysis',
    icon: Camera,
    prompt: 'Analyze this food photo'
  }, {
    label: 'Macro Calculator',
    icon: BarChart3,
    prompt: 'Calculate my daily macros'
  }],
  'biometrics-engine': [{
    label: 'Analyze Sleep',
    icon: Moon,
    prompt: 'Analyze my sleep data from last week'
  }, {
    label: 'HRV Insights',
    icon: Activity,
    prompt: 'What do my HRV trends mean?'
  }, {
    label: 'Recovery Score',
    icon: Heart,
    prompt: 'Show me my current recovery status'
  }],
  'motivation-coach': [{
    label: 'Set Goals',
    icon: Target,
    prompt: 'Help me set realistic fitness goals'
  }, {
    label: 'Build Habits',
    icon: Clock,
    prompt: 'Help me build a workout habit'
  }, {
    label: 'Overcome Barriers',
    icon: Activity,
    prompt: 'I\'m struggling with motivation'
  }],
  'progress-tracker': [{
    label: 'Progress Report',
    icon: BarChart3,
    prompt: 'Show me my progress report'
  }, {
    label: 'Goal Timeline',
    icon: Calendar,
    prompt: 'When will I reach my goals?'
  }, {
    label: 'Photo Comparison',
    icon: Camera,
    prompt: 'Compare my progress photos'
  }],
  'recovery-corrective': [{
    label: 'Recovery Assessment',
    icon: Activity,
    prompt: 'Analyze my current recovery status based on sleep, HRV, and fatigue levels'
  }, {
    label: 'Mobility Plan',
    icon: Dumbbell,
    prompt: 'Create a personalized mobility and stretching routine for me'
  }, {
    label: 'Injury Prevention',
    icon: Shield,
    prompt: 'Identify my injury risk factors and create prevention strategies'
  }, {
    label: 'Sleep Optimization',
    icon: Moon,
    prompt: 'Help me optimize my sleep for better recovery'
  }, {
    label: 'Stress Management',
    icon: Heart,
    prompt: 'Teach me techniques to manage physical and mental stress'
  }],
  'biohacking-innovator': [{
    label: 'Cold Therapy',
    icon: Snowflake,
    prompt: 'Design a progressive cold exposure routine for recovery and resilience'
  }, {
    label: 'Breathwork',
    icon: Wind,
    prompt: 'Teach me advanced breathing techniques for performance and recovery'
  }, {
    label: 'Supplement Stack',
    icon: Apple,
    prompt: 'Create a personalized supplement protocol based on my goals'
  }, {
    label: 'Fasting Protocol',
    icon: Clock,
    prompt: 'Design a safe and effective intermittent fasting schedule for me'
  }, {
    label: 'Circadian Rhythm',
    icon: Sun,
    prompt: 'Help me optimize my body clock for better sleep and energy'
  }],
  'success-liaison': [{
    label: 'Weekly Check-in',
    icon: Calendar,
    prompt: 'Let\'s do a weekly check-in to review my progress and adjust my plan'
  }, {
    label: 'Goal Review',
    icon: Target,
    prompt: 'Help me evaluate and refine my fitness goals based on my progress'
  }, {
    label: 'Motivation Boost',
    icon: Heart,
    prompt: 'I need some personalized encouragement to overcome mental barriers'
  }, {
    label: 'Success Planning',
    icon: Map,
    prompt: 'Create a comprehensive roadmap for achieving my fitness goals'
  }, {
    label: 'Habit Tracker',
    icon: CheckCircle,
    prompt: 'Help me track and optimize my daily wellness habits'
  }, {
    label: 'Celebrate Wins',
    icon: Trophy,
    prompt: 'Let\'s acknowledge my achievements and plan some rewards'
  }]
};
