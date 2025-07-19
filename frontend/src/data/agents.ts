
import type { Agent } from '@/types/agent';

export const FITNESS_AGENTS: Agent[] = [
  {
    id: 'nexus',
    name: 'NEXUS',
    title: 'NEXUS - Coordinador IA & Éxito',
    specialty: 'Orquestador & Éxito del Cliente',
    description: 'Tu coordinador inteligente que orquesta conversaciones y garantiza tu éxito con filosofía NGX',
    avatar: '🧠',
    color: 'from-purple-500 to-indigo-600',
    accentColor: 'purple-500',
    icon: 'Circle',
    capabilities: ['Análisis de Intención', 'Coordinación de Agentes', 'Customer Success', 'Filosofía NGX'],
    personality: 'analytical',
    actions: [
      {
        id: 'intent-analysis',
        label: 'Análisis de Intención',
        description: 'Analizar tu mensaje y dirigirte al especialista correcto',
        icon: 'Brain',
        category: 'analysis'
      },
      {
        id: 'agent-coordination',
        label: 'Coordinación de Agentes',
        description: 'Coordinar múltiples agentes para solicitudes complejas',
        icon: 'Network',
        category: 'guidance'
      },
      {
        id: 'success-planning',
        label: 'Planificación de Éxito',
        description: 'Crear roadmap integral para lograr tus objetivos',
        icon: 'Map',
        category: 'plan'
      },
      {
        id: 'weekly-checkin',
        label: 'Check-in Semanal',
        description: 'Revisar progreso y ajustar plan semanal',
        icon: 'Calendar',
        category: 'tracking'
      }
    ]
  },
  {
    id: 'blaze',
    name: 'BLAZE',
    title: 'BLAZE - Especialista en Entrenamiento',
    specialty: 'Entrenamiento Físico',
    description: 'Especialista en ciencia de la hipertrofia y programación de entrenamiento individualizado',
    avatar: '🔥',
    color: 'from-red-500 to-orange-600',
    accentColor: 'red-500',
    icon: 'Target',
    capabilities: ['Ciencia de la Hipertrofia', 'Fuerza & Potencia', 'Periodización Avanzada', 'Análisis Biomecánico'],
    personality: 'motivational',
    actions: [
      {
        id: 'hypertrophy-plan',
        label: 'Plan de Hipertrofia',
        description: 'Crear programa personalizado de ganancia muscular',
        icon: 'Dumbbell',
        category: 'plan'
      },
      {
        id: 'strength-power',
        label: 'Fuerza & Potencia',
        description: 'Programación S&C especializada',
        icon: 'Zap',
        category: 'plan'
      },
      {
        id: 'biomechanics-analysis',
        label: 'Análisis Biomecánico',
        description: 'Analizar técnica y optimizar movimientos',
        icon: 'Eye',
        category: 'assessment'
      },
      {
        id: 'periodization',
        label: 'Periodización',
        description: 'Planificación avanzada de entrenamiento',
        icon: 'Calendar',
        category: 'plan'
      }
    ]
  },
  {
    id: 'sage',
    name: 'SAGE',
    title: 'SAGE - Especialista en Nutrición',
    specialty: 'Nutrición & Nutrigenómica',
    description: 'Experto en nutrición de precisión y personalización según fenotipo y genética',
    avatar: '🌿',
    color: 'from-emerald-500 to-green-600',
    accentColor: 'emerald-500',
    icon: 'Leaf',
    capabilities: ['Nutrición de Precisión', 'Nutrigenómica', 'Timing Nutricional', 'Suplementación Estratégica'],
    personality: 'supportive',
    actions: [
      {
        id: 'precision-nutrition',
        label: 'Nutrición de Precisión',
        description: 'Plan nutricional personalizado según tu genética',
        icon: 'Target',
        category: 'plan'
      },
      {
        id: 'nutrient-timing',
        label: 'Timing Nutricional',
        description: 'Optimizar horarios de comidas para rendimiento',
        icon: 'Clock',
        category: 'guidance'
      },
      {
        id: 'microbiota-analysis',
        label: 'Análisis de Microbiota',
        description: 'Optimizar salud intestinal e inmunológica',
        icon: 'Microscope',
        category: 'assessment'
      },
      {
        id: 'strategic-supplements',
        label: 'Suplementación Estratégica',
        description: 'Protocolo de suplementos basado en evidencia',
        icon: 'Pill',
        category: 'plan'
      }
    ]
  },
  {
    id: 'wave',
    name: 'WAVE',
    title: 'WAVE - Recuperación & Biométricos',
    specialty: 'Recuperación & Biométricos',
    description: 'Fusión de análisis biométrico y estrategias de recuperación para optimización completa',
    avatar: '🌊',
    color: 'from-cyan-500 to-blue-600',
    accentColor: 'cyan-500',
    icon: 'BarChart3',
    capabilities: ['Ritmos Circadianos', 'HRV Analysis', 'Recuperación Avanzada', 'Biometría Integral'],
    personality: 'analytical',
    actions: [
      {
        id: 'circadian-optimization',
        label: 'Optimización Circadiana',
        description: 'Alinear ritmos biológicos para mejor recuperación',
        icon: 'Sun',
        category: 'guidance'
      },
      {
        id: 'hrv-deep-analysis',
        label: 'Análisis HRV Profundo',
        description: 'Interpretación avanzada de variabilidad cardíaca',
        icon: 'Heart',
        category: 'analysis'
      },
      {
        id: 'recovery-protocols',
        label: 'Protocolos de Recuperación',
        description: 'Crioterapia, termoterapia y técnicas avanzadas',
        icon: 'RotateCcw',
        category: 'plan'
      },
      {
        id: 'sleep-optimization',
        label: 'Optimización del Sueño',
        description: 'Mejorar calidad y arquitectura del sueño',
        icon: 'Moon',
        category: 'guidance'
      }
    ]
  },
  {
    id: 'luna',
    name: 'LUNA',
    title: 'LUNA - Especialista en Salud Femenina',
    specialty: 'Salud Femenina',
    description: 'Especialista en ciclos hormonales, salud reproductiva y entrenamiento específico femenino',
    avatar: '🌙',
    color: 'from-pink-500 to-rose-600',
    accentColor: 'pink-500',
    icon: 'Heart',
    capabilities: ['Ciclos Hormonales', 'Perimenopausia', 'Nutrición Femenina', 'Salud Pélvica'],
    personality: 'empathetic',
    actions: [
      {
        id: 'hormonal-cycles',
        label: 'Entrenamiento por Ciclos',
        description: 'Adaptar entrenamiento a fases hormonales',
        icon: 'Calendar',
        category: 'plan'
      },
      {
        id: 'menopause-support',
        label: 'Apoyo Menopausia',
        description: 'Estrategias para perimenopausia y menopausia',
        icon: 'Shield',
        category: 'guidance'
      },
      {
        id: 'pelvic-health',
        label: 'Salud Pélvica',
        description: 'Fortalecimiento de suelo pélvico',
        icon: 'Activity',
        category: 'plan'
      },
      {
        id: 'pregnancy-postpartum',
        label: 'Embarazo & Postparto',
        description: 'Entrenamiento seguro durante y después del embarazo',
        icon: 'Baby',
        category: 'guidance'
      }
    ]
  },
  {
    id: 'spark',
    name: 'SPARK',
    title: 'SPARK - Especialista en Motivación',
    specialty: 'Motivación & Comportamiento',
    description: 'Experto en psicología del cambio de hábitos y neurociencia del comportamiento',
    avatar: '⚡',
    color: 'from-yellow-500 to-amber-600',
    accentColor: 'yellow-500',
    icon: 'Lightbulb',
    capabilities: ['Psicología del Cambio', 'Neurociencia Comportamental', 'Habit Stacking', 'Mentalidad NGX'],
    personality: 'empathetic',
    actions: [
      {
        id: 'habit-psychology',
        label: 'Psicología de Hábitos',
        description: 'Crear hábitos duraderos basados en neurociencia',
        icon: 'Brain',
        category: 'plan'
      },
      {
        id: 'motivation-systems',
        label: 'Sistemas de Motivación',
        description: 'Desarrollar motivación intrínseca sostenible',
        icon: 'Zap',
        category: 'guidance'
      },
      {
        id: 'limiting-beliefs',
        label: 'Creencias Limitantes',
        description: 'Identificar y superar barreras mentales',
        icon: 'Unlock',
        category: 'assessment'
      },
      {
        id: 'behavioral-anchors',
        label: 'Anclajes Mentales',
        description: 'Técnicas de visualización y anclaje',
        icon: 'Anchor',
        category: 'guidance'
      }
    ]
  },
  {
    id: 'stella',
    name: 'STELLA',
    title: 'STELLA - Especialista en Análisis',
    specialty: 'Progreso & Evaluación',
    description: 'Especialista en KPIs fisiológicos, análisis de datos y toma de decisiones basada en evidencia',
    avatar: '⭐',
    color: 'from-violet-500 to-purple-600',
    accentColor: 'violet-500',
    icon: 'TrendingUp',
    capabilities: ['KPIs Fisiológicos', 'Bioestadística', 'Análisis de Progreso', 'Visualización de Datos'],
    personality: 'analytical',
    actions: [
      {
        id: 'physiological-kpis',
        label: 'KPIs Fisiológicos',
        description: 'Métricas de masa magra, fuerza y VO2Max',
        icon: 'BarChart',
        category: 'analysis'
      },
      {
        id: 'progress-tracking',
        label: 'Seguimiento de Progreso',
        description: 'Análisis integral de tu evolución',
        icon: 'TrendingUp',
        category: 'tracking'
      },
      {
        id: 'data-visualization',
        label: 'Visualización de Datos',
        description: 'Reportes automáticos y dashboards personalizados',
        icon: 'PieChart',
        category: 'analysis'
      },
      {
        id: 'performance-tests',
        label: 'Tests Funcionales',
        description: 'Evaluaciones físicas y de rendimiento',
        icon: 'TestTube',
        category: 'assessment'
      }
    ]
  },
  {
    id: 'nova',
    name: 'NOVA',
    title: 'NOVA - Especialista en Optimización',
    specialty: 'Biohacking & Optimización',
    description: 'Especialista en biohacking cognitivo, nootrópicos y tecnologías de optimización avanzada',
    avatar: '✨',
    color: 'from-indigo-500 to-cyan-600',
    accentColor: 'indigo-500',
    icon: 'Zap',
    capabilities: ['Biohacking Cognitivo', 'Cronobiología', 'Tecnología Wearable', 'Optimización Mitocondrial'],
    personality: 'technical',
    actions: [
      {
        id: 'cognitive-biohacking',
        label: 'Biohacking Cognitivo',
        description: 'Optimización cerebral y nootrópicos',
        icon: 'Brain',
        category: 'plan'
      },
      {
        id: 'chronobiology',
        label: 'Cronobiología',
        description: 'Manipulación de luz y ritmos circadianos',
        icon: 'Sun',
        category: 'guidance'
      },
      {
        id: 'intermittent-fasting',
        label: 'Ayuno Intermitente',
        description: 'Protocolos de ayuno y autofagia',
        icon: 'Clock',
        category: 'plan'
      },
      {
        id: 'wearable-optimization',
        label: 'Optimización Wearable',
        description: 'Feedback loops y tecnología de seguimiento',
        icon: 'Watch',
        category: 'guidance'
      }
    ]
  },
  {
    id: 'codex',
    name: 'CODEX.072',
    title: 'CODEX.072 - Especialista en Genética',
    specialty: 'Genética & Datos Personales',
    description: 'Especialista en interpretación de ADN, polimorfismos y personalización genética',
    avatar: '🧬',
    color: 'from-teal-500 to-emerald-600',
    accentColor: 'teal-500',
    icon: 'Dna',
    capabilities: ['Interpretación de ADN', 'Polimorfismos', 'Nutrigenómica', 'Farmacogenómica'],
    personality: 'technical',
    actions: [
      {
        id: 'dna-interpretation',
        label: 'Interpretación de ADN',
        description: 'Análisis de test genéticos (23andMe, Nebula)',
        icon: 'FileSearch',
        category: 'analysis'
      },
      {
        id: 'snip-analysis',
        label: 'Análisis SNIPs',
        description: 'Personalización basada en polimorfismos',
        icon: 'Target',
        category: 'assessment'
      },
      {
        id: 'nutrigenomics',
        label: 'Nutrigenómica',
        description: 'Nutrición personalizada según genética',
        icon: 'Apple',
        category: 'plan'
      },
      {
        id: 'longevity-genetics',
        label: 'Genética de Longevidad',
        description: 'Riesgos genéticos y estrategias preventivas',
        icon: 'Shield',
        category: 'guidance'
      }
    ]
  },
  {
    id: 'guardian',
    name: 'GUARDIAN',
    title: 'GUARDIAN - Seguridad & Compliance',
    specialty: 'Seguridad & Compliance',
    description: 'Especialista en protección de datos, compliance médico y seguridad de la información',
    avatar: '🛡️',
    color: 'from-slate-500 to-gray-600',
    accentColor: 'slate-500',
    icon: 'Shield',
    capabilities: ['HIPAA Compliance', 'Protección de Datos', 'Seguridad Info', 'Auditoría Médica'],
    personality: 'protective',
    actions: [
      {
        id: 'data-protection',
        label: 'Protección de Datos',
        description: 'Análisis de privacidad y protección de información personal',
        icon: 'Lock',
        category: 'assessment'
      },
      {
        id: 'compliance-check',
        label: 'Verificación Compliance',
        description: 'Auditoría HIPAA y regulaciones médicas',
        icon: 'CheckCircle',
        category: 'analysis'
      },
      {
        id: 'security-protocols',
        label: 'Protocolos de Seguridad',
        description: 'Implementar medidas de seguridad personalizadas',
        icon: 'Shield',
        category: 'plan'
      },
      {
        id: 'risk-assessment',
        label: 'Evaluación de Riesgos',
        description: 'Identificar vulnerabilidades y riesgos de seguridad',
        icon: 'AlertTriangle',
        category: 'assessment'
      }
    ]
  },
  {
    id: 'node',
    name: 'NODE',
    title: 'NODE - Integración de Sistemas',
    specialty: 'Integración & Automatización',
    description: 'Especialista en conexión de sistemas, APIs y automatización de workflows',
    avatar: '🔗',
    color: 'from-orange-500 to-red-600',
    accentColor: 'orange-500',
    icon: 'Network',
    capabilities: ['APIs Integration', 'Workflow Automation', 'Data Sync', 'System Architecture'],
    personality: 'systematic',
    actions: [
      {
        id: 'api-integration',
        label: 'Integración APIs',
        description: 'Conectar sistemas externos y servicios de terceros',
        icon: 'Link',
        category: 'plan'
      },
      {
        id: 'workflow-automation',
        label: 'Automatización Workflows',
        description: 'Crear flujos automatizados para tareas repetitivas',
        icon: 'Workflow',
        category: 'plan'
      },
      {
        id: 'data-synchronization',
        label: 'Sincronización de Datos',
        description: 'Mantener datos consistentes entre sistemas',
        icon: 'RefreshCw',
        category: 'guidance'
      },
      {
        id: 'system-monitoring',
        label: 'Monitoreo de Sistemas',
        description: 'Supervisar salud y rendimiento de integraciones',
        icon: 'Activity',
        category: 'tracking'
      }
    ]
  }
];
