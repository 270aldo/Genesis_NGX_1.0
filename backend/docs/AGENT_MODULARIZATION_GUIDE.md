# Agent Modularization Guide
## Transforming Monolithic Agents into Modular Architecture

### 🎯 Objective
Reduce agent files from 1,900-3,800 lines to manageable 300-500 line modules.

### 📁 New Structure

```
agents/
└── agent_name/
    ├── __init__.py           # Public exports
    ├── agent.py              # Main agent class (300 lines max)
    ├── config.py             # Agent-specific configuration
    ├── prompts/              # Prompt management
    │   ├── __init__.py
    │   ├── base_prompt.py
    │   └── examples.py
    ├── skills/               # Individual skills
    │   ├── __init__.py
    │   ├── skill_1.py
    │   └── skill_2.py
    ├── services/             # Data/Security/Integration services
    │   ├── __init__.py
    │   ├── data_service.py
    │   └── security_service.py
    └── models/               # Pydantic models
        ├── __init__.py
        ├── requests.py
        └── responses.py
```

### 🔧 Refactoring Strategy

#### 1. Extract Configuration (config.py)
```python
# Before: In agent.py (100+ lines)
class EliteTrainingStrategist(ADKAgent):
    def __init__(self):
        self.config = {
            "model": "gemini-1.5-flash",
            "temperature": 0.7,
            "max_tokens": 8192,
            # ... 50+ config lines
        }

# After: config.py (50 lines)
from dataclasses import dataclass

@dataclass
class BlazeConfig:
    model: str = "gemini-1.5-flash"
    temperature: float = 0.7
    max_tokens: int = 8192
    # ... organized configuration

# In agent.py (5 lines)
from .config import BlazeConfig

class EliteTrainingStrategist(ADKAgent):
    def __init__(self):
        self.config = BlazeConfig()
```

#### 2. Extract Skills (skills/)
```python
# Before: In agent.py (500+ lines per skill)
class EliteTrainingStrategist(ADKAgent):
    async def analyze_performance(self, data):
        # 200 lines of performance analysis
        
    async def generate_workout(self, params):
        # 300 lines of workout generation

# After: skills/performance_analysis.py
from agents.shared.skills.base_skill import BaseSkill

class PerformanceAnalysisSkill(BaseSkill):
    async def execute(self, data):
        # Focused 200 lines

# After: skills/workout_generation.py  
class WorkoutGenerationSkill(BaseSkill):
    async def execute(self, params):
        # Focused 300 lines

# In agent.py
from .skills import PerformanceAnalysisSkill, WorkoutGenerationSkill

class EliteTrainingStrategist(ADKAgent):
    def __init__(self):
        self.skills = {
            "performance": PerformanceAnalysisSkill(),
            "workout": WorkoutGenerationSkill()
        }
```

#### 3. Extract Prompts (prompts/)
```python
# Before: In agent.py (300+ lines)
SYSTEM_PROMPT = """
[300 lines of prompt]
"""

# After: prompts/base_prompt.py
class BlazePrompts:
    SYSTEM = """..."""
    EXAMPLES = [...]
    
# In agent.py
from .prompts import BlazePrompts
```

#### 4. Extract Models (models/)
```python
# Before: Scattered throughout agent.py
def process_request(self, data: Dict[str, Any]):
    # Implicit validation

# After: models/requests.py
from pydantic import BaseModel

class WorkoutRequest(BaseModel):
    user_id: str
    fitness_level: str
    goals: List[str]
    
# In agent.py
from .models import WorkoutRequest

def process_request(self, request: WorkoutRequest):
    # Type-safe processing
```

### 📊 Expected Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Main file lines | 3,000+ | 300 | -90% |
| Total lines | 3,000 | 3,000 | Same (but organized) |
| Files per agent | 1 | 15-20 | Modular |
| Test coverage | Hard | Easy | +50% easier |
| Maintenance | 😰 | 😊 | 10x better |

### 🚀 Migration Example

```bash
# Run modularization script
python scripts/modularize_agent.py agents/elite_training_strategist/

# Output:
✓ Extracted 5 skills (1,500 lines)
✓ Extracted configuration (100 lines)  
✓ Extracted prompts (300 lines)
✓ Extracted models (200 lines)
✓ Main agent.py reduced to 298 lines
```

### ✅ Benefits

1. **Easier Testing**: Test individual skills in isolation
2. **Better Reusability**: Share skills between agents
3. **Faster Development**: Find code quickly
4. **Reduced Conflicts**: Multiple devs can work on different modules
5. **Type Safety**: Pydantic models catch errors early

### 🔄 Rollback Plan

If modularization causes issues:
1. Original files are preserved as `agent_original.py`
2. Run `python scripts/restore_agent.py agent_name`
3. All imports automatically revert