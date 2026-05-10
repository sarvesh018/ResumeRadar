import { useEffect, useState } from 'react'
import { ArrowLeft, Save } from 'lucide-react'
import { getSettings, setSettings } from '../../shared/storage'
import { resetApiClient } from '../api/client'
import type { AppSettings } from '../../shared/types'

interface Props {
  onBack: () => void
}

export default function Settings({ onBack }: Props) {
  const [backend_url, setBackendUrl] = useState('')
  const [enable_auto_capture, setEnableAutoCapture] = useState(true)
  const [saved, setSaved] = useState(false)
  const [testStatus, setTestStatus] = useState<'idle' | 'testing' | 'ok' | 'fail'>('idle')

  useEffect(() => {
    getSettings().then((settings) => {
      setBackendUrl(settings.backend_url)
      setEnableAutoCapture(settings.enable_auto_capture)
    })
  }, [])

  const handleSave = async () => {
    const newSettings: AppSettings = {
      backend_url: backend_url.replace(/\/$/, ''),
      enable_auto_capture,
    }
    await setSettings(newSettings)
    resetApiClient()
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const testConnection = async () => {
    setTestStatus('testing')
    const url = backend_url.replace(/\/$/, '')
    
    // Try common health endpoints
    const endpoints = ['/health', '/health/live', '/api/v1/auth/health/live']
    
    for (const endpoint of endpoints) {
      try {
        const response = await fetch(`${url}${endpoint}`, { method: 'GET' })
        if (response.ok) {
          setTestStatus('ok')
          setTimeout(() => setTestStatus('idle'), 3000)
          return
        }
      } catch {
        // Try next endpoint
      }
    }
    
    setTestStatus('fail')
    setTimeout(() => setTestStatus('idle'), 3000)
  }

  return (
    <div className="flex flex-col h-[500px]">
      <div className="px-4 py-3 border-b border-gray-200 bg-white flex items-center gap-2">
        <button onClick={onBack} className="p-1 text-gray-500 hover:text-gray-900 rounded">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <h1 className="text-sm font-semibold">Settings</h1>
      </div>

      <div className="flex-1 overflow-auto p-4 space-y-4">
        <div>
          <label className="label">Backend URL</label>
          <input
            type="url" value={backend_url}
            onChange={(e) => setBackendUrl(e.target.value)}
            className="input font-mono text-xs" placeholder="http://localhost:8080"
          />
          <p className="text-xs text-gray-500 mt-1">
            The Nginx gateway URL. Use http://localhost:8080 for local Docker setup.
          </p>

          <button onClick={testConnection} className="text-xs text-brand-600 hover:underline mt-2">
            Test connection
          </button>

          {testStatus === 'testing' && <span className="text-xs text-gray-500 ml-2">Testing...</span>}
          {testStatus === 'ok' && <span className="text-xs text-green-600 ml-2">✓ Connected</span>}
          {testStatus === 'fail' && <span className="text-xs text-red-600 ml-2">✗ Cannot connect</span>}
        </div>

        <div className="border-t border-gray-200 pt-4">
          <label className="flex items-start gap-3 cursor-pointer">
            <input
              type="checkbox" checked={enable_auto_capture}
              onChange={(e) => setEnableAutoCapture(e.target.checked)}
              className="mt-0.5"
            />
            <div>
              <div className="text-sm font-medium text-gray-900">Enable auto-capture</div>
              <div className="text-xs text-gray-500 mt-0.5">
                Automatically detect job applications on supported sites and pre-fill the form.
              </div>
            </div>
          </label>
        </div>

        <div className="border-t border-gray-200 pt-4">
          <h3 className="text-xs font-semibold text-gray-700 mb-2">Supported Sites</h3>
          <ul className="text-xs text-gray-600 space-y-1">
            <li>✓ Naukri.com</li>
            <li className="text-gray-400">⏳ LinkedIn (coming soon)</li>
          </ul>
        </div>
      </div>

      <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
        <button onClick={handleSave} className="btn btn-primary w-full flex items-center justify-center gap-2">
          <Save className="w-4 h-4" />
          {saved ? 'Saved!' : 'Save Settings'}
        </button>
      </div>
    </div>
  )
}