import { AuthData, AppSettings, CapturedJob, ExtractedJobData } from './types'

const KEYS = {
  AUTH: 'auth',
  SETTINGS: 'settings',
  JOB_QUEUE: 'job_queue',
} as const

const DEFAULT_SETTINGS: AppSettings = {
  backend_url: 'http://localhost:8080',
  enable_auto_capture: true,
}

// AUTH
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

// SETTINGS
export async function getSettings(): Promise<AppSettings> {
  const result = await chrome.storage.local.get(KEYS.SETTINGS)
  return result[KEYS.SETTINGS] || DEFAULT_SETTINGS
}
export async function setSettings(settings: AppSettings): Promise<void> {
  await chrome.storage.local.set({ [KEYS.SETTINGS]: settings })
}

// JOB QUEUE
export async function getJobQueue(): Promise<CapturedJob[]> {
  const result = await chrome.storage.local.get(KEYS.JOB_QUEUE)
  const queue: CapturedJob[] = result[KEYS.JOB_QUEUE] || []
  return [...queue].sort((a, b) =>
    new Date(b.job.extracted_at).getTime() - new Date(a.job.extracted_at).getTime()
  )
}

export async function addJobToQueue(job: ExtractedJobData): Promise<{ added: boolean; total: number }> {
  const result = await chrome.storage.local.get(KEYS.JOB_QUEUE)
  const queue: CapturedJob[] = result[KEYS.JOB_QUEUE] || []

  const isDuplicate = queue.some(
    (q) => q.job.jd_url === job.jd_url
      && q.job.company === job.company
      && q.job.role_title === job.role_title
  )

  if (isDuplicate) {
    return { added: false, total: queue.length }
  }

  const newEntry: CapturedJob = {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
    job,
    status: 'pending',
    created_at: new Date().toISOString(),
  }

  const updated = [...queue, newEntry]
  await chrome.storage.local.set({ [KEYS.JOB_QUEUE]: updated })
  return { added: true, total: updated.length }
}

export async function updateQueueEntry(id: string, updates: Partial<CapturedJob>): Promise<void> {
  const result = await chrome.storage.local.get(KEYS.JOB_QUEUE)
  const queue: CapturedJob[] = result[KEYS.JOB_QUEUE] || []
  const updated = queue.map((entry) =>
    entry.id === id ? { ...entry, ...updates } : entry
  )
  await chrome.storage.local.set({ [KEYS.JOB_QUEUE]: updated })
}

export async function removeFromQueue(ids: string[]): Promise<void> {
  const result = await chrome.storage.local.get(KEYS.JOB_QUEUE)
  const queue: CapturedJob[] = result[KEYS.JOB_QUEUE] || []
  const filtered = queue.filter((entry) => !ids.includes(entry.id))
  await chrome.storage.local.set({ [KEYS.JOB_QUEUE]: filtered })
}

export async function clearQueue(): Promise<void> {
  await chrome.storage.local.set({ [KEYS.JOB_QUEUE]: [] })
}

export async function getPendingCount(): Promise<number> {
  const queue = await getJobQueue()
  return queue.filter((q) => q.status === 'pending').length
}