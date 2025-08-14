import { analyzeUserIntent } from '../intentAnalysis';

describe('analyzeUserIntent', () => {
  describe('single agent detection', () => {
    describe('blaze (workout/training)', () => {
      it('detects workout-related keywords', () => {
        expect(analyzeUserIntent('I need a workout plan')).toContain('blaze');
        expect(analyzeUserIntent('What exercises should I do?')).toContain('blaze');
        expect(analyzeUserIntent('Help me with training')).toContain('blaze');
        expect(analyzeUserIntent('I want to go to the gym')).toContain('blaze');
        expect(analyzeUserIntent('Build muscle strength')).toContain('blaze');
        expect(analyzeUserIntent('Cardio routine recommendations')).toContain('blaze');
      });

      it('detects Spanish workout keywords', () => {
        expect(analyzeUserIntent('Necesito un plan de entrenamiento')).toContain('blaze');
        expect(analyzeUserIntent('Quiero ganar fuerza')).toContain('blaze');
        expect(analyzeUserIntent('Rutina de ejercicio')).toContain('blaze');
        expect(analyzeUserIntent('Programa de hipertrofia')).toContain('blaze');
        expect(analyzeUserIntent('Desarrollar potencia muscular')).toContain('blaze');
      });
    });

    describe('sage (nutrition/diet)', () => {
      it('detects nutrition-related keywords', () => {
        expect(analyzeUserIntent('What should I eat today?')).toContain('sage');
        expect(analyzeUserIntent('Help with my diet plan')).toContain('sage');
        expect(analyzeUserIntent('How many calories do I need?')).toContain('sage');
        expect(analyzeUserIntent('Macro tracking advice')).toContain('sage');
        expect(analyzeUserIntent('Meal prep suggestions')).toContain('sage');
        expect(analyzeUserIntent('Food recommendations')).toContain('sage');
      });

      it('detects Spanish nutrition keywords', () => {
        expect(analyzeUserIntent('Ayuda con mi nutrición')).toContain('sage');
        expect(analyzeUserIntent('Plan de comida saludable')).toContain('sage');
        expect(analyzeUserIntent('Información sobre dieta')).toContain('sage');
        expect(analyzeUserIntent('Recomendaciones de suplemento')).toContain('sage');
        expect(analyzeUserIntent('Análisis nutrigenómico')).toContain('sage');
      });
    });

    describe('wave (biometrics/recovery)', () => {
      it('detects biometric-related keywords', () => {
        expect(analyzeUserIntent('Track my heart rate')).toContain('wave');
        expect(analyzeUserIntent('HRV analysis needed')).toContain('wave');
        expect(analyzeUserIntent('Recovery metrics')).toContain('wave');
        expect(analyzeUserIntent('Sleep tracking data')).toContain('wave');
        expect(analyzeUserIntent('Stress level monitoring')).toContain('wave');
        expect(analyzeUserIntent('Biometric data analysis')).toContain('wave');
      });

      it('detects Spanish biometric keywords', () => {
        expect(analyzeUserIntent('Análisis de sueño')).toContain('wave');
        expect(analyzeUserIntent('Datos biométricos')).toContain('wave');
        expect(analyzeUserIntent('Ritmo circadiano')).toContain('wave');
        expect(analyzeUserIntent('Período de descanso')).toContain('wave');
        expect(analyzeUserIntent('Métricas de recuperación')).toContain('wave');
      });
    });

    describe('luna (women health)', () => {
      it('detects women health keywords', () => {
        expect(analyzeUserIntent('Women-specific fitness advice')).toContain('luna');
        expect(analyzeUserIntent('Female hormone optimization')).toContain('luna');
        expect(analyzeUserIntent('Menstrual cycle tracking')).toContain('luna');
        expect(analyzeUserIntent('Pregnancy workout modifications')).toContain('luna');
        expect(analyzeUserIntent('Menopause health support')).toContain('luna');
      });

      it('detects Spanish women health keywords', () => {
        expect(analyzeUserIntent('Salud de la mujer')).toContain('luna');
        expect(analyzeUserIntent('Hormonas femeninas')).toContain('luna');
        expect(analyzeUserIntent('Ciclo menstrual')).toContain('luna');
        expect(analyzeUserIntent('Ejercicio durante embarazo')).toContain('luna');
        expect(analyzeUserIntent('Apoyo en menopausia')).toContain('luna');
      });
    });

    describe('spark (motivation/mindset)', () => {
      it('detects motivation-related keywords', () => {
        expect(analyzeUserIntent('I need motivation to workout')).toContain('spark');
        expect(analyzeUserIntent('Help building healthy habits')).toContain('spark');
        expect(analyzeUserIntent('Struggling to reach my goals')).toContain('spark');
        expect(analyzeUserIntent('Feeling stuck in my routine')).toContain('spark');
        expect(analyzeUserIntent('Mental barriers to fitness')).toContain('spark');
        expect(analyzeUserIntent('Mindset coaching needed')).toContain('spark');
      });

      it('detects Spanish motivation keywords', () => {
        expect(analyzeUserIntent('Necesito motivación')).toContain('spark');
        expect(analyzeUserIntent('Crear hábitos saludables')).toContain('spark');
        expect(analyzeUserIntent('Alcanzar mis metas')).toContain('spark');
        expect(analyzeUserIntent('Cambiar mi mentalidad')).toContain('spark');
        expect(analyzeUserIntent('Apoyo psicológico')).toContain('spark');
      });
    });

    describe('stella (progress tracking)', () => {
      it('detects progress tracking keywords', () => {
        expect(analyzeUserIntent('Track my progress over time')).toContain('stella');
        expect(analyzeUserIntent('Measure my achievements')).toContain('stella');
        expect(analyzeUserIntent('Goal tracking system')).toContain('stella');
        expect(analyzeUserIntent('Show me my results')).toContain('stella');
      });

      it('detects Spanish progress keywords', () => {
        expect(analyzeUserIntent('Seguimiento de progreso')).toContain('stella');
        expect(analyzeUserIntent('Medición de resultados')).toContain('stella');
        expect(analyzeUserIntent('Análisis estadístico')).toContain('stella');
        expect(analyzeUserIntent('KPI de fitness')).toContain('stella');
      });
    });

    describe('nova (biohacking)', () => {
      it('detects biohacking keywords', () => {
        expect(analyzeUserIntent('Biohacking techniques')).toContain('nova');
        expect(analyzeUserIntent('Optimize my performance')).toContain('nova');
        expect(analyzeUserIntent('Cold therapy benefits')).toContain('nova');
        expect(analyzeUserIntent('Breathing optimization')).toContain('nova');
        expect(analyzeUserIntent('Intermittent fasting')).toContain('nova');
        expect(analyzeUserIntent('Supplement recommendations')).toContain('nova');
      });

      it('detects Spanish biohacking keywords', () => {
        expect(analyzeUserIntent('Técnicas de biohacking')).toContain('nova');
        expect(analyzeUserIntent('Optimización del rendimiento')).toContain('nova');
        expect(analyzeUserIntent('Ayuno intermitente')).toContain('nova');
        expect(analyzeUserIntent('Nootrópicos naturales')).toContain('nova');
        expect(analyzeUserIntent('Cronobiología aplicada')).toContain('nova');
      });
    });

    describe('codex (genetics)', () => {
      it('detects genetics-related keywords', () => {
        expect(analyzeUserIntent('Genetic analysis for fitness')).toContain('codex');
        expect(analyzeUserIntent('DNA-based recommendations')).toContain('codex');
        expect(analyzeUserIntent('SNP polymorphism impact')).toContain('codex');
        expect(analyzeUserIntent('23andMe data integration')).toContain('codex');
      });

      it('detects Spanish genetics keywords', () => {
        expect(analyzeUserIntent('Análisis genético')).toContain('codex');
        expect(analyzeUserIntent('Información del ADN')).toContain('codex');
        expect(analyzeUserIntent('Polimorfismo genético')).toContain('codex');
        expect(analyzeUserIntent('Nutrigenómica personalizada')).toContain('codex');
        expect(analyzeUserIntent('Farmacogenómica aplicada')).toContain('codex');
      });
    });
  });

  describe('multiple agent detection', () => {
    it('detects multiple relevant agents', () => {
      const result = analyzeUserIntent('I need a workout plan and nutrition advice');
      expect(result).toContain('blaze');
      expect(result).toContain('sage');
      expect(result).toHaveLength(2);
    });

    it('detects workout and recovery agents', () => {
      const result = analyzeUserIntent('Training program with sleep tracking');
      expect(result).toContain('blaze');
      expect(result).toContain('wave');
    });

    it('detects nutrition and genetics agents', () => {
      const result = analyzeUserIntent('Diet plan based on my DNA analysis');
      expect(result).toContain('sage');
      expect(result).toContain('codex');
    });

    it('detects women health and motivation agents', () => {
      const result = analyzeUserIntent('Female-specific goals and motivation support');
      expect(result).toContain('luna');
      expect(result).toContain('spark');
    });

    it('handles complex multi-agent queries', () => {
      const result = analyzeUserIntent(
        'I need a comprehensive approach: workout plan, nutrition advice, sleep tracking, and progress measurement'
      );
      expect(result).toContain('blaze'); // workout
      expect(result).toContain('sage');  // nutrition
      expect(result).toContain('wave');  // sleep
      expect(result).toContain('stella'); // progress
      expect(result).toHaveLength(4);
    });
  });

  describe('fallback behavior', () => {
    it('returns nexus for unrelated queries', () => {
      expect(analyzeUserIntent('Hello, how are you?')).toEqual(['nexus']);
      expect(analyzeUserIntent('What is the weather like?')).toEqual(['nexus']);
      expect(analyzeUserIntent('Tell me a joke')).toEqual(['nexus']);
      expect(analyzeUserIntent('Random unrelated text')).toEqual(['nexus']);
    });

    it('returns nexus for empty string', () => {
      expect(analyzeUserIntent('')).toEqual(['nexus']);
    });

    it('returns nexus for whitespace-only string', () => {
      expect(analyzeUserIntent('   ')).toEqual(['nexus']);
      expect(analyzeUserIntent('\n\t')).toEqual(['nexus']);
    });
  });

  describe('case insensitivity', () => {
    it('handles uppercase keywords', () => {
      expect(analyzeUserIntent('WORKOUT PLAN')).toContain('blaze');
      expect(analyzeUserIntent('NUTRITION ADVICE')).toContain('sage');
      expect(analyzeUserIntent('SLEEP TRACKING')).toContain('wave');
    });

    it('handles mixed case keywords', () => {
      expect(analyzeUserIntent('WorkOut PlAn')).toContain('blaze');
      expect(analyzeUserIntent('NuTrItIoN aDvIcE')).toContain('sage');
      expect(analyzeUserIntent('SlEeP tRaCkInG')).toContain('wave');
    });

    it('handles lowercase keywords', () => {
      expect(analyzeUserIntent('workout plan')).toContain('blaze');
      expect(analyzeUserIntent('nutrition advice')).toContain('sage');
      expect(analyzeUserIntent('sleep tracking')).toContain('wave');
    });
  });

  describe('partial word matching', () => {
    it('detects keywords within larger words', () => {
      expect(analyzeUserIntent('bodybuilding')).toEqual(['nexus']); // 'build' alone doesn't match
      expect(analyzeUserIntent('workouts')).toContain('blaze'); // 'workout' matches
      expect(analyzeUserIntent('nutritional')).toContain('sage'); // 'nutrition' matches
      expect(analyzeUserIntent('sleeping')).toContain('wave'); // 'sleep' matches
    });

    it('detects keywords in sentences', () => {
      expect(analyzeUserIntent('I really need help with my workout routine')).toContain('blaze');
      expect(analyzeUserIntent('Can you analyze my nutrition habits?')).toContain('sage');
      expect(analyzeUserIntent('My sleep patterns are irregular')).toContain('wave');
    });
  });

  describe('edge cases', () => {
    it('handles special characters', () => {
      expect(analyzeUserIntent('workout-plan!')).toContain('blaze');
      expect(analyzeUserIntent('nutrition@home')).toContain('sage');
      expect(analyzeUserIntent('sleep_tracking#123')).toContain('wave');
    });

    it('handles very long messages', () => {
      const longMessage = 'This is a very long message that contains the word workout ' + 'a'.repeat(1000);
      expect(analyzeUserIntent(longMessage)).toContain('blaze');
    });

    it('handles messages with only numbers', () => {
      expect(analyzeUserIntent('12345')).toEqual(['nexus']);
      expect(analyzeUserIntent('0')).toEqual(['nexus']);
    });

    it('handles messages with only special characters', () => {
      expect(analyzeUserIntent('!@#$%^&*()')).toEqual(['nexus']);
      expect(analyzeUserIntent('.,;:"')).toEqual(['nexus']);
    });

    it('handles Unicode characters', () => {
      expect(analyzeUserIntent('workout with émojis 💪')).toContain('blaze');
      expect(analyzeUserIntent('nutrición con acentos')).toContain('sage');
    });
  });

  describe('performance considerations', () => {
    it('processes keywords efficiently', () => {
      const start = performance.now();

      // Process multiple queries
      for (let i = 0; i < 100; i++) {
        analyzeUserIntent('workout nutrition sleep progress genetics');
      }

      const end = performance.now();
      const duration = end - start;

      // Should complete 100 queries in reasonable time (< 100ms)
      expect(duration).toBeLessThan(100);
    });

    it('handles repeated calls consistently', () => {
      const message = 'workout and nutrition plan';
      const firstResult = analyzeUserIntent(message);

      // Call multiple times
      for (let i = 0; i < 10; i++) {
        const result = analyzeUserIntent(message);
        expect(result).toEqual(firstResult);
      }
    });
  });

  describe('real-world examples', () => {
    it('handles typical user queries', () => {
      expect(analyzeUserIntent('Can you help me create a workout routine?')).toContain('blaze');
      expect(analyzeUserIntent('What should I eat to lose weight?')).toContain('sage');
      expect(analyzeUserIntent('I want to track my sleep quality')).toContain('wave');
      expect(analyzeUserIntent('How can I stay motivated to exercise?')).toContain('spark');
      expect(analyzeUserIntent('Show me my fitness progress this month')).toContain('stella');
    });

    it('handles conversational context', () => {
      expect(analyzeUserIntent('Actually, I was thinking about my workout schedule')).toContain('blaze');
      expect(analyzeUserIntent('Well, regarding my diet, what do you think?')).toContain('sage');
      expect(analyzeUserIntent('Oh, and also about my sleep habits')).toContain('wave');
    });

    it('handles questions vs statements', () => {
      expect(analyzeUserIntent('How do I improve my workout?')).toContain('blaze');
      expect(analyzeUserIntent('I want to improve my workout')).toContain('blaze');
      expect(analyzeUserIntent('Workout improvement needed')).toContain('blaze');
    });

    it('handles negative contexts', () => {
      expect(analyzeUserIntent('I hate my current workout plan')).toContain('blaze');
      expect(analyzeUserIntent('My diet is not working')).toContain('sage');
      expect(analyzeUserIntent('Sleep tracking shows poor results')).toContain('wave');
    });
  });

  describe('return value validation', () => {
    it('always returns an array', () => {
      expect(Array.isArray(analyzeUserIntent('test'))).toBe(true);
      expect(Array.isArray(analyzeUserIntent(''))).toBe(true);
      expect(Array.isArray(analyzeUserIntent('workout nutrition'))).toBe(true);
    });

    it('never returns an empty array', () => {
      expect(analyzeUserIntent('random text').length).toBeGreaterThan(0);
      expect(analyzeUserIntent('').length).toBeGreaterThan(0);
      expect(analyzeUserIntent('   ').length).toBeGreaterThan(0);
    });

    it('returns valid agent identifiers', () => {
      const validAgents = ['blaze', 'sage', 'wave', 'luna', 'spark', 'stella', 'nova', 'codex', 'nexus'];
      const result = analyzeUserIntent('workout nutrition sleep');

      result.forEach(agent => {
        expect(validAgents).toContain(agent);
      });
    });

    it('returns unique agents (no duplicates)', () => {
      const result = analyzeUserIntent('workout workout exercise training');
      const uniqueAgents = [...new Set(result)];
      expect(result).toEqual(uniqueAgents);
    });
  });
});
