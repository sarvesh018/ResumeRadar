import { AuthData, AppSettings, ExtractedJobData } from './types'

const KEYS = {
  AUTH: 'auth',
  SETTINGS: 'settings',
  LATEST_JOB: 'latest_job',
} as const

const DEFAULT_SETTINGS: AppSettings = {
  backend_url: 'http://localhost:8080',
  enable_auto_capture: true,
}

export async function getAuth(): Promise<AuthData | null> {
  const result = await chrome.storage.local.get(KEYS.AUTH)
  return result[KEYS.AUTH] || null
}

export async function setAuth(auth: AuthData): Promise<void> {
  await chrome.storage.local.set({ [KEYS.AUTH]: auth })
}

export async function clearAuth(): Promise<void> {
  await chrome.storage.local.remove(KEYS.AUTH)
}

export async function getSettings(): Promise<AppSettings> {
  const result = await chrome.storage.local.get(KEYS.SETTINGS)
  return result[KEYS.SETTINGS] || DEFAULT_SETTINGS
}

export async function setSettings(settings: AppSettings): Promise<void> {
  await chrome.storage.local.set({ [KEYS.SETTINGS]: settings })
}

export async function getLatestJob(): Promise<ExtractedJobData | null> {
  const result = await chrome.storage.local.get(KEYS.LATEST_JOB)
  return result[KEYS.LATEST_JOB] || null
}

export async function setLatestJob(job: ExtractedJobData): Promise<void> {
  await chrome.storage.local.set({ [KEYS.LATEST_JOB]: job })
}

export async function clearLatestJob(): Promise<void> {
  await chrome.storage.local.remove(KEYS.LATEST_JOB)
}