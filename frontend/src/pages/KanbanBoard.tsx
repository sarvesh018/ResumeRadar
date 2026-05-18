import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, X, SlidersHorizontal, Trash2, CheckSquare, Square } from 'lucide-react'
import toast from 'react-hot-toast'
import { applications } from '../api/applications'
import type { Application, ApplicationStatus } from '../types/api'

const COLUMN_ORDER: ApplicationStatus[] = [
  'applied',
  'screening',
  'interviewing',
  'offer',
  'rejected',
  'withdrawn',
]

const STATUS_LABELS: Record<string, string> = {
  applied: 'Applied',
  screening: 'Screening',
  interviewing: 'Interviewing',
  offer: 'Offer',
  rejected: 'Rejected',
  withdrawn: 'Withdrawn',
}

const STATUS_COLORS: Record<string, string> = {
  applied: 'bg-blue-50 border-blue-300',
  screening: 'bg-yellow-50 border-yellow-300',
  interviewing: 'bg-purple-50 border-purple-300',
  offer: 'bg-green-50 border-green-300',
  rejected: 'bg-red-50 border-red-300',
  withdrawn: 'bg-gray-50 border-gray-300',
}

const STATUS_BADGES: Record<string, string> = {
  applied: 'bg-blue-100 text-blue-700',
  screening: 'bg-yellow-100 text-yellow-700',
  interviewing: 'bg-purple-100 text-purple-700',
  offer: 'bg-green-100 text-green-700',
  rejected: 'bg-red-100 text-red-700',
  withdrawn: 'bg-gray-100 text-gray-700',
}

type RemoteFilter = 'all' | 'remote' | 'onsite'

