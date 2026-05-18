import { useState } from 'react'
import { Settings as SettingsIcon, LogOut } from 'lucide-react'
import { clearAuth } from '../../shared/storage'
import type { AuthData } from '../../shared/types'
import QueueList from '../components/QueueList'
import BatchProcessor from '../components/BatchProcessor'

interface Props {
  auth: AuthData
  onLogout: () => void
  onOpenSettings: () => void
}

type View = 'queue' | 'processing'

export default function Home({ auth, onLogout, onOpenSettings }: Props) {
  const [view, setView] = useState<View>('queue')
  const [batchSelectedIds, setBatchSelectedIds] = useState<string[]>([])
  const [batchResumeId, setBatchResumeId] = useState<string>('')

  const handleLogout = async () => {
    await clearAuth()
    onLogout()
  }

  const handleStartBatch = (ids: string[], resumeId: string) => {
    setBatchSelectedIds(ids)
    setBatchResumeId(resumeId)
    setView('processing')
  }

  const handleBatchDone = () => {
    setView('queue')
    setBatchSelectedIds([])
  }

  if (view === 'processing') {
    return (
      <BatchProcessor
        selectedIds={batchSelectedIds}
        resumeId={batchResumeId}
        onDone={handleBatchDone}
        onCancel={handleBatchDone}
      />
    )
  }

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

      <QueueList onStartBatch={handleStartBatch} />
    </div>
  )
}