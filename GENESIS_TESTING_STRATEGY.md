# 🧪 GENESIS TESTING STRATEGY

## From 40% to 85%+ Coverage with Elite Testing Practices

> **Goal**: Implement comprehensive testing that ensures reliability, catches bugs early, and enables confident deployments.

## 📊 Current State vs Target

### Current Testing Coverage

- **Backend**: ~40% (mostly unit tests)
- **Frontend**: ~30% (basic component tests)
- **E2E**: 0% (not implemented)
- **Integration**: Limited
- **Performance**: None

### Target Testing Matrix

- **Backend**: 85%+ (unit + integration)
- **Frontend**: 80%+ (unit + integration + visual)
- **E2E**: Critical user paths covered
- **Integration**: All agent communications
- **Performance**: Load + stress testing

---

## 🏗️ TESTING INFRASTRUCTURE SETUP

### Backend Testing Stack

```bash
# Core Testing Tools
pytest==8.3.4          # Test framework
pytest-asyncio==0.25.0 # Async support
pytest-cov==6.0.0      # Coverage reporting
pytest-mock==3.14.0    # Mocking support
pytest-xdist==3.6.1    # Parallel execution
factory-boy==3.3.1     # Test data factories
faker==33.1.0          # Fake data generation

# API Testing
httpx==0.28.1          # Async HTTP client
pytest-httpx==0.35.0   # HTTPX fixtures

# Database Testing
pytest-postgresql==6.1.1  # Postgres fixtures
sqlalchemy-utils==0.42.0  # DB utilities
```

### Frontend Testing Stack

```json
{
  "devDependencies": {
    "@testing-library/react": "^16.1.0",
    "@testing-library/jest-dom": "^6.6.4",
    "@testing-library/user-event": "^14.6.0",
    "@vitest/ui": "^2.2.0",
    "@playwright/test": "^1.50.0",
    "msw": "^2.7.0",
    "jest-axe": "^9.0.0",
    "@storybook/react": "^8.5.0"
  }
}
```

---

## 🎯 TESTING PYRAMID IMPLEMENTATION

### Level 1: Unit Tests (Foundation)

#### Backend Unit Tests Structure

```python
# tests/unit/agents/test_orchestrator.py
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_vertex_client():
    """Mock Vertex AI client for testing"""
    with patch('agents.orchestrator.vertex_ai_client') as mock:
        mock.generate_content = AsyncMock()
        yield mock

@pytest.mark.asyncio
async def test_orchestrator_routes_to_correct_agent(mock_vertex_client):
    """Test that orchestrator correctly identifies and routes requests"""
    # Arrange
    orchestrator = OrchestratorAgent()
    user_input = "I need a workout plan"

    # Act
    result = await orchestrator.process(user_input)

    # Assert
    assert result.agent == "elite_training_strategist"
    assert result.confidence > 0.8
```

#### Frontend Unit Tests Structure

```typescript
// src/components/chat/__tests__/ChatMessage.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatMessage } from '../ChatMessage';

describe('ChatMessage Component', () => {
  it('should render message content correctly', () => {
    const message = {
      id: '1',
      content: 'Test message',
      role: 'user',
      timestamp: new Date()
    };

    render(<ChatMessage message={message} />);

    expect(screen.getByText('Test message')).toBeInTheDocument();
    expect(screen.getByRole('article')).toHaveAttribute('aria-label', 'User message');
  });

  it('should handle edit action when user owns message', async () => {
    const onEdit = jest.fn();
    const user = userEvent.setup();

    render(<ChatMessage message={message} onEdit={onEdit} canEdit />);

    await user.click(screen.getByRole('button', { name: 'Edit message' }));

    expect(onEdit).toHaveBeenCalledWith(message.id);
  });
});
```

### Level 2: Integration Tests

#### Backend Integration Tests