export default function KanbanBoard() {
  const queryClient = useQueryClient()
  const [showAddForm, setShowAddForm] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [remoteFilter, setRemoteFilter] = useState<RemoteFilter>('all')
  const [minMatchScore, setMinMatchScore] = useState(0)
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false)

  // Select mode for bulk delete
  const [selectMode, setSelectMode] = useState(false)
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())

  const { data: board, isLoading } = useQuery({
    queryKey: ['kanban'],
    queryFn: applications.board,
  })

  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: ApplicationStatus }) =>
      applications.updateStatus(id, status),
    onSuccess: () => {
      toast.success('Status updated')
      queryClient.invalidateQueries({ queryKey: ['kanban'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.title || 'Update failed')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => applications.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['kanban'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.title || 'Delete failed')
    },
  })

  const handleDeleteOne = async (app: Application) => {
    const confirmed = confirm(
      `Delete this application?\n\n${app.role_title} at ${app.company}\n\nThis cannot be undone.`
    )
    if (!confirmed) return
    deleteMutation.mutate(app.id, {
      onSuccess: () => toast.success('Application deleted'),
    })
  }

  const handleBulkDelete = async () => {
    if (selectedIds.size === 0) return
    const confirmed = confirm(
      `Delete ${selectedIds.size} application(s)?\n\nThis cannot be undone.`
    )
    if (!confirmed) return

    const ids = Array.from(selectedIds)
    let success = 0
    let failed = 0
    for (const id of ids) {
      try {
        await applications.delete(id)
        success++
      } catch {
        failed++
      }
    }

    queryClient.invalidateQueries({ queryKey: ['kanban'] })
    setSelectedIds(new Set())
    setSelectMode(false)

    if (failed === 0) {
      toast.success(`Deleted ${success} application(s)`)
    } else {
      toast.error(`Deleted ${success}, failed ${failed}`)
    }
  }

  const toggleSelect = (id: string) => {
    const next = new Set(selectedIds)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    setSelectedIds(next)
  }

  const toggleSelectMode = () => {
    setSelectMode(!selectMode)
    setSelectedIds(new Set())
  }

  const filteredColumns = useMemo(() => {
    if (!board) return []

    const filterApp = (app: Application): boolean => {
      if (searchQuery) {
        const q = searchQuery.toLowerCase()
        const matchesCompany = app.company.toLowerCase().includes(q)
        const matchesRole = app.role_title.toLowerCase().includes(q)
        if (!matchesCompany && !matchesRole) return false
      }
      if (remoteFilter === 'remote' && !app.is_remote) return false
      if (remoteFilter === 'onsite' && app.is_remote) return false
      if (minMatchScore > 0) {
        if (app.match_score === null || app.match_score === undefined) return false
        if (app.match_score * 100 < minMatchScore) return false
      }
      return true
    }

    return COLUMN_ORDER.map((status) => {
      const col = board.columns.find((c) => c.status === status)
      if (!col) return { status, count: 0, applications: [], totalCount: 0 }
      const filtered = col.applications.filter(filterApp)
      return {
        status: col.status,
        count: filtered.length,
        totalCount: col.applications.length,
        applications: filtered,
      }
    })
  }, [board, searchQuery, remoteFilter, minMatchScore])

  const hasActiveFilters =
    searchQuery !== '' || remoteFilter !== 'all' || minMatchScore > 0

  const clearFilters = () => {
    setSearchQuery('')
    setRemoteFilter('all')
    setMinMatchScore(0)
  }

  if (isLoading) {
    return <div className="p-8 text-gray-500">Loading...</div>
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-gray-900">Applications</h1>
        <div className="flex gap-2">
          <button
            onClick={toggleSelectMode}
            className={`btn flex items-center gap-2 ${
              selectMode ? 'btn-primary' : 'btn-secondary'
            }`}
          >
            <CheckSquare className="w-4 h-4" />
            {selectMode ? 'Cancel selection' : 'Select'}
          </button>
          <button
            onClick={() => setShowAddForm(true)}
            className="btn btn-primary flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Add Application
          </button>
        </div>
      </div>

      {/* Bulk action bar (only visible in select mode with selections) */}
      {selectMode && selectedIds.size > 0 && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center justify-between">
          <span className="text-sm text-red-800 font-medium">
            {selectedIds.size} application(s) selected
          </span>
          <button
            onClick={handleBulkDelete}
            className="btn flex items-center gap-2 bg-red-600 text-white hover:bg-red-700"
          >
            <Trash2 className="w-4 h-4" />
            Delete Selected
          </button>
        </div>
      )}

      <div className="card mb-6">
        <div className="flex items-center gap-3 flex-wrap">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            <input
              type="text"
              placeholder="Search by company or role..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input"
              style={{ paddingLeft: '2.25rem' }}
            />
          </div>

          <select
            value={remoteFilter}
            onChange={(e) => setRemoteFilter(e.target.value as RemoteFilter)}
            className="input w-auto"
          >
            <option value="all">All locations</option>
            <option value="remote">Remote only</option>
            <option value="onsite">Onsite only</option>
          </select>

          <button
            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
            className="btn btn-secondary flex items-center gap-2 text-sm"
          >
            <SlidersHorizontal className="w-4 h-4" />
            Advanced
          </button>

          {hasActiveFilters && (
            <button
              onClick={clearFilters}
              className="flex items-center gap-1 text-sm text-brand-600 hover:text-brand-700"
            >
              <X className="w-4 h-4" />
              Clear
            </button>
          )}
        </div>

        {showAdvancedFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <label className="text-xs font-medium text-gray-700 block mb-1">
              Minimum Match Score: {minMatchScore}%
            </label>
            <input
              type="range"
              min="0"
              max="100"
              step="10"
              value={minMatchScore}
              onChange={(e) => setMinMatchScore(parseInt(e.target.value))}
              className="w-full md:w-1/2"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1 md:w-1/2">
              <span>0%</span>
              <span>50%</span>
              <span>100%</span>
            </div>
          </div>
        )}
      </div>

      {showAddForm && (
        <AddApplicationForm
          onClose={() => setShowAddForm(false)}
          onSuccess={() => {
            setShowAddForm(false)
            queryClient.invalidateQueries({ queryKey: ['kanban'] })
          }}
        />
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {filteredColumns.map((column) => (
          <KanbanColumn
            key={column.status}
            status={column.status}
            applications={column.applications}
            count={column.count}
            totalCount={column.totalCount}
            isFiltered={hasActiveFilters}
            selectMode={selectMode}
            selectedIds={selectedIds}
            onStatusChange={(id, status) =>
              updateStatusMutation.mutate({ id, status })
            }
            onDelete={handleDeleteOne}
            onToggleSelect={toggleSelect}
          />
        ))}
      </div>

      {hasActiveFilters && (
        <div className="mt-4 text-sm text-gray-600 text-center">
          Showing{' '}
          <span className="font-semibold text-gray-900">
            {filteredColumns.reduce((sum, c) => sum + c.count, 0)}
          </span>{' '}
          of{' '}
          <span className="font-semibold text-gray-900">
            {filteredColumns.reduce((sum, c) => sum + c.totalCount, 0)}
          </span>{' '}
          applications
        </div>
      )}
    </div>
  )
}

