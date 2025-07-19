
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useAgentStore } from '@/store/agentStore';
import { useChatStore } from '@/store/chatStore';
import { useNavigate } from 'react-router-dom';
import { useIsMobile } from '@/hooks/use-mobile';
import { cn } from '@/lib/utils';
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
  Map,
  ArrowLeft
} from 'lucide-react';

const agentActions = {
  'blaze': {
    name: 'BLAZE',
    color: 'from-red-500 to-orange-600',
    actions: [{
      label: 'Create Workout Plan',
      icon: Dumbbell,
      prompt: 'Create a personalized workout plan for me',
      category: 'plan'
    }, {
      label: 'Schedule Training',
      icon: Calendar,
      prompt: 'Help me schedule my training sessions',
      category: 'plan'
    }, {
      label: 'Form Check',
      icon: Camera,
      prompt: 'I want to check my exercise form',
      category: 'assessment'
    }]
  },
  'sage': {
    name: 'SAGE',
    color: 'from-emerald-500 to-green-600',
    actions: [{
      label: 'Meal Plan',
      icon: Utensils,
      prompt: 'Create a meal plan for my goals',
      category: 'plan'
    }, {
      label: 'Food Analysis',
      icon: Camera,
      prompt: 'Analyze this food photo',
      category: 'analysis'
    }, {
      label: 'Macro Calculator',
      icon: BarChart3,
      prompt: 'Calculate my daily macros',
      category: 'analysis'
    }]
  },
  'wave': {
    name: 'WAVE',
    color: 'from-cyan-500 to-blue-600',
    actions: [{
      label: 'Analyze Sleep',
      icon: Moon,
      prompt: 'Analyze my sleep data from last week',
      category: 'analysis'
    }, {
      label: 'HRV Insights',
      icon: Activity,
      prompt: 'What do my HRV trends mean?',
      category: 'analysis'
    }, {
      label: 'Recovery Score',
      icon: Heart,
      prompt: 'Show me my current recovery status',
      category: 'assessment'
    }]
  },
  'spark': {
    name: 'SPARK',
    color: 'from-yellow-500 to-amber-600',
    actions: [{
      label: 'Recovery Assessment',
      icon: Activity,
      prompt: 'Analyze my current recovery status based on sleep, HRV, and fatigue levels',
      category: 'assessment'
    }, {
      label: 'Mobility Plan',
      icon: Dumbbell,
      prompt: 'Create a personalized mobility and stretching routine for me',
      category: 'plan'
    }, {
      label: 'Injury Prevention',
      icon: Shield,
      prompt: 'Identify my injury risk factors and create prevention strategies',
      category: 'plan'
    }, {
      label: 'Sleep Optimization',
      icon: Moon,
      prompt: 'Help me optimize my sleep for better recovery',
      category: 'guidance'
    }, {
      label: 'Stress Management',
      icon: Heart,
      prompt: 'Teach me techniques to manage physical and mental stress',
      category: 'guidance'
    }]
  },
  'nova': {
    name: 'NOVA',
    color: 'from-indigo-500 to-cyan-600',
    actions: [{
      label: 'Cold Therapy',
      icon: Snowflake,
      prompt: 'Design a progressive cold exposure routine for recovery and resilience',
      category: 'plan'
    }, {
      label: 'Breathwork',
      icon: Wind,
      prompt: 'Teach me advanced breathing techniques for performance and recovery',
      category: 'guidance'
    }, {
      label: 'Supplement Stack',
      icon: Apple,
      prompt: 'Create a personalized supplement protocol based on my goals',
      category: 'plan'
    }, {
      label: 'Fasting Protocol',
      icon: Clock,
      prompt: 'Design a safe and effective intermittent fasting schedule for me',
      category: 'plan'
    }, {
      label: 'Circadian Rhythm',
      icon: Sun,
      prompt: 'Help me optimize my body clock for better sleep and energy',
      category: 'guidance'
    }]
  },
  'nexus': {
    name: 'NEXUS',
    color: 'from-purple-500 to-indigo-600',
    actions: [{
      label: 'Weekly Check-in',
      icon: Calendar,
      prompt: 'Let\'s do a weekly check-in to review my progress and adjust my plan',
      category: 'tracking'
    }, {
      label: 'Goal Review',
      icon: Target,
      prompt: 'Help me evaluate and refine my fitness goals based on my progress',
      category: 'assessment'
    }, {
      label: 'Motivation Boost',
      icon: Heart,
      prompt: 'I need some personalized encouragement to overcome mental barriers',
      category: 'guidance'
    }, {
      label: 'Success Planning',
      icon: Map,
      prompt: 'Create a comprehensive roadmap for achieving my fitness goals',
      category: 'plan'
    }, {
      label: 'Habit Tracker',
      icon: CheckCircle,
      prompt: 'Help me track and optimize my daily wellness habits',
      category: 'tracking'
    }, {
      label: 'Success Planning',
      icon: Trophy,
      prompt: 'Create comprehensive roadmap for achieving my fitness goals',
      category: 'guidance'
    }]
  },
  'stella': {
    name: 'STELLA',
    color: 'from-violet-500 to-purple-600',
    actions: [{
      label: 'Progress Analytics',
      icon: BarChart3,
      prompt: 'Analyze my progress data and KPIs',
      category: 'analysis'
    }, {
      label: 'Performance Tests',
      icon: Target,
      prompt: 'Design functional movement and performance tests',
      category: 'assessment'
    }, {
      label: 'Data Visualization',
      icon: Trophy,
      prompt: 'Create custom dashboards and reports',
      category: 'tracking'
    }]
  },
  'luna': {
    name: 'LUNA',
    color: 'from-pink-500 to-rose-600',
    actions: [{
      label: 'Hormonal Cycles',
      icon: Calendar,
      prompt: 'Adapt training to my menstrual cycle phases',
      category: 'plan'
    }, {
      label: 'Pelvic Health',
      icon: Activity,
      prompt: 'Create pelvic floor strengthening program',
      category: 'plan'
    }, {
      label: 'Menopause Support',
      icon: Shield,
      prompt: 'Help with perimenopause and menopause strategies',
      category: 'guidance'
    }]
  },
  'codex': {
    name: 'CODEX.072',
    color: 'from-teal-500 to-emerald-600',
    actions: [{
      label: 'DNA Analysis',
      icon: Target,
      prompt: 'Interpret my genetic test results for personalization',
      category: 'analysis'
    }, {
      label: 'Nutrigenomics',
      icon: Apple,
      prompt: 'Create nutrition plan based on my genetics',
      category: 'plan'
    }, {
      label: 'Longevity Genetics',
      icon: Shield,
      prompt: 'Assess genetic risks and prevention strategies',
      category: 'assessment'
    }]
  }
};

