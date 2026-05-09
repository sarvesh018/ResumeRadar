import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Target } from 'lucide-react'
import toast from 'react-hot-toast'
import { resumes } from '../api/profile'
import { matcher } from '../api/match'
import type { MatchResult } from '../types/api'

export default function MatchAnalysis() {
  const [selectedResumeId, setSelectedResumeId] = useState('')
  const [jdText, setJdText] = useState('')
  const [jdCompany, setJdCompany] = useState('')
  const [jdRole, setJdRole] = useState('')
  const [result, setResult] = useState<MatchResult | null>(null)

  const { data: resumesData } = useQuery({
    queryKey: ['resumes'],
    queryFn: resumes.list,
  })

  const matchMutation = useMutation({
    mutationFn: () => matcher.match(selectedResumeId, jdText, jdCompany || undefined, jdRole || undefined),
    onSuccess: (data) => {
      setResult(data)
      toast.success(`Match score: ${(data.overall_score * 100).toFixed(0)}%`)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.title || 'Match failed')
    },
  })

  return (
    <div className="p-8 max-w-5xl">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Match Analysis</h1>

      <div className="card mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Resume</label>
            <select
              value={selectedResumeId}
              onChange={(e) => setSelectedResumeId(e.target.value)}
              className="input"
            >
              <option value="">Select a resume...</option>
              {resumesData?.resumes.map((r) => (
                <option key={r.id} value={r.id}>{r.version_name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Company</label>
            <input
              type="text"
              value={jdCompany}
              onChange={(e) => setJdCompany(e.target.value)}
              className="input"
              placeholder="e.g., Google"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
            <input
              type="text"
              value={jdRole}
              onChange={(e) => setJdRole(e.target.value)}
              className="input"
              placeholder="e.g., Senior DevOps Engineer"
            />
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">Job Description</label>
          <textarea
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            className="input min-h-[200px]"
            placeholder="Paste the full job description here (minimum 50 characters)..."
          />
        </div>

        <button
          onClick={() => matchMutation.mutate()}
          disabled={!selectedResumeId || jdText.length < 50 || matchMutation.isPending}
          className="btn btn-primary flex items-center gap-2"
        >
          <Target className="w-4 h-4" />
          {matchMutation.isPending ? 'Analyzing...' : 'Run Match'}
        </button>
      </div>

      {result && (
        <div className="space-y-4">
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Overall Score</h2>
            <div className="flex items-end gap-4 mb-4">
              <div className="text-5xl font-bold text-brand-600">
                {(result.overall_score * 100).toFixed(0)}%
              </div>
              <div className="text-gray-600 mb-2">match</div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <div className="text-sm text-gray-600">Keyword</div>
                <div className="text-xl font-semibold">{(result.keyword_score * 100).toFixed(0)}%</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Semantic</div>
                <div className="text-xl font-semibold">{(result.semantic_score * 100).toFixed(0)}%</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Taxonomy</div>
                <div className="text-xl font-semibold">{(result.taxonomy_score * 100).toFixed(0)}%</div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="card">
              <h3 className="font-semibold text-green-700 mb-3">
                Matched Skills ({result.matched_skills.filter(s => s.jd_required).length})
              </h3>
              <div className="flex flex-wrap gap-2">
                {result.matched_skills
                  .filter(s => s.jd_required)
                  .map((skill) => (
                    <span key={skill.skill} className="px-2 py-1 bg-green-50 text-green-700 rounded text-sm">
                      {skill.skill}
                    </span>
                  ))}
              </div>
            </div>

            <div className="card">
              <h3 className="font-semibold text-red-700 mb-3">
                Missing Skills ({result.missing_skills.length})
              </h3>
              <div className="flex flex-wrap gap-2">
                {result.missing_skills.map((skill) => (
                  <span key={skill.skill} className="px-2 py-1 bg-red-50 text-red-700 rounded text-sm">
                    {skill.skill}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {result.suggestions.length > 0 && (
            <div className="card">
              <h3 className="font-semibold mb-3">Suggestions</h3>
              <ul className="space-y-2">
                {result.suggestions.map((s, i) => (
                  <li key={i} className="flex gap-2 text-sm">
                    <span className="text-brand-600">→</span>
                    <span className="text-gray-700">{s.text}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}