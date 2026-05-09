import { matcherApi } from './client'
import type { MatchResult } from '../types/api'

export const matcher = {
  match: async (resume_id: string, jd_text: string, jd_company?: string, jd_role?: string): Promise<MatchResult> => {
    const { data } = await matcherApi.post('/api/v1/match', {
      resume_id, jd_text, jd_company, jd_role,
    })
    return data
  },

  get: async (id: string): Promise<MatchResult> => {
    const { data } = await matcherApi.get(`/api/v1/match/${id}`)
    return data
  },

  history: async () => {
    const { data } = await matcherApi.get('/api/v1/match/history')
    return data
  },
}