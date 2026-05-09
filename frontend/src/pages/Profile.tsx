import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { profile } from '../api/profile'

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
    }
  }, [data])

  const updateMutation = useMutation({
    mutationFn: () => profile.update({
      ...form,
      years_experience: form.years_experience ? parseInt(form.years_experience) : null,
    }),
    onSuccess: () => {
      toast.success('Profile updated')
      queryClient.invalidateQueries({ queryKey: ['profile'] })
    },
  })

  if (isLoading) return <div className="p-8 text-gray-500">Loading...</div>

  return (
    <div className="p-8 max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Profile</h1>

      <div className="card space-y-4">
        {[
          { key: 'full_name', label: 'Full name' },
          { key: 'headline', label: 'Headline' },
          { key: 'location', label: 'Location' },
          { key: 'years_experience', label: 'Years of experience', type: 'number' },
          { key: 'linkedin_url', label: 'LinkedIn URL' },
          { key: 'github_url', label: 'GitHub URL' },
          { key: 'portfolio_url', label: 'Portfolio URL' },
        ].map((field) => (
          <div key={field.key}>
            <label className="block text-sm font-medium text-gray-700 mb-1">{field.label}</label>
            <input
              type={field.type || 'text'}
              value={form[field.key as keyof typeof form]}
              onChange={(e) => setForm({ ...form, [field.key]: e.target.value })}
              className="input"
            />
          </div>
        ))}

        <button
          onClick={() => updateMutation.mutate()}
          disabled={updateMutation.isPending}
          className="btn btn-primary"
        >
          {updateMutation.isPending ? 'Saving...' : 'Save Profile'}
        </button>
      </div>
    </div>
  )
}