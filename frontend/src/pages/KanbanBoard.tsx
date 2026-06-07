import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Plus, Search, X, SlidersHorizontal,
  Trash2, CheckSquare, Square, Info, Loader2, ExternalLink,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { applications } from '../api/applications'
import { matcher } from '../api/match'
import type { Application, ApplicationStatus, MatchResult } from '../types/api'

const COLUMN_ORDER: ApplicationStatus[] = [
  'applied', 'screening', 'interviewing', 'offer', 'rejected', 'withdrawn',
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
  const [selectMode, setSelectMode] = useState(false)
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())

  // Skills modal state
  const [activeMatchResultId, setActiveMatchResultId] = useState<string | null>(null)
  const [activeAppInfo, setActiveAppInfo] = useState<{ company: string; role: string } | null>(null)

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
  })

  const handleDeleteOne = (app: Application) => {
    if (!confirm(`Delete this application?\n\n${app.role_title} at ${app.company}\n\nThis cannot be undone.`)) return
    deleteMutation.mutate(app.id, {
      onSuccess: () => toast.success('Application deleted'),
    })
  }

  const handleBulkDelete = async () => {
    if (selectedIds.size === 0) return
    if (!confirm(`Delete ${selectedIds.size} application(s)?\n\nThis cannot be undone.`)) return
    let success = 0, failed = 0
    for (const id of Array.from(selectedIds)) {
      try { await applications.delete(id); success++ }
      catch { failed++ }
    }
    queryClient.invalidateQueries({ queryKey: ['kanban'] })
    setSelectedIds(new Set())
    setSelectMode(false)
    failed === 0
      ? toast.success(`Deleted ${success} application(s)`)
      : toast.error(`Deleted ${success}, failed ${failed}`)
  }

  const handleShowSkills = (app: Application) => {
    if (!app.match_result_id) return
    setActiveMatchResultId(app.match_result_id)
    setActiveAppInfo({ company: app.company, role: app.role_title })
  }

  const toggleSelect = (id: string) => {
    const next = new Set(selectedIds)
    next.has(id) ? next.delete(id) : next.add(id)
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
        if (!app.company.toLowerCase().includes(q) && !app.role_title.toLowerCase().includes(q)) return false
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
      return { status: col.status, count: filtered.length, totalCount: col.applications.length, applications: filtered }
    })
  }, [board, searchQuery, remoteFilter, minMatchScore])

  const hasActiveFilters = searchQuery !== '' || remoteFilter !== 'all' || minMatchScore > 0

  if (isLoading) return <div className="p-8 text-gray-500">Loading...</div>

  return (
    <div className="p-8">
      {/* Skills modal */}
      {activeMatchResultId && activeAppInfo && (
        <SkillsModal
          matchResultId={activeMatchResultId}
          company={activeAppInfo.company}
          role={activeAppInfo.role}
          onClose={() => { setActiveMatchResultId(null); setActiveAppInfo(null) }}
        />
      )}

      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-gray-900">Applications</h1>
        <div className="flex gap-2">
          <button
            onClick={toggleSelectMode}
            className={`btn flex items-center gap-2 ${selectMode ? 'btn-primary' : 'btn-secondary'}`}
          >
            <CheckSquare className="w-4 h-4" />
            {selectMode ? 'Cancel' : 'Select'}
          </button>
          <button onClick={() => setShowAddForm(true)} className="btn btn-primary flex items-center gap-2">
            <Plus className="w-4 h-4" /> Add Application
          </button>
        </div>
      </div>

      {selectMode && selectedIds.size > 0 && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center justify-between">
          <span className="text-sm text-red-800 font-medium">{selectedIds.size} application(s) selected</span>
          <button onClick={handleBulkDelete} className="btn flex items-center gap-2 bg-red-600 text-white hover:bg-red-700">
            <Trash2 className="w-4 h-4" /> Delete Selected
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
          <select value={remoteFilter} onChange={(e) => setRemoteFilter(e.target.value as RemoteFilter)} className="input w-auto">
            <option value="all">All locations</option>
            <option value="remote">Remote only</option>
            <option value="onsite">Onsite only</option>
          </select>
          <button onClick={() => setShowAdvancedFilters(!showAdvancedFilters)} className="btn btn-secondary flex items-center gap-2 text-sm">
            <SlidersHorizontal className="w-4 h-4" /> Advanced
          </button>
          {hasActiveFilters && (
            <button onClick={() => { setSearchQuery(''); setRemoteFilter('all'); setMinMatchScore(0) }} className="flex items-center gap-1 text-sm text-brand-600 hover:text-brand-700">
              <X className="w-4 h-4" /> Clear
            </button>
          )}
        </div>
        {showAdvancedFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <label className="text-xs font-medium text-gray-700 block mb-1">
              Minimum Match Score: {minMatchScore}%
            </label>
            <input type="range" min="0" max="100" step="10" value={minMatchScore}
              onChange={(e) => setMinMatchScore(parseInt(e.target.value))} className="w-full md:w-1/2" />
            <div className="flex justify-between text-xs text-gray-500 mt-1 md:w-1/2">
              <span>0%</span><span>50%</span><span>100%</span>
            </div>
          </div>
        )}
      </div>

      {showAddForm && (
        <AddApplicationForm
          onClose={() => setShowAddForm(false)}
          onSuccess={() => { setShowAddForm(false); queryClient.invalidateQueries({ queryKey: ['kanban'] }) }}
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
            onStatusChange={(id, status) => updateStatusMutation.mutate({ id, status })}
            onDelete={handleDeleteOne}
            onToggleSelect={toggleSelect}
            onShowSkills={handleShowSkills}
          />
        ))}
      </div>

      {hasActiveFilters && (
        <div className="mt-4 text-sm text-gray-600 text-center">
          Showing <span className="font-semibold text-gray-900">{filteredColumns.reduce((s, c) => s + c.count, 0)}</span>{' '}
          of <span className="font-semibold text-gray-900">{filteredColumns.reduce((s, c) => s + c.totalCount, 0)}</span> applications
        </div>
      )}
    </div>
  )
}

