import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from './client';

export function useBusiness() {
  return useQuery({
    queryKey: ['business'],
    queryFn: () => api.get('/businesses/me').then((r) => r.data),
  });
}

export function useConnections() {
  return useQuery({
    queryKey: ['connections'],
    queryFn: () => api.get('/businesses/me/connections').then((r) => r.data),
  });
}

export function useOnboarding() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post('/businesses/onboarding', data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['business'] }),
  });
}

export function useUpdateBusiness() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.put('/businesses/me', data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['business'] }),
  });
}
