import { analyticsApi } from './client'
import type { DashboardSummary, FunnelResponse } from '../types/api'

export const analytics = {
  dashboard: async (): Promise<DashboardSummary> => {
    const { data } = await analyticsApi.get('/api/v1/analytics/dashboard')
    return data
  },

  funnel: async (): Promise<FunnelResponse> => {
    const { data } = await analyticsApi.get('/api/v1/analytics/funnel')
    return data
  },

  resumeComparison: async () => {
    const { data } = await analyticsApi.get('/api/v1/analytics/resumes')
    return data
  },

  scoreCallback: async () => {
    const { data } = await analyticsApi.get('/api/v1/analytics/score-callback')
    return data
  },

  trends: async (period: 'weekly' | 'monthly' = 'weekly') => {
    const { data } = await analyticsApi.get('/api/v1/analytics/trends', { params: { period } })
    return data
  },
}