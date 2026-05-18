import { useEffect, useRef, useState } from 'react'
import {
  CheckCircle2, AlertCircle, Loader2, ChevronLeft, Play, X,
} from 'lucide-react'
import { matchApi, applicationApi } from '../api/client'
import { getJobQueue, updateQueueEntry } from '../../shared/storage'
import type { CapturedJob } from '../../shared/types'

interface Props {
  selectedIds: string[]
  resumeId: string
  onDone: () => void
  onCancel: () => void
}

interface RowState {
  entry: CapturedJob
  status: 'pending' | 'processing' | 'matched' | 'saved' | 'error'
  match_score?: number
  error?: string
}

export default function BatchProcessor({ selectedIds, resumeId, onDone, onCancel }: Props) {
  const [rows, setRows] = useState<RowState[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [running, setRunning] = useState(false)
  const [done, setDone] = useState(false)
  const cancelRef = useRef(false)

  useEffect(() => {
    getJobQueue().then((queue) => {
      const selectedEntries = queue.filter((q) => selectedIds.includes(q.id))
      setRows(
        selectedEntries.map((entry) => ({
          entry,
          status: entry.status === 'saved' ? 'saved' : 'pending',
          match_score: entry.match_score,
        }))
      )
    })
  }, [selectedIds])

  const startProcessing = async () => {
    setRunning(true)
    cancelRef.current = false

    for (let i = 0; i < rows.length; i++) {
      if (cancelRef.current) break
      const row = rows[i]
      if (row.status === 'saved') continue
      setCurrentIndex(i)
      await processOne(i)
    }

    setRunning(false)
    setDone(true)
  }

  const processOne = async (index: number) => {
    const row = rows[index]

    setRows((prev) => prev.map((r, i) => i === index ? { ...r, status: 'processing' } : r))
    await updateQueueEntry(row.entry.id, { status: 'processing' })

    try {
      const matchResult = await matchApi.run(
        resumeId,
        row.entry.job.jd_text,
        row.entry.job.company,
        row.entry.job.role_title,
      )

      await applicationApi.create({
        company: row.entry.job.company,
        role_title: row.entry.job.role_title,
        resume_id: resumeId,
        match_result_id: matchResult.id,
        jd_url: row.entry.job.jd_url,
        location: row.entry.job.location,
        is_remote: row.entry.job.is_remote,
        salary_min: row.entry.job.salary_min,
        salary_max: row.entry.job.salary_max,
        match_score: matchResult.overall_score,
      })

      setRows((prev) =>
        prev.map((r, i) =>
          i === index ? { ...r, status: 'saved', match_score: matchResult.overall_score } : r
        )
      )
      await updateQueueEntry(row.entry.id, {
        status: 'saved',
        match_result_id: matchResult.id,
        match_score: matchResult.overall_score,
      })
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.response?.data?.title || err.message || 'Processing failed'
      const errorMsg = typeof msg === 'string' ? msg : 'Processing failed'

      setRows((prev) =>
        prev.map((r, i) => i === index ? { ...r, status: 'error', error: errorMsg } : r)
      )
      await updateQueueEntry(row.entry.id, { status: 'error', error: errorMsg })
    }
  }

  const handleCancel = () => { cancelRef.current = true }

  const savedCount = rows.filter((r) => r.status === 'saved').length
  const errorCount = rows.filter((r) => r.status === 'error').length

  return (
    <div className="flex flex-col h-[500px]">
      <div className="px-4 py-3 border-b border-gray-200 bg-white flex items-center justify-between">
        <div className="flex items-center gap-2">
          {!running && !done && (
            <button onClick={onCancel} className="text-gray-500 hover:text-gray-900">
              <ChevronLeft className="w-4 h-4" />
            </button>
          )}
          <div>
            <div className="text-sm font-semibold">Batch Processing</div>
            <div className="text-xs text-gray-500">
              {rows.length} job{rows.length !== 1 ? 's' : ''} selected
            </div>
          </div>
        </div>
      </div>

      {(running || done) && (
        <div className="px-4 py-2 bg-gray-50 border-b border-gray-200">
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-700">
              {done ? 'Complete' : `Processing ${currentIndex + 1} of ${rows.length}`}
            </span>
            <span className="text-gray-600">{savedCount} saved · {errorCount} failed</span>
          </div>
          <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-brand-600 transition-all"
              style={{ width: `${rows.length === 0 ? 0 : ((savedCount + errorCount) / rows.length) * 100}%` }}
            />
          </div>
        </div>
      )}

      <div className="flex-1 overflow-auto divide-y divide-gray-200">
        {rows.map((row, index) => (
          <ResultRow key={row.entry.id} row={row} isCurrent={running && index === currentIndex} />
        ))}
      </div>

      <div className="px-4 py-3 border-t border-gray-200 bg-gray-50 space-y-2">
        {!running && !done && (
          <>
            <button
              onClick={startProcessing}
              disabled={rows.length === 0}
              className="btn btn-primary w-full flex items-center justify-center gap-2"
            >
              <Play className="w-4 h-4" /> Start Processing
            </button>
            <button onClick={onCancel} className="btn btn-secondary w-full">Cancel</button>
          </>
        )}
        {running && (
          <button onClick={handleCancel} className="btn btn-secondary w-full flex items-center justify-center gap-2">
            <X className="w-4 h-4" /> Stop after current
          </button>
        )}
        {done && (
          <>
            <a href="http://localhost:3000/applications" target="_blank" rel="noopener noreferrer"
               className="btn btn-primary w-full block text-center">
              View on Dashboard
            </a>
            <button onClick={onDone} className="btn btn-secondary w-full">Back to Queue</button>
          </>
        )}
      </div>
    </div>
  )
}

interface RowProps { row: RowState; isCurrent: boolean }

function ResultRow({ row, isCurrent }: RowProps) {
  const { entry, status, match_score, error } = row

  return (
    <div className={`px-4 py-2.5 ${isCurrent ? 'bg-brand-50' : ''}`}>
      <div className="flex items-start gap-2">
        <div className="mt-0.5">
          {status === 'pending' && <div className="w-4 h-4 rounded-full border-2 border-gray-300" />}
          {status === 'processing' && <Loader2 className="w-4 h-4 text-brand-600 animate-spin" />}
          {status === 'saved' && <CheckCircle2 className="w-4 h-4 text-green-600" />}
          {status === 'error' && <AlertCircle className="w-4 h-4 text-red-600" />}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <div className="text-xs font-medium text-gray-900 truncate flex-1">{entry.job.role_title}</div>
            {match_score !== undefined && (
              <span className="text-xs font-bold text-brand-600 flex-shrink-0">
                {Math.round(match_score * 100)}%
              </span>
            )}
          </div>
          <div className="text-xs text-gray-600 truncate">{entry.job.company}</div>
          {error && <div className="text-xs text-red-600 mt-0.5 truncate">{error}</div>}
        </div>
      </div>
    </div>
  )
}