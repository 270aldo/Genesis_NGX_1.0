# NGX Agents - Estándar de Documentación A+

## 🎯 **OBJETIVO: 95%+ DOCUMENTATION COVERAGE**

### 📊 **MÉTRICAS DE DOCUMENTACIÓN A+**
- **API Documentation**: 100% de métodos públicos documentados
- **Code Documentation**: 95% de funciones con docstrings
- **User Guides**: Guías completas para cada funcionalidad
- **Troubleshooting**: Soluciones para 90% de problemas comunes

## 📚 **ESTRUCTURA OBLIGATORIA DE DOCUMENTACIÓN**

```
docs/agents/{agent_name}/
├── README.md                       # Overview y quick start
├── architecture/
│   ├── overview.md                 # Arquitectura general
│   ├── skills_framework.md         # Framework de skills
│   ├── personality_system.md       # Sistema de personalidad
│   └── dependencies.md             # Dependencias y servicios
├── api_reference/
│   ├── agent_api.md               # API principal del agente
│   ├── skills_api.md              # APIs de skills
│   ├── schemas_api.md             # Esquemas de datos
│   └── exceptions_api.md          # Excepciones custom
├── user_guides/
│   ├── getting_started.md         # Guía de inicio
│   ├── basic_usage.md             # Uso básico
│   ├── advanced_features.md       # Características avanzadas
│   └── personalization.md         # Personalización PRIME/LONGEVITY
├── examples/
│   ├── basic_examples.md          # Ejemplos básicos
│   ├── advanced_workflows.md      # Workflows complejos
│   ├── integration_examples.md    # Ejemplos de integración
│   └── code_samples/              # Código de ejemplo
├── troubleshooting/
│   ├── common_issues.md           # Problemas comunes
│   ├── error_codes.md             # Códigos de error
│   ├── performance_tuning.md      # Optimización
│   └── debugging_guide.md         # Guía de debugging
├── deployment/
│   ├── installation.md            # Instalación
│   ├── configuration.md           # Configuración
│   ├── monitoring.md              # Monitoreo
│   └── security.md                # Configuración de seguridad
└── changelog/
    ├── CHANGELOG.md               # Historial de cambios
    ├── migration_guides.md        # Guías de migración
    └── breaking_changes.md        # Cambios importantes
```

## 📖 **README.MD OBLIGATORIO**

```markdown
# {Agent Name} - {Agent Description}

![Status](https://img.shields.io/badge/Status-A%2B%20Certified-green)
![Coverage](https://img.shields.io/badge/Coverage-85%25%2B-brightgreen)
![License](https://img.shields.io/badge/License-Proprietary-red)

## 🎯 Overview

The {Agent Name} is a specialized AI agent within the NGX Agents ecosystem that {brief_description}. It provides ultra-personalized responses adapted for NGX PRIME and NGX LONGEVITY programs.

### Key Features

- ⚡ **Ultra-Personalized Responses**: Adapts communication style based on user program (PRIME/LONGEVITY)
- 🧠 **Advanced AI Integration**: Powered by Google Gemini and Vertex AI
- 🛡️ **Enterprise Security**: GDPR/HIPAA compliant with audit logging
- 📊 **Comprehensive Analytics**: Performance monitoring and business metrics
- 🔄 **A2A Integration**: Seamless communication with other NGX agents
- 🎭 **Personality System**: {MBTI_TYPE} personality with domain expertise

### Performance Metrics

| Metric | Value | Benchmark |
|--------|-------|-----------|
| Response Time | < 500ms | ✅ A+ |
| Accuracy | > 95% | ✅ A+ |
| Test Coverage | > 85% | ✅ A+ |
| Error Rate | < 0.1% | ✅ A+ |

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- NGX Agents Core Platform
- Google Cloud credentials
- Redis instance

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configurations

# Initialize agent
python -m agents.{agent_name}.setup
```

### Basic Usage

