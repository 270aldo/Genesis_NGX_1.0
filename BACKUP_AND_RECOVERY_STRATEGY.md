# 🔒 GENESIS Backup and Recovery Strategy

## Executive Summary

This document outlines the comprehensive backup and disaster recovery strategy for the GENESIS production system. Our approach ensures **99.9% availability**, **<4 hour RTO (Recovery Time Objective)**, and **<1 hour RPO (Recovery Point Objective)**.

## 📊 System Components

### Critical Data Assets

1. **PostgreSQL Database (Supabase)**
   - User profiles and authentication
   - Conversations and chat history
   - Agent configurations
   - Training/nutrition plans
   - Analytics and metrics

2. **Redis Cache**
   - Session data
   - Temporary agent state
   - Rate limiting counters
   - Real-time metrics

3. **File Storage (GCS/S3)**
   - User uploaded images
   - Generated reports
   - Model artifacts
   - Training datasets

4. **Configuration & Secrets**
   - Environment variables
   - API keys and credentials
   - SSL certificates
   - Service configurations

## 🎯 Backup Strategy

### 1. Database Backups (PostgreSQL/Supabase)

#### Automated Backups

```bash
# Daily automated backups at 2 AM UTC
0 2 * * * /usr/local/bin/backup-database.sh

# Script: /usr/local/bin/backup-database.sh
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="genesis_backup_${TIMESTAMP}"

# Supabase automatic backups (managed)
# - Point-in-time recovery: Last 7 days
# - Daily snapshots: Retained for 30 days
# - Weekly snapshots: Retained for 3 months

# Additional logical backup
pg_dump $DATABASE_URL | gzip > /backups/db/${BACKUP_NAME}.sql.gz

# Upload to GCS
gsutil cp /backups/db/${BACKUP_NAME}.sql.gz gs://genesis-backups/db/

# Verify backup
if [ $? -eq 0 ]; then
    echo "Backup successful: ${BACKUP_NAME}"
    # Send success notification
    curl -X POST $SLACK_WEBHOOK -d "{\"text\":\"✅ Database backup completed: ${BACKUP_NAME}\"}"
else
    echo "Backup failed: ${BACKUP_NAME}"
    # Send alert
    curl -X POST $PAGERDUTY_ALERT -d "{\"alert\":\"Database backup failed\"}"
fi

# Cleanup old local backups (keep last 7 days)
find /backups/db -name "*.sql.gz" -mtime +7 -delete
```

#### Manual Backup Command

```bash
# On-demand backup before major changes
make backup-db

# Makefile target
backup-db:
 @echo "Creating manual database backup..."
 @pg_dump $(DATABASE_URL) | gzip > backups/manual_$(shell date +%Y%m%d_%H%M%S).sql.gz
 @echo "Backup completed"
```

### 2. Redis Backup

#### Persistent Redis Configuration

```conf
# redis.conf
save 900 1      # Save after 900 sec if at least 1 key changed
save 300 10     # Save after 300 sec if at least 10 keys changed
save 60 10000   # Save after 60 sec if at least 10000 keys changed

appendonly yes  # Enable AOF persistence
appendfsync everysec  # Sync to disk every second

# Backup location
dir /data/redis/
dbfilename dump.rdb
appendfilename "appendonly.aof"
```

#### Backup Script

```bash
#!/bin/bash
# redis-backup.sh
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create snapshot
redis-cli BGSAVE

# Wait for completion
while [ $(redis-cli LASTSAVE) -eq $(redis-cli LASTSAVE) ]; do
    sleep 1
done

# Copy files
cp /data/redis/dump.rdb /backups/redis/dump_${TIMESTAMP}.rdb
cp /data/redis/appendonly.aof /backups/redis/aof_${TIMESTAMP}.aof

# Upload to cloud storage
gsutil cp /backups/redis/* gs://genesis-backups/redis/
```

### 3. File Storage Backup

#### GCS/S3 Cross-Region Replication

```yaml
# terraform/storage.tf
resource "google_storage_bucket" "main" {
  name     = "genesis-production"
  location = "US"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  # Cross-region replication
  replication {
    role = "SOURCE"
    destination_bucket = google_storage_bucket.backup.id
  }
}

resource "google_storage_bucket" "backup" {
  name     = "genesis-production-backup"
  location = "EU"  # Different region for disaster recovery

  versioning {
    enabled = true
  }
}
```

### 4. Configuration & Secrets Backup

#### Kubernetes Secrets Backup

