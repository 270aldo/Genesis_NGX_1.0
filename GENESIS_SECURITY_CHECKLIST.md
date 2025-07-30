# 🔒 GENESIS SECURITY CHECKLIST
## Critical Security Tasks for Production Readiness

> **Priority**: CRITICAL - Complete these before ANY production deployment

## 🚨 IMMEDIATE ACTIONS (Day 1)

### Secrets & Environment Variables
- [ ] **Remove hardcoded JWT fallback** in `/backend/app/core/server.py:117`
  ```python
  # REMOVE THIS:
  secret_key=getattr(settings, "jwt_secret", "dev-secret-key")
  # REPLACE WITH:
  secret_key=settings.jwt_secret  # Will fail if not set
  ```

- [ ] **Audit all .env files**
  ```bash
  find . -name "*.env*" -type f | grep -v .gitignore
  ```

- [ ] **Rotate all existing secrets**
  - [ ] JWT_SECRET
  - [ ] SUPABASE_KEY
  - [ ] SUPABASE_JWT_SECRET
  - [ ] GOOGLE_APPLICATION_CREDENTIALS
  - [ ] Any API keys

### Dependency Security
- [ ] **Update vulnerable packages**
  ```bash
  cd backend
  pip install --upgrade cryptography urllib3 requests
  poetry update
  pip-audit
  ```

- [ ] **Frontend dependency audit**
  ```bash
  cd frontend
  npm audit fix
  npm update
  ```

---

## 🛡️ API SECURITY (Day 2-3)

### CORS Configuration
- [ ] **Update CORS settings** in `/backend/app/core/server.py`
  ```python
  # Current (INSECURE):
  allow_origins=["*"]
  allow_headers=["*"]
  
  # Replace with:
  allow_origins=[
      "https://app.genesis-ngx.com",
      "https://staging.genesis-ngx.com",
      "http://localhost:5173" if settings.debug else None
  ].filter(None)
  
  allow_headers=[
      "Authorization",
      "Content-Type", 
      "X-Request-ID",
      "X-Session-ID"
  ]
  ```

### Host Validation
- [ ] **Fix TrustedHostMiddleware**
  ```python
  # Current (INSECURE):
  allowed_hosts=["*"]
  
  # Replace with:
  allowed_hosts=[
      "api.genesis-ngx.com",
      "localhost" if settings.debug else None,
      "127.0.0.1" if settings.debug else None
  ].filter(None)
  ```

### Rate Limiting
- [ ] **Implement auth-specific rate limiting**
  ```python
  from slowapi import Limiter
  from slowapi.util import get_remote_address
  
  auth_limiter = Limiter(
      key_func=get_remote_address,
      default_limits=["100/hour"]
  )
  
  @router.post("/login")
  @auth_limiter.limit("5/minute")
  async def login(...):
  ```

- [ ] **Add rate limiting by user**
  ```python
  def get_user_id(request: Request):
      # Extract user ID from JWT
      return user_id or get_remote_address(request)
  
  user_limiter = Limiter(key_func=get_user_id)
  ```

### Input Validation
- [ ] **Add global input sanitization**
  ```python
  from bleach import clean
  
  class SanitizationMiddleware:
      async def __call__(self, request: Request, call_next):
          if request.method in ["POST", "PUT", "PATCH"]:
              body = await request.body()
              # Sanitize input
          return await call_next(request)
  ```

- [ ] **Validate all JSON inputs**
  - [ ] Check max size
  - [ ] Validate nested depth
  - [ ] Sanitize strings
  - [ ] Validate data types

---

## 🔐 AUTHENTICATION & AUTHORIZATION (Day 3)

### Token Security
- [ ] **Implement token refresh**
  ```python
  @router.post("/auth/refresh")
  async def refresh_token(
      refresh_token: str = Body(...),
      db: AsyncSession = Depends(get_db)
  ):
      # Implement refresh logic
  ```

- [ ] **Add token revocation**
  ```python
  # Create revoked_tokens table
  # Check token against revocation list
  ```

- [ ] **Implement session timeout**
  - [ ] 30 min access token
  - [ ] 7 day refresh token
  - [ ] Sliding session option

### Password Security
- [ ] **Enforce password policy**
  ```python
  PASSWORD_RULES = {
      "min_length": 12,
      "require_uppercase": True,
      "require_lowercase": True,
      "require_numbers": True,
      "require_special": True,
      "check_breach": True  # HaveIBeenPwned
  }
  ```

- [ ] **Implement account lockout**
  - [ ] 5 failed attempts = 15 min lockout
  - [ ] Progressive delays
  - [ ] CAPTCHA after 3 attempts

---

## 📊 SECURITY MONITORING (Day 4)

### Logging & Auditing
- [ ] **Create security logger**
  ```python
  class SecurityLogger:
      def log_auth_failure(self, user_id, ip, reason):
          logger.warning(f"AUTH_FAIL: {user_id} from {ip} - {reason}")
          
      def log_suspicious_activity(self, event_type, details):
          logger.error(f"SUSPICIOUS: {event_type} - {details}")
          
      def log_data_access(self, user_id, resource, action):
          logger.info(f"DATA_ACCESS: {user_id} {action} {resource}")
  ```

- [ ] **Implement audit trail**
  - [ ] All data modifications
  - [ ] Permission changes
  - [ ] Admin actions
  - [ ] Failed auth attempts