```python
from agents.{agent_name} import {Agent}Agent
from agents.{agent_name}.core import AgentDependencies, {Agent}Config

# Initialize agent
dependencies = AgentDependencies(...)
config = {Agent}Config()
agent = {Agent}Agent(dependencies, config)

# Initialize
await agent.initialize()

# Process message
response = await agent.handle_message(
    "Your message here",
    context={"user_id": "user123", "program_type": "NGX_PRIME"}
)

print(response["content"])
```

## 🏗️ Architecture

### Core Components

- **Agent Core**: Main coordination and message handling
- **Skills Framework**: Modular skill system with {X} specialized skills
- **Personality System**: Ultra-personalized response adaptation
- **Integration Layer**: External service connections and APIs

### Skills Overview

| Skill | Description | Input | Output |
|-------|-------------|-------|--------|
| `{skill_1}` | {description} | {input_schema} | {output_schema} |
| `{skill_2}` | {description} | {input_schema} | {output_schema} |

[See full API reference →](api_reference/skills_api.md)

## 🎭 Personality Adaptation

The agent adapts its communication style based on the user's program:

### NGX PRIME
- **Style**: Strategic, direct, performance-focused
- **Vocabulary**: Executive language, ROI-oriented
- **Tone**: Professional, efficient, results-driven

### NGX LONGEVITY  
- **Style**: Nurturing, holistic, wellness-focused
- **Vocabulary**: Empathetic language, health-oriented
- **Tone**: Caring, supportive, balanced

[Learn more about personalization →](user_guides/personalization.md)

## 📊 Configuration

### Environment Variables

```bash
# Required
NGX_AGENT_{AGENT_ID}_GEMINI_API_KEY=your_api_key
NGX_AGENT_{AGENT_ID}_REDIS_URL=redis://localhost:6379

# Optional
NGX_AGENT_{AGENT_ID}_MAX_RESPONSE_TIME=30.0
NGX_AGENT_{AGENT_ID}_ENABLE_PERSONALITY=true
NGX_AGENT_{AGENT_ID}_LOG_LEVEL=INFO
```

### Configuration Options

```python
@dataclass
class {Agent}Config:
    max_response_time: float = 30.0
    retry_attempts: int = 3
    cache_ttl: int = 3600
    enable_personality_adaptation: bool = True
    # ... see full config reference
```

[See full configuration guide →](deployment/configuration.md)

## 🧪 Testing

```bash
# Run all tests
pytest tests/agents/{agent_name}/

# Run with coverage
pytest tests/agents/{agent_name}/ --cov=agents.{agent_name} --cov-report=html

# Performance tests
pytest tests/agents/{agent_name}/performance/ -m performance
```

## 📈 Monitoring

### Health Checks

```bash
# Agent health
curl http://localhost:8000/health/agents/{agent_name}

# Detailed metrics
curl http://localhost:8000/metrics/agents/{agent_name}
```

### Key Metrics

- Response time percentiles (p50, p95, p99)
- Error rates by skill and error type
- Personality adaptation success rates
- External service dependency health

[See full monitoring guide →](deployment/monitoring.md)

## 🔒 Security

### Data Protection

- **Encryption**: All sensitive data encrypted at rest and in transit
- **Audit Logging**: Comprehensive logging of all operations
- **Access Control**: Role-based permissions and rate limiting
- **Compliance**: GDPR/HIPAA compliant data handling

[See security guide →](deployment/security.md)

## 🤝 Contributing

1. Follow A+ coding standards
2. Maintain 85%+ test coverage
3. Update documentation for any changes
4. Follow conventional commit messages

## 📞 Support

- **Documentation**: [Full docs →](./architecture/overview.md)
- **Issues**: [Troubleshooting →](./troubleshooting/common_issues.md)
- **API Reference**: [API docs →](./api_reference/agent_api.md)

## 📝 License

Proprietary software. All rights reserved.

---

**Status**: A+ Certified | **Last Updated**: {date} | **Version**: {version}
```

## 📋 **API REFERENCE OBLIGATORIO**

```markdown
# {Agent Name} - API Reference

## Agent Class

### `{Agent}Agent`

