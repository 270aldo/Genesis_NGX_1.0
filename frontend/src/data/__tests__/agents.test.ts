import { FITNESS_AGENTS, getAgentById, getAgentsBySpecialty, getAvailableSpecialties } from '../agents';

describe('agents data', () => {
  describe('FITNESS_AGENTS', () => {
    it('contains expected agents', () => {
      expect(FITNESS_AGENTS).toBeDefined();
      expect(Array.isArray(FITNESS_AGENTS)).toBe(true);
      expect(FITNESS_AGENTS.length).toBeGreaterThan(0);
    });

    it('has required agent properties', () => {
      FITNESS_AGENTS.forEach(agent => {
        expect(agent).toHaveProperty('id');
        expect(agent).toHaveProperty('name');
        expect(agent).toHaveProperty('specialty');
        expect(agent).toHaveProperty('description');
        expect(typeof agent.id).toBe('string');
        expect(typeof agent.name).toBe('string');
        expect(typeof agent.specialty).toBe('string');
        expect(typeof agent.description).toBe('string');
      });
    });

    it('has unique agent IDs', () => {
      const ids = FITNESS_AGENTS.map(agent => agent.id);
      const uniqueIds = new Set(ids);
      expect(uniqueIds.size).toBe(ids.length);
    });

    it('includes NEXUS agent', () => {
      const nexusAgent = FITNESS_AGENTS.find(agent => agent.id === 'nexus');
      expect(nexusAgent).toBeDefined();
      expect(nexusAgent?.name).toContain('NEXUS');
    });
  });

  describe('getAgentById', () => {
    it('returns agent for valid ID', () => {
      const agent = getAgentById('nexus');
      expect(agent).toBeDefined();
      expect(agent?.id).toBe('nexus');
    });

    it('returns undefined for invalid ID', () => {
      const agent = getAgentById('non-existent');
      expect(agent).toBeUndefined();
    });

    it('handles empty string', () => {
      const agent = getAgentById('');
      expect(agent).toBeUndefined();
    });

    it('handles null input gracefully', () => {
      const agent = getAgentById(null as any);
      expect(agent).toBeUndefined();
    });
  });

  describe('getAgentsBySpecialty', () => {
    it('returns agents matching specialty', () => {
      const trainingAgents = getAgentsBySpecialty('training');
      expect(Array.isArray(trainingAgents)).toBe(true);
      trainingAgents.forEach(agent => {
        expect(agent.specialty.toLowerCase()).toContain('training');
      });
    });

    it('returns empty array for non-existent specialty', () => {
      const agents = getAgentsBySpecialty('non-existent-specialty');
      expect(agents).toEqual([]);
    });

    it('performs case-insensitive matching', () => {
      const upperCaseAgents = getAgentsBySpecialty('TRAINING');
      const lowerCaseAgents = getAgentsBySpecialty('training');
      expect(upperCaseAgents).toEqual(lowerCaseAgents);
    });

    it('handles partial matches', () => {
      const nutritionAgents = getAgentsBySpecialty('nutri');
      expect(nutritionAgents.length).toBeGreaterThanOrEqual(0);
      nutritionAgents.forEach(agent => {
        expect(agent.specialty.toLowerCase()).toContain('nutri');
      });
    });
  });

  describe('getAvailableSpecialties', () => {
    it('returns unique list of specialties', () => {
      const specialties = getAvailableSpecialties();
      expect(Array.isArray(specialties)).toBe(true);
      expect(specialties.length).toBeGreaterThan(0);

      const uniqueSpecialties = new Set(specialties);
      expect(uniqueSpecialties.size).toBe(specialties.length);
    });

    it('returns specialties in alphabetical order', () => {
      const specialties = getAvailableSpecialties();
      const sortedSpecialties = [...specialties].sort();
      expect(specialties).toEqual(sortedSpecialties);
    });

    it('excludes empty or null specialties', () => {
      const specialties = getAvailableSpecialties();
      specialties.forEach(specialty => {
        expect(specialty).toBeTruthy();
        expect(typeof specialty).toBe('string');
        expect(specialty.trim().length).toBeGreaterThan(0);
      });
    });
  });

  describe('agent data integrity', () => {
    it('has consistent data structure', () => {
      FITNESS_AGENTS.forEach(agent => {
        // Check required fields
        expect(agent.id).toBeTruthy();
        expect(agent.name).toBeTruthy();
        expect(agent.specialty).toBeTruthy();
        expect(agent.description).toBeTruthy();

        // Check optional fields are properly typed if present
        if (agent.avatar) {
          expect(typeof agent.avatar).toBe('string');
        }

        if (agent.color) {
          expect(typeof agent.color).toBe('string');
        }

        if (agent.tags) {
          expect(Array.isArray(agent.tags)).toBe(true);
        }
      });
    });

    it('has reasonable description lengths', () => {
      FITNESS_AGENTS.forEach(agent => {
        expect(agent.description.length).toBeGreaterThan(10);
        expect(agent.description.length).toBeLessThan(500);
      });
    });

    it('has valid ID format', () => {
      FITNESS_AGENTS.forEach(agent => {
        // IDs should be lowercase, alphanumeric with possible hyphens/underscores
        expect(agent.id).toMatch(/^[a-z0-9_-]+$/);
        expect(agent.id.length).toBeGreaterThan(0);
        expect(agent.id.length).toBeLessThan(50);
      });
    });

    it('has proper name formatting', () => {
      FITNESS_AGENTS.forEach(agent => {
        expect(agent.name.trim()).toBe(agent.name); // No leading/trailing spaces
        expect(agent.name.length).toBeGreaterThan(0);
        expect(agent.name.length).toBeLessThan(100);
      });
    });
  });

  describe('specific agent validations', () => {
    it('NEXUS agent has coordination specialty', () => {
      const nexusAgent = getAgentById('nexus');
      expect(nexusAgent?.specialty.toLowerCase()).toContain('coordinat');
    });

    it('includes fitness-focused agents', () => {
      const fitnessKeywords = ['training', 'fitness', 'workout', 'exercise', 'strength', 'cardio'];
      const hasFitnessAgents = FITNESS_AGENTS.some(agent =>
        fitnessKeywords.some(keyword =>
          agent.specialty.toLowerCase().includes(keyword) ||
          agent.description.toLowerCase().includes(keyword)
        )
      );
      expect(hasFitnessAgents).toBe(true);
    });

    it('includes nutrition-focused agents', () => {
      const nutritionKeywords = ['nutrition', 'diet', 'food', 'meal', 'eating'];
      const hasNutritionAgents = FITNESS_AGENTS.some(agent =>
        nutritionKeywords.some(keyword =>
          agent.specialty.toLowerCase().includes(keyword) ||
          agent.description.toLowerCase().includes(keyword)
        )
      );
      expect(hasNutritionAgents).toBe(true);
    });
  });
});
