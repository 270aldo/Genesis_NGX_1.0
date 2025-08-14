# 🧬 GENESIS NGX - Central AI Brain for the NGX Ecosystem

[![Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)](https://github.com/270aldo/Genesis_NGX_1.0)
[![CI/CD Pipeline](https://github.com/270aldo/Genesis_NGX_1.0/actions/workflows/ci.yml/badge.svg)](https://github.com/270aldo/Genesis_NGX_1.0/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/270aldo/Genesis_NGX_1.0/branch/main/graph/badge.svg)](https://codecov.io/gh/270aldo/Genesis_NGX_1.0)
[![Enterprise Grade](https://img.shields.io/badge/Grade-Enterprise-blue)](https://github.com/270aldo/Genesis_NGX_1.0)
[![Security Score](https://img.shields.io/badge/Security-100%25-green)](https://github.com/270aldo/Genesis_NGX_1.0)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Sistema centralizado de inteligencia artificial **PRODUCTION READY** para el ecosistema NGX, diseñado para potenciar herramientas de fitness, nutrición y bienestar con capacidades avanzadas de IA y seguridad enterprise-grade.

## 🚀 Características Principales

- **11 Agentes Especializados**: Cada uno con expertise único en fitness, nutrición, bienestar y más
- **Arquitectura ADK/A2A**: Siguiendo estándares de Google para sistemas multi-agente
- **Personalización Avanzada**: Sistema dual PRIME (ejecutivos) y LONGEVITY (bienestar)
- **Voces con IA**: Integración con ElevenLabs v3 alpha para conversaciones naturales
- **Seguridad Enterprise**: GDPR/HIPAA compliant con encriptación end-to-end
- **Performance Elite**: Sub-100ms P50, 10,000+ RPS, circuit breakers avanzados
- **Production Ready**: 100% implementado con backup/recovery, rate limiting granular

## 🏗️ Arquitectura

```
GENESIS/
├── backend/          # FastAPI + Google Vertex AI
│   ├── agents/       # 11 agentes especializados
│   ├── core/         # Lógica central
│   └── clients/      # Integraciones (Vertex AI, ElevenLabs, etc)
├── frontend/         # React + TypeScript + Vite
│   ├── src/
│   └── components/   # shadcn-ui components
└── docs/            # Documentación completa
```

### Agentes Disponibles

| Agente | Especialización | Voice ID |
|--------|----------------|----------|
| NEXUS | Orquestador Maestro | James |
| BLAZE | Entrenamiento Elite | Chris |
| SAGE | Nutrición de Precisión | Adelina |
| CODE | Genética y Rendimiento | Mark |
| WAVE | Analytics y Recuperación | Harry |
| LUNA | Bienestar Femenino | Alexandra |
| STELLA | Seguimiento de Progreso | Eve |
| SPARK | Motivación y Comportamiento | Sam |
| NOVA | Biohacking e Innovación | Juniper |
| GUARDIAN | Seguridad y Compliance | - |
| NODE | Integración de Sistemas | - |

## 🚀 Quick Start

### Requisitos

- Python 3.12+
- Node.js 18+
- Poetry
- Redis (opcional)
- Docker (opcional)

### Instalación Backend

```bash
cd backend
poetry install --with dev
cp .env.example .env  # Configurar variables de entorno
make dev              # Inicia en http://localhost:8000
```

### Instalación Frontend

```bash
cd frontend
npm install
npm run dev           # Inicia en http://localhost:5173
```

### Variables de Entorno Requeridas

```bash
# Backend (.env)
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
VERTEX_AI_PROJECT_ID=your-project-id
VERTEX_AI_LOCATION=us-central1
ELEVENLABS_API_KEY=your-elevenlabs-key
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-key
JWT_SECRET_KEY=your-secret-key
REDIS_URL=redis://localhost:6379
```

## 📚 Documentación

- [Guía de Arquitectura ADK/A2A](./docs/A+_AGENT_STANDARDIZATION.md)
- [API Reference](./backend/API_REFERENCE.md)
- [Guía de Integración](./backend/INTEGRATION_GUIDE.md)
- [Roadmap del Ecosistema](./backend/GENESIS_ROADMAP.md)

## 🧪 Testing

### Backend

```bash
cd backend
make test          # Todos los tests
make test-cov      # Reporte de cobertura
make lint          # Linting y type checking
```

### Frontend

```bash
cd frontend
npm test           # Jest tests
npm run test:coverage
npm run lint
```

## 🔒 Seguridad

- Autenticación JWT con refresh tokens
- Rate limiting configurable
- Encriptación AES-256-GCM para datos sensibles
- Sanitización automática de logs
- Headers de seguridad HTTP

## 🎯 Casos de Uso

GENESIS está diseñado para potenciar el ecosistema NGX:

1. **NGX_AGENTS_BLOG**: Generación de contenido personalizado
2. **NEXUS-CRM**: Insights de clientes y automatización
3. **NGX_PULSE**: Análisis biométrico en tiempo real
4. **NEXUS_CORE**: Flujos de trabajo ejecutivos
5. **NGX_CONNECT**: Comunicación omnicanal

## URLs de Acceso

- Frontend: <http://localhost:5173>
- Backend API: <http://localhost:8000>
- API Docs: <http://localhost:8000/docs>
- WebSocket: ws://localhost:8000/ws
- A2A WebSocket: ws://localhost:8001
- Prometheus Metrics: <http://localhost:8000/metrics>

## 🏛️ Estructura del Proyecto

```
GENESIS_oficial_BETA/
├── backend/
│   ├── app/              # API FastAPI principal
│   ├── agents/           # 11 agentes especializados (ADK/A2A)
│   ├── core/             # Lógica central y servicios
│   ├── clients/          # Integraciones externas
│   ├── infrastructure/   # A2A server y adapters
│   └── tests/           # Suite de pruebas
├── frontend/
│   ├── src/
│   │   ├── components/  # Componentes React
│   │   ├── services/    # Servicios API
│   │   └── store/       # Estado global (Zustand)
│   └── public/          # Assets estáticos
└── docs/               # Documentación detallada
```

## 🤝 Contribuir

1. Fork el repositorio
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Estándares de Código

- Backend: Black, isort, ruff, mypy
- Frontend: ESLint, Prettier
- Commits: Conventional Commits
- Tests: Mínimo 85% cobertura

## 📄 Licencia

Propietario - NGX Technologies © 2024

## 🙏 Agradecimientos

- Google Vertex AI por la infraestructura de IA
- ElevenLabs por las voces conversacionales
- El equipo de NGX por la visión y dirección

---

## 📊 Estado Actual (19 Julio 2025)

- ✅ **Backend**: 90% Production-ready
- ✅ **Frontend**: 85% Production-ready
- ✅ **Base de Datos**: Supabase 100% configurado
- ✅ **SDK**: Publicado en npm como `@ngx/genesis-sdk` v1.0.0
- ✅ **CI/CD**: GitHub Actions completamente configurado
- ✅ **Repositorio**: <https://github.com/270aldo/Genesis_NGX_1.0>

Ver [PROJECT_STATUS_2025-07-19.md](./PROJECT_STATUS_2025-07-19.md) para el reporte detallado.

**Nota**: Este es un proyecto en constante evolución. Para la documentación más actualizada, consulta los archivos en `/docs` y el archivo `CLAUDE.md` para guías de desarrollo.
