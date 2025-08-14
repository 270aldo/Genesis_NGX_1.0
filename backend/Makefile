.PHONY: setup setup-full setup-dev setup-test dev test test-unit test-integration test-agents test-contract test-ai test-cov test-cov-html test-adk lint format clean test-performance help

# Environment and Development Setup
setup:
	poetry install --no-root --with dev,test

setup-full:
	poetry install --no-root --with dev,test,agents,clients,core,tools,telemetry

setup-dev:
	poetry install --no-root --with dev,test,agents,clients,core,tools

setup-test:
	poetry install --no-root --only test

dev:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Core Testing Commands
test:
	poetry run pytest

test-unit:
	poetry run pytest -m unit --maxfail=10

test-integration:
	poetry run pytest -m integration --maxfail=5

test-agents:
	poetry run pytest -m agents --maxfail=3

test-contract:
	poetry run pytest tests/contract/ -v --maxfail=5

test-ai:
	poetry run pytest tests/ai/ -v --maxfail=3

test-semantic:
	poetry run pytest tests/ai/test_semantic_similarity.py -v

# Specific Test Categories
test-adk:
	./scripts/test_adk_integration.sh

test-beta:
	poetry run pytest tests/beta_validation/ -v --maxfail=3

# Performance Testing
test-performance:
	cd ../load-tests && k6 run tests/load-test.js

test-stress:
	cd ../load-tests && k6 run tests/stress-test.js

# Coverage Reports
test-cov:
	poetry run pytest --cov=core --cov=clients --cov=agents --cov=tools --cov=app \
		--cov-report=term-missing --cov-fail-under=85

test-cov-html:
	poetry run pytest --cov=core --cov=clients --cov=agents --cov=tools --cov=app \
		--cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in coverage_html_report/index.html"

test-cov-xml:
	poetry run pytest --cov=core --cov=clients --cov=agents --cov=tools --cov=app \
		--cov-report=xml --cov-report=term-missing

# Advanced Testing
test-regression:
	poetry run pytest tests/ --maxfail=20 --tb=short

test-smoke:
	poetry run pytest tests/unit/test_health.py tests/integration/test_api.py -v

test-parallel:
	poetry run pytest -n auto --maxfail=10

# Agent-Specific Testing
test-blaze:
	poetry run pytest tests/agents/elite_training_strategist/ -v

test-sage:
	poetry run pytest tests/agents/precision_nutrition_architect/ -v

test-stella:
	poetry run pytest tests/agents/progress_tracker/ -v

test-orchestrator:
	poetry run pytest tests/agents/orchestrator/ -v

# API Testing
test-openapi:
	poetry run pytest tests/contract/openapi/ -v

test-a2a:
	poetry run pytest tests/contract/a2a/ -v

test-api-bruno:
	cd ../api-tests && bru run --env local

# Code Quality
lint:
	poetry run ruff check core clients agents tools app
	poetry run mypy core clients agents tools app

lint-fix:
	poetry run ruff check --fix core clients agents tools app

format:
	poetry run black core clients agents tools app
	poetry run isort core clients agents tools app

format-check:
	poetry run black --check --diff core clients agents tools app
	poetry run isort --check-only --diff core clients agents tools app

# Security
security-check:
	poetry run bandit -r core clients agents tools app
	poetry run safety check

# CI/CD Integration
ci-test:
	poetry run pytest --maxfail=5 --tb=short --cov=core --cov=clients --cov=agents \
		--cov=tools --cov=app --cov-report=xml --cov-report=term-missing

ci-lint:
	poetry run ruff check . --output-format=github
	poetry run mypy . --ignore-missing-imports

# Cleanup
clean:
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf coverage_html_report
	rm -rf htmlcov
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf */*/__pycache__
	rm -rf */*/*/__pycache__
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.pyd" -delete
	find . -name ".DS_Store" -delete

clean-results:
	rm -rf test-results/
	rm -rf reports/

# Help
help:
	@echo "GENESIS Backend Testing Commands"
	@echo "==============================="
	@echo ""
	@echo "Setup:"
	@echo "  setup          - Install basic dependencies"
	@echo "  setup-full     - Install all dependencies"
	@echo "  dev            - Start development server"
	@echo ""
	@echo "Testing:"
	@echo "  test           - Run all tests"
	@echo "  test-unit      - Run unit tests"
	@echo "  test-integration - Run integration tests"
	@echo "  test-agents    - Run agent tests"
	@echo "  test-contract  - Run contract tests"
	@echo "  test-ai        - Run AI quality tests"
	@echo ""
	@echo "Coverage:"
	@echo "  test-cov       - Run tests with coverage"
	@echo "  test-cov-html  - Generate HTML coverage report"
	@echo ""
	@echo "Specialized:"
	@echo "  test-blaze     - Test BLAZE agent"
	@echo "  test-sage      - Test SAGE agent"
	@echo "  test-stella    - Test STELLA agent"
	@echo "  test-performance - Run K6 load tests"
	@echo ""
	@echo "Quality:"
	@echo "  lint           - Run linting"
	@echo "  format         - Format code"
	@echo "  security-check - Security analysis"
	@echo ""
	@echo "Utilities:"
	@echo "  clean          - Clean cache files"
	@echo "  help           - Show this help"
