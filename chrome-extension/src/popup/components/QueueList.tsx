import { useEffect, useState } from 'react'
import {
  Briefcase, Trash2, Play, CheckCircle2, AlertCircle,
  Loader2, ExternalLink, Clock,
} from 'lucide-react'
import { getJobQueue, removeFromQueue, clearQueue } from '../../shared/storage'
import type { CapturedJob, Resume } from '../../shared/types'
import { resumeApi } from '../api/client'

interface Props {
  onStartBatch: (selectedIds: string[], resumeId: string) => void
}

export default function QueueList({ onStartBatch }: Props) {
  const [queue, setQueue] = useState<CapturedJob[]>([])
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [resumes, setResumes] = useState<Resume[]>([])
  const [selectedResumeId, setSelectedResumeId] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    refresh()
    loadResumes()
  }, [])

  const refresh = async () => {
    setLoading(true)
    const list = await getJobQueue()
    setQueue(list)
    setLoading(false)
  }

  const loadResumes = async () => {
    try {
      const list = await resumeApi.list()
      setResumes(list)
      const primary = list.find((r) => r.is_primary)
      setSelectedResumeId(primary?.id || list[0]?.id || '')
    } catch {
      setError('Could not load resumes. Upload one at the dashboard first.')
    }
  }

  const toggleOne = (id: string) => {
    const next = new Set(selected)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    setSelected(next)
  }

  const toggleAll = () => {
    const pendingIds = queue.filter((q) => q.status === 'pending').map((q) => q.id)
    if (selected.size === pendingIds.length) {
      setSelected(new Set())
    } else {
      setSelected(new Set(pendingIds))
    }
  }

  const handleDeleteSelected = async () => {
    if (selected.size === 0) return
    if (!confirm(`Delete ${selected.size} job(s) from queue?`)) return
    await removeFromQueue(Array.from(selected))
    setSelected(new Set())
    refresh()
  }

  const handleClearAll = async () => {
    if (queue.length === 0) return
    if (!confirm('Clear all jobs from queue? This cannot be undone.')) return
    await clearQueue()
    setSelected(new Set())
    refresh()
  }

  const handleMatchSelected = () => {
    if (selected.size === 0) return
    if (!selectedResumeId) {
      setError('Please select a resume')
      return
    }
    onStartBatch(Array.from(selected), selectedResumeId)
  }

  const handleMatchAll = () => {
    const pendingIds = queue.filter((q) => q.status === 'pending').map((q) => q.id)
    if (pendingIds.length === 0) return
    if (!selectedResumeId) {
      setError('Please select a resume')
      return
    }
    onStartBatch(pendingIds, selectedResumeId)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[400px]">
        <Loader2 className="w-6 h-6 text-brand-600 animate-spin" />
      </div>
    )
  }

  const pendingCount = queue.filter((q) => q.status === 'pending').length
  const savedCount = queue.filter((q) => q.status === 'saved').length

  return (
    <>
      <div className="px-4 py-2 bg-gray-50 border-b border-gray-200 flex justify-between text-xs">
        <span className="text-gray-600"><strong className="text-gray-900">{queue.length}</strong> total</span>
        <span className="text-gray-600"><strong className="text-amber-700">{pendingCount}</strong> pending</span>
        <span className="text-gray-600"><strong className="text-green-700">{savedCount}</strong> saved</span>
      </div>

      {resumes.length > 0 && (
        <div className="px-4 py-2 border-b border-gray-200">
          <label className="text-xs text-gray-600 block mb-1">Resume for batch:</label>
          <select
            value={selectedResumeId}
            onChange={(e) => setSelectedResumeId(e.target.value)}
            className="input text-xs py-1"
          >
            {resumes.map((r) => (
              <option key={r.id} value={r.id}>
                {r.version_name} {r.is_primary && '(Primary)'}
              </option>
            ))}
          </select>
        </div>
      )}

      {error && (
        <div className="px-4 py-2 bg-red-50 text-xs text-red-700 border-b border-red-200">{error}</div>
      )}

      <div className="flex-1 overflow-auto">
        {queue.length === 0 ? (
          <div className="text-center py-12 px-4">
            <Briefcase className="w-12 h-12 text-gray-300 mx-auto mb-2" />
            <div className="text-sm text-gray-500 mb-1">No jobs captured</div>
            <div className="text-xs text-gray-400">Click Apply on Naukri to start capturing</div>
          </div>
        ) : (
          <>
            {pendingCount > 0 && (
              <div className="px-4 py-2 bg-brand-50 border-b border-brand-100 flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={selected.size === pendingCount && pendingCount > 0}
                  onChange={toggleAll}
                  className="cursor-pointer"
                />
                <span className="text-xs text-gray-700">
                  {selected.size > 0
                    ? `${selected.size} of ${pendingCount} selected`
                    : `Select all ${pendingCount} pending`}
                </span>
              </div>
            )}

            <div className="divide-y divide-gray-200">
              {queue.map((entry) => (
                <QueueRow
                  key={entry.id}
                  entry={entry}
                  selected={selected.has(entry.id)}
                  onToggle={() => toggleOne(entry.id)}
                />
              ))}
            </div>
          </>
        )}
      </div>

      {queue.length > 0 && (
        <div className="px-4 py-3 border-t border-gray-200 bg-gray-50 space-y-2">
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={handleMatchSelected}
              disabled={selected.size === 0 || !selectedResumeId}
              className="btn btn-primary flex items-center justify-center gap-1 text-xs"
            >
              <Play className="w-3 h-3" /> Match Selected ({selected.size})
            </button>
            <button
              onClick={handleMatchAll}
              disabled={pendingCount === 0 || !selectedResumeId}
              className="btn btn-primary flex items-center justify-center gap-1 text-xs"
            >
              <Play className="w-3 h-3" /> Match All ({pendingCount})
            </button>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={handleDeleteSelected}
              disabled={selected.size === 0}
              className="btn btn-secondary flex items-center justify-center gap-1 text-xs"
            >
              <Trash2 className="w-3 h-3" /> Delete Selected
            </button>
            <button
              onClick={handleClearAll}
              className="btn btn-secondary flex items-center justify-center gap-1 text-xs text-red-600"
            >
              <Trash2 className="w-3 h-3" /> Clear All
            </button>
          </div>
        </div>
      )}
    </>
  )
}

