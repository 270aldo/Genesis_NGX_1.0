# CI/CD Pipeline Documentation

## Overview

This repository uses a comprehensive CI/CD pipeline built with GitHub Actions to ensure code quality, security, and reliable deployments. The pipeline consists of three main workflows:

1. **CI/CD Pipeline** (`test.yml`) - Main testing and integration workflow
2. **Release Pipeline** (`release.yml`) - Deployment and release management
3. **Code Quality & Security** (`quality.yml`) - Daily quality and security checks

## Workflows

### 1. CI/CD Pipeline (`test.yml`)

**Triggers:**

- Push to `main`, `develop`, `feature/*` branches
- Pull requests to `main`, `develop`

**Jobs:**

- **Backend Tests**: Python testing with Poetry, Redis service
- **Frontend Tests**: Node.js testing with npm
- **Security Scan**: Trivy vulnerability scanning
- **Integration Suite**: End-to-end integration testing
- **Test Summary**: Consolidated test reporting

**Features:**

- Parallel job execution for speed
- Comprehensive caching (Poetry venv, npm packages)
- Coverage reporting to Codecov
- Test result artifacts
- Beta validation on main branch only

### 2. Release Pipeline (`release.yml`)

**Triggers:**

- Git tags matching `v*.*.*`
- Manual workflow dispatch

**Jobs:**

- **Create Release**: Automated GitHub releases with changelog
- **Build and Test**: Multi-platform Docker image building
- **Deploy Staging**: Automatic staging deployment
- **Deploy Production**: Production deployment for stable releases
- **Post-deployment Monitoring**: Health checks and monitoring

**Features:**

- Multi-architecture Docker builds (AMD64, ARM64)
- Container registry integration (GitHub Container Registry)
- Security scanning with Trivy
- Progressive deployment (staging → production)
- Automated rollback capabilities
- Slack notifications

### 3. Code Quality & Security (`quality.yml`)

**Triggers:**

- Daily schedule (6 AM UTC)
- Push to main/develop branches
- Pull requests
- Manual workflow dispatch

**Jobs:**

- **Code Quality Analysis**: Linting, formatting, type checking
- **Dependency Check**: Outdated packages and license analysis
- **Performance Benchmark**: Automated performance testing
- **Security Scanning**: Trivy, Semgrep security analysis
- **Coverage Analysis**: Comprehensive test coverage reporting
- **Quality Gate**: Pass/fail quality criteria

**Features:**

- SonarCloud integration
- Security vulnerability scanning
- Performance benchmarking
- License compatibility checks
- Quality gate enforcement

## Branch Protection Rules

The following branch protection rules are recommended:

### Main Branch (`main`)

- Require pull request reviews (minimum 2 reviewers)
- Require status checks to pass before merging:
  - `Backend Tests`
  - `Frontend Tests`
  - `Security Scan`
  - `Integration Suite`
- Require branches to be up to date before merging
- Require conversation resolution before merging
- Restrict pushes to administrators only
- Allow force pushes for administrators only
- Allow deletions by administrators only

### Develop Branch (`develop`)

- Require pull request reviews (minimum 1 reviewer)
- Require status checks to pass before merging:
  - `Backend Tests`
  - `Frontend Tests`
  - `Security Scan`
- Require branches to be up to date before merging
- Restrict pushes to administrators and maintainers

## Required Secrets

### GitHub Secrets

Configure the following secrets in your GitHub repository:

#### General

- `CODECOV_TOKEN` - Codecov integration token
- `SONAR_TOKEN` - SonarCloud authentication token
- `SONAR_PROJECT_KEY` - SonarCloud project key
- `SONAR_ORGANIZATION` - SonarCloud organization

#### Deployment

- `KUBE_CONFIG_STAGING` - Base64 encoded kubeconfig for staging
- `KUBE_CONFIG_PRODUCTION` - Base64 encoded kubeconfig for production
- `DEPLOYMENT_WEBHOOK` - Webhook URL for deployment tracking

#### Notifications

- `SLACK_WEBHOOK` - Slack webhook for general notifications
- `SLACK_WEBHOOK_CRITICAL` - Slack webhook for critical alerts

