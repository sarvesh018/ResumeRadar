import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';
import type { MatchRequest, MatchResponse } from '../types';

async function runMatch(data: MatchRequest) {
  const res = await apiClient.post<MatchResponse>('/api/v1/match', data);
  return res.data;
}

async function fetchMatch(id: string) {
  const res = await apiClient.get<MatchResponse>(`/api/v1/match/${id}`);
  return res.data;
}

async function fetchHistory() {
  const res = await apiClient.get('/api/v1/match/history');
  return res.data;
}

export function useMatch() {
  const queryClient = useQueryClient();

  const runMatchMutation = useMutation({
    mutationFn: runMatch,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['match', 'history'] }),
  });

  const matchQuery = (id: string) =>
    useQuery({ queryKey: ['match', id], queryFn: () => fetchMatch(id), enabled: !!id });

  const historyQuery = useQuery({ queryKey: ['match', 'history'], queryFn: fetchHistory });

  return { runMatchMutation, matchQuery, historyQuery };
}