interface RowProps {
  entry: CapturedJob
  selected: boolean
  onToggle: () => void
}

function QueueRow({ entry, selected, onToggle }: RowProps) {
  const { job, status } = entry

  const statusUI: Record<string, { icon: any; color: string; label: string }> = {
    pending: { icon: Clock, color: 'text-amber-500', label: 'Pending' },
    processing: { icon: Loader2, color: 'text-brand-600 animate-spin', label: 'Processing...' },
    matched: { icon: CheckCircle2, color: 'text-blue-600', label: 'Matched' },
    saved: { icon: CheckCircle2, color: 'text-green-600', label: 'Saved' },
    error: { icon: AlertCircle, color: 'text-red-600', label: 'Error' },
  }
  const StatusIcon = statusUI[status].icon

  return (
    <div className="px-4 py-3 hover:bg-gray-50">
      <div className="flex items-start gap-2">
        {status === 'pending' && (
          <input
            type="checkbox"
            checked={selected}
            onChange={onToggle}
            className="mt-0.5 cursor-pointer"
          />
        )}

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1 mb-0.5">
            <StatusIcon className={`w-3 h-3 ${statusUI[status].color}`} />
            <span className="text-xs text-gray-500">{statusUI[status].label}</span>
            {entry.match_score !== undefined && (
              <span className="text-xs font-semibold text-brand-600 ml-auto">
                {Math.round(entry.match_score * 100)}%
              </span>
            )}
          </div>

          <div className="text-sm font-medium text-gray-900 truncate">{job.role_title}</div>
          <div className="text-xs text-gray-600 truncate">
            {job.company}{job.location && ` · ${job.location}`}
          </div>

          {entry.error && (
            <div className="text-xs text-red-600 mt-1 truncate">{entry.error}</div>
          )}

          <a
            href={job.jd_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-0.5 text-xs text-gray-400 hover:text-brand-600 mt-1"
          >
            View on Naukri <ExternalLink className="w-2.5 h-2.5" />
          </a>
        </div>
      </div>
    </div>
  )
}