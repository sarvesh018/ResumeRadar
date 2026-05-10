import { useState } from 'react'
import { Settings as SettingsIcon, LogIn } from 'lucide-react'
import { authApi } from '../api/client'
import { setAuth } from '../../shared/storage'
import type { AuthData } from '../../shared/types'

interface Props {
  onSuccess: (auth: AuthData) => void
  onOpenSettings: () => void
}

export default function Login({ onSuccess, onOpenSettings }: Props) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const tokens = await authApi.login(email, password)
      await setAuth({
        access_token: tokens.access_token,
        refresh_token: tokens.refresh_token,
        user: { id: '', email: '', full_name: null },
      })
      const user = await authApi.me()

      const authData: AuthData = {
        access_token: tokens.access_token,
        refresh_token: tokens.refresh_token,
        user,
      }
      await setAuth(authData)
      onSuccess(authData)
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.response?.data?.title || err.message || 'Login failed'
      setError(typeof msg === 'string' ? msg : 'Login failed')
      if (err.code === 'ERR_NETWORK' || err.message?.includes('Network')) {
        setError('Cannot connect to backend. Check Settings to configure the URL.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-lg font-bold text-brand-700">ResumeRadar</h1>
          <p className="text-xs text-gray-500">Sign in to continue</p>
        </div>
        <button onClick={onOpenSettings} className="text-gray-400 hover:text-gray-700" title="Settings">
          <SettingsIcon className="w-4 h-4" />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label className="label">Email</label>
          <input
            type="email" required value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input" placeholder="you@example.com" autoFocus
          />
        </div>

        <div>
          <label className="label">Password</label>
          <input
            type="password" required minLength={8} value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="input" placeholder="********"
          />
        </div>

        {error && <div className="text-xs text-red-600 bg-red-50 p-2 rounded">{error}</div>}

        <button
          type="submit" disabled={loading || !email || password.length < 8}
          className="btn btn-primary w-full flex items-center justify-center gap-2"
        >
          <LogIn className="w-4 h-4" />
          {loading ? 'Signing in...' : 'Sign in'}
        </button>
      </form>

      <p className="text-xs text-gray-500 mt-6 text-center">
        Don't have an account? Sign up at{' '}
        <a href="http://localhost:3000/register" target="_blank" rel="noopener noreferrer" className="text-brand-600 hover:underline">
          ResumeRadar
        </a>
      </p>
    </div>
  )
}