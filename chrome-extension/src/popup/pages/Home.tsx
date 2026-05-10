import { useEffect, useState } from 'react'
import { Settings as SettingsIcon, LogOut, Briefcase, Eye } from 'lucide-react'
import { clearAuth, getLatestJob } from '../../shared/storage'
import type { AuthData, ExtractedJobData } from '../../shared/types'

interface Props {
  auth: AuthData
  onLogout: () => void
  onOpenSettings: () => void
}

export default function Home({ auth, onLogout, onOpenSettings }: Props) {
  const [latestJob, setLatestJob] = useState<ExtractedJobData | null>(null)
  const [currentSite, setCurrentSite] = useState<string>('')

  useEffect(() => {
    getLatestJob().then(setLatestJob)
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tab = tabs[0]
      if (tab?.url) {
        try {
          setCurrentSite(new URL(tab.url).hostname)
        } catch {}
      }
    })
  }, [])

  const handleLogout = async () => {
    await clearAuth()
    onLogout()
  }

  const isOnSupportedSite =
    currentSite.includes('naukri.com') || currentSite.includes('linkedin.com')

  return (
    <div className="flex flex-col h-[500px]">
      <div className="px-4 py-3 border-b border-gray-200 bg-white flex items-center justify-between">
        <div>
          <div className="text-sm font-bold text-brand-700">ResumeRadar</div>
          <div className="text-xs text-gray-500 truncate max-w-[200px]">{auth.user.email}</div>
        </div>
        <div className="flex gap-1">
          <button onClick={onOpenSettings} className="p-1.5 text-gray-400 hover:text-gray-700 rounded" title="Settings">
            <SettingsIcon className="w-4 h-4" />
          </button>
          <button onClick={handleLogout} className="p-1.5 text-gray-400 hover:text-red-600 rounded" title="Sign out">
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-4">
        <div className="mb-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
          <div className="flex items-center gap-2">
            <Eye className="w-4 h-4 text-gray-500" />
            <span className="text-xs text-gray-600">Current site:</span>
            <span className="text-xs font-mono text-gray-900">{currentSite || 'unknown'}</span>
          </div>
          {isOnSupportedSite ? (
            <div className="text-xs text-green-700 mt-1">✓ Auto-capture is active on this site</div>
          ) : (
            <div className="text-xs text-gray-500 mt-1">Visit naukri.com to start auto-capturing applications</div>
          )}
        </div>

        {latestJob ? (
          <div className="bg-white rounded-lg border border-brand-200 p-4">
            <div className="flex items-start gap-2 mb-3">
              <Briefcase className="w-5 h-5 text-brand-600 mt-0.5" />
              <div className="flex-1">
                <div className="text-sm font-semibold text-gray-900">{latestJob.role_title}</div>
                <div className="text-xs text-gray-600">{latestJob.company}</div>
                {latestJob.location && (
                  <div className="text-xs text-gray-500 mt-1">
                    {latestJob.location}{latestJob.is_remote && ' · Remote'}
                  </div>
                )}
              </div>
            </div>

            <div className="text-xs text-gray-500 mb-3">JD preview: {latestJob.jd_text.slice(0, 120)}...</div>

            <button className="btn btn-primary w-full" disabled>
              Match & Save (coming in Part 2)
            </button>
          </div>
        ) : (
          <div className="text-center py-12">
            <Briefcase className="w-12 h-12 text-gray-300 mx-auto mb-2" />
            <div className="text-sm text-gray-500 mb-1">No job detected yet</div>
            <div className="text-xs text-gray-400">Apply to a job on Naukri to auto-capture details</div>
          </div>
        )}
      </div>

      <div className="px-4 py-2 border-t border-gray-200 bg-gray-50 text-xs text-gray-500 text-center">
        Open ResumeRadar:{' '}
        <a href="http://localhost:3000" target="_blank" rel="noopener noreferrer" className="text-brand-600 hover:underline">
          Dashboard
        </a>
      </div>
    </div>
  )
}