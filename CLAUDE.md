# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚀 Plan Maestro de Optimización GENESIS - Estado Actual

### ✅ Fase 1 Completada (Tareas Críticas)
- [x] Eliminados 3 archivos CLAUDE.md duplicados
- [x] Eliminado directorio /backend/kubernetes/ duplicado
- [x] Movidos archivos de test de /scripts a /tests
- [x] Eliminados scripts de limpieza redundantes
- [x] Consolidado settings.py (solo en /core)
- [x] Implementado rate limiting en autenticación (slowapi)
- [x] Corregidos 33 bare excepts en 19 archivos
- [x] Agregados headers de seguridad HTTP

### ✅ Fase 2 Completada (Mejoras Importantes)
- [x] Migrar a SDK oficial de Google ADK (pendiente disponibilidad)
- [x] Implementar endpoints estándar A2A
- [x] Eliminar cliente Gemini duplicado
- [x] Mejorar prompts con seguridad explícita
- [x] Configurar testing en frontend (Jest + RTL)
- [ ] Implementar streaming real con SSE

### 📋 Fase 3 Pendiente (Optimizaciones)
- [ ] Refactorizar main.py (600+ líneas)
- [ ] Implementar lazy loading en frontend
- [ ] Configurar code splitting
- [ ] Agregar paginación en endpoints
- [ ] Optimizar queries con índices
- [ ] Configurar CDN para assets

## Project Overview

NGX Agents - A multi-agent AI system for fitness and nutrition combining:
- **Backend**: FastAPI with 11 specialized AI agents using Google Vertex AI
- **Frontend**: React/TypeScript with Vite and shadcn-ui

## Essential Commands

### Backend Development
```bash
# Setup and run
cd backend
poetry install --with dev
make dev  # Runs on port 8000

# Testing
make test           # Run all tests
make test-unit      # Unit tests only
make test-agents    # Agent tests only
make test-cov       # Generate coverage report (target: 85%+)

# Code quality
make lint           # Run ruff and mypy
make format         # Auto-format with black and isort
make check          # Run all checks before committing
```

### Frontend Development
```bash
# Setup and run
cd frontend
npm install
npm run dev         # Runs on port 5173

# Testing
npm test            # Run Jest tests
npm run test:watch  # Watch mode
npm run test:coverage # Coverage report

# Build and quality
npm run build       # Production build
npm run lint        # ESLint checking
npm run preview     # Preview production build
```

## Architecture Overview

### Backend Architecture
The backend uses an **Agent-to-Agent (A2A)** communication pattern where:
- Each agent inherits from `BaseAgent` and follows A+ standardization
- Agents communicate through the A2A server (`infrastructure/a2a_server.py`)
- The Orchestrator agent (`agents/orchestrator.py`) coordinates all agent interactions
- All agents use async/await patterns and are designed for streaming responses

### Key Agent Responsibilities
- **Orchestrator**: Routes requests and coordinates multi-agent workflows
- **Training/Nutrition**: Generate personalized plans using Vertex AI
- **Progress Tracker**: Monitors user metrics and integrates with wearables
- **Guardian**: Handles security, compliance, and audit logging
- **Node**: System integration and external API management

### Frontend Architecture
- **State Management**: Zustand stores in `/src/store/`
- **API Layer**: TanStack Query with services in `/src/services/`
- **Components**: shadcn-ui components with Tailwind CSS
- **Forms**: React Hook Form + Zod for validation

## Development Guidelines

### When Adding New Features
1. **Backend**: Follow the A+ agent pattern in `/docs/A+_AGENT_STANDARDIZATION.md`
2. **Frontend**: Use existing component patterns from `/src/components/`
3. **Testing**: Maintain 85%+ coverage, use appropriate test markers
4. **Documentation**: Update relevant docs following A+ standards

### API Development
- All endpoints go in `/app/routers/`
- Use FastAPI dependency injection for auth/services
- Support streaming responses where applicable
- Follow OpenAPI documentation standards

### Working with AI Agents
- Agent prompts are in `/agents/{agent_name}/{agent_name}_prompt.py`
- Use the personality system (PRIME vs LONGEVITY) when applicable
- Implement proper error handling and circuit breakers
- Always test agent responses with unit and integration tests

### Database and External Services
- **Supabase**: Primary database (PostgreSQL)
- **Redis**: Caching layer for performance
- **Vertex AI**: Primary LLM provider
- **External APIs**: Wearables integration through Node agent

## Common Tasks

### Adding a New Agent
1. Create agent class in `/agents/new_agent/`
2. Inherit from `BaseAgent` and implement required methods
3. Register in A2A server configuration
4. Add router endpoints if needed
5. Write comprehensive tests (unit + integration)

### Modifying Frontend Components
1. Check existing patterns in `/src/components/ui/`
2. Use Tailwind classes and follow shadcn-ui conventions
3. Add TypeScript types in component files
4. Update Zustand store if state management needed

### Running Specific Tests
```bash
# Backend
pytest tests/unit/test_specific.py::test_function_name
pytest -m agents  # Run only agent tests
pytest -k "orchestrator"  # Run tests matching pattern

# Frontend
npm test -- --testNamePattern="Component"
```

## Important Configuration Files
- **Backend**: `pyproject.toml`, `Makefile`, `.env`
- **Frontend**: `vite.config.ts`, `tailwind.config.ts`, `tsconfig.json`
- **Docker**: `Dockerfile` (multi-stage), `docker-compose.yml`
- **CI/CD**: `.github/workflows/` (when implemented)

## Performance Considerations
- Use Redis caching for expensive operations
- Implement streaming for long-running agent responses
- Use connection pooling for database queries
- Monitor with Prometheus metrics at `/metrics`

## Security Notes
- JWT tokens handled by `core/auth.py` (migrating to Supabase Auth)
- All sensitive config in environment variables
- GDPR/HIPAA compliance features in Guardian agent
- Never commit `.env` files or expose API keys