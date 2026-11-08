import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './api';
import type { KnowledgeBaseRead, KnowledgeBaseReadFull, KnowledgeBaseCreate, DocumentReadFull } from '../types/api';

// Query keys
export const kbKeys = {
  all: ['kb'] as const,
  lists: () => [...kbKeys.all, 'list'] as const,
  list: (filters: string) => [...kbKeys.lists(), { filters }] as const,
  details: () => [...kbKeys.all, 'detail'] as const,
  detail: (id: string) => [...kbKeys.details(), id] as const,
};

// Get all knowledge bases
export const useKnowledgeBases = () => {
  return useQuery({
    queryKey: kbKeys.lists(),
    queryFn: async () => {
      const { data } = await apiClient.get<KnowledgeBaseRead[]>('/api/v1/control/kb');
      return data;
    },
  });
};

// Get knowledge base by ID
export const useKnowledgeBase = (id: string) => {
  return useQuery({
    queryKey: kbKeys.detail(id),
    queryFn: async () => {
      const { data } = await apiClient.get<KnowledgeBaseReadFull>(`/api/v1/control/kb/${id}`);
      return data;
    },
    enabled: !!id,
  });
};

// Create knowledge base
export const useCreateKnowledgeBase = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (kb: KnowledgeBaseCreate) => {
      const { data } = await apiClient.post<KnowledgeBaseRead>('/api/v1/control/kb', kb);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: kbKeys.lists() });
    },
  });
};

// Update knowledge base
export const useUpdateKnowledgeBase = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, kb }: { id: string; kb: KnowledgeBaseCreate }) => {
      const { data } = await apiClient.put<KnowledgeBaseReadFull>(`/api/v1/control/kb/${id}`, kb);
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: kbKeys.lists() });
      queryClient.invalidateQueries({ queryKey: kbKeys.detail(variables.id) });
    },
  });
};

// Delete knowledge base
export const useDeleteKnowledgeBase = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/control/kb/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: kbKeys.lists() });
    },
  });
};

// Upload document to knowledge base
export const useUploadDocument = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ kbId, file }: { kbId: string; file: File }) => {
      const formData = new FormData();
      formData.append('file', file);
      const { data } = await apiClient.post<DocumentReadFull>(
        `/api/v1/control/kb/${kbId}/documents`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: kbKeys.detail(variables.kbId) });
    },
  });
};

// Delete document from knowledge base
export const useDeleteDocument = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ kbId, docId }: { kbId: string; docId: string }) => {
      await apiClient.delete(`/api/v1/control/kb/${kbId}/documents/${docId}`);
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: kbKeys.detail(variables.kbId) });
    },
  });
};