```python
# tests/integration/test_agent_communication.py
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_agent_workflow(
    test_client: TestClient,
    test_db: AsyncSession,
    mock_redis: Redis
):
    """Test complete workflow from API to agent response"""
    # Create test user
    user = await create_test_user(test_db)
    token = generate_test_token(user)

    # Send request
    response = await test_client.post(
        "/api/v1/chat/message",
        json={"content": "Create a nutrition plan for muscle gain"},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "precision_nutrition_architect"
    assert "nutrition_plan" in data["response"]

    # Verify database state
    messages = await get_user_messages(test_db, user.id)
    assert len(messages) == 2  # User message + agent response

    # Verify cache
    cached = await mock_redis.get(f"user:{user.id}:last_response")
    assert cached is not None
```

#### Frontend Integration Tests

```typescript
// src/services/__tests__/api.integration.test.tsx
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useChatMessages } from '../hooks/useChatMessages';
import { server } from '../mocks/server';
import { rest } from 'msw';

describe('Chat API Integration', () => {
  it('should fetch and update messages in real-time', async () => {
    const wrapper = ({ children }) => (
      <QueryClientProvider client={new QueryClient()}>
        {children}
      </QueryClientProvider>
    );

    const { result } = renderHook(() => useChatMessages(), { wrapper });

    // Wait for initial load
    await waitFor(() => {
      expect(result.current.messages).toHaveLength(5);
    });

    // Simulate new message
    server.use(
      rest.post('/api/v1/chat/message', (req, res, ctx) => {
        return res(ctx.json({ id: '6', content: 'New message' }));
      })
    );

    // Send message
    await result.current.sendMessage('Test message');

    // Verify update
    await waitFor(() => {
      expect(result.current.messages).toHaveLength(6);
    });
  });
});
```

### Level 3: End-to-End Tests

#### Critical User Paths

```typescript
// e2e/tests/user-journey.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Complete User Journey', () => {
  test('New user onboarding to first workout plan', async ({ page }) => {
    // 1. Landing page
    await page.goto('/');
    await expect(page).toHaveTitle('GENESIS - AI Fitness Platform');

    // 2. Sign up
    await page.click('text=Get Started');
    await page.fill('[name=email]', 'test@example.com');
    await page.fill('[name=password]', 'SecurePass123!');
    await page.click('button[type=submit]');

    // 3. Onboarding
    await expect(page).toHaveURL('/onboarding');
    await page.selectOption('[name=goal]', 'muscle-gain');
    await page.fill('[name=age]', '28');
    await page.click('text=Continue');

    // 4. Chat with AI
    await expect(page).toHaveURL('/dashboard');
    await page.fill('[placeholder="Ask me anything..."]', 'I want to build muscle');
    await page.press('[placeholder="Ask me anything..."]', 'Enter');

    // 5. Verify AI response
    await expect(page.locator('.agent-badge')).toContainText('Elite Training Strategist');
    await expect(page.locator('.message-content')).toContainText('workout plan');

    // 6. Save plan
    await page.click('text=Save to My Plans');
    await expect(page.locator('.toast')).toContainText('Plan saved successfully');
  });
});
```

---

## 🔄 CONTINUOUS TESTING WORKFLOW

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest-unit
        name: Run unit tests
        entry: pytest tests/unit -x
        language: system
        pass_filenames: false
        always_run: true

      - id: frontend-tests
        name: Run frontend tests
        entry: npm test -- --run
        language: system
        pass_filenames: false
        always_run: true
```

### CI Pipeline

```yaml
# .github/workflows/test.yml
name: Comprehensive Testing

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          poetry install --with dev

      - name: Run unit tests
        run: |
          cd backend
          pytest tests/unit -v --cov=app --cov-report=xml

      - name: Run integration tests
        run: |
          cd backend
          docker-compose -f docker-compose.test.yml up -d
          pytest tests/integration -v

      - name: Upload coverage
        uses: codecov/codecov-action@v4

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install and test
        run: |
          cd frontend
          npm ci
          npm run test:ci
          npm run test:coverage

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    steps:
      - uses: actions/checkout@v4

      - name: Run E2E tests
        run: |
          docker-compose up -d
          npx playwright test

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: playwright-report/
```

---

## 🎪 TEST DATA MANAGEMENT

### Test Factories

```python
# tests/factories.py
import factory
from factory import fuzzy
from datetime import datetime, timedelta

class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Faker('email')
    name = factory.Faker('name')
    age = fuzzy.FuzzyInteger(18, 65)
    fitness_level = fuzzy.FuzzyChoice(['beginner', 'intermediate', 'advanced'])
    created_at = fuzzy.FuzzyDateTime(
        datetime.now() - timedelta(days=30),
        datetime.now()
    )

class WorkoutPlanFactory(factory.Factory):
    class Meta:
        model = WorkoutPlan

    user = factory.SubFactory(UserFactory)
    name = factory.Faker('catch_phrase')
    difficulty = fuzzy.FuzzyChoice(['easy', 'medium', 'hard'])
    duration_weeks = fuzzy.FuzzyInteger(4, 12)
    exercises = factory.LazyFunction(
        lambda: [ExerciseFactory() for _ in range(random.randint(5, 10))]
    )
```

### Fixtures Organization

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def app():
    """Create application for testing"""
    from app.main import create_app
    return create_app(testing=True)

@pytest.fixture
async def client(app):
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def authenticated_client(client, test_user):
    """Client with authentication"""
    token = generate_token(test_user)
    client.headers["Authorization"] = f"Bearer {token}"
    yield client

@pytest.fixture
async def db_session():
    """Create clean database session"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

---

## 📈 COVERAGE GOALS & TRACKING

### Coverage Configuration

```ini
# pytest.ini
[tool:pytest]
minversion = 6.0
addopts =
    -ra
    -q
    --strict-markers
    --cov=app
    --cov=agents
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=85

testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    unit: Unit tests (fast)
    integration: Integration tests (slower)
    e2e: End-to-end tests (slowest)
    slow: Slow tests
    requires_redis: Tests requiring Redis
    requires_db: Tests requiring database
```

### Coverage Tracking Dashboard

```python
# scripts/coverage_report.py
"""Generate detailed coverage report with trends"""

def generate_coverage_report():
    """Generate HTML report with coverage trends"""
    report = {
        "timestamp": datetime.now(),
        "backend": {
            "total": 85.3,
            "by_module": {
                "agents": 82.1,
                "api": 89.5,
                "core": 91.2,
                "services": 79.8
            }
        },
        "frontend": {
            "total": 78.9,
            "by_component": {
                "chat": 85.2,
                "dashboard": 72.3,
                "agents": 81.7,
                "common": 90.1
            }
        }
    }

    # Generate HTML dashboard
    create_dashboard(report)
```

---

## 🔥 PERFORMANCE TESTING

### Load Testing with Locust

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between

class GenesisUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login and get token"""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password"  # pragma: allowlist secret
        })
        self.token = response.json()["access_token"]
        self.client.headers["Authorization"] = f"Bearer {self.token}"

    @task(3)
    def send_chat_message(self):
        """Send chat message"""
        self.client.post("/api/v1/chat/message", json={
            "content": "What's a good workout for today?"
        })

    @task(1)
    def get_workout_plans(self):
        """Fetch workout plans"""
        self.client.get("/api/v1/workouts/plans")

    @task(2)
    def get_nutrition_advice(self):
        """Get nutrition recommendations"""
        self.client.post("/api/v1/nutrition/advice", json={
            "goal": "muscle_gain",
            "calories": 2500
        })
```

### Stress Testing Scenarios

```bash
# Run different load scenarios
# Baseline: 100 users
locust -f tests/performance/locustfile.py --users 100 --spawn-rate 10

# Stress: 1000 users
locust -f tests/performance/locustfile.py --users 1000 --spawn-rate 50

# Spike: Sudden traffic
locust -f tests/performance/locustfile.py --users 5000 --spawn-rate 500
```

---

## 🛡️ SECURITY TESTING

### Security Test Suite

```python
# tests/security/test_auth_security.py
import pytest
from datetime import datetime, timedelta

@pytest.mark.security
class TestAuthSecurity:
    async def test_sql_injection_prevention(self, client):
        """Test SQL injection prevention"""
        malicious_inputs = [
            "' OR '1'='1",
            "admin'--",
            "'; DROP TABLE users;--",
            "' UNION SELECT * FROM users--"
        ]

        for payload in malicious_inputs:
            response = await client.post("/api/v1/auth/login", json={
                "email": payload,
                "password": "password"  # pragma: allowlist secret
            })
            assert response.status_code == 422  # Validation error

    async def test_xss_prevention(self, client, auth_headers):
        """Test XSS prevention"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')"
        ]

        for payload in xss_payloads:
            response = await client.post(
                "/api/v1/chat/message",
                json={"content": payload},
                headers=auth_headers
            )

            # Verify sanitization
            data = response.json()
            assert "<script>" not in data["content"]
            assert "javascript:" not in data["content"]
```

---

## 📊 TEST METRICS & REPORTING

### Key Metrics to Track

1. **Coverage Percentage** (target: 85%+)
2. **Test Execution Time** (target: <5 min for unit tests)
3. **Flaky Test Rate** (target: <1%)
4. **Test Failure Rate** (monitor trends)
5. **Performance Benchmarks** (response times)

### Automated Reporting

```python
# scripts/test_reporter.py
def generate_test_report():
    """Generate comprehensive test report"""
    return {
        "summary": {
            "total_tests": 1247,
            "passed": 1235,
            "failed": 12,
            "skipped": 0,
            "duration": "4m 32s"
        },
        "coverage": {
            "overall": 83.7,
            "backend": 85.2,
            "frontend": 79.8,
            "e2e": "15/15 scenarios"
        },
        "performance": {
            "avg_response_time": "87ms",
            "p95_response_time": "142ms",
            "p99_response_time": "298ms"
        },
        "trends": {
            "coverage_delta": "+2.3%",
            "new_tests": 47,
            "fixed_tests": 5
        }
    }
```

---

## 🚀 TESTING BEST PRACTICES

### 1. Test Naming Convention

```python
# Good test names
def test_orchestrator_routes_fitness_query_to_training_agent():
def test_user_cannot_access_other_users_data():
def test_chat_message_displays_loading_state_during_send():

# Bad test names
def test_1():
def test_orchestrator():
def test_it_works():
```

### 2. AAA Pattern (Arrange, Act, Assert)

```python
async def test_agent_response_includes_metadata():
    # Arrange
    agent = NutritionAgent()
    user_query = "High protein breakfast ideas"

    # Act
    response = await agent.process(user_query)

    # Assert
    assert response.metadata.confidence > 0.7
    assert response.metadata.agent_name == "nutrition"
    assert len(response.suggestions) >= 3
```

### 3. Test Independence

- No shared state between tests
- Each test creates its own data
- Clean up after each test
- Use transactions for database tests

### 4. Meaningful Assertions

```python
# Good assertions
assert user.age >= 18, "User must be 18 or older"
assert response.status_code == 200, f"Expected 200, got {response.status_code}"

# Bad assertions
assert result  # What does this mean?
assert True    # Always passes
```

---

## 🎯 QUICK START TESTING CHECKLIST

### Week 1: Foundation

- [ ] Set up pytest with all plugins
- [ ] Configure coverage reporting
- [ ] Create test database
- [ ] Set up test factories
- [ ] Write first 10 unit tests

### Week 2: Expansion

- [ ] Add integration tests
- [ ] Set up MSW for frontend
- [ ] Configure Playwright
- [ ] Implement CI pipeline
- [ ] Reach 60% coverage

### Week 3: Maturity

- [ ] Add performance tests
- [ ] Security test suite
- [ ] Visual regression tests
- [ ] Mutation testing
- [ ] Reach 75% coverage

### Week 4: Excellence

- [ ] Full E2E test suite
- [ ] Automated reporting
- [ ] Test optimization
- [ ] Documentation
- [ ] Achieve 85%+ coverage

---

**Remember**: Tests are not a burden, they're your safety net. Write tests like your production depends on it - because it does! 🧪
