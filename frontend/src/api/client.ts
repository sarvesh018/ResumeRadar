import axios, { type AxiosInstance } from "axios";

const URLS = {
  auth: import.meta.env.VITE_AUTH_URL || 'http://localhost:8001',
  profile: import.meta.env.VITE_PROFILE_URL || 'http://localhost:8002',
  matcher: import.meta.env.VITE_MATCHER_URL || 'http://localhost:8003',
  tracker: import.meta.env.VITE_TRACKER_URL || 'http://localhost:8004',
  analytics: import.meta.env.VITE_ANALYTICS_URL || 'http://localhost:8005',
}

function createClient(baseURL: string): AxiosInstance {
  const client = axios.create({ baseURL, timeout: 300000 })

  client.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  })

  client.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      }
      return Promise.reject(error)
    }
  )

  return client
}

export const authApi = createClient(URLS.auth)
export const profileApi = createClient(URLS.profile)
export const matcherApi = createClient(URLS.matcher)
export const trackerApi = createClient(URLS.tracker)
export const analyticsApi = createClient(URLS.analytics)