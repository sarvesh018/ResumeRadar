import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import toast from 'react-hot-toast'
import { applications } from '../api/applications'
import type { Application, ApplicationStatus } from '../types/api'

const STATUS_COLORS: Record<string, string> = {
  wishlist: 'bg-gray-50 border-gray-300',
  applied: 'bg-blue-50 border-blue-300',
  screening: 'bg-yellow-50 border-yellow-300',
  interviewing: 'bg-purple-50 border-purple-300',
  offer: 'bg-green-50 border-green-300',
  rejected: 'bg-red-50 border-red-300',
  withdrawn: 'bg-gray-50 border-gray-300',
}

export default function KanbanBoard() {
  const queryClient = useQueryClient()
  const [showAddForm, setShowAddForm] = useState(false)

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

  if (isLoading) return <div className="p-8 text-gray-500">Loading...</div>

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Applications</h1>
        <button
          onClick={() => setShowAddForm(true)}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add Application
        </button>
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

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 overflow-x-auto">
        {board?.columns.filter(c => !['rejected', 'withdrawn'].includes(c.status) || c.count > 0).map((column) => (
          <div key={column.status} className="min-w-[250px]">
            <div className="font-semibold capitalize text-gray-700 mb-2 flex justify-between">
              <span>{column.status}</span>
              <span className="text-sm text-gray-500">{column.count}</span>
            </div>

            <div className={`border-2 border-dashed rounded-lg p-3 min-h-[200px] ${STATUS_COLORS[column.status]}`}>
              <div className="space-y-2">
                {column.applications.map((app) => (
                  <ApplicationCard
                    key={app.id}
                    app={app}
                    onStatusChange={(status) => updateStatusMutation.mutate({ id: app.id, status })}
                  />
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function ApplicationCard({ app, onStatusChange }: { app: Application; onStatusChange: (s: ApplicationStatus) => void }) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-3">
      <div className="font-medium text-sm">{app.role_title}</div>
      <div className="text-xs text-gray-600 mb-2">{app.company}</div>

      {app.match_score && (
        <div className="text-xs text-brand-600 mb-2">
          Match: {(app.match_score * 100).toFixed(0)}%
        </div>
      )}

      {app.allowed_transitions.length > 0 && (
        <select
          value=""
          onChange={(e) => e.target.value && onStatusChange(e.target.value as ApplicationStatus)}
          className="text-xs w-full border border-gray-200 rounded px-2 py-1"
        >
          <option value="">Move to...</option>
          {app.allowed_transitions.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      )}
    </div>
  )
}

function AddApplicationForm({ onClose, onSuccess }: { onClose: () => void; onSuccess: () => void }) {
  const [company, setCompany] = useState('')
  const [roleTitle, setRoleTitle] = useState('')
  const [matchScore, setMatchScore] = useState('')

  const createMutation = useMutation({
    mutationFn: () => applications.create({
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