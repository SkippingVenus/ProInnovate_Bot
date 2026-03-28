import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from './client';

export function useMessages(filters = {}) {
  return useQuery({
    queryKey: ['messages', filters],
    queryFn: () =>
      api.get('/messages/', { params: filters }).then((r) => r.data),
  });
}

export function useSyncMessages() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.post('/messages/sync').then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['messages'] }),
  });
}

export function useApproveMessage() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, respuesta }) =>
      api.post(`/messages/${id}/approve`, { respuesta }).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['messages'] }),
  });
}

export function useIgnoreMessage() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.post(`/messages/${id}/ignore`).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['messages'] }),
  });
}

export function useRegenerateResponse() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.post(`/messages/${id}/regenerate`).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['messages'] }),
  });
}
