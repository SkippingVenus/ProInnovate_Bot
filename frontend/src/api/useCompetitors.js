import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from './client';

export function useCompetitors() {
  return useQuery({
    queryKey: ['competitors'],
    queryFn: () => api.get('/competitors/').then((r) => r.data),
  });
}

export function useCreateCompetitor() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post('/competitors/', data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['competitors'] }),
  });
}

export function useDeleteCompetitor() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(`/competitors/${id}`).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['competitors'] }),
  });
}
