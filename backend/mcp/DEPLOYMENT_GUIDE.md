# GENESIS MCP High Availability Deployment Guide

## Overview

This guide covers deploying the GENESIS MCP Gateway with high availability, automatic failover, and comprehensive monitoring.

## Architecture

```
                           ┌─────────────┐
                           │  HAProxy    │
                           │(Load Balancer)│
                           └──────┬──────┘
                    ┌─────────────┴─────────────┐
                    │                           │
            ┌───────▼────────┐         ┌───────▼────────┐
            │ MCP Gateway    │         │ MCP Gateway    │
            │   (Primary)    │         │   (Backup)     │
            └───────┬────────┘         └───────┬────────┘
                    │                           │
            ┌───────▼────────┐         ┌───────▼────────┐
            │GENESIS Backend │         │GENESIS Backend │
            │   (Primary)    │         │   (Backup)     │
            └───────┬────────┘         └───────┬────────┘
                    │                           │
                    └─────────────┬─────────────┘
                          ┌───────▼────────┐
                          │   PostgreSQL   │
                          │     Redis      │
                          └────────────────┘
```

## Prerequisites

- Docker & Docker Compose (for containerized deployment)
- Python 3.11+ (for native deployment)
- PostgreSQL 15+
- Redis 7+
- SSL certificates (for production)
- At least 4GB RAM per node
- 20GB disk space

## Deployment Options

### Option 1: Docker Compose (Recommended for Development/Staging)

1. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start the HA Cluster**
   ```bash
   docker-compose -f docker-compose.ha.yml up -d
   ```

3. **Verify Health**
   ```bash
   # Check all services are running
   docker-compose -f docker-compose.ha.yml ps
   
   # Check health endpoints
   curl http://localhost:3000/health  # MCP Gateway
   curl http://localhost:8000/health  # GENESIS Backend
   curl http://localhost:8404/stats  # HAProxy stats
   ```

### Option 2: Kubernetes (Recommended for Production)

1. **Create Namespace**
   ```bash
   kubectl create namespace genesis
   ```

2. **Apply Configurations**
   ```bash
   kubectl apply -f k8s/configmap.yaml
   kubectl apply -f k8s/secrets.yaml
   kubectl apply -f k8s/deployments.yaml
   kubectl apply -f k8s/services.yaml
   kubectl apply -f k8s/ingress.yaml
   ```

3. **Enable Autoscaling**
   ```bash
   kubectl apply -f k8s/hpa.yaml
   ```

### Option 3: Systemd Service (Native Linux)

1. **Install Dependencies**
   ```bash
   cd /opt/genesis/backend
   pip install -r requirements.txt
   ```

2. **Configure Services**
   ```bash
   # Copy service files
   sudo cp mcp/genesis-orchestrator.service /etc/systemd/system/
   
   # Create genesis user
   sudo useradd -r -s /bin/false genesis
   sudo chown -R genesis:genesis /opt/genesis
   
   # Create log directory
   sudo mkdir -p /var/log/genesis
   sudo chown genesis:genesis /var/log/genesis
   ```

3. **Enable and Start Services**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable genesis-orchestrator
   sudo systemctl start genesis-orchestrator
   ```

## High Availability Configuration

### 1. Database Replication

For PostgreSQL high availability:

```sql
-- On primary
ALTER SYSTEM SET wal_level = replica;
ALTER SYSTEM SET max_wal_senders = 3;
ALTER SYSTEM SET wal_keep_segments = 64;
ALTER SYSTEM SET hot_standby = on;
```

### 2. Redis Sentinel

Configure Redis Sentinel for automatic failover:

```conf
# sentinel.conf
sentinel monitor genesis-redis 127.0.0.1 6379 2
sentinel down-after-milliseconds genesis-redis 5000
sentinel failover-timeout genesis-redis 10000
sentinel parallel-syncs genesis-redis 1
```

### 3. Load Balancer Configuration

HAProxy handles automatic failover between instances:

- Health checks every 5 seconds
- Failover after 3 consecutive failures
- Automatic recovery when instance returns

## Monitoring Setup

### 1. Access Monitoring Dashboards

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3002 (admin/admin)
- **HAProxy Stats**: http://localhost:8404/stats

### 2. Import Grafana Dashboards

1. Log into Grafana
2. Import dashboard JSON from `mcp/grafana-dashboards/`
3. Configure data source to Prometheus

### 3. Configure Alerts

Alerts are automatically loaded from `mcp/alerts/genesis_alerts.yml`

To receive notifications:

1. Configure Alertmanager
2. Set up notification channels (email, Slack, PagerDuty)

## Security Considerations

### 1. SSL/TLS Configuration

```bash
# Generate self-signed cert (development only)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout genesis.key -out genesis.crt

