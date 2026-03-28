import { useQuery } from '@tanstack/react-query';
import api from './client';

export function useDashboard() {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: () => api.get('/reports/dashboard').then((r) => r.data),
    refetchInterval: 60_000, // Actualizar cada minuto
  });
}

export function useMetrics(params = {}) {
  return useQuery({
    queryKey: ['metrics', params],
    queryFn: () => api.get('/reports/metrics', { params }).then((r) => r.data),
  });
}
