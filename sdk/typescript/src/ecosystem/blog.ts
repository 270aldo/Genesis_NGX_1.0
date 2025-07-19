/**
 * GENESIS Blog Client for NGX_AGENTS_BLOG integration
 */

import { GenesisEcosystemClient } from '../client'
import { GenesisConfig, GenesisResponse } from '../types'
import {
  BlogContentRequest,
  BlogContentResponse,
  EcosystemRequest
} from '../types/ecosystem'

export class GENESISBlogClient extends GenesisEcosystemClient {
  constructor(config: Omit<GenesisConfig, 'app'>) {
    super({ ...config, app: 'blog' })
  }

  /**
   * Generate blog content using GENESIS agents
   */
  async generateContent(params: Omit<BlogContentRequest, keyof EcosystemRequest>): Promise<GenesisResponse<BlogContentResponse>> {
    const request: BlogContentRequest = {
      ...params,
      app_id: this.config.app,
      app_version: this.config.version || '1.0.0',
      request_id: this.generateRequestId(),
      timestamp: new Date(),
      metadata: params.metadata || {}
    }

    return this.post<BlogContentResponse>('/api/v1/ecosystem/blog/generate-content', request)
  }

  /**
   * Generate article with default settings
   */
  async generateArticle(
    topic: string,
    authorAgent: string = 'sage',
    wordCount: number = 800
  ): Promise<GenesisResponse<BlogContentResponse>> {
    return this.generateContent({
      topic,
      author_agent: authorAgent,
      content_type: 'article',
      target_audience: 'general',
      word_count: wordCount,
      include_examples: true,
      seo_keywords: []
    })
  }

  /**
   * Generate tutorial content
   */
  async generateTutorial(
    topic: string,
    authorAgent: string = 'blaze',
    audience: 'beginner' | 'intermediate' | 'advanced' = 'beginner'
  ): Promise<GenesisResponse<BlogContentResponse>> {
    return this.generateContent({
      topic,
      author_agent: authorAgent,
      content_type: 'tutorial',
      target_audience: audience,
      word_count: 1200,
      include_examples: true,
      seo_keywords: []
    })
  }

  /**
   * Generate research content
   */
  async generateResearch(
    topic: string,
    authorAgent: string = 'nova',
    keywords: string[] = []
  ): Promise<GenesisResponse<BlogContentResponse>> {
    return this.generateContent({
      topic,
      author_agent: authorAgent,
      content_type: 'research',
      target_audience: 'advanced',
      word_count: 2000,
      include_examples: true,
      seo_keywords: keywords
    })
  }

  /**
   * Get content suggestions based on trending topics
   */
  async getContentSuggestions(
    category: string,
    count: number = 5
  ): Promise<GenesisResponse<string[]>> {
    // This would call a specialized endpoint
    return this.post<string[]>('/api/v1/ecosystem/blog/suggestions', {
      category,
      count,
      app_id: this.config.app
    })
  }

  /**
   * Analyze content performance
   */
  async analyzeContent(
    contentId: string,
    metrics: string[] = ['readability', 'seo', 'engagement']
  ): Promise<GenesisResponse<any>> {
    return this.post('/api/v1/ecosystem/blog/analyze', {
      content_id: contentId,
      metrics,
      app_id: this.config.app
    })
  }

  /**
   * Batch generate multiple content pieces
   */
  async batchGenerate(
    requests: Array<Omit<BlogContentRequest, keyof EcosystemRequest>>
  ): Promise<GenesisResponse<BlogContentResponse[]>> {
    const batchRequests = requests.map(req => ({
      ...req,
      app_id: this.config.app,
      app_version: this.config.version || '1.0.0',
      request_id: this.generateRequestId(),
      timestamp: new Date()
    }))

    return this.post<BlogContentResponse[]>('/api/v1/ecosystem/blog/batch-generate', {
      requests: batchRequests
    })
  }
}