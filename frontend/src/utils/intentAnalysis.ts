
export const analyzeUserIntent = (message: string): string[] => {
  const keywords = {
    'blaze': ['workout', 'exercise', 'training', 'gym', 'strength', 'cardio', 'plan', 'muscle', 'hipertrofia', 'fuerza', 'potencia', 'entrenamiento', 'ejercicio'],
    'sage': ['food', 'eat', 'nutrition', 'diet', 'calories', 'macro', 'meal', 'nutrición', 'comida', 'dieta', 'nutrigenómica', 'suplemento'],
    'wave': ['sleep', 'heart rate', 'hrv', 'recovery', 'stress', 'data', 'sueño', 'recuperación', 'biométrico', 'circadiano', 'descanso'],
    'luna': ['women', 'female', 'hormones', 'cycle', 'menstrual', 'pregnancy', 'menopause', 'mujer', 'femenino', 'hormonas', 'ciclo', 'embarazo', 'menopausia'],
    'spark': ['motivation', 'habit', 'goal', 'stuck', 'barrier', 'mindset', 'motivación', 'hábito', 'meta', 'objetivo', 'mentalidad', 'psicología'],
    'stella': ['progress', 'track', 'measure', 'goal', 'achievement', 'result', 'progreso', 'medición', 'resultados', 'kpi', 'análisis', 'estadística'],
    'nova': ['biohack', 'optimize', 'supplement', 'cold', 'breathe', 'fast', 'biohacking', 'optimización', 'ayuno', 'nootrópico', 'cronobiología'],
    'codex': ['genetics', 'dna', 'genes', 'snp', 'polymorphism', 'genética', 'adn', 'polimorfismo', '23andme', 'nutrigenómica', 'farmacogenómica']
  };

  const relevantAgents: string[] = [];
  const lowerMessage = message.toLowerCase();

  Object.entries(keywords).forEach(([agentId, agentKeywords]) => {
    if (agentKeywords.some(keyword => lowerMessage.includes(keyword))) {
      relevantAgents.push(agentId);
    }
  });

  return relevantAgents.length > 0 ? relevantAgents : ['nexus'];
};