interface ColumnProps {
  status: string
  applications: Application[]
  count: number
  totalCount: number
  isFiltered: boolean
  selectMode: boolean
  selectedIds: Set<string>
  onStatusChange: (id: string, status: ApplicationStatus) => void
  onDelete: (app: Application) => void
  onToggleSelect: (id: string) => void
}

function KanbanColumn({
  status,
  applications,
  count,
  totalCount,
  isFiltered,
  selectMode,
  selectedIds,
  onStatusChange,
  onDelete,
  onToggleSelect,
}: ColumnProps) {
  return (
    <div className="min-w-[250px]">
      <div className="mb-2 flex justify-between items-center">
        <span className="font-semibold text-gray-700">
          {STATUS_LABELS[status]}
        </span>
        <span
          className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_BADGES[status]}`}
        >
          {isFiltered && count !== totalCount
            ? `${count} / ${totalCount}`
            : count}
        </span>
      </div>

      <div
        className={`border-2 border-dashed rounded-lg p-2 ${STATUS_COLORS[status]}`}
        style={{ minHeight: '120px' }}
      >
        {applications.length === 0 ? (
          <div className="text-xs text-gray-400 text-center py-6">
            {isFiltered ? 'No matches' : 'Empty'}
          </div>
        ) : (
          <div
            className="space-y-2 overflow-y-auto pr-1"
            style={{ maxHeight: '520px' }}
          >
            {applications.map((app) => (
              <ApplicationCard
                key={app.id}
                app={app}
                selectMode={selectMode}
                isSelected={selectedIds.has(app.id)}
                onStatusChange={(newStatus) => onStatusChange(app.id, newStatus)}
                onDelete={() => onDelete(app)}
                onToggleSelect={() => onToggleSelect(app.id)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

interface CardProps {
  app: Application
  selectMode: boolean
  isSelected: boolean
  onStatusChange: (s: ApplicationStatus) => void
  onDelete: () => void
  onToggleSelect: () => void
}

function ApplicationCard({
  app,
  selectMode,
  isSelected,
  onStatusChange,
  onDelete,
  onToggleSelect,
}: CardProps) {
  const allowedTransitions = (app.allowed_transitions || []).filter(
    (s) => s !== 'wishlist'
  )

  return (
    <div
      className={`bg-white rounded-lg shadow-sm border p-3 transition-all relative group ${
        isSelected
          ? 'border-brand-500 ring-2 ring-brand-200'
          : 'border-gray-200 hover:shadow-md'
      } ${selectMode ? 'cursor-pointer' : ''}`}
      onClick={selectMode ? onToggleSelect : undefined}
    >
      {/* Select checkbox (only in select mode) */}
      {selectMode && (
        <div className="absolute top-2 right-2">
          {isSelected ? (
            <CheckSquare className="w-4 h-4 text-brand-600" />
          ) : (
            <Square className="w-4 h-4 text-gray-300" />
          )}
        </div>
      )}

      {/* Delete button (only when not in select mode, on hover) */}
      {!selectMode && (
        <button
          onClick={(e) => {
            e.stopPropagation()
            onDelete()
          }}
          className="absolute top-2 right-2 p-1 rounded text-gray-300 hover:text-red-600 hover:bg-red-50 opacity-0 group-hover:opacity-100 transition-opacity"
          title="Delete application"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      )}

      <div
        className={`font-medium text-sm text-gray-900 line-clamp-1 ${
          selectMode ? 'pr-6' : 'pr-5'
        }`}
        title={app.role_title}
      >
        {app.role_title}
      </div>
      <div className="text-xs text-gray-600 mb-1 line-clamp-1" title={app.company}>
        {app.company}
      </div>

      <div className="flex items-center gap-2 mb-2 flex-wrap">
        {app.match_score !== null && app.match_score !== undefined && (
          <span className="text-xs text-brand-600 font-semibold">
            {(app.match_score * 100).toFixed(0)}% match
          </span>
        )}
        {app.is_remote && (
          <span className="text-xs px-1.5 py-0.5 bg-green-100 text-green-700 rounded">
            Remote
          </span>
        )}
        {app.location && !app.is_remote && (
          <span className="text-xs text-gray-500 truncate">{app.location}</span>
        )}
      </div>

      <div className="text-xs text-gray-400 mb-2">
        {new Date(app.applied_date).toLocaleDateString()}
      </div>

      {!selectMode && allowedTransitions.length > 0 && (
        <select
          value=""
          onChange={(e) => {
            if (e.target.value) {
              onStatusChange(e.target.value as ApplicationStatus)
            }
          }}
          onClick={(e) => e.stopPropagation()}
          className="text-xs w-full border border-gray-200 rounded px-2 py-1 bg-gray-50"
        >
          <option value="">Move to...</option>
          {allowedTransitions.map((s) => (
            <option key={s} value={s}>
              {STATUS_LABELS[s] || s}
            </option>
          ))}
        </select>
      )}
    </div>
  )
}

interface AddFormProps {
  onClose: () => void
  onSuccess: () => void
}

function AddApplicationForm({ onClose, onSuccess }: AddFormProps) {
  const [company, setCompany] = useState('')
  const [roleTitle, setRoleTitle] = useState('')
  const [matchScore, setMatchScore] = useState('')

  const createMutation = useMutation({
    mutationFn: () =>
      applications.create({
        company,
        role_title: roleTitle,
        match_score: matchScore ? parseFloat(matchScore) : undefined,
      }),
    onSuccess: () => {
      toast.success('Application added')
      onSuccess()
    },
  })

  return (
    <div className="card mb-6">
      <h3 className="font-semibold mb-4">New Application</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
        <input
          placeholder="Company"
          value={company}
          onChange={(e) => setCompany(e.target.value)}
          className="input"
        />
        <input
          placeholder="Role title"
          value={roleTitle}
          onChange={(e) => setRoleTitle(e.target.value)}
          className="input"
        />
        <input
          placeholder="Match score (0-1)"
          type="number"
          step="0.01"
          min="0"
          max="1"
          value={matchScore}
          onChange={(e) => setMatchScore(e.target.value)}
          className="input"
        />
      </div>
      <div className="flex gap-2">
        <button
          onClick={() => createMutation.mutate()}
          disabled={!company || !roleTitle || createMutation.isPending}
          className="btn btn-primary"
        >
          Add
        </button>
        <button onClick={onClose} className="btn btn-secondary">
          Cancel
        </button>
      </div>
    </div>
  )
}