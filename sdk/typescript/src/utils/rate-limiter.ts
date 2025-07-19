/**
 * Rate limiting utility for GENESIS SDK
 */

interface RateLimitConfig {
  requests_per_minute: number
  requests_per_hour: number
}

const RATE_LIMITS: Record<string, RateLimitConfig> = {
  blog: { requests_per_minute: 60, requests_per_hour: 1000 },
  crm: { requests_per_minute: 100, requests_per_hour: 2000 },
  pulse: { requests_per_minute: 120, requests_per_hour: 3000 },
  core: { requests_per_minute: 60, requests_per_hour: 1000 },
  conversations: { requests_per_minute: 200, requests_per_hour: 5000 },
  main: { requests_per_minute: 300, requests_per_hour: 10000 }
}

export class RateLimiter {
  private app: string
  private minuteRequests: number[] = []
  private hourRequests: number[] = []

  constructor(app: string) {
    this.app = app
  }

  async checkLimit(): Promise<void> {
    const now = Date.now()
    const oneMinuteAgo = now - 60 * 1000
    const oneHourAgo = now - 60 * 60 * 1000

    // Clean old requests
    this.minuteRequests = this.minuteRequests.filter(time => time > oneMinuteAgo)
    this.hourRequests = this.hourRequests.filter(time => time > oneHourAgo)

    const limits = RATE_LIMITS[this.app] || RATE_LIMITS.main

    // Check minute limit
    if (this.minuteRequests.length >= limits.requests_per_minute) {
      const oldestRequest = Math.min(...this.minuteRequests)
      const waitTime = oldestRequest + 60 * 1000 - now
      throw new Error(`Rate limit exceeded. Please wait ${Math.ceil(waitTime / 1000)} seconds.`)
    }

    // Check hour limit
    if (this.hourRequests.length >= limits.requests_per_hour) {
      const oldestRequest = Math.min(...this.hourRequests)
      const waitTime = oldestRequest + 60 * 60 * 1000 - now
      throw new Error(`Hourly rate limit exceeded. Please wait ${Math.ceil(waitTime / 60000)} minutes.`)
    }

    // Add current request
    this.minuteRequests.push(now)
    this.hourRequests.push(now)
  }

  getRemainingRequests(): { minute: number; hour: number } {
    const now = Date.now()
    const oneMinuteAgo = now - 60 * 1000
    const oneHourAgo = now - 60 * 60 * 1000

    this.minuteRequests = this.minuteRequests.filter(time => time > oneMinuteAgo)
    this.hourRequests = this.hourRequests.filter(time => time > oneHourAgo)

    const limits = RATE_LIMITS[this.app] || RATE_LIMITS.main

    return {
      minute: Math.max(0, limits.requests_per_minute - this.minuteRequests.length),
      hour: Math.max(0, limits.requests_per_hour - this.hourRequests.length)
    }
  }

  reset(): void {
    this.minuteRequests = []
    this.hourRequests = []
  }
}