import { useState, useEffect } from 'react'
import type {KeyboardEvent} from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { X, Plus } from 'lucide-react'
import toast from 'react-hot-toast'
import { profile } from '../api/profile'

// Common tech skills as suggestions
const SKILL_SUGGESTIONS = [
  'Python', 'JavaScript', 'TypeScript', 'Java', 'Go', 'Rust', 'C++',
  'React', 'Angular', 'Vue', 'Node.js', 'Django', 'FastAPI', 'Flask',
  'Docker', 'Kubernetes', 'Terraform', 'Ansible', 'Jenkins', 'GitHub Actions',
  'AWS', 'GCP', 'Azure', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis',
  'Elasticsearch', 'Kafka', 'GraphQL', 'REST API', 'Git', 'Linux',
  'Machine Learning', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy',
  'Grafana', 'Prometheus', 'Datadog', 'Bash', 'Microservices',
]

export default function Profile() {
  const queryClient = useQueryClient()
  const { data, isLoading } = useQuery({ queryKey: ['profile'], queryFn: profile.get })

  const [form, setForm] = useState({
    full_name: '',
    headline: '',
    location: '',
    years_experience: '',
    linkedin_url: '',
    github_url: '',
    portfolio_url: '',
  })

  const [skills, setSkills] = useState<string[]>([])
  const [skillInput, setSkillInput] = useState('')
  const [showSuggestions, setShowSuggestions] = useState(false)

  useEffect(() => {
    if (data) {
      setForm({
        full_name: data.full_name || '',
        headline: data.headline || '',
        location: data.location || '',
        years_experience: data.years_experience?.toString() || '',
        linkedin_url: data.linkedin_url || '',
        github_url: data.github_url || '',
        portfolio_url: data.portfolio_url || '',
      })
      setSkills(data.technical_skills || [])
    }
  }, [data])

  const updateMutation = useMutation({
    mutationFn: () =>
      profile.update({
        ...form,
        years_experience: form.years_experience
          ? parseInt(form.years_experience)
          : null,
        technical_skills: skills,
      }),
    onSuccess: () => {
      toast.success('Profile updated')
      queryClient.invalidateQueries({ queryKey: ['profile'] })
    },
    onError: () => toast.error('Failed to update profile'),
  })

  const addSkill = (skill: string) => {
    const trimmed = skill.trim()
    if (!trimmed) return
    if (skills.map(s => s.toLowerCase()).includes(trimmed.toLowerCase())) {
      toast.error('Skill already added')
      return
    }
    setSkills([...skills, trimmed])
    setSkillInput('')
    setShowSuggestions(false)
  }

  const removeSkill = (skill: string) => {
    setSkills(skills.filter(s => s !== skill))
  }

  const handleSkillKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      if (skillInput.trim()) addSkill(skillInput)
    }
    if (e.key === 'Backspace' && !skillInput && skills.length > 0) {
      removeSkill(skills[skills.length - 1])
    }
  }

  const filteredSuggestions = SKILL_SUGGESTIONS.filter(
    s =>
      s.toLowerCase().includes(skillInput.toLowerCase()) &&
      !skills.map(sk => sk.toLowerCase()).includes(s.toLowerCase())
  ).slice(0, 8)

  if (isLoading) return <div className="p-8 text-gray-500">Loading...</div>

  return (
    <div className="p-8 max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Profile</h1>

      <div className="card space-y-4">
        {/* Basic info fields */}
        {[
          { key: 'full_name', label: 'Full name', placeholder: 'John Doe' },
          { key: 'headline', label: 'Headline', placeholder: 'Senior DevOps Engineer' },
          { key: 'location', label: 'Location', placeholder: 'Pune, India' },
          { key: 'years_experience', label: 'Years of experience', type: 'number', placeholder: '5' },
          { key: 'linkedin_url', label: 'LinkedIn URL', placeholder: 'https://linkedin.com/in/...' },
          { key: 'github_url', label: 'GitHub URL', placeholder: 'https://github.com/...' },
          { key: 'portfolio_url', label: 'Portfolio URL', placeholder: 'https://...' },
        ].map((field) => (
          <div key={field.key}>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {field.label}
            </label>
            <input
              type={field.type || 'text'}
              placeholder={field.placeholder}
              value={form[field.key as keyof typeof form]}
              onChange={(e) => setForm({ ...form, [field.key]: e.target.value })}
              className="input"
            />
          </div>
        ))}

        {/* Technical Skills section */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Technical Skills
          </label>
          <p className="text-xs text-gray-500 mb-2">
            These skills are used to supplement your resume during match analysis.
            Type a skill and press Enter or comma to add.
          </p>

          {/* Tags display + input */}
          <div
            className="input min-h-[48px] flex flex-wrap gap-2 items-center cursor-text"
            onClick={() => document.getElementById('skill-input')?.focus()}
          >
            {skills.map((skill) => (
              <span
                key={skill}
                className="inline-flex items-center gap-1 px-2 py-0.5 bg-brand-100 text-brand-700 rounded-full text-sm font-medium"
              >
                {skill}
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    removeSkill(skill)
                  }}
                  className="text-brand-400 hover:text-brand-700"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
            <input
              id="skill-input"
              type="text"
              value={skillInput}
              onChange={(e) => {
                setSkillInput(e.target.value)
                setShowSuggestions(e.target.value.length > 0)
              }}
              onKeyDown={handleSkillKeyDown}
              onFocus={() => setShowSuggestions(skillInput.length > 0)}
              onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
              placeholder={skills.length === 0 ? 'Type a skill and press Enter...' : ''}
              className="border-none outline-none text-sm flex-1 min-w-[120px] bg-transparent p-0"
            />
          </div>

          {/* Add button */}
          {skillInput.trim() && (
            <button
              type="button"
              onClick={() => addSkill(skillInput)}
              className="mt-1 text-xs text-brand-600 hover:underline flex items-center gap-1"
            >
              <Plus className="w-3 h-3" />
              Add "{skillInput.trim()}"
            </button>
          )}

          {/* Autocomplete suggestions */}
          {showSuggestions && filteredSuggestions.length > 0 && (
            <div className="mt-1 border border-gray-200 rounded-lg shadow-sm bg-white overflow-hidden">
              {filteredSuggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  onMouseDown={(e) => {
                    e.preventDefault()
                    addSkill(suggestion)
                  }}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 text-gray-700"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}

          {/* Quick-add popular skills */}
          {skills.length === 0 && !skillInput && (
            <div className="mt-2">
              <p className="text-xs text-gray-400 mb-1">Quick add:</p>
              <div className="flex flex-wrap gap-1">
                {['Python', 'Docker', 'AWS', 'React', 'Kubernetes', 'PostgreSQL'].map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => addSkill(s)}
                    className="text-xs px-2 py-0.5 border border-gray-300 rounded-full text-gray-600 hover:border-brand-400 hover:text-brand-600"
                  >
                    + {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          <p className="text-xs text-gray-400 mt-2">
            {skills.length} skill{skills.length !== 1 ? 's' : ''} added
          </p>
        </div>

        <button
          onClick={() => updateMutation.mutate()}
          disabled={updateMutation.isPending}
          className="btn btn-primary w-full"
        >
          {updateMutation.isPending ? 'Saving...' : 'Save Profile'}
        </button>
      </div>
    </div>
  )
}