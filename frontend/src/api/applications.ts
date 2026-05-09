import { trackerApi } from './client'
import type { Application, KanbanBoard, ApplicationStatus } from '../types/api'

export const applications = {
  list: async (status?: string): Promise<{ applications: Application[]; total: number }> => {
    const params = status ? { status } : {}
    const { data } = await trackerApi.get('/api/v1/applications', { params })
    return data
  },

  get: async (id: string): Promise<Application> => {
    const { data } = await trackerApi.get(`/api/v1/applications/${id}`)
    return data
  },

  board: async (): Promise<KanbanBoard> => {
    const { data } = await trackerApi.get('/api/v1/applications/board')
    return data
  },

  create: async (input: Partial<Application>): Promise<Application> => {
    const { data } = await trackerApi.post('/api/v1/applications', input)
    return data
  },

  update: async (id: string, updates: Partial<Application>): Promise<Application> => {
    const { data } = await trackerApi.put(`/api/v1/applications/${id}`, updates)
    return data
  },

  updateStatus: async (id: string, status: ApplicationStatus, notes?: string): Promise<Application> => {
    const { data } = await trackerApi.patch(`/api/v1/applications/${id}/status`, {
      status, notes,
    })
    return data
  },

  delete: async (id: string) => {
    await trackerApi.delete(`/api/v1/applications/${id}`)
  },
}