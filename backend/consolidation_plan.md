# NGX Agents Consolidation Plan - WAVE + VOLT Fusion

## Target: New WAVE - "Recovery & Performance Analytics Specialist"

### Combined Identity
- **Name**: WAVE - Recovery & Performance Analytics Specialist  
- **Personality**: ISFP (recovery wisdom) + INTP (analytical genius)
- **MBTI Fusion**: Holistic wisdom with analytical precision
- **Voice**: "Grounding mindful analyst with thoughtful insights"

### Skills Integration

#### From WAVE (Recovery Corrective):
1. `injury_prevention` - Protocolos de prevención de lesiones
2. `rehabilitation` - Programas de rehabilitación
3. `mobility_assessment` - Evaluación de movilidad
4. `sleep_optimization` - Optimización del sueño
5. `hrv_protocol` - Protocolos HRV
6. `chronic_pain` - Manejo del dolor crónico
7. `general_recovery` - Recuperación general
8. `posture_analysis` - Análisis de postura
9. `movement_analysis` - Análisis de movimiento
10. **5 Conversational Skills** - Recovery-focused conversations

#### From VOLT (Biometrics Insight Engine):
1. `biometric_analysis` - Análisis de datos biométricos
2. `pattern_recognition` - Reconocimiento de patrones
3. `trend_identification` - Identificación de tendencias
4. `data_visualization` - Visualización de datos
5. `biometric_image_analysis` - Análisis de imágenes biométricas
6. **5 Conversational Skills** - Analytics-focused conversations

### New Combined Skills Architecture
Total: **19 Skills** (9 WAVE + 5 VOLT + 5 new hybrid skills)

#### Hybrid Skills (New):
1. `recovery_analytics_fusion` - Combines recovery protocols with biometric data analysis
2. `performance_recovery_optimization` - Optimizes recovery based on performance metrics
3. `injury_prediction_analytics` - Predicts injury risk using biometric patterns
4. `holistic_wellness_dashboard` - Unified view of recovery + biometrics
5. `adaptive_recovery_protocol` - Recovery plans that adapt based on biometric feedback

### PersonalityAdapter Integration
- **PRIME**: "Strategic performance optimization through data-driven recovery analytics"
- **LONGEVITY**: "Holistic wellness through mindful recovery and gentle biometric insights"

### Directory Structure
```
agents/wave_performance_analytics/
├── __init__.py
├── agent.py                    # Main consolidated agent
├── schemas.py                  # All input/output schemas  
├── core/
│   ├── recovery_engine.py      # Recovery-focused logic
│   ├── analytics_engine.py     # Biometrics-focused logic
│   └── fusion_engine.py        # Hybrid capabilities
└── skills/
    ├── recovery_skills.py      # From WAVE
    ├── analytics_skills.py     # From VOLT  
    └── hybrid_skills.py        # New combined skills
```

## Implementation Steps

### Phase 1: Create New Directory Structure
1. Create `agents/wave_performance_analytics/`
2. Set up core modules and skills directories
3. Copy and adapt schemas from both agents

### Phase 2: Merge Agent Classes
1. Create new WAVEPerformanceAnalytics class
2. Integrate both skill sets
3. Combine PersonalityAdapter configurations
4. Merge conversation capabilities

### Phase 3: Skills Integration  
1. Copy recovery skills from WAVE
2. Copy analytics skills from VOLT
3. Create 5 new hybrid skills
4. Update skill handlers and schemas

### Phase 4: Testing & Validation
1. Test all skill functionality
2. Validate PersonalityAdapter works for both contexts
3. Test conversational capabilities
4. Verify A2A communication

### Phase 5: Update Routing
1. Update NEXUS orchestrator routing
2. Remove VOLT from active agent list
3. Update WAVE capabilities registration
4. Test end-to-end agent communication

## Benefits of Consolidation
- **Unified Experience**: Single agent for all recovery + analytics needs
- **Cross-domain Insights**: Recovery decisions informed by biometric data
- **Reduced Complexity**: 13 → 12 agents (step toward 9)
- **Enhanced Capabilities**: New hybrid skills not possible before
- **Improved UX**: Clear value proposition combining recovery wisdom + data science