// ── Skills Modal ──────────────────────────────────────────────
interface SkillsModalProps {
  matchResultId: string
  company: string
  role: string
  onClose: () => void
}

function SkillsModal({ matchResultId, company, role, onClose }: SkillsModalProps) {
  const { data, isLoading, error } = useQuery<MatchResult>({
    queryKey: ['match', matchResultId],
    queryFn: () => matcher.get(matchResultId),
    staleTime: 5 * 60 * 1000,
  })

  return (
    // Backdrop
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ backgroundColor: 'rgba(0,0,0,0.4)' }}
      onClick={onClose}
    >
      {/* Modal panel */}
      <div
        className="bg-white rounded-xl shadow-xl w-full max-w-md max-h-[85vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-5 py-4 border-b border-gray-200 flex items-start justify-between">
          <div>
            <div className="font-semibold text-gray-900 text-sm">{role}</div>
            <div className="text-xs text-gray-500 mt-0.5">{company}</div>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700 ml-4 mt-0.5">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-auto px-5 py-4">
          {isLoading && (
            <div className="flex items-center justify-center py-10">
              <Loader2 className="w-6 h-6 text-brand-600 animate-spin mr-2" />
              <span className="text-sm text-gray-500">Loading match details...</span>
            </div>
          )}

          {error && (
            <div className="text-sm text-red-600 py-6 text-center">
              Could not load match details. The match analysis may have been deleted.
            </div>
          )}

          {data && (
            <div className="space-y-4">
              {/* Score summary */}
              <div className="flex items-center gap-3">
                <div className="text-center">
                  <div className={`text-3xl font-bold ${
                    data.overall_score >= 0.7 ? 'text-green-600' :
                    data.overall_score >= 0.5 ? 'text-amber-600' : 'text-red-600'
                  }`}>
                    {Math.round(data.overall_score * 100)}%
                  </div>
                  <div className="text-xs text-gray-500">Overall</div>
                </div>
                <div className="flex-1 grid grid-cols-3 gap-2">
                  <div className="bg-gray-50 rounded p-2 text-center">
                    <div className="text-sm font-semibold">{Math.round(data.keyword_score * 100)}%</div>
                    <div className="text-xs text-gray-500">Keyword</div>
                  </div>
                  <div className="bg-gray-50 rounded p-2 text-center">
                    <div className="text-sm font-semibold">{Math.round(data.semantic_score * 100)}%</div>
                    <div className="text-xs text-gray-500">Semantic</div>
                  </div>
                  <div className="bg-gray-50 rounded p-2 text-center">
                    <div className="text-sm font-semibold">{Math.round(data.taxonomy_score * 100)}%</div>
                    <div className="text-xs text-gray-500">Taxonomy</div>
                  </div>
                </div>
              </div>

              {/* Matched skills */}
              {data.matched_skills?.filter((s: any) => s.jd_required).length > 0 && (
                <div>
                  <div className="text-xs font-semibold text-gray-700 mb-2 flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-green-500 inline-block" />
                    Matched Skills ({data.matched_skills.filter((s: any) => s.jd_required).length})
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {data.matched_skills
                      .filter((s: any) => s.jd_required)
                      .map((s: any) => (
                        <span
                          key={s.skill}
                          className="px-2 py-0.5 bg-green-50 text-green-700 border border-green-200 rounded-full text-xs"
                        >
                          {s.skill}
                        </span>
                      ))}
                  </div>
                </div>
              )}

              {/* Missing skills */}
              {data.missing_skills?.length > 0 && (
                <div>
                  <div className="text-xs font-semibold text-gray-700 mb-2 flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-red-500 inline-block" />
                    Missing Skills ({data.missing_skills.length})
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {data.missing_skills.map((s: any) => (
                      <span
                        key={s.skill}
                        className="px-2 py-0.5 bg-red-50 text-red-700 border border-red-200 rounded-full text-xs"
                        title={s.suggestion || ''}
                      >
                        {s.skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* No match data edge case */}
              {data.matched_skills?.length === 0 && data.missing_skills?.length === 0 && (
                <div className="text-xs text-gray-500 text-center py-4">
                  No skill breakdown available for this match.
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ── Kanban Column ─────────────────────────────────────────────
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
  onShowSkills: (app: Application) => void
}

function KanbanColumn({
  status, applications, count, totalCount, isFiltered,
  selectMode, selectedIds, onStatusChange, onDelete, onToggleSelect, onShowSkills,
}: ColumnProps) {
  return (
    <div className="min-w-[250px]">
      <div className="mb-2 flex justify-between items-center">
        <span className="font-semibold text-gray-700">{STATUS_LABELS[status]}</span>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_BADGES[status]}`}>
          {isFiltered && count !== totalCount ? `${count} / ${totalCount}` : count}
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
          <div className="space-y-2 overflow-y-auto pr-1" style={{ maxHeight: '520px' }}>
            {applications.map((app) => (
              <ApplicationCard
                key={app.id}
                app={app}
                selectMode={selectMode}
                isSelected={selectedIds.has(app.id)}
                onStatusChange={(s) => onStatusChange(app.id, s)}
                onDelete={() => onDelete(app)}
                onToggleSelect={() => onToggleSelect(app.id)}
                onShowSkills={() => onShowSkills(app)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

// ── Application Card ──────────────────────────────────────────
interface CardProps {
  app: Application
  selectMode: boolean
  isSelected: boolean
  onStatusChange: (s: ApplicationStatus) => void
  onDelete: () => void
  onToggleSelect: () => void
  onShowSkills: () => void
}

function ApplicationCard({
  app, selectMode, isSelected, onStatusChange, onDelete, onToggleSelect, onShowSkills,
}: CardProps) {
  const allowedTransitions = (app.allowed_transitions || []).filter(s => s !== 'wishlist')
  const hasMatchData = !!app.match_result_id

  return (
    <div
      className={`bg-white rounded-lg shadow-sm border p-3 transition-all relative group ${
        isSelected ? 'border-brand-500 ring-2 ring-brand-200' : 'border-gray-200 hover:shadow-md'
      } ${selectMode ? 'cursor-pointer' : ''}`}
      onClick={selectMode ? onToggleSelect : undefined}
    >
      {/* Select checkbox */}
      {selectMode && (
        <div className="absolute top-2 right-2">
          {isSelected
            ? <CheckSquare className="w-4 h-4 text-brand-600" />
            : <Square className="w-4 h-4 text-gray-300" />}
        </div>
      )}

      {/* Action buttons (hover, normal mode only) */}
      {!selectMode && (
        <div className="absolute top-2 right-2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          {/* Job link — only show when jd_url exists */}
          {app.jd_url ? (
            <a
              href={app.jd_url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="p-1 rounded text-gray-300 hover:text-blue-600 hover:bg-blue-50"
              title="Open job listing"
            >
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          ) : null}
          {/* Info / skills icon — only show when match data exists */}
          {hasMatchData && (
            <button
              onClick={(e) => { e.stopPropagation(); onShowSkills() }}
              className="p-1 rounded text-gray-300 hover:text-brand-600 hover:bg-brand-50"
              title="View matched & missing skills"
            >
              <Info className="w-3.5 h-3.5" />
            </button>
          )}
          {/* Delete icon */}
          <button
            onClick={(e) => { e.stopPropagation(); onDelete() }}
            className="p-1 rounded text-gray-300 hover:text-red-600 hover:bg-red-50"
            title="Delete application"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      <div
        className={`font-medium text-sm text-gray-900 line-clamp-1 ${selectMode ? 'pr-6' : 'pr-20'}`}
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
          <span className="text-xs px-1.5 py-0.5 bg-green-100 text-green-700 rounded">Remote</span>
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
          onChange={(e) => { if (e.target.value) onStatusChange(e.target.value as ApplicationStatus) }}
          onClick={(e) => e.stopPropagation()}
          className="text-xs w-full border border-gray-200 rounded px-2 py-1 bg-gray-50"
        >
          <option value="">Move to...</option>
          {allowedTransitions.map((s) => (
            <option key={s} value={s}>{STATUS_LABELS[s] || s}</option>
          ))}
        </select>
      )}
    </div>
  )
}

// ── Add Application Form ──────────────────────────────────────
interface AddFormProps {
  onClose: () => void
  onSuccess: () => void
}

function AddApplicationForm({ onClose, onSuccess }: AddFormProps) {
  const [company, setCompany] = useState('')
  const [roleTitle, setRoleTitle] = useState('')
  const [matchScore, setMatchScore] = useState('')

  const createMutation = useMutation({
    mutationFn: () => applications.create({
      company, role_title: roleTitle,
      match_score: matchScore ? parseFloat(matchScore) : undefined,
    }),
    onSuccess: () => { toast.success('Application added'); onSuccess() },
  })

  return (
    <div className="card mb-6">
      <h3 className="font-semibold mb-4">New Application</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
        <input placeholder="Company" value={company} onChange={(e) => setCompany(e.target.value)} className="input" />
        <input placeholder="Role title" value={roleTitle} onChange={(e) => setRoleTitle(e.target.value)} className="input" />
        <input placeholder="Match score (0-1)" type="number" step="0.01" min="0" max="1"
          value={matchScore} onChange={(e) => setMatchScore(e.target.value)} className="input" />
      </div>
      <div className="flex gap-2">
        <button onClick={() => createMutation.mutate()} disabled={!company || !roleTitle || createMutation.isPending} className="btn btn-primary">
          Add
        </button>
        <button onClick={onClose} className="btn btn-secondary">Cancel</button>
      </div>
    </div>
  )
}