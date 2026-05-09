import { useState, useRef } from 'react';
import { useResumes } from '../hooks/useResumes';
import Button from '../components/shared/Button';
import Input from '../components/shared/Input';
import toast from 'react-hot-toast';

export default function ResumeUpload() {
  const { uploadMutation, resumesQuery } = useResumes();
  const [versionName, setVersionName] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    const file = fileRef.current?.files?.[0];
    if (!file || !versionName.trim()) return toast.error('Please provide a version name and select a file');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('version_name', versionName.trim());

    uploadMutation.mutate(formData, {
      onSuccess: () => {
        toast.success('Resume uploaded!');
        setVersionName('');
        if (fileRef.current) fileRef.current.value = '';
      },
    });
  };

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Upload Resume</h1>
      <form onSubmit={handleUpload} className="space-y-4 bg-white p-6 rounded-lg shadow">
        <Input
          label="Version Name (e.g., DevOps v2)"
          value={versionName}
          onChange={(e) => setVersionName(e.target.value)}
          required
        />
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Resume File (PDF/DOCX)</label>
          <input type="file" ref={fileRef} accept=".pdf,.docx" className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100" />
        </div>
        <Button type="submit" isLoading={uploadMutation.isPending}>Upload</Button>
      </form>

      <h2 className="text-xl font-semibold mt-8 mb-4">Your Resumes</h2>
      <ul className="space-y-2">
        {resumesQuery.data?.map((r) => (
          <li key={r.id} className="bg-white p-3 rounded shadow text-sm">{r.version_name} ({r.file_type})</li>
        ))}
      </ul>
    </div>
  );
}