Main agent class implementing the {domain} specialist.

#### Constructor

```python
def __init__(
    self, 
    dependencies: AgentDependencies, 
    config: {Agent}Config
) -> None
```

**Parameters:**
- `dependencies` (AgentDependencies): Injected dependencies including PersonalityAdapter, external clients
- `config` ({Agent}Config): Agent configuration settings

**Raises:**
- `{Agent}Error`: If initialization fails
- `ValidationError`: If dependencies or config are invalid

#### Methods

##### `async def initialize() -> None`

Initialize the agent and its components.

**Raises:**
- `{Agent}Error`: If initialization fails

**Example:**
```python
agent = {Agent}Agent(dependencies, config)
await agent.initialize()
```

##### `async def handle_message(message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`

Process an incoming message with full personality adaptation.

**Parameters:**
- `message` (str): User message to process
- `context` (Optional[Dict[str, Any]]): User and session context

**Returns:**
- `Dict[str, Any]`: Response with adapted content and metadata

**Response Schema:**
```python
{
    "success": bool,
    "content": str,
    "confidence_score": float,
    "processing_time_ms": int,
    "adaptation_metadata": {
        "program_type": str,
        "adaptation_applied": bool,
        "confidence_score": float
    },
    "skills_used": List[str],
    "timestamp": str
}
```

**Raises:**
- `{Agent}Error`: For agent-specific errors
- `ValidationError`: For invalid input

**Example:**
```python
response = await agent.handle_message(
    "Help me with {domain_specific_request}",
    context={
        "user_id": "user123",
        "program_type": "NGX_PRIME"
    }
)
```

## Skills API

### Core Skills

#### `{primary_skill_name}`

{Skill description and purpose}

**Input Schema:**
```python
class {Skill}Input(BaseModel):
    parameter1: str = Field(..., description="Parameter description")
    parameter2: Optional[int] = Field(None, description="Optional parameter")
```

**Output Schema:**
```python
class {Skill}Output(BaseModel):
    result: str = Field(..., description="Primary result")
    confidence: float = Field(..., ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

**Usage:**
```python
result = await agent.skills_manager.execute_skill(
    "{primary_skill_name}",
    {Skill}Input(parameter1="value"),
    context
)
```

## Exception Hierarchy

### `{Agent}Error`

Base exception for all agent errors.

**Attributes:**
- `message` (str): Error description
- `suggestions` (List[str]): Suggested solutions

### `{Agent}ValidationError`

Raised when input validation fails.

### `{Agent}ProcessingError`

Raised when core processing fails.

### `{Agent}ExternalServiceError`

Raised when external service integration fails.

**Example Error Handling:**
```python
try:
    response = await agent.handle_message(message, context)
except {Agent}ValidationError as e:
    # Handle validation errors
    logger.warning(f"Validation failed: {e}")
except {Agent}ExternalServiceError as e:
    # Handle service failures
    logger.error(f"External service error: {e}")
```
```

## 🎯 **DOCSTRING STANDARD OBLIGATORIO**

```python
async def handle_message(
    self, 
    message: str, 
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process incoming message with ultra-personalized response adaptation.
    
    This method coordinates the full message processing pipeline including
    intent analysis, skill execution, personality adaptation, and response
    formatting. It ensures responses are tailored to the user's program type
    (NGX PRIME vs NGX LONGEVITY) and personal preferences.
    
    Args:
        message: User's input message to process. Should be non-empty string
                containing the user's request or query.
        context: Optional context dictionary containing:
                - user_id (str): Unique user identifier
                - program_type (str): 'NGX_PRIME' or 'NGX_LONGEVITY'
                - user_profile (Dict): User demographics and preferences
                - session_context (Dict): Conversation history and state
    
    Returns:
        Dictionary containing the agent's response:
        - success (bool): Whether processing completed successfully
        - content (str): The adapted response content
        - confidence_score (float): Confidence in the response (0.0-1.0)
        - processing_time_ms (int): Processing time in milliseconds
        - adaptation_metadata (Dict): Personality adaptation details
        - skills_used (List[str]): Skills that were executed
        - timestamp (str): ISO timestamp of response generation
    
    Raises:
        {Agent}ValidationError: When message is empty or context is malformed
        {Agent}ProcessingError: When core processing logic fails
        {Agent}ExternalServiceError: When external service calls fail
    
    Example:
        >>> context = {
        ...     "user_id": "user123",
        ...     "program_type": "NGX_PRIME",
        ...     "user_profile": {"age": 30, "goals": ["strength"]}
        ... }
        >>> response = await agent.handle_message("Create a workout plan", context)
        >>> print(response["success"])  # True
        >>> print(response["content"])  # "Here's your strategic workout plan..."
    
    Note:
        - Response time target: < 500ms for simple queries
        - Personality adaptation is applied automatically based on program_type
        - All interactions are logged for audit and analytics purposes
        - Fallback responses are provided if external services fail
    """
```

