# GitHub Secrets Setup Guide

This guide walks you through setting up all required secrets for the CI/CD pipeline.

## Required Secrets Overview

### 🔐 Essential Secrets (Required for CI/CD to work)

- `CODECOV_TOKEN` - Code coverage reporting
- `SONAR_TOKEN` - Code quality analysis
- `SONAR_PROJECT_KEY` - SonarCloud project identifier
- `SONAR_ORGANIZATION` - SonarCloud organization

### 🚀 Deployment Secrets (Required for automated deployments)

- `KUBE_CONFIG_STAGING` - Kubernetes configuration for staging
- `KUBE_CONFIG_PRODUCTION` - Kubernetes configuration for production
- `DEPLOYMENT_WEBHOOK` - Webhook for deployment tracking

### 📢 Notification Secrets (Optional but recommended)

- `SLACK_WEBHOOK` - General notifications
- `SLACK_WEBHOOK_CRITICAL` - Critical alert notifications

## Step-by-Step Setup

### 1. Access Repository Settings

1. Go to your GitHub repository
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** > **Actions**

### 2. Essential Secrets Setup

#### Codecov Token Setup

1. **Get Codecov Token:**
   - Visit [codecov.io](https://codecov.io)
   - Sign in with your GitHub account
   - Navigate to your repository
   - Go to Settings > General
   - Copy the **Repository Upload Token**

2. **Add to GitHub:**
   - In GitHub repository secrets, click **New repository secret**
   - Name: `CODECOV_TOKEN`
   - Value: Paste the token from Codecov
   - Click **Add secret**

#### SonarCloud Setup

1. **Create SonarCloud Project:**
   - Visit [sonarcloud.io](https://sonarcloud.io)
   - Sign in with your GitHub account
   - Click **Add a project**
   - Select your repository
   - Choose organization or create new one

2. **Get SonarCloud Token:**
   - Go to your SonarCloud profile (top-right avatar)
   - Click **My Account** > **Security**
   - Generate a new token with a descriptive name
   - Copy the token immediately (it won't be shown again)

3. **Add SonarCloud Secrets:**
   - `SONAR_TOKEN`: The token you just generated
   - `SONAR_PROJECT_KEY`: Found in your SonarCloud project settings (usually `your-org_your-repo`)
   - `SONAR_ORGANIZATION`: Your SonarCloud organization key

### 3. Deployment Secrets Setup

#### Kubernetes Configuration

1. **Get Kubeconfig Files:**

   For staging:

   ```bash
   # Get your staging kubeconfig
   kubectl config view --raw --minify --context=staging-context > staging-kubeconfig.yaml

   # Base64 encode it
   base64 -i staging-kubeconfig.yaml | tr -d '\n' | pbcopy
   ```

   For production:

   ```bash
   # Get your production kubeconfig
   kubectl config view --raw --minify --context=production-context > production-kubeconfig.yaml

   # Base64 encode it
   base64 -i production-kubeconfig.yaml | tr -d '\n' | pbcopy
   ```

2. **Add Kubernetes Secrets:**
   - `KUBE_CONFIG_STAGING`: Base64 encoded staging kubeconfig
   - `KUBE_CONFIG_PRODUCTION`: Base64 encoded production kubeconfig

#### Deployment Webhook (Optional)

If you have a deployment tracking system:

- `DEPLOYMENT_WEBHOOK`: URL endpoint for deployment notifications

### 4. Notification Secrets Setup

#### Slack Webhooks (Optional but recommended)

1. **Create Slack Apps:**
   - Go to [api.slack.com/apps](https://api.slack.com/apps)
   - Click **Create New App** > **From scratch**
   - Name your app (e.g., "GENESIS CI/CD")
   - Select your workspace

2. **Configure Incoming Webhooks:**
   - In your app settings, go to **Incoming Webhooks**
   - Activate incoming webhooks
   - Click **Add New Webhook to Workspace**
   - Choose the channel for notifications
   - Copy the webhook URL

3. **Add Slack Secrets:**
   - `SLACK_WEBHOOK`: For general CI/CD notifications
   - `SLACK_WEBHOOK_CRITICAL`: For critical alerts (can be same as above or different channel)

### 5. Environment-Specific Secrets

For each environment (staging, production), you may need additional secrets:

#### Backend Environment Secrets

```bash
# Database connections
DATABASE_URL
REDIS_URL

# Google Cloud / Vertex AI
VERTEX_AI_PROJECT
VERTEX_AI_LOCATION
GOOGLE_APPLICATION_CREDENTIALS

# Third-party APIs
ELEVENLABS_API_KEY
SUPABASE_URL
SUPABASE_ANON_KEY
```

#### Frontend Environment Secrets

```bash
# API endpoints
VITE_API_URL
VITE_WS_URL

# Feature flags
VITE_FEATURE_FLAGS_ENDPOINT
```

## Security Best Practices

### ✅ Do's

- Use environment-specific secrets (staging vs production)
- Regularly rotate secrets (quarterly or semi-annually)
- Use least-privilege access for service accounts
- Monitor secret usage in audit logs
- Use descriptive names for secrets

### ❌ Don'ts

- Never commit secrets to version control
- Don't share secrets via chat or email
- Avoid using production secrets in staging
- Don't use generic names like `SECRET` or `TOKEN`
- Never log secret values

## Verification

### Test CI/CD Pipeline

1. Create a test branch
2. Make a small change
3. Open a pull request
4. Verify all checks pass:
   - ✅ Backend Tests
   - ✅ Frontend Tests
   - ✅ Security Scan
   - ✅ Code Quality checks

### Test Deployments

1. Create a test tag: `git tag v0.1.0-test`
2. Push tag: `git push origin v0.1.0-test`
3. Verify deployment workflow runs
4. Check staging deployment
5. Clean up test tag if needed

## Troubleshooting

### Common Issues

#### "Secret not found" Errors

- Verify secret name matches exactly (case-sensitive)
- Check if secret is set at repository level, not organization level
- Ensure the workflow has access to the secret

#### Authentication Failures

- Verify token/key format is correct
- Check if token has expired
- Ensure sufficient permissions for the token

#### Deployment Failures

- Verify kubeconfig is properly base64 encoded
- Check if Kubernetes cluster is accessible
- Ensure service account has necessary permissions

### Getting Help

1. **Check GitHub Actions logs:**
   - Go to Actions tab in your repository
   - Click on the failed workflow
   - Expand the failed step to see detailed logs

2. **Validate secrets locally:**

   ```bash
   # Test Codecov token
   curl -X GET "https://codecov.io/api/v2/github/your-org/your-repo" \
     -H "Authorization: Bearer $CODECOV_TOKEN"

   # Test SonarCloud token
   curl -X GET "https://sonarcloud.io/api/user_tokens/search" \
     -H "Authorization: Bearer $SONAR_TOKEN"
   ```

3. **Contact team:**
   - DevOps team for infrastructure-related issues
   - Security team for secret management questions
   - Create GitHub issue for pipeline improvements

## Maintenance Schedule

### Monthly

- [ ] Review secret usage in audit logs
- [ ] Check for unused secrets
- [ ] Verify webhook endpoints are responding

### Quarterly

- [ ] Rotate service account keys
- [ ] Update API tokens
- [ ] Review and update access permissions

### Semi-annually

- [ ] Rotate all secrets
- [ ] Review security practices
- [ ] Update documentation

---

**Important:** Keep this guide updated as new secrets are added or existing ones are modified. Always test changes in a non-production environment first.
