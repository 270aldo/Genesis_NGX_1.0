/**
 * GENESIS Pulse Client for NGX_PULSE integration
 */

import { GenesisEcosystemClient } from '../client'
import { GenesisConfig, GenesisResponse } from '../types'
import {
  PulseBiometricRequest,
  PulseBiometricResponse,
  BiometricDataPoint,
  EcosystemRequest
} from '../types/ecosystem'

export class GENESISPulseClient extends GenesisEcosystemClient {
  constructor(config: Omit<GenesisConfig, 'app'>) {
    super({ ...config, app: 'pulse' })
  }

  /**
   * Analyze biometric data using GENESIS agents
   */
  async analyzeBiometrics(
    params: Omit<PulseBiometricRequest, keyof EcosystemRequest>
  ): Promise<GenesisResponse<PulseBiometricResponse>> {
    const request: PulseBiometricRequest = {
      ...params,
      app_id: this.config.app,
      app_version: this.config.version || '1.0.0',
      request_id: this.generateRequestId(),
      timestamp: new Date(),
      metadata: params.metadata || {}
    }

    return this.post<PulseBiometricResponse>('/api/v1/ecosystem/pulse/analyze-biometrics', request)
  }

  /**
   * Analyze HRV data
   */
  async analyzeHRV(
    userId: string,
    hrvData: BiometricDataPoint[],
    depth: 'quick' | 'standard' | 'comprehensive' = 'standard'
  ): Promise<GenesisResponse<PulseBiometricResponse>> {
    return this.analyzeBiometrics({
      user_id: userId,
      biometric_type: 'hrv',
      data_points: hrvData,
      analysis_depth: depth,
      include_recommendations: true
    })
  }

  /**
   * Analyze sleep data
   */
  async analyzeSleep(
    userId: string,
    sleepData: BiometricDataPoint[],
    includeRecommendations: boolean = true
  ): Promise<GenesisResponse<PulseBiometricResponse>> {
    return this.analyzeBiometrics({
      user_id: userId,
      biometric_type: 'sleep',
      data_points: sleepData,
      analysis_depth: 'comprehensive',
      include_recommendations: includeRecommendations
    })
  }

  /**
   * Analyze activity data
   */
  async analyzeActivity(
    userId: string,
    activityData: BiometricDataPoint[]
  ): Promise<GenesisResponse<PulseBiometricResponse>> {
    return this.analyzeBiometrics({
      user_id: userId,
      biometric_type: 'activity',
      data_points: activityData,
      analysis_depth: 'standard',
      include_recommendations: true
    })
  }

  /**
   * Analyze recovery data
   */
  async analyzeRecovery(
    userId: string,
    recoveryData: BiometricDataPoint[]
  ): Promise<GenesisResponse<PulseBiometricResponse>> {
    return this.analyzeBiometrics({
      user_id: userId,
      biometric_type: 'recovery',
      data_points: recoveryData,
      analysis_depth: 'comprehensive',
      include_recommendations: true
    })
  }

  /**
   * Sync wearable data
   */
  async syncWearableData(
    userId: string,
    device: 'whoop' | 'oura' | 'apple_watch' | 'garmin' | 'fitbit',
    startDate: Date,
    endDate: Date = new Date()
  ): Promise<GenesisResponse<any>> {
    return this.post('/api/v1/ecosystem/pulse/sync-wearable', {
      user_id: userId,
      device,
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString(),
      app_id: this.config.app
    })
  }

  /**
   * Get health insights dashboard
   */
  async getHealthInsights(
    userId: string,
    timeRange: 'day' | 'week' | 'month' | 'quarter' = 'week'
  ): Promise<GenesisResponse<any>> {
    return this.get(`/api/v1/ecosystem/pulse/insights/${userId}`, {
      params: { time_range: timeRange }
    })
  }

  /**
   * Get personalized health recommendations
   */
  async getRecommendations(
    userId: string,
    categories: string[] = ['sleep', 'recovery', 'activity', 'nutrition']
  ): Promise<GenesisResponse<any>> {
    return this.post('/api/v1/ecosystem/pulse/recommendations', {
      user_id: userId,
      categories,
      app_id: this.config.app
    })
  }

  /**
   * Set health goals
   */
  async setHealthGoals(
    userId: string,
    goals: Array<{
      metric: string
      target: number
      timeframe: string
    }>
  ): Promise<GenesisResponse<any>> {
    return this.post('/api/v1/ecosystem/pulse/goals', {
      user_id: userId,
      goals,
      app_id: this.config.app
    })
  }

  /**
   * Get anomaly alerts
   */
  async getAnomalyAlerts(
    userId: string,
    severity: 'all' | 'warning' | 'critical' = 'all'
  ): Promise<GenesisResponse<any>> {
    return this.get(`/api/v1/ecosystem/pulse/alerts/${userId}`, {
      params: { severity }
    })
  }

  /**
   * Batch analyze multiple users
   */
  async batchAnalyze(
    users: Array<{
      user_id: string
      biometric_type: PulseBiometricRequest['biometric_type']
      data_points: BiometricDataPoint[]
    }>
  ): Promise<GenesisResponse<PulseBiometricResponse[]>> {
    const requests = users.map(user => ({
      user_id: user.user_id,
      biometric_type: user.biometric_type,
      data_points: user.data_points,
      analysis_depth: 'standard' as const,
      include_recommendations: true,
      app_id: this.config.app,
      app_version: this.config.version || '1.0.0',
      request_id: this.generateRequestId(),
      timestamp: new Date()
    }))

    return this.post<PulseBiometricResponse[]>('/api/v1/ecosystem/pulse/batch-analyze', {
      requests
    })
  }
}