import { profileApi } from './client'
import type { Profile, Resume, ResumeDetail, Skill } from '../types/api'

export const profile = {
  get: async (): Promise<Profile> => {
    const { data } = await profileApi.get('/api/v1/profile')
    return data
  },

  update: async (updates: Partial<Profile>): Promise<Profile> => {
    const { data } = await profileApi.put('/api/v1/profile', updates)
    return data
  },
}

export const resumes = {
  list: async (): Promise<{ resumes: Resume[]; total: number }> => {
    const { data } = await profileApi.get('/api/v1/resumes')
    return data
  },

  get: async (id: string): Promise<ResumeDetail> => {
    const { data } = await profileApi.get(`/api/v1/resumes/${id}`)
    return data
  },

  upload: async (file: File, version_name: string): Promise<{ resume: ResumeDetail; message: string }> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('version_name', version_name)
    const { data } = await profileApi.post('/api/v1/resumes/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },

  delete: async (id: string) => {
    await profileApi.delete(`/api/v1/resumes/${id}`)
  },

  getSkills: async (id: string): Promise<Skill[]> => {
    const { data } = await profileApi.get(`/api/v1/resumes/${id}/skills`)
    return data
  },
}