import { useEffect, useState } from 'react'
import { getAuth } from '../shared/storage'
import { AuthData } from '../shared/types'
import Login from './pages/Login'
import Home from './pages/Home'
import Settings from './pages/Settings'

type View = 'loading' | 'login' | 'home' | 'settings'

export default function App() {
  const [view, setView] = useState<View>('loading')
  const [auth, setAuth] = useState<AuthData | null>(null)

  useEffect(() => {
    getAuth().then((data) => {
      setAuth(data)
      setView(data ? 'home' : 'login')
    })
  }, [])

  const handleLoginSuccess = (authData: AuthData) => {
    setAuth(authData)
    setView('home')
  }

  const handleLogout = () => {
    setAuth(null)
    setView('login')
  }

  if (view === 'loading') {
    return (
      <div className="flex items-center justify-center h-[500px]">
        <div className="text-gray-500">Loading...</div>
      </div>
    )
  }

  if (view === 'login') {
    return <Login onSuccess={handleLoginSuccess} onOpenSettings={() => setView('settings')} />
  }

  if (view === 'settings') {
    return <Settings onBack={() => setView(auth ? 'home' : 'login')} />
  }

  if (view === 'home' && auth) {
    return <Home auth={auth} onLogout={handleLogout} onOpenSettings={() => setView('settings')} />
  }

  return null
}