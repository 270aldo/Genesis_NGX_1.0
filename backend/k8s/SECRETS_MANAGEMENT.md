# Kubernetes Secrets Management Guide

## ⚠️ IMPORTANT: Never Commit Secrets to Version Control

This guide explains how to properly manage secrets for the NGX Agents Kubernetes deployment.

## Required Secrets

### 1. RabbitMQ Credentials

```bash
kubectl create secret generic rabbitmq-secret \
  --from-literal=user=$RABBITMQ_USER \
  --from-literal=password=$RABBITMQ_PASSWORD \
  -n ngx-agents
```

### 2. Flower UI Credentials

```bash
kubectl create secret generic flower-secret \
  --from-literal=user=$FLOWER_USER \
  --from-literal=password=$FLOWER_PASSWORD \
  -n ngx-agents
```

### 3. Flower Basic Auth (Ingress Protection)

```bash
# Generate htpasswd hash
FLOWER_AUTH=$(htpasswd -nb $FLOWER_ADMIN_USER $FLOWER_ADMIN_PASSWORD | base64)

# Create secret
kubectl create secret generic flower-basic-auth \
  --from-literal=auth=$FLOWER_AUTH \
  -n ngx-agents
```

### 4. Database Credentials

```bash
kubectl create secret generic postgres-secret \
  --from-literal=username=$DB_USER \
  --from-literal=password=$DB_PASSWORD \
  --from-literal=database=$DB_NAME \
  -n ngx-agents
```

### 5. API Keys

```bash
kubectl create secret generic api-keys \
  --from-literal=vertex-ai-key=$VERTEX_AI_KEY \
  --from-literal=elevenlabs-key=$ELEVENLABS_KEY \
  --from-literal=supabase-key=$SUPABASE_KEY \
  --from-literal=supabase-url=$SUPABASE_URL \
  -n ngx-agents
```

## Best Practices

1. **Use External Secret Management**:
   - Consider using Google Secret Manager, HashiCorp Vault, or Kubernetes Secrets Store CSI Driver
   - Rotate secrets regularly

2. **Environment-Specific Secrets**:

   ```bash
   # Development
   kubectl apply -f k8s/secrets/dev-secrets.yaml -n ngx-agents-dev

   # Staging
   kubectl apply -f k8s/secrets/staging-secrets.yaml -n ngx-agents-staging

   # Production
   kubectl apply -f k8s/secrets/prod-secrets.yaml -n ngx-agents-prod
   ```

3. **Secret Rotation**:
   - Implement automated secret rotation
   - Use versioned secrets
   - Update deployments without downtime

4. **Access Control**:
   - Use RBAC to limit secret access
   - Create service accounts with minimal permissions
   - Audit secret access regularly

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Deploy Secrets
  env:
    RABBITMQ_USER: ${{ secrets.RABBITMQ_USER }}
    RABBITMQ_PASSWORD: ${{ secrets.RABBITMQ_PASSWORD }}
    FLOWER_USER: ${{ secrets.FLOWER_USER }}
    FLOWER_PASSWORD: ${{ secrets.FLOWER_PASSWORD }}
  run: |
    kubectl create secret generic rabbitmq-secret \
      --from-literal=user=$RABBITMQ_USER \
      --from-literal=password=$RABBITMQ_PASSWORD \
      -n ngx-agents \
      --dry-run=client -o yaml | kubectl apply -f -
```

## Verification

Check that all required secrets are present:

```bash
kubectl get secrets -n ngx-agents

# Expected output:
# NAME                  TYPE     DATA   AGE
# rabbitmq-secret       Opaque   2      1d
# flower-secret         Opaque   2      1d
# flower-basic-auth     Opaque   1      1d
# postgres-secret       Opaque   3      1d
# api-keys             Opaque   4      1d
```

## Emergency Procedures

### Secret Compromise

1. Immediately rotate the compromised secret
2. Update all pods using the secret
3. Audit logs for unauthorized access
4. Review and update access controls

### Recovery

```bash
# Backup secrets
kubectl get secret <secret-name> -n ngx-agents -o yaml > backup-secret.yaml

# Restore secrets
kubectl apply -f backup-secret.yaml
```

## Security Checklist

- [ ] All secrets removed from code and config files
- [ ] Secrets stored in Kubernetes secrets or external manager
- [ ] RBAC configured for secret access
- [ ] Secret rotation policy implemented
- [ ] Audit logging enabled for secret access
- [ ] CI/CD uses secure secret injection
- [ ] No secrets in container images
- [ ] No secrets in environment variables visible in pod spec

Remember: **NEVER** commit actual secret values to version control!