```bash
#!/bin/bash
# backup-k8s-secrets.sh
NAMESPACE="production"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Export all secrets
kubectl get secrets -n $NAMESPACE -o yaml > /backups/k8s/secrets_${TIMESTAMP}.yaml

# Encrypt with GPG
gpg --encrypt --recipient backup@genesis.com /backups/k8s/secrets_${TIMESTAMP}.yaml

# Upload encrypted backup
gsutil cp /backups/k8s/secrets_${TIMESTAMP}.yaml.gpg gs://genesis-backups/k8s/

# Cleanup unencrypted file
shred -u /backups/k8s/secrets_${TIMESTAMP}.yaml
```

## 🔄 Recovery Procedures

### 1. Database Recovery

#### Point-in-Time Recovery (Supabase)

```sql
-- Restore to specific timestamp
-- Via Supabase Dashboard or CLI
supabase db restore --timestamp "2024-01-15 10:30:00"
```

#### Manual Recovery from Backup

```bash
#!/bin/bash
# restore-database.sh
BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./restore-database.sh <backup_file>"
    exit 1
fi

# Download from GCS if needed
if [[ $BACKUP_FILE == gs://* ]]; then
    gsutil cp $BACKUP_FILE /tmp/restore.sql.gz
    BACKUP_FILE="/tmp/restore.sql.gz"
fi

# Stop application to prevent writes
kubectl scale deployment genesis-api --replicas=0

# Restore database
gunzip < $BACKUP_FILE | psql $DATABASE_URL

# Verify restoration
psql $DATABASE_URL -c "SELECT COUNT(*) FROM users;"

# Restart application
kubectl scale deployment genesis-api --replicas=3

echo "Database restoration completed"
```

### 2. Redis Recovery

```bash
#!/bin/bash
# restore-redis.sh
BACKUP_RDB=$1

# Stop Redis to prevent data corruption
redis-cli SHUTDOWN SAVE

# Backup current data (just in case)
cp /data/redis/dump.rdb /data/redis/dump.rdb.backup

# Restore from backup
cp $BACKUP_RDB /data/redis/dump.rdb

# Start Redis
redis-server /etc/redis/redis.conf

# Verify
redis-cli PING
redis-cli DBSIZE
```

### 3. Full System Recovery

#### Disaster Recovery Runbook

```bash
#!/bin/bash
# disaster-recovery.sh

echo "🚨 Starting Disaster Recovery Process"

# 1. Verify backup availability
echo "Step 1: Checking backups..."
gsutil ls gs://genesis-backups/db/ | tail -1
gsutil ls gs://genesis-backups/redis/ | tail -1

# 2. Provision new infrastructure (if needed)
echo "Step 2: Provisioning infrastructure..."
cd terraform/
terraform init
terraform apply -auto-approve

# 3. Restore database
echo "Step 3: Restoring database..."
LATEST_DB_BACKUP=$(gsutil ls gs://genesis-backups/db/ | tail -1)
./scripts/restore-database.sh $LATEST_DB_BACKUP

# 4. Restore Redis
echo "Step 4: Restoring Redis cache..."
LATEST_REDIS_BACKUP=$(gsutil ls gs://genesis-backups/redis/dump_*.rdb | tail -1)
./scripts/restore-redis.sh $LATEST_REDIS_BACKUP

# 5. Deploy application
echo "Step 5: Deploying application..."
kubectl apply -f k8s/

# 6. Restore configurations
echo "Step 6: Restoring configurations..."
LATEST_SECRETS=$(gsutil ls gs://genesis-backups/k8s/secrets_*.yaml.gpg | tail -1)
./scripts/restore-secrets.sh $LATEST_SECRETS

# 7. Verify services
echo "Step 7: Verifying services..."
./scripts/health-check.sh

# 8. DNS failover (if needed)
echo "Step 8: Updating DNS..."
gcloud dns record-sets transaction start --zone=genesis-zone
gcloud dns record-sets transaction add --name=api.genesis.com \
    --ttl=300 --type=A --zone=genesis-zone NEW_IP_ADDRESS
gcloud dns record-sets transaction execute --zone=genesis-zone

echo "✅ Disaster Recovery Complete"
```

## 📈 Monitoring & Alerting

### Backup Monitoring

