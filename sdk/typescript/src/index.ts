/**
 * @ngx/genesis-sdk
 * Official SDK for NGX GENESIS Ecosystem Integration
 * 
 * This SDK provides a unified interface for all NGX ecosystem tools to
 * interact with the GENESIS backend, centralizing AI processing and
 * reducing operational costs.
 */

export { GenesisEcosystemClient } from './client'
export { GenesisAuthClient } from './auth'
export { GenesisAgentsClient } from './agents'
export { GENESISBlogClient } from './ecosystem/blog'
export { GENESISCRMClient } from './ecosystem/crm'
export { GENESISPulseClient } from './ecosystem/pulse'
export { GENESISCoreClient } from './ecosystem/core'
export { GENESISConversationsClient } from './ecosystem/conversations'

// Export types
export * from './types'
export * from './types/ecosystem'

// Export utilities
export * from './utils/errors'
export * from './utils/logger'
export * from './utils/rate-limiter'

// Export version
export const VERSION = '1.0.0'