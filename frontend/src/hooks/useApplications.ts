import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';
import type { ApplicationDetail, KanbanBoard } from '../types/index';

const fetchApps = () => apiClient.get('/api/v1/applications').then(res => res.data);
const fetchKanban = () => apiClient.get('/api/v1/applications/board').then(res => res.data);
const fetchApp = (id: string) => apiClient.get(`/api/v1/applications/${id}`).then(res => res.data);

export function useApplications() {
  const queryClient = useQueryClient();

  const appsQuery = useQuery({ queryKey: ['applications'], queryFn: fetchApps });
  const kanbanQuery = useQuery<KanbanBoard>({ queryKey: ['applications', 'board'], queryFn: fetchKanban });
  const appQuery = (id: string) => useQuery<ApplicationDetail>({ queryKey: ['application', id], queryFn: () => fetchApp(id), enabled: !!id });

  const createMutation = useMutation({
    mutationFn: (data: any) => apiClient.post('/api/v1/applications', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['applications'] }),
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status, notes }: { id: string; status: string; notes?: string }) =>
      apiClient.patch(`/api/v1/applications/${id}/status`, { status, notes }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['applications'] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => apiClient.delete(`/api/v1/applications/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['applications'] }),
  });

  return { appsQuery, kanbanQuery, appQuery, createMutation, updateStatusMutation, deleteMutation };
}