```yaml
# monitoring/backup-alerts.yml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: backup-alerts
spec:
  groups:
  - name: backup
    rules:
    - alert: BackupFailed
      expr: backup_last_success_timestamp < time() - 86400
      for: 1h
      annotations:
        summary: "Backup has not succeeded in 24 hours"

    - alert: BackupStorageFull
      expr: backup_storage_used_bytes / backup_storage_total_bytes > 0.9
      for: 30m
      annotations:
        summary: "Backup storage is 90% full"
```

### Recovery Testing

```bash
# Monthly recovery drill
0 0 1 * * /usr/local/bin/recovery-test.sh

#!/bin/bash
# recovery-test.sh
echo "Starting monthly recovery drill..."

# Create test environment
kubectl create namespace recovery-test

# Restore to test environment
./scripts/restore-database.sh --namespace recovery-test
./scripts/restore-redis.sh --namespace recovery-test

# Run validation tests
pytest tests/recovery/

# Cleanup
kubectl delete namespace recovery-test

# Report results
echo "Recovery drill completed successfully"
```

## 🔐 Security Considerations

### Encryption

- **At Rest**: All backups encrypted with AES-256
- **In Transit**: TLS 1.3 for all transfers
- **Key Management**: Rotated monthly via Google KMS

### Access Control

```yaml
# IAM permissions for backup service account
- roles/storage.admin  # For backup buckets only
- roles/cloudsql.admin  # For database backups
- roles/monitoring.metricWriter  # For metrics
```

### Compliance

- **GDPR**: 30-day deletion policy for user-requested data removal
- **HIPAA**: Encrypted backups with audit logging
- **SOC2**: Quarterly recovery testing documented

## 📋 Backup Schedule Summary

| Component | Frequency | Retention | Location |
|-----------|-----------|-----------|----------|
| Database (Full) | Daily | 30 days | GCS + Supabase |
| Database (Incremental) | Hourly | 7 days | Supabase PITR |
| Redis | Every 15 min | 24 hours | Local + GCS |
| Files | Real-time | Versioned | GCS with replication |
| Configs | On change | 90 days | GCS encrypted |
| Secrets | Daily | 30 days | GCS encrypted |

## 🎯 Recovery Objectives

### RTO (Recovery Time Objective)

- **Critical Services**: < 1 hour
- **Full System**: < 4 hours
- **Data Corruption**: < 2 hours

### RPO (Recovery Point Objective)

- **Database**: < 1 hour
- **Cache**: < 15 minutes
- **Files**: Real-time (versioned)

## 📝 Testing & Validation

### Quarterly Tests

1. **Backup Verification**: Restore random backup to test environment
2. **Failover Test**: Simulate region failure
3. **Recovery Drill**: Full system recovery exercise
4. **Data Integrity**: Checksum validation

### Automation

```bash
# Automated backup validation
#!/bin/bash
# validate-backups.sh

# Test database backup
RANDOM_BACKUP=$(gsutil ls gs://genesis-backups/db/ | shuf -n 1)
pg_restore --list $RANDOM_BACKUP > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Database backup valid"
else
    echo "❌ Database backup corrupted: $RANDOM_BACKUP"
    exit 1
fi

# Test Redis backup
RANDOM_REDIS=$(gsutil ls gs://genesis-backups/redis/ | shuf -n 1)
redis-check-rdb $RANDOM_REDIS
if [ $? -eq 0 ]; then
    echo "✅ Redis backup valid"
else
    echo "❌ Redis backup corrupted: $RANDOM_REDIS"
    exit 1
fi
```

## 🚀 Quick Recovery Commands

```bash
# Emergency recovery commands
make recovery-db         # Restore latest database
make recovery-redis       # Restore latest Redis
make recovery-full        # Full system recovery
make recovery-test        # Test recovery process
make backup-all          # Create immediate backup of everything
```

## 📞 Emergency Contacts

- **On-Call Engineer**: PagerDuty rotation
- **Database Admin**: <db-team@genesis.com>
- **Cloud Infrastructure**: <infra-team@genesis.com>
- **Security Team**: <security@genesis.com>

## 📚 Related Documentation

- [Incident Response Plan](./docs/INCIDENT_RESPONSE.md)
- [Security Policies](./docs/SECURITY_POLICIES.md)
- [Infrastructure as Code](./terraform/README.md)
- [Monitoring Guide](./monitoring/README.md)

---

**Last Updated**: 2024-01-15
**Review Frequency**: Quarterly
**Next Review**: 2024-04-15
**Owner**: DevOps Team

✅ **This strategy ensures GENESIS maintains enterprise-grade reliability with comprehensive backup coverage and rapid recovery capabilities.**
