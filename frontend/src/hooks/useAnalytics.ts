import { useQuery } from '@tanstack/react-query';
import apiClient from '../api/client';
import type { DashboardSummary, FunnelResponse, ResumeComparisonResponse, ScoreCallbackResponse, TrendResponse } from '../types';

export function useAnalytics() {
  const dashboardQuery = useQuery<DashboardSummary>({ queryKey: ['analytics', 'dashboard'], queryFn: () => apiClient.get('/api/v1/analytics/dashboard').then(res => res.data) });
  const funnelQuery = useQuery<FunnelResponse>({ queryKey: ['analytics', 'funnel'], queryFn: () => apiClient.get('/api/v1/analytics/funnel').then(res => res.data) });
  const resumeComparisonQuery = useQuery<ResumeComparisonResponse>({ queryKey: ['analytics', 'resumes'], queryFn: () => apiClient.get('/api/v1/analytics/resumes').then(res => res.data) });
  const scoreCallbackQuery = useQuery<ScoreCallbackResponse>({ queryKey: ['analytics', 'score-callback'], queryFn: () => apiClient.get('/api/v1/analytics/score-callback').then(res => res.data) });
  const trendsQuery = useQuery<TrendResponse>({ queryKey: ['analytics', 'trends', 'weekly'], queryFn: () => apiClient.get('/api/v1/analytics/trends?period=weekly').then(res => res.data) });

  return { dashboardQuery, funnelQuery, resumeComparisonQuery, scoreCallbackQuery, trendsQuery };
}