# For production, use Let's Encrypt
certbot --nginx -d api.genesis.com
```

### 2. API Key Rotation

```bash
# Generate new API key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update in environment
export MCP_API_KEY=new_key_here
```

### 3. Network Security

- Use private networks for internal communication
- Enable firewall rules
- Implement rate limiting
- Use VPN for management access

## Maintenance Operations

### 1. Rolling Updates

```bash
# Update primary first
docker-compose -f docker-compose.ha.yml up -d --no-deps mcp-gateway-primary

# Verify health
curl http://localhost:3000/health

# Update backup
docker-compose -f docker-compose.ha.yml up -d --no-deps mcp-gateway-backup
```

### 2. Backup Procedures

```bash
# Database backup
pg_dump -h localhost -U genesis genesis > genesis_backup_$(date +%Y%m%d).sql

# Redis backup
redis-cli BGSAVE
```

### 3. Log Management

```bash
# Rotate logs
logrotate -f /etc/logrotate.d/genesis

# Archive old logs
tar -czf logs_$(date +%Y%m).tar.gz /var/log/genesis/*.log.*
```

## Troubleshooting

### Service Won't Start

1. Check logs: `journalctl -u genesis-orchestrator -f`
2. Verify permissions: `ls -la /opt/genesis`
3. Check port availability: `netstat -tlnp | grep 3000`

### High Latency

1. Check resource usage: `htop`
2. Review slow queries: `pg_stat_statements`
3. Check Redis memory: `redis-cli info memory`

### Failover Not Working

1. Verify health check URLs
2. Check HAProxy configuration
3. Review firewall rules

## Performance Tuning

### 1. PostgreSQL Optimization

```sql
-- Adjust based on available RAM
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
```

### 2. Redis Optimization

```conf
maxmemory 4gb
maxmemory-policy allkeys-lru
save ""  # Disable persistence for cache-only usage
```

### 3. Python/FastAPI Optimization

```python
# Use uvloop for better async performance
import uvloop
uvloop.install()

# Configure workers based on CPU cores
workers = multiprocessing.cpu_count() * 2 + 1
```

## Scaling Guidelines

### Horizontal Scaling

- Add more MCP Gateway instances behind load balancer
- Scale GENESIS Backend based on CPU usage
- Use read replicas for database

### Vertical Scaling

- Minimum: 2 CPU, 4GB RAM
- Recommended: 4 CPU, 8GB RAM
- Production: 8+ CPU, 16GB+ RAM

## Disaster Recovery

### 1. Backup Strategy

- Daily full database backups
- Continuous WAL archiving
- Geo-replicated storage

### 2. Recovery Time Objectives

- RTO: < 1 hour
- RPO: < 15 minutes

### 3. Disaster Recovery Test

Run quarterly DR tests:

1. Simulate primary failure
2. Failover to backup region
3. Restore from backups
4. Verify data integrity

## Support and Resources

- Documentation: `/docs/mcp/`
- Issues: GitHub Issues
- Monitoring: Grafana dashboards
- Logs: `/var/log/genesis/`

---

For production deployment assistance, contact the DevOps team.