### Intrusion Detection
- [ ] **Detect anomalies**
  ```python
  class AnomalyDetector:
      async def check_request_pattern(self, user_id, endpoint):
          # Check for unusual patterns
          # - Rapid requests
          # - Unusual endpoints
          # - Geographic anomalies
  ```

- [ ] **Alert on suspicious activity**
  - [ ] Multiple failed logins
  - [ ] Unusual API usage
  - [ ] Data exfiltration attempts
  - [ ] SQL injection attempts

---

## 🏥 GDPR/HIPAA COMPLIANCE (Day 5)

### Data Privacy
- [ ] **Implement data export**
  ```python
  @router.get("/users/me/data")
  async def export_user_data(user: User = Depends(get_current_user)):
      # Export all user data in JSON/CSV
  ```

- [ ] **Right to deletion**
  ```python
  @router.delete("/users/me")
  async def delete_user_data(user: User = Depends(get_current_user)):
      # Soft delete with anonymization
      # Hard delete after retention period
  ```

- [ ] **Consent management**
  ```python
  @router.post("/users/me/consent")
  async def update_consent(
      consent: ConsentUpdate,
      user: User = Depends(get_current_user)
  ):
      # Track consent changes
  ```

### Data Protection
- [ ] **Encrypt PII at rest**
  ```python
  from cryptography.fernet import Fernet
  
  class PIIEncryption:
      def encrypt_field(self, value: str) -> str:
          return self.cipher.encrypt(value.encode())
          
      def decrypt_field(self, encrypted: str) -> str:
          return self.cipher.decrypt(encrypted).decode()
  ```

- [ ] **Implement data retention**
  - [ ] User data: 7 years
  - [ ] Logs: 1 year
  - [ ] Sessions: 30 days
  - [ ] Automated cleanup

---

## 🔍 SECURITY HEADERS (Quick Wins)

### Add Missing Headers
- [ ] **Implement all security headers**
  ```python
  SECURITY_HEADERS = {
      "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
      "X-Content-Type-Options": "nosniff",
      "X-Frame-Options": "DENY",
      "X-XSS-Protection": "1; mode=block",
      "Referrer-Policy": "strict-origin-when-cross-origin",
      "Permissions-Policy": "geolocation=(), camera=(), microphone=()",
      "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'",
      "Expect-CT": "max-age=86400, enforce"
  }
  ```

---

## 📋 SECURITY TESTING CHECKLIST

### Automated Testing
- [ ] **SAST (Static Analysis)**
  ```bash
  # Python
  bandit -r backend/
  safety check
  
  # JavaScript
  npm audit
  eslint --ext .js,.jsx,.ts,.tsx .
  ```

- [ ] **DAST (Dynamic Analysis)**
  - [ ] OWASP ZAP scan
  - [ ] Burp Suite testing
  - [ ] API fuzzing

### Manual Testing
- [ ] **Authentication bypass attempts**
- [ ] **SQL injection tests**
- [ ] **XSS payload tests**
- [ ] **CSRF validation**
- [ ] **Authorization checks**
- [ ] **Rate limit testing**

---

## 🚀 DEPLOYMENT SECURITY

### Infrastructure
- [ ] **Secure environment variables**
  - [ ] Use AWS Secrets Manager
  - [ ] Or HashiCorp Vault
  - [ ] Never commit .env files

- [ ] **Network security**
  - [ ] Configure firewall rules
  - [ ] Use VPC/private subnets
  - [ ] Enable DDoS protection
  - [ ] Configure WAF rules

### Monitoring
- [ ] **Set up alerts for:**
  - [ ] Failed auth > 10/minute
  - [ ] 500 errors > 5/minute
  - [ ] Unusual traffic patterns
  - [ ] Database connection failures
  - [ ] High memory/CPU usage

---

## ✅ VALIDATION CHECKLIST

Before marking security as complete:

### Code Review
- [ ] No hardcoded secrets
- [ ] No commented credentials
- [ ] No debug endpoints
- [ ] No console.logs with sensitive data

### Configuration
- [ ] All secrets in env vars
- [ ] Secure defaults
- [ ] No wildcards in production
- [ ] Proper error messages (no stack traces)

### Testing
- [ ] Security test suite passes
- [ ] Penetration test conducted
- [ ] Vulnerability scan clean
- [ ] Load test completed

### Documentation
- [ ] Security procedures documented
- [ ] Incident response plan
- [ ] Data breach protocol
- [ ] Recovery procedures

---

## 🏆 SECURITY SCORECARD

Track your progress:

| Category | Status | Score |
|----------|--------|-------|
| Secrets Management | 🔴 TODO | 0/10 |
| API Security | 🔴 TODO | 0/10 |
| Authentication | 🔴 TODO | 0/10 |
| Data Protection | 🔴 TODO | 0/10 |
| Monitoring | 🔴 TODO | 0/10 |
| **TOTAL** | **TODO** | **0/50** |

**Target: 45/50 minimum for production**

---

## 🆘 EMERGENCY CONTACTS

In case of security incident:

1. **Immediate**: Disable affected services
2. **Alert**: Team lead and CTO
3. **Document**: Everything in incident log
4. **Investigate**: Root cause analysis
5. **Remediate**: Fix and deploy
6. **Report**: Update stakeholders

---

**Remember**: Security is not a feature, it's a requirement. Take it seriously! 🔒