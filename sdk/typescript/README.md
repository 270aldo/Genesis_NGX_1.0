# @ngx/genesis-sdk

Official TypeScript SDK for NGX GENESIS Ecosystem Integration

## Overview

The GENESIS SDK provides a unified interface for all NGX ecosystem tools to interact with the GENESIS backend, centralizing AI processing and reducing operational costs by up to 80%.

## Installation

```bash
npm install @ngx/genesis-sdk
# or
yarn add @ngx/genesis-sdk
```

## Quick Start

```typescript
import { GenesisAuthClient, GenesisAgentsClient } from '@ngx/genesis-sdk'

// Initialize auth client
const auth = new GenesisAuthClient({
  baseURL: 'https://api.genesis.ngx.com',
  apiKey: 'your-api-key'
})

// Login
const { data: tokens } = await auth.login('user@example.com', 'password')

// Initialize agents client with auth token
const agents = new GenesisAgentsClient({
  baseURL: 'https://api.genesis.ngx.com',
  apiKey: tokens.access_token
})

// Ask an agent
const { data: response } = await agents.askSage('What should I eat for breakfast?')
console.log(response.response)
```

## Ecosystem Clients

### Blog Client (NGX_AGENTS_BLOG)

```typescript
import { GENESISBlogClient } from '@ngx/genesis-sdk'

const blog = new GENESISBlogClient({
  baseURL: 'https://api.genesis.ngx.com',
  apiKey: 'your-api-key'
})

// Generate an article
const { data } = await blog.generateArticle(
  'The Science of Recovery',
  'wave', // agent to use
  1000    // word count
)
```

### CRM Client (NEXUS-CRM)

```typescript
import { GENESISCRMClient } from '@ngx/genesis-sdk'

const crm = new GENESISCRMClient({
  baseURL: 'https://api.genesis.ngx.com',
  apiKey: 'your-api-key'
})

// Analyze customer
const { data } = await crm.calculateChurnRisk(
  'customer-123',
  { usage_days: 45, sessions: 120 },
  90 // prediction window
)
```

### Pulse Client (NGX_PULSE)

```typescript
import { GENESISPulseClient } from '@ngx/genesis-sdk'

const pulse = new GENESISPulseClient({
  baseURL: 'https://api.genesis.ngx.com',
  apiKey: 'your-api-key'
})

// Analyze HRV data
const { data } = await pulse.analyzeHRV(
  'user-123',
  [
    { timestamp: '2024-01-15T08:00:00Z', value: 65, unit: 'ms' },
    { timestamp: '2024-01-15T09:00:00Z', value: 72, unit: 'ms' }
  ]
)
```

### Core Client (NEXUS_CORE)

```typescript
import { GENESISCoreClient } from '@ngx/genesis-sdk'

const core = new GENESISCoreClient({
  baseURL: 'https://api.genesis.ngx.com',
  apiKey: 'your-api-key'
})

// Execute workflow
const { data } = await core.executeAnalysis(
  'monthly-performance',
  { time_range: '30d', metrics: ['engagement', 'retention'] }
)
```

### Conversations Client (NEXUS_Conversations)

```typescript
import { GENESISConversationsClient } from '@ngx/genesis-sdk'

const conversations = new GENESISConversationsClient({
  baseURL: 'https://api.genesis.ngx.com',
  apiKey: 'your-api-key'
})

// Get conversation insights
const { data } = await conversations.getSummary('session-123')
```

## Authentication

The SDK supports multiple authentication methods:

```typescript
// Email/Password
await auth.login('user@example.com', 'password')

// Refresh token
await auth.refreshToken()

// Check auth status
if (auth.isAuthenticated()) {
  // Make authenticated requests
}
```

## Error Handling

All SDK methods return a `GenesisResponse` object:

```typescript
interface GenesisResponse<T> {
  success: boolean
  data?: T
  error?: {
    code: string
    message: string
    details?: any
  }
}

// Example usage
const { success, data, error } = await agents.runAgent('nexus', { prompt: 'Hello' })

if (success) {
  console.log(data)
} else {
  console.error(error.message)
}
```

## Rate Limiting

The SDK includes built-in rate limiting per application:

- Blog: 60 req/min, 1000 req/hour
- CRM: 100 req/min, 2000 req/hour
- Pulse: 120 req/min, 3000 req/hour
- Core: 60 req/min, 1000 req/hour
- Conversations: 200 req/min, 5000 req/hour

## Configuration

```typescript
const client = new GenesisEcosystemClient({
  baseURL: 'https://api.genesis.ngx.com',
  apiKey: 'your-api-key',
  app: 'blog', // Application identifier
  version: '1.0.0',
  timeout: 30000, // 30 seconds
  maxRetries: 3,
  debug: true // Enable debug logging
})

// Update configuration
client.updateConfig({
  apiKey: 'new-api-key'
})
```

## Streaming Responses

For real-time streaming responses:

```typescript
await agents.streamAgent(
  'nexus',
  { prompt: 'Tell me a story' },
  (chunk) => {
    // Handle each chunk
    process.stdout.write(chunk)
  },
  () => {
    // Complete callback
    console.log('\nDone!')
  },
  (error) => {
    // Error callback
    console.error('Stream error:', error)
  }
)
```

## TypeScript Support

The SDK is written in TypeScript and provides full type definitions:

```typescript
import type {
  GenesisAgent,
  GenesisResponse,
  BlogContentRequest,
  CRMAnalysisResponse
} from '@ngx/genesis-sdk'
```

## Examples

See the `/examples` directory for more detailed usage examples:

- Basic authentication flow
- Blog content generation pipeline
- Customer analysis automation
- Health metrics dashboard
- Multi-agent conversations

## Development

```bash
# Install dependencies
npm install

# Build SDK
npm run build

# Run tests
npm test

# Type checking
npm run type-check

# Linting
npm run lint
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT © NGX Technologies

## Support

- Documentation: https://docs.genesis.ngx.com
- Issues: https://github.com/ngx-technologies/genesis-sdk/issues
- Discord: https://discord.gg/ngx-genesis