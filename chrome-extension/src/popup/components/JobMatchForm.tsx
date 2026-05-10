import { useEffect, useState } from 'react'
import { Briefcase, Loader2, Check, X, ExternalLink, RefreshCw } from 'lucide-react'
import { resumeApi, matchApi, applicationApi } from '../api/client'
import { clearLatestJob } from '../../shared/storage'
import type { ExtractedJobData, Resume, MatchResult } from '../../shared/types'

interface Props {
  job: ExtractedJobData
  onClear: () => void
}

type Step = 'review' | 'matching' | 'result' | 'saving' | 'saved'

export default function JobMatchForm({ job, onClear }: Props) {
  const [step, setStep] = useState<Step>('review')
  const [resumes, setResumes] = useState<Resume[]>([])
  const [selectedResumeId, setSelectedResumeId] = useState<string>('')
  const [matchResult, setMatchResult] = useState<MatchResult | null>(null)
  const [error, setError] = useState<string>('')
  const [editedCompany, setEditedCompany] = useState(job.company)
  const [editedRole, setEditedRole] = useState(job.role_title)

  useEffect(() => {
    resumeApi.list()
      .then((list) => {
        setResumes(list)
        const primary = list.find(r => r.is_primary)
        if (primary) setSelectedResumeId(primary.id)
        else if (list.length > 0) setSelectedResumeId(list[0].id)
      })
      .catch(() => {
        setError('Failed to load resumes. Make sure you have uploaded at least one.')
      })
  }, [])

  const handleRunMatch = async () => {
    if (!selectedResumeId) {
      setError('Please select a resume')
      return
    }
    setStep('matching')
    setError('')
    try {
      const result = await matchApi.run(selectedResumeId, job.jd_text, editedCompany, editedRole)
      setMatchResult(result)
      setStep('result')
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.response?.data?.title || 'Match analysis failed'
      setError(typeof msg === 'string' ? msg : 'Match analysis failed')
      setStep('review')
    }
  }

  const handleSaveApplication = async () => {
    if (!matchResult) return
    setStep('saving')
    setError('')
    try {
      await applicationApi.create({
        company: editedCompany,
        role_title: editedRole,
        resume_id: selectedResumeId,
        match_result_id: matchResult.id,
        jd_url: job.jd_url,
        location: job.location,
        is_remote: job.is_remote,
        salary_min: job.salary_min,
        salary_max: job.salary_max,
        match_score: matchResult.overall_score,
      })
      setStep('saved')
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to save application'
      setError(typeof msg === 'string' ? msg : 'Failed to save application')
      setStep('result')
    }
  }

  const handleDismiss = async () => {
    await clearLatestJob()
    chrome.runtime.sendMessage({ type: 'CLEAR_LATEST_JOB' })
    onClear()
  }

  // SAVED state
  if (step === 'saved') {
    return (
      <div className="p-6 text-center">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Check className="w-8 h-8 text-green-600" />
        </div>
        <h2 className="text-lg font-bold text-gray-900 mb-2">Application Saved!</h2>
        <p className="text-sm text-gray-600 mb-4">{editedRole} at {editedCompany}</p>
        {matchResult && (
          <p className="text-xs text-gray-500 mb-6">
            Match score: <span className="font-semibold text-brand-600">
              {(matchResult.overall_score * 100).toFixed(0)}%
            </span>
          </p>
        )}
        <div className="space-y-2">
          <a href="http://localhost:3000/applications" target="_blank" rel="noopener noreferrer"
             className="btn btn-primary w-full flex items-center justify-center gap-2">
            View on Dashboard <ExternalLink className="w-4 h-4" />
          </a>
          <button onClick={handleDismiss} className="btn btn-secondary w-full">Close</button>
        </div>
      </div>
    )
  }

  if (step === 'saving') {
    return (
      <div className="p-6 text-center py-12">
        <Loader2 className="w-12 h-12 text-brand-600 mx-auto mb-3 animate-spin" />
        <p className="text-sm text-gray-600">Saving application...</p>
      </div>
    )
  }

  if (step === 'matching') {
    return (
      <div className="p-6 text-center py-12">
        <Loader2 className="w-12 h-12 text-brand-600 mx-auto mb-3 animate-spin" />
        <p className="text-sm font-medium text-gray-900">Analyzing match...</p>
        <p className="text-xs text-gray-500 mt-1">This takes 3-5 seconds</p>
      </div>
    )
  }

  // RESULT state
  if (step === 'result' && matchResult) {
    const scorePercent = Math.round(matchResult.overall_score * 100)
    const scoreColor = scorePercent >= 70 ? 'text-green-600' : scorePercent >= 50 ? 'text-amber-600' : 'text-red-600'

    return (
      <div className="flex flex-col h-[500px]">
        <div className="px-4 py-3 border-b border-gray-200 bg-white">
          <div className="text-sm font-semibold text-gray-900 truncate">{editedRole}</div>
          <div className="text-xs text-gray-600 truncate">{editedCompany}</div>
        </div>

        <div className="flex-1 overflow-auto p-4 space-y-4">
          <div className="text-center">
            <div className={`text-5xl font-bold ${scoreColor}`}>{scorePercent}%</div>
            <div className="text-xs text-gray-500 mt-1">Match Score</div>
          </div>

          <div className="grid grid-cols-3 gap-2 text-center">
            <div className="p-2 bg-gray-50 rounded">
              <div className="text-xs text-gray-500">Keyword</div>
              <div className="text-sm font-semibold">{Math.round(matchResult.keyword_score * 100)}%</div>
            </div>
            <div className="p-2 bg-gray-50 rounded">
              <div className="text-xs text-gray-500">Semantic</div>
              <div className="text-sm font-semibold">{Math.round(matchResult.semantic_score * 100)}%</div>
            </div>
            <div className="p-2 bg-gray-50 rounded">
              <div className="text-xs text-gray-500">Taxonomy</div>
              <div className="text-sm font-semibold">{Math.round(matchResult.taxonomy_score * 100)}%</div>
            </div>
          </div>

          {matchResult.missing_skills.length > 0 && (
            <div>
              <div className="text-xs font-semibold text-gray-700 mb-2">
                Missing Skills ({matchResult.missing_skills.length})
              </div>
              <div className="flex flex-wrap gap-1">
                {matchResult.missing_skills.slice(0, 8).map((s) => (
                  <span key={s.skill} className="px-2 py-0.5 bg-red-50 text-red-700 text-xs rounded">{s.skill}</span>
                ))}
              </div>
            </div>
          )}

          {matchResult.matched_skills.filter(s => s.jd_required).length > 0 && (
            <div>
              <div className="text-xs font-semibold text-gray-700 mb-2">
                Matched Skills ({matchResult.matched_skills.filter(s => s.jd_required).length})
              </div>
              <div className="flex flex-wrap gap-1">
                {matchResult.matched_skills.filter(s => s.jd_required).slice(0, 8).map((s) => (
                  <span key={s.skill} className="px-2 py-0.5 bg-green-50 text-green-700 text-xs rounded">{s.skill}</span>
                ))}
              </div>
            </div>
          )}
        </div>

        {error && <div className="px-4 text-xs text-red-600">{error}</div>}

        <div className="px-4 py-3 border-t border-gray-200 bg-gray-50 space-y-2">
          <button onClick={handleSaveApplication} className="btn btn-primary w-full flex items-center justify-center gap-2">
            <Check className="w-4 h-4" /> Save Application
          </button>
          <button onClick={handleDismiss} className="btn btn-secondary w-full">Cancel</button>
        </div>
      </div>
    )
  }

  // REVIEW state (default)
  return (
    <div className="flex flex-col h-[500px]">
      <div className="px-4 py-3 border-b border-gray-200 bg-white flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Briefcase className="w-4 h-4 text-brand-600" />
          <span className="text-sm font-semibold">Job Captured</span>
        </div>
        <button onClick={handleDismiss} className="text-gray-400 hover:text-gray-700">
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 overflow-auto p-4 space-y-3">
        <div>
          <label className="label">Company</label>
          <input type="text" value={editedCompany} onChange={(e) => setEditedCompany(e.target.value)} className="input" />
        </div>

        <div>
          <label className="label">Role</label>
          <input type="text" value={editedRole} onChange={(e) => setEditedRole(e.target.value)} className="input" />
        </div>

        {job.location && (
          <div className="text-xs text-gray-600">
            <span className="text-gray-400">Location:</span> {job.location}
            {job.is_remote && <span className="ml-1 text-green-600">· Remote</span>}
          </div>
        )}

        <div>
          <label className="label">Resume to match</label>
          {resumes.length === 0 ? (
            <div className="text-xs text-gray-500 p-2 bg-gray-50 rounded">
              No resumes found.{' '}
              <a href="http://localhost:3000/resumes" target="_blank" rel="noopener noreferrer" className="text-brand-600 hover:underline">
                Upload one
              </a>
            </div>
          ) : (
            <select value={selectedResumeId} onChange={(e) => setSelectedResumeId(e.target.value)} className="input">
              {resumes.map((r) => (
                <option key={r.id} value={r.id}>{r.version_name} {r.is_primary && '(Primary)'}</option>
              ))}
            </select>
          )}
        </div>

        <div>
          <label className="label">Job description ({job.jd_text.length} chars)</label>
          <div className="text-xs text-gray-600 bg-gray-50 p-2 rounded max-h-32 overflow-y-auto">
            {job.jd_text.slice(0, 500)}{job.jd_text.length > 500 && '...'}
          </div>
        </div>

        {error && <div className="text-xs text-red-600 bg-red-50 p-2 rounded">{error}</div>}
      </div>

      <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
        <button onClick={handleRunMatch} disabled={!selectedResumeId || resumes.length === 0}
                className="btn btn-primary w-full flex items-center justify-center gap-2">
          <RefreshCw className="w-4 h-4" /> Run Match Analysis
        </button>
      </div>
    </div>
  )
}