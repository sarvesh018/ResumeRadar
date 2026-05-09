import { useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Upload, FileText, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { resumes } from '../api/profile'

export default function Resumes() {
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [file, setFile] = useState<File | null>(null)
  const [versionName, setVersionName] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['resumes'],
    queryFn: resumes.list,
  })

  const uploadMutation = useMutation({
    mutationFn: () => resumes.upload(file!, versionName),
    onSuccess: (data) => {
      toast.success(`Resume uploaded with ${data.resume.skill_count} skills extracted`)
      setFile(null)
      setVersionName('')
      if (fileInputRef.current) fileInputRef.current.value = ''
      queryClient.invalidateQueries({ queryKey: ['resumes'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.title || 'Upload failed')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => resumes.delete(id),
    onSuccess: () => {
      toast.success('Resume deleted')
      queryClient.invalidateQueries({ queryKey: ['resumes'] })
    },
  })

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">My Resumes</h1>

      <div className="card mb-6">
        <h2 className="text-lg font-semibold mb-4">Upload new resume</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Version name</label>
            <input
              type="text"
              value={versionName}
              onChange={(e) => setVersionName(e.target.value)}
              className="input"
              placeholder="e.g., DevOps-focused v2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">File (PDF or DOCX)</label>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="input"
            />
          </div>

          <button
            onClick={() => uploadMutation.mutate()}
            disabled={!file || !versionName || uploadMutation.isPending}
            className="btn btn-primary flex items-center gap-2"
          >
            <Upload className="w-4 h-4" />
            {uploadMutation.isPending ? 'Uploading...' : 'Upload Resume'}
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="text-gray-500">Loading...</div>
      ) : data?.resumes.length === 0 ? (
        <div className="card text-center py-8 text-gray-500">
          No resumes yet. Upload your first one above.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data?.resumes.map((resume) => (
            <div key={resume.id} className="card">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <FileText className="w-8 h-8 text-brand-600" />
                  <div>
                    <div className="font-semibold">{resume.version_name}</div>
                    <div className="text-sm text-gray-600">
                      {resume.file_type.toUpperCase()} · {new Date(resume.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => {
                    if (confirm('Delete this resume?')) deleteMutation.mutate(resume.id)
                  }}
                  className="text-gray-400 hover:text-red-600"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}