export const QuickActions: React.FC = () => {
  const navigate = useNavigate();
  const isMobile = useIsMobile();
  const { setActiveAgent } = useAgentStore();
  const { addMessage, getCurrentConversation, createConversation } = useChatStore();
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const handleQuickAction = (agentId: string, prompt: string) => {
    // Set the active agent
    setActiveAgent(agentId);
    
    // Create or get conversation
    let conversationId = getCurrentConversation()?.id;
    if (!conversationId) {
      conversationId = createConversation();
    }
    
    // Add the message
    addMessage(conversationId, {
      content: prompt,
      role: 'user',
      agentId: agentId
    });
    
    // Navigate to chat with the specific agent
    navigate(`/chat/${agentId}`);
  };

  
  
  const getAllActions = () => {
    return Object.entries(agentActions).flatMap(([agentId, agentData]) =>
      agentData.actions.map(action => ({ ...action, agentId, agentName: agentData.name, agentColor: agentData.color }))
    );
  };

  const filteredActions = selectedCategory === 'all' 
    ? getAllActions() 
    : getAllActions().filter(action => action.category === selectedCategory);

  return (
    <div className="min-h-screen bg-black grok-gradient relative overflow-hidden">
      {/* Floating orbs */}
      <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute top-3/4 right-1/4 w-96 h-96 bg-violet-700/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      
      <div className="relative z-10 p-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate(-1)}
            className="text-white/70 hover:text-white hover:bg-white/10"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Quick Actions</h1>
            <p className="text-white/70">Fast track your fitness journey with AI-powered actions</p>
          </div>
        </div>

        {/* Category Filter */}
        <div className="mb-8">
          <Tabs value={selectedCategory} onValueChange={setSelectedCategory} className="w-full">
            <TabsList className={cn(
              "grid bg-black/20 border border-purple-500/20",
              isMobile ? "grid-cols-3" : "grid-cols-6"
            )}>
              <TabsTrigger value="all" className="text-white/70 data-[state=active]:text-white data-[state=active]:bg-purple-500/20">All</TabsTrigger>
              <TabsTrigger value="plan" className="text-white/70 data-[state=active]:text-white data-[state=active]:bg-purple-500/20">Plans</TabsTrigger>
              <TabsTrigger value="assessment" className="text-white/70 data-[state=active]:text-white data-[state=active]:bg-purple-500/20">Assess</TabsTrigger>
              <TabsTrigger value="analysis" className="text-white/70 data-[state=active]:text-white data-[state=active]:bg-purple-500/20">Analyze</TabsTrigger>
              <TabsTrigger value="guidance" className="text-white/70 data-[state=active]:text-white data-[state=active]:bg-purple-500/20">Guide</TabsTrigger>
              <TabsTrigger value="tracking" className="text-white/70 data-[state=active]:text-white data-[state=active]:bg-purple-500/20">Track</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        {/* Actions Grid */}
        <div className={cn(
          "grid gap-4",
          isMobile ? "grid-cols-1" : "grid-cols-2 lg:grid-cols-3"
        )}>
          {filteredActions.map((action, index) => {
            const ActionIcon = action.icon;
            return (
              <Card 
                key={`${action.agentId}-${index}`}
                className="bg-black/40 border border-purple-500/20 hover:border-purple-500/40 transition-all duration-300 hover:scale-[1.02] cursor-pointer group"
                onClick={() => handleQuickAction(action.agentId, action.prompt)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className={cn("w-10 h-10 rounded-lg bg-gradient-to-r flex items-center justify-center", action.agentColor)}>
                      <ActionIcon className="w-5 h-5 text-white" />
                    </div>
                    <Badge variant="secondary" className="bg-purple-500/20 text-purple-300 text-xs border border-purple-500/30">
                      {action.agentName}
                    </Badge>
                  </div>
                  <CardTitle className="text-white text-lg group-hover:text-purple-300 transition-colors">
                    {action.label}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-white/60 text-sm leading-relaxed">
                    {action.prompt}
                  </CardDescription>
                  <div className="mt-3">
                    <Badge variant="outline" className="text-xs text-white/50 border-white/20 capitalize">
                      {action.category}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {filteredActions.length === 0 && (
          <div className="text-center py-12">
            <p className="text-white/60">No actions found for the selected category.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default QuickActions;
