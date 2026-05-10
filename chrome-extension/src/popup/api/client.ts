import axios, { AxiosInstance } from 'axios'
import { getAuth, getSettings, clearAuth } from '../../shared/storage'
import type { Resume, MatchResult } from '../../shared/types'

let cachedClient: AxiosInstance | null = null
let cachedBackendUrl: string | null = null

async function getClient(): Promise<AxiosInstance> {
  const settings = await getSettings()
  const baseURL = settings.backend_url

  if (cachedClient && cachedBackendUrl === baseURL) {
    return cachedClient
  }

  const client = axios.create({ baseURL, timeout: 30000 })

  client.interceptors.request.use(async (config) => {
    const auth = await getAuth()
    if (auth?.access_token) {
      config.headers.Authorization = `Bearer ${auth.access_token}`
    }
    return config
  })

  client.interceptors.response.use(
    (response) => response,
    async (error) => {
      if (error.response?.status === 401) {
        await clearAuth()
      }
      return Promise.reject(error)
    }
  )

  cachedClient = client
  cachedBackendUrl = baseURL
  return client
}

export const authApi = {
  login: async (email: string, password: string) => {
    const client = await getClient()
    const { data } = await client.post('/api/v1/auth/login', { email, password })
    return data as {
      access_token: string
      refresh_token: string
      token_type: string
      expires_in: number
    }
  },

  register: async (email: string, password: string, full_name?: string) => {
    const client = await getClient()
    const { data } = await client.post('/api/v1/auth/register', {
      email, password, full_name,
    })
    return data
  },

  me: async () => {
    const client = await getClient()
    const { data } = await client.get('/api/v1/auth/me')
    return data
  },
}

export const resumeApi = {
  list: async (): Promise<Resume[]> => {
    const client = await getClient()
    const { data } = await client.get('/api/v1/resumes')
    return data.resumes
  },
}

export const matchApi = {
  run: async (
    resume_id: string,
    jd_text: string,
    jd_company?: string,
    jd_role?: string
  ): Promise<MatchResult> => {
    const client = await getClient()
    const { data } = await client.post('/api/v1/match', {
      resume_id, jd_text, jd_company, jd_role,
    })
    return data
  },
}

export const applicationApi = {
  create: async (input: {
    company: string
    role_title: string
    resume_id?: string
    match_result_id?: string
    jd_url?: string
    location?: string
    is_remote?: boolean
    salary_min?: number
    salary_max?: number
    match_score?: number
    notes?: string
  }) => {
    const client = await getClient()
    const { data } = await client.post('/api/v1/applications', input)
    return data
  },
}

export function resetApiClient() {
  cachedClient = null
  cachedBackendUrl = null
}