## 📚 **USER GUIDES OBLIGATORIOS**

### **GETTING STARTED**

```markdown
# Getting Started with {Agent Name}

## What is {Agent Name}?

The {Agent Name} is your AI specialist for {domain}. It provides personalized guidance adapted to your specific program and goals.

## First Steps

### 1. Basic Interaction

Start with simple requests:

```
"Help me with {basic_request}"
```

The agent will automatically adapt its response based on your program type.

### 2. Understanding Program Types

**NGX PRIME Users:**
- Get strategic, performance-focused guidance
- Receive direct, efficient communication
- Access advanced optimization techniques

**NGX LONGEVITY Users:**
- Receive nurturing, holistic guidance  
- Get comprehensive, patient explanations
- Focus on sustainable, long-term approaches

### 3. Providing Context

For better personalization, include:
- Your current goals
- Experience level
- Specific preferences
- Any constraints or limitations

## Common Use Cases

### Use Case 1: {Primary Use Case}
**Request:** "{example_request_1}"
**Response:** The agent will provide {expected_response_type}

### Use Case 2: {Secondary Use Case}
**Request:** "{example_request_2}"
**Response:** You'll receive {expected_response_type}

## Tips for Best Results

1. **Be Specific**: More detailed requests get more personalized responses
2. **Provide Context**: Mention your program type if it's not detected
3. **Ask Follow-ups**: The agent maintains conversation context
4. **Use Natural Language**: Speak naturally, the agent understands

## Next Steps

- [Advanced Features →](advanced_features.md)
- [Personalization Guide →](personalization.md)
- [API Documentation →](../api_reference/agent_api.md)
```

## ✅ **CHECKLIST DE DOCUMENTACIÓN A+**

### **Documentación Obligatoria:**
- [ ] **README.md completo** con quick start y overview
- [ ] **API Reference completa** con todos los métodos públicos
- [ ] **User Guide básico** con ejemplos prácticos
- [ ] **Architecture Overview** con diagramas
- [ ] **Configuration Guide** con todas las opciones
- [ ] **Troubleshooting Guide** con problemas comunes
- [ ] **Installation Guide** paso a paso
- [ ] **Security Documentation** para datos sensibles
- [ ] **Performance Benchmarks** documentados
- [ ] **Changelog** con historial de versiones

### **Calidad de Documentación:**
- [ ] **100% de métodos públicos** documentados
- [ ] **95% de funciones** con docstrings completos
- [ ] **Ejemplos de código** funcionando y actualizados
- [ ] **Diagramas de arquitectura** claros y precisos
- [ ] **Enlaces internos** funcionando correctamente
- [ ] **Formato consistente** en todo el proyecto
- [ ] **Lenguaje claro y técnico** apropiado
- [ ] **Actualizaciones automáticas** de métricas y badges

### **Métricas de Calidad:**
- [ ] **Tiempo de comprensión** < 30 minutos para nuevos desarrolladores
- [ ] **Completitud de ejemplos** 100% de features cubiertas
- [ ] **Precisión técnica** 100% de información correcta
- [ ] **Mantenimiento** documentación actualizada en cada release