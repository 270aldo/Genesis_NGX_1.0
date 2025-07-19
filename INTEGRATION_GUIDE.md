# 🔌 GENESIS Ecosystem Integration Guide

> Step-by-step guide for integrating NGX tools with GENESIS central intelligence

## 📚 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [SDK Installation](#sdk-installation)
4. [Authentication](#authentication)
5. [Tool-Specific Integrations](#tool-specific-integrations)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## 🌐 Overview

GENESIS serves as the central AI brain for the entire NGX ecosystem. This guide will help you integrate your NGX tool to leverage GENESIS's powerful AI capabilities while reducing costs by up to 80%.

### Benefits of Integration
- ✅ Centralized AI processing (no separate Vertex AI costs)
- ✅ Unified user experience
- ✅ Shared context across tools
- ✅ Automatic updates and improvements
- ✅ Built-in compliance and security

## 📋 Prerequisites

Before starting integration, ensure you have:

1. **API Credentials**
   - GENESIS API Key
   - Tool-specific App ID
   - Webhook secret (if applicable)

2. **Development Environment**
   - Node.js 18+ (for JavaScript/TypeScript)
   - Python 3.11+ (for Python)
   - Docker (optional, for testing)

3. **Access Requirements**
   - GENESIS staging environment access
   - Tool repository write access
   - Monitoring dashboard access

## 📦 SDK Installation

### TypeScript/JavaScript

```bash
# NPM
npm install @ngx/genesis-sdk

# Yarn
yarn add @ngx/genesis-sdk

# PNPM
pnpm add @ngx/genesis-sdk
```

### Python (Coming Soon)

```bash
pip install ngx-genesis-sdk
```

## 🔐 Authentication

### Environment Variables

Create a `.env` file in your project root:

```env
# GENESIS Configuration
GENESIS_API_URL=https://api.genesis.ngx.com
GENESIS_API_KEY=your-api-key-here
GENESIS_APP_ID=your-app-id  # blog, crm, pulse, core, conversations

# Optional
GENESIS_API_VERSION=1.0.0
GENESIS_TIMEOUT=30000
GENESIS_DEBUG=false
```

### Basic Setup

```typescript
import { GenesisEcosystemClient } from '@ngx/genesis-sdk'

const client = new GenesisEcosystemClient({
  baseURL: process.env.GENESIS_API_URL,
  apiKey: process.env.GENESIS_API_KEY,
  app: process.env.GENESIS_APP_ID,
  debug: process.env.NODE_ENV === 'development'
})

// Test connection
const { success, data } = await client.healthCheck()
if (success) {
  console.log('Connected to GENESIS!')
}
```

## 🛠️ Tool-Specific Integrations

### 1. NGX_AGENTS_BLOG Integration

#### Step 1: Install SDK

```bash
cd ngx_agents_blog
npm install @ngx/genesis-sdk
```

#### Step 2: Create Genesis Service

```typescript
// services/genesis.service.ts
import { GENESISBlogClient } from '@ngx/genesis-sdk'

export const genesisClient = new GENESISBlogClient({
  baseURL: process.env.GENESIS_API_URL!,
  apiKey: process.env.GENESIS_API_KEY!
})

// Helper functions
export async function generateArticle(topic: string, agent: string = 'sage') {
  const { success, data, error } = await genesisClient.generateArticle(
    topic,
    agent,
    800 // word count
  )
  
  if (!success) {
    throw new Error(error?.message || 'Failed to generate article')
  }
  
  return data
}
```

#### Step 3: Update Existing Code

Replace direct AI calls with GENESIS SDK:

```typescript
// Before
const article = await vertexAI.generateContent(prompt)

// After
const article = await generateArticle(topic, 'sage')
```

#### Step 4: Implement Caching

```typescript
import { Redis } from 'ioredis'

const redis = new Redis()

export async function getCachedArticle(topic: string) {
  const cacheKey = `article:${topic.toLowerCase().replace(/\s+/g, '-')}`
  
  // Check cache
  const cached = await redis.get(cacheKey)
  if (cached) return JSON.parse(cached)
  
  // Generate new
  const article = await generateArticle(topic)
  
  // Cache for 24 hours
  await redis.setex(cacheKey, 86400, JSON.stringify(article))
  
  return article
}
```

#### Step 5: Setup Webhooks

```typescript
// routes/webhooks.ts
app.post('/webhooks/genesis', async (req, res) => {
  const { event, data } = req.body
  
  switch (event) {
    case 'content.generated':
      await publishArticle(data.content)
      break
    case 'content.updated':
      await updateArticle(data.content)
      break
  }
  
  res.json({ received: true })
})
```

### 2. NEXUS-CRM Integration

#### Step 1: Install Dependencies

```bash
cd nexus-crm
npm install @ngx/genesis-sdk
```

#### Step 2: Create CRM Service

```typescript
// services/genesis-crm.service.ts
import { GENESISCRMClient } from '@ngx/genesis-sdk'

class GenesisCRMService {
  private client: GENESISCRMClient
  
  constructor() {
    this.client = new GENESISCRMClient({
      baseURL: process.env.GENESIS_API_URL!,
      apiKey: process.env.GENESIS_API_KEY!
    })
  }
  
  async analyzeCustomer(customerId: string) {
    // Get customer data from your database
    const customer = await db.customers.findOne(customerId)
    
    // Analyze with GENESIS
    const { data } = await this.client.analyzeBehavior(
      customerId,
      {
        signupDate: customer.createdAt,
        lastActive: customer.lastActiveAt,
        totalSessions: customer.sessionCount,
        subscription: customer.plan,
        engagement: customer.engagementScore
      }
    )
    
    // Store insights
    await db.customerInsights.upsert({
      customerId,
      ...data
    })
    
    return data
  }
  
  async trackAgentUsage(customerId: string, usage: any) {
    await this.client.trackAgentUsage(customerId, usage.agentId, {
      duration: usage.duration,
      queries: usage.queryCount,
      satisfaction: usage.rating
    })
  }
}

export const genesisCRM = new GenesisCRMService()
```

#### Step 3: Implement Real-time Tracking

```typescript
// middleware/tracking.middleware.ts
export async function trackGenesisUsage(req, res, next) {
  const startTime = Date.now()
  
  res.on('finish', async () => {
    if (req.path.includes('/api/genesis/')) {
      await genesisCRM.trackAgentUsage(req.user.id, {
        agentId: req.params.agentId,
        duration: Date.now() - startTime,
        queryCount: 1,
        rating: req.body.rating
      })
    }
  })
  
  next()
}
```

#### Step 4: Setup Automated Insights

```typescript
// jobs/customer-insights.job.ts
import { CronJob } from 'cron'

// Run every day at 2 AM
new CronJob('0 2 * * *', async () => {
  const customers = await db.customers.findActive()
  
  for (const customer of customers) {
    try {
      const insights = await genesisCRM.analyzeCustomer(customer.id)
      
      // Check for alerts
      if (insights.predictions.churn_risk > 0.7) {
        await notifyAccountManager(customer, 'HIGH_CHURN_RISK')
      }
      
      if (insights.predictions.ltv_estimate > 5000) {
        await notifyAccountManager(customer, 'HIGH_VALUE_CUSTOMER')
      }
    } catch (error) {
      logger.error('Customer analysis failed', { customerId: customer.id, error })
    }
  }
})
```

### 3. NGX_PULSE Integration

#### Step 1: Setup Biometric Pipeline

```typescript
// services/genesis-pulse.service.ts
import { GENESISPulseClient } from '@ngx/genesis-sdk'

export class BiometricAnalyzer {
  private client: GENESISPulseClient
  
  constructor() {
    this.client = new GENESISPulseClient({
      baseURL: process.env.GENESIS_API_URL!,
      apiKey: process.env.GENESIS_API_KEY!
    })
  }
  
  async processWearableData(userId: string, device: string, data: any[]) {
    // Transform device-specific data to standard format
    const biometricData = this.transformData(device, data)
    
    // Analyze with GENESIS
    const { data: analysis } = await this.client.analyzeBiometrics({
      user_id: userId,
      biometric_type: this.detectType(biometricData),
      data_points: biometricData,
      analysis_depth: 'comprehensive',
      include_recommendations: true
    })
    
    return analysis
  }
  
  private transformData(device: string, rawData: any[]) {
    switch (device) {
      case 'whoop':
        return rawData.map(d => ({
          timestamp: d.recorded_at,
          value: d.hrv,
          unit: 'ms',
          device: 'whoop',
          metadata: { strain: d.strain, recovery: d.recovery }
        }))
      case 'oura':
        return rawData.map(d => ({
          timestamp: d.day,
          value: d.hrv_average,
          unit: 'ms',
          device: 'oura',
          metadata: { readiness: d.readiness_score }
        }))
      // Add more device mappings
    }
  }
}
```

#### Step 2: Real-time Streaming

```typescript
// websocket/biometric-stream.ts
import { WebSocket } from 'ws'

export function setupBiometricStream(wss: WebSocket.Server) {
  wss.on('connection', (ws, req) => {
    const userId = getUserFromRequest(req)
    
    ws.on('message', async (data) => {
      const biometric = JSON.parse(data.toString())
      
      // Quick analysis for real-time feedback
      const { data: result } = await pulseClient.analyzeBiometrics({
        user_id: userId,
        biometric_type: biometric.type,
        data_points: [biometric],
        analysis_depth: 'quick',
        include_recommendations: false
      })
      
      // Send back insights
      ws.send(JSON.stringify({
        type: 'insight',
        data: result
      }))
      
      // Check for alerts
      if (result.metrics.risk_factors.length > 0) {
        ws.send(JSON.stringify({
          type: 'alert',
          severity: 'warning',
          message: 'Abnormal reading detected'
        }))
      }
    })
  })
}
```

### 4. NEXUS_CORE Integration

#### Step 1: Workflow Engine Setup

```typescript
// services/genesis-workflows.service.ts
import { GENESISCoreClient } from '@ngx/genesis-sdk'

export class WorkflowEngine {
  private client: GENESISCoreClient
  
  constructor() {
    this.client = new GENESISCoreClient({
      baseURL: process.env.GENESIS_API_URL!,
      apiKey: process.env.GENESIS_API_KEY!
    })
  }
  
  async executeMonthlyReport(params: any) {
    const { data } = await this.client.generateReport(
      'monthly_executive',
      {
        time_range: 'last_30_days',
        metrics: ['user_growth', 'revenue', 'engagement', 'health_outcomes'],
        format: 'pdf'
      }
    )
    
    // Send to executives
    await emailService.send({
      to: params.recipients,
      subject: 'Monthly Executive Report',
      attachments: [data.report_url]
    })
    
    return data
  }
  
  async createAutomation(config: any) {
    return await this.client.createAutomation(
      config.name,
      {
        type: config.trigger.type,
        config: config.trigger.params
      },
      config.actions
    )
  }
}
```

### 5. NEXUS_Conversations Integration

#### Step 1: Enhanced Insights

```typescript
// services/conversation-insights.service.ts
import { GENESISConversationsClient } from '@ngx/genesis-sdk'

export class ConversationInsights {
  private client: GENESISConversationsClient
  
  async analyzeSession(sessionId: string) {
    // Get all insights types
    const [summary, chemistry, virality, quality] = await Promise.all([
      this.client.getSummary(sessionId),
      this.client.analyzeChemistry(sessionId),
      this.client.calculateVirality(sessionId),
      this.client.assessQuality(sessionId)
    ])
    
    return {
      sessionId,
      insights: {
        summary: summary.data,
        chemistry: chemistry.data,
        virality: virality.data,
        quality: quality.data
      }
    }
  }
}
```

## 📊 Best Practices

### 1. Error Handling

Always handle SDK errors gracefully:

```typescript
try {
  const { success, data, error } = await client.someMethod()
  
  if (!success) {
    // Log error details
    logger.error('GENESIS API Error', {
      code: error.code,
      message: error.message,
      details: error.details
    })
    
    // Fallback logic
    return getFallbackResponse()
  }
  
  return data
} catch (error) {
  // Network or unexpected errors
  logger.error('Unexpected error', error)
  throw new ServiceUnavailableError('GENESIS service temporarily unavailable')
}
```

### 2. Rate Limiting

Respect rate limits to avoid service disruption:

```typescript
import { RateLimiter } from 'limiter'

// Tool-specific limits
const limiter = new RateLimiter({
  tokensPerInterval: 60,  // requests
  interval: 'minute'
})

async function makeRequest() {
  await limiter.removeTokens(1)
  return client.makeApiCall()
}
```

### 3. Caching Strategy

Implement intelligent caching:

```typescript
class CacheManager {
  private cache = new Map()
  private ttls = {
    agents: 3600,        // 1 hour
    content: 86400,      // 24 hours
    analysis: 1800,      // 30 minutes
    insights: 300        // 5 minutes
  }
  
  async get(key: string, fetcher: () => Promise<any>, type: string) {
    const cached = this.cache.get(key)
    
    if (cached && cached.expires > Date.now()) {
      return cached.data
    }
    
    const data = await fetcher()
    
    this.cache.set(key, {
      data,
      expires: Date.now() + (this.ttls[type] * 1000)
    })
    
    return data
  }
}
```

### 4. Monitoring

Track integration health:

```typescript
import { StatsD } from 'node-statsd'

const metrics = new StatsD()

// Track API calls
async function trackApiCall(method: string, success: boolean, duration: number) {
  metrics.increment(`genesis.api.${method}.${success ? 'success' : 'error'}`)
  metrics.timing(`genesis.api.${method}.duration`, duration)
}

// Usage
const start = Date.now()
const result = await client.generateContent(...)
trackApiCall('generateContent', result.success, Date.now() - start)
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Authentication Errors

**Error**: `401 Unauthorized`

**Solution**:
- Verify API key is correct
- Check API key hasn't expired
- Ensure app ID matches your tool

```typescript
// Debug authentication
console.log('API Key:', process.env.GENESIS_API_KEY?.substring(0, 10) + '...')
console.log('App ID:', process.env.GENESIS_APP_ID)
```

#### 2. Rate Limiting

**Error**: `429 Too Many Requests`

**Solution**:
- Implement exponential backoff
- Use caching more aggressively
- Request rate limit increase if needed

```typescript
async function retryWithBackoff(fn: Function, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn()
    } catch (error) {
      if (error.status === 429 && i < maxRetries - 1) {
        await sleep(Math.pow(2, i) * 1000)
        continue
      }
      throw error
    }
  }
}
```

#### 3. Timeout Issues

**Error**: `Request timeout`

**Solution**:
- Increase timeout for long operations
- Use async endpoints for heavy processing
- Implement progress tracking

```typescript
const client = new GenesisClient({
  timeout: 60000, // 60 seconds for heavy operations
  // ... other config
})
```

#### 4. Data Format Errors

**Error**: `Invalid request format`

**Solution**:
- Validate data before sending
- Check API documentation
- Use TypeScript types

```typescript
import { z } from 'zod'

const BiometricSchema = z.object({
  timestamp: z.string().datetime(),
  value: z.number(),
  unit: z.string(),
  device: z.string().optional()
})

// Validate before sending
const validated = BiometricSchema.parse(data)
```

### Debug Mode

Enable debug logging for troubleshooting:

```typescript
const client = new GenesisClient({
  debug: true,  // Enables detailed logging
  // ... other config
})

// Or set via environment
GENESIS_DEBUG=true npm start
```

## 📞 Support

### Resources
- **Documentation**: https://docs.genesis.ngx.com
- **API Reference**: https://api.genesis.ngx.com/docs
- **Status Page**: https://status.genesis.ngx.com

### Contact
- **Technical Support**: support@ngx.com
- **Slack Channel**: #genesis-integration
- **Office Hours**: Monday-Friday 9am-5pm PST

---

**Last Updated**: 2025-07-17  
**Version**: 1.0.0  
**Maintainers**: NGX Platform Team