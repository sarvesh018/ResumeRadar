import { authApi } from './client'
import type { User, TokenResponse } from '../types/api'

export const auth = {
  register: async (email: string, password: string, full_name?: string) => {
    const { data } = await authApi.post('/api/v1/auth/register', {
      email, password, full_name,
    })
    return data
  },

  login: async (email: string, password: string): Promise<TokenResponse> => {
    const { data } = await authApi.post<TokenResponse>('/api/v1/auth/login', {
      email, password,
    })
    return data
  },

  me: async (): Promise<User> => {
    const { data } = await authApi.get<User>('/api/v1/auth/me')
    return data
  },
}