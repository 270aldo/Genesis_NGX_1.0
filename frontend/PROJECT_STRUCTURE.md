# NGX Agents - Estructura Completa del Proyecto

## 📁 Mapeo de Directorios del Escritorio

### Proyectos Principales
```
/Users/aldoolivas/Desktop/
├── 📂 nexus-chat-frontend/                    # ✅ PROYECTO OFICIAL ACTUAL
│   ├── src/                                   # Frontend React + TypeScript
│   ├── CLAUDE.md                              # Documentación técnica completa
│   ├── PROJECT_STRUCTURE.md                   # Este archivo
│   └── package.json                           # Dependencias y scripts
│
├── 📂 GENESIS-NGX-Agents/                     # ✅ BACKEND OFICIAL
│   ├── backend/                               # FastAPI + Python
│   ├── README.md                              # Documentación backend
│   └── docker-compose.yml                     # Configuración Docker
│
├── 📂 Copia de ngx-agents/                    # 📦 BACKUP LEGACY
│   ├── agents/                                # Versión anterior de agentes
│   ├── claude.md                              # Documentación legacy
│   └── requirements.txt                       # Dependencias Python legacy
│
└── 📂 NGXBRAIN/                               # 📋 DOCUMENTACIÓN & BRANDING
    ├── *.pdf                                  # Documentos estratégicos
    ├── AGENTES NGX.pdf                        # Especificaciones agentes
    └── ARQUITECTURA DE CONOCIMIENTO NGX.pdf   # Arquitectura del sistema
```

### Status de Proyectos

#### ✅ ACTIVOS
1. **nexus-chat-frontend** - Frontend oficial con Hybrid Intelligence Engine
2. **GENESIS-NGX-Agents** - Backend FastAPI con 11 agentes consolidados

#### 📦 BACKUPS/LEGACY (No eliminar)
1. **Copia de ngx-agents** - Backup de desarrollo anterior
2. **ngx-agents.zip** - Archivo comprimido de versión anterior
3. **Copia de ngx-agents01.zip** - Backup adicional

#### 📋 DOCUMENTACIÓN
1. **NGXBRAIN** - Centro de conocimiento y branding
2. **Marketing PDFS** - Recursos de marketing
3. **Audios ElevenLabs** - Samples de voz de agentes

## 🏗️ Arquitectura de Desarrollo

### Frontend Oficial: nexus-chat-frontend
```
nexus-chat-frontend/
├── 🎯 CORE INNOVATION
│   ├── src/components/hybridIntelligence/      # Hybrid Intelligence Engine
│   ├── src/services/api/hybridIntelligence.service.ts
│   ├── src/store/hybridIntelligenceStore.ts
│   └── src/hooks/useHybridIntelligencePersonalization.ts
│
├── 🤖 AGENT SYSTEM
│   ├── src/components/agents/                  # Componentes personalizados
│   ├── src/services/api/agents.service.ts      # API agentes
│   └── src/store/agentsStore.ts                # Estado agentes
│
├── 💬 CHAT SYSTEM
│   ├── src/components/chat/                    # Interfaz chat personalizada
│   ├── src/services/websocket/a2a.service.ts  # Agent-to-Agent WebSocket
│   └── src/store/chatStore.ts                  # Estado conversaciones
│
├── 🔐 AUTH SYSTEM
│   ├── src/components/auth/                    # Autenticación migrada
│   ├── src/services/api/auth.service.ts        # Servicios auth
│   └── src/store/authStore.ts                  # Estado usuario
│
├── 🎤 VOICE INTEGRATION
│   ├── src/components/agents/VoiceEnergyBall.tsx
│   ├── src/services/api/voice.service.ts       # ElevenLabs 2.0
│   └── src/hooks/useVoice.ts                   # Hook voz
│
├── 📊 BIOMETRIC SYSTEM
│   ├── src/services/websocket/biometricUpdates.service.ts
│   ├── src/components/hybridIntelligence/BiometricDataInput.tsx
│   └── src/hooks/useBiometricUpdates.ts
│
├── 🧠 LEARNING SYSTEM
│   ├── src/components/feedback/LearningFeedbackSystem.tsx
│   └── src/services/api/hybridIntelligence.service.ts
│
└── 🧪 TESTING
    ├── src/components/hybridIntelligence/__tests__/
    └── vitest.config.ts
```

### Backend: GENESIS-NGX-Agents
```
GENESIS-NGX-Agents/backend/
├── 🤖 AGENTS (11 total)
│   ├── 👁️ Visibles (9): BLAZE, NOVA, SAGE, WAVE, LUNA, VOX, ECHO, ZEN, APEX
│   └── 🔒 Backend (2): GUARDIAN, NODE
│
├── 🧠 HYBRID INTELLIGENCE
│   ├── hybrid_intelligence/                    # Motor IA 2-capas
│   ├── personality_adapters/                   # Adaptadores PRIME/LONGEVITY
│   └── biometric_integration/                  # Modulación fisiológica
│
├── 🌐 API ENDPOINTS
│   ├── FastAPI application
│   ├── WebSocket A2A (puerto 9000)
│   └── WebSocket Biometric (puerto 9000)
│
├── 🔊 VOICE INTEGRATION
│   ├── elevenlabs_integration/
│   └── voice_activity_detection/
│
└── 🗄️ DATA PERSISTENCE
    ├── Supabase integration
    ├── Redis caching
    └── Embeddings management
```

## 🔄 Flujo de Migración Completado

### 1. Análisis Inicial ✅
- **Origen**: Múltiples versiones de ngx-agents
- **Destino**: nexus-chat-frontend como frontend oficial
- **Backend**: GENESIS-NGX-Agents mantenido

### 2. Migración de Servicios ✅
```bash
# ORIGEN → DESTINO
GENESIS-NGX-Agents/backend/auth/ → nexus-chat-frontend/src/services/api/auth.service.ts
GENESIS-NGX-Agents/backend/agents/ → nexus-chat-frontend/src/services/api/agents.service.ts
GENESIS-NGX-Agents/backend/chat/ → nexus-chat-frontend/src/services/api/chat.service.ts
GENESIS-NGX-Agents/backend/voice/ → nexus-chat-frontend/src/services/api/voice.service.ts
```

### 3. Consolidación de Agentes ✅
```bash
# ANTES: 13 agentes dispersos
# DESPUÉS: 11 agentes consolidados
BLAZE + NOVA + SAGE + WAVE + LUNA + VOX + ECHO + ZEN + APEX (9 visibles)
GUARDIAN + NODE (2 backend)
```

### 4. Implementación Hybrid Intelligence ✅
```bash
# NUEVA IMPLEMENTACIÓN (Core Innovation)
hybridIntelligenceService.ts      # Servicio principal IA
hybridIntelligenceStore.ts        # Estado global Zustand
useHybridIntelligencePersonalization.ts  # Hook React
HybridIntelligenceDashboard.tsx   # Dashboard principal
ArchetypeAssessment.tsx           # Evaluación PRIME/LONGEVITY
BiometricDataInput.tsx            # Entrada datos fisiológicos
```

## 🚀 Estado de Implementación

### ✅ COMPLETADO (100%)
1. **Migración Frontend-Backend** - Servicios API integrados
2. **Hybrid Intelligence Engine** - Sistema 2-capas funcional
3. **Personalización en Tiempo Real** - Hook y componentes
4. **Sistema de Agentes** - 11 agentes consolidados
5. **Integración de Voz** - ElevenLabs 2.0 con VAD
6. **WebSocket Real-time** - A2A y biométricos
7. **Sistema de Aprendizaje** - Feedback continuo
8. **Testing** - Tests de integración

### 📋 PENDIENTE
1. **Testing Exhaustivo** - Pruebas del sistema completo
2. **Optimización Performance** - Optimizaciones finales
3. **Deployment Producción** - Configuración productiva

## 🔧 Comandos de Gestión

### Frontend (nexus-chat-frontend)
```bash
cd /Users/aldoolivas/Desktop/nexus-chat-frontend
npm install                    # Instalar dependencias
npm run dev                    # Desarrollo local
npm run build                  # Build producción
npm run test                   # Ejecutar tests
npm run lint                   # Linting código
npm run type-check            # Verificar tipos TypeScript
```

### Backend (GENESIS-NGX-Agents)
```bash
cd /Users/aldoolivas/Desktop/GENESIS-NGX-Agents/backend
python -m venv venv           # Crear entorno virtual
source venv/bin/activate      # Activar entorno
pip install -r requirements.txt  # Instalar dependencias
uvicorn app.main:app --reload --port 8000  # Servidor desarrollo
```

### Docker (Sistema Completo)
```bash
cd /Users/aldoolivas/Desktop/GENESIS-NGX-Agents
docker-compose up -d          # Levantar todos los servicios
docker-compose logs -f        # Ver logs en tiempo real
docker-compose down           # Detener servicios
```

## 📊 Métricas del Proyecto

### Frontend
- **Líneas de código**: ~15,000
- **Componentes**: 45+
- **Servicios**: 8
- **Stores**: 4
- **Tests**: 25+ casos

### Backend
- **Agentes activos**: 11
- **Endpoints API**: 50+
- **WebSocket connections**: 2
- **Modelos IA integrados**: 4

### Innovación Core
- **Hybrid Intelligence Engine**: 2-layer personalization
- **Archetype System**: PRIME vs LONGEVITY
- **Real-time Modulation**: Biometric-based adaptation
- **Learning Loop**: Continuous improvement

## 🔒 Backups y Seguridad

### Archivos de Respaldo Mantenidos
```bash
# NUNCA ELIMINAR - Son backups de desarrollo
/Users/aldoolivas/Desktop/Copia de ngx-agents/
/Users/aldoolivas/Desktop/ngx-agents.zip
/Users/aldoolivas/Desktop/agentes-ngx-modificado.zip
/Users/aldoolivas/Desktop/nexus-core2.zip
```

### Documentación Preservada
```bash
# Centro de conocimiento del proyecto
/Users/aldoolivas/Desktop/NGXBRAIN/
/Users/aldoolivas/Desktop/Marketing PDFS/
/Users/aldoolivas/Desktop/Audios ElevenLabs/
```

## 🎯 Próximos Pasos

1. **Phase Testing**: Pruebas exhaustivas del Hybrid Intelligence Engine
2. **Performance Optimization**: Optimización de componentes críticos
3. **Production Deployment**: Setup para entorno productivo
4. **Device Integration**: Conexión con dispositivos biométricos reales
5. **Analytics & Monitoring**: Implementación de métricas avanzadas

---

**✨ NOTA**: Este documento mapea la estructura completa del proyecto NGX Agents después de la migración exitosa a nexus-chat-frontend como frontend oficial. El **Hybrid Intelligence Engine** implementado representa la verdadera diferenciación competitiva del sistema.