import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';
import type { Resume, ResumeDetail } from '../types/index';

const fetchResumes = () => apiClient.get<Resume[]>('/api/v1/resumes').then(res => res.data);
const fetchResume = (id: string) => apiClient.get<ResumeDetail>(`/api/v1/resumes/${id}`).then(res => res.data);

export function useResumes() {
  const queryClient = useQueryClient();

  const resumesQuery = useQuery({ queryKey: ['resumes'], queryFn: fetchResumes });
  const resumeQuery = (id: string) => useQuery({ queryKey: ['resume', id], queryFn: () => fetchResume(id), enabled: !!id });

  const uploadMutation = useMutation({
    mutationFn: (formData: FormData) => apiClient.post('/api/v1/resumes/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['resumes'] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => apiClient.delete(`/api/v1/resumes/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['resumes'] }),
  });

  return { resumesQuery, resumeQuery, uploadMutation, deleteMutation };
}