### Environment Variables

Each environment (staging, production) should have:

#### Backend Environment Variables

```bash
ENVIRONMENT=staging|production
REDIS_URL=redis://redis-host:6379
DATABASE_URL=postgresql://user:pass@host:5432/db
LOG_LEVEL=INFO
VERTEX_AI_PROJECT=your-gcp-project
VERTEX_AI_LOCATION=us-central1
```

#### Frontend Environment Variables

```bash
VITE_API_URL=https://api.yourapp.com
VITE_ENVIRONMENT=staging|production
NODE_ENV=production
```

## Quality Gates

### Code Coverage Requirements

- **Backend**: Minimum 85% coverage
- **Frontend**: Minimum 80% coverage
- **New Code**: Minimum 90% coverage

### Security Requirements

- No high or critical vulnerabilities in dependencies
- All security scans must pass
- No secrets in code

### Performance Requirements

- API response time < 2 seconds
- Build time < 10 minutes
- Bundle size increase < 10%

## Deployment Strategy

### Staging Deployment

- Automatic deployment on merge to `main`
- Smoke tests after deployment
- Available at staging URLs

### Production Deployment

- Triggered by version tags (`v1.0.0`)
- Requires successful staging deployment
- Comprehensive health checks
- Monitoring for 10 minutes post-deployment
- Automatic rollback on failure

### Rollback Procedure

```bash
# Tag the previous stable version
git tag v1.0.1-rollback

# Trigger deployment workflow with manual dispatch
# Select production environment and specify rollback version
```

## Monitoring and Alerting

### Metrics Collected

- Test pass/fail rates
- Deployment success rates
- Code coverage trends
- Security vulnerability counts
- Performance benchmarks

### Alert Conditions

- Test failures on main branch
- Security vulnerabilities detected
- Deployment failures
- Performance degradation
- Coverage drops below threshold

### Notification Channels

- Slack for general updates
- Email for critical alerts
- GitHub status checks
- Pull request comments

## Development Workflow

### Conventional Commits

All commits must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
type(scope): description

feat(agents): add new nutrition analysis capabilities
fix(api): resolve authentication timeout issue
docs(readme): update deployment instructions
test(unit): add coverage for user service
```

### Pull Request Process

1. Create feature branch from `develop`
2. Implement changes with tests
3. Run local quality checks
4. Create pull request with template
5. Address review feedback
6. Merge to `develop` after approval
7. Create release PR to `main` when ready

### Pre-commit Hooks

Install pre-commit hooks for consistent code quality:

```bash
# Backend
cd backend
poetry install --with dev
poetry run pre-commit install

# Frontend
cd frontend
npm install
npm run prepare
```

## Troubleshooting

### Common Issues

#### Build Failures

- Check dependency versions compatibility
- Verify environment variables are set
- Review test output for specific failures

#### Deployment Issues

- Verify Kubernetes cluster connectivity
- Check resource quotas and limits
- Review application logs

#### Security Scan Failures

- Update vulnerable dependencies
- Add security exceptions if needed (with justification)
- Check for exposed secrets

### Getting Help

- Check workflow logs in GitHub Actions tab
- Review failed job artifacts
- Contact DevOps team for infrastructure issues
- Create GitHub issue for pipeline improvements

## Pipeline Metrics

The CI/CD pipeline tracks the following key metrics:

- **Build Success Rate**: Target > 95%
- **Test Coverage**: Backend > 85%, Frontend > 80%
- **Deployment Time**: Target < 10 minutes
- **Mean Time to Recovery**: Target < 30 minutes
- **Security Vulnerabilities**: Target = 0 high/critical

## Future Improvements

Planned enhancements to the CI/CD pipeline:

1. **Advanced Testing**
   - Visual regression testing
   - Load testing integration
   - Chaos engineering tests

2. **Enhanced Security**
   - SAST/DAST integration
   - Container image signing
   - Supply chain security

3. **Deployment Enhancements**
   - Blue/green deployments
   - Canary releases
   - Feature flag integration

4. **Monitoring Integration**
   - Synthetic monitoring
   - Real user monitoring
   - Advanced alerting rules
