import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './api';
import type { PromptRead, PromptCreate } from '../types/api';

// Query keys
export const promptKeys = {
  all: ['prompts'] as const,
  lists: () => [...promptKeys.all, 'list'] as const,
  list: (filters: string) => [...promptKeys.lists(), { filters }] as const,
  details: () => [...promptKeys.all, 'detail'] as const,
  detail: (id: number) => [...promptKeys.details(), id] as const,
};

// Get all prompts
export const usePrompts = () => {
  return useQuery({
    queryKey: promptKeys.lists(),
    queryFn: async () => {
      const { data } = await apiClient.get<PromptRead[]>('/api/v1/control/prompts');
      return data;
    },
  });
};

// Get prompt by ID
export const usePrompt = (id: number) => {
  return useQuery({
    queryKey: promptKeys.detail(id),
    queryFn: async () => {
      const { data } = await apiClient.get<PromptRead>(`/api/v1/control/prompts/${id}`);
      return data;
    },
    enabled: !!id,
  });
};

// Create prompt
export const useCreatePrompt = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (prompt: PromptCreate) => {
      const { data } = await apiClient.post<PromptRead>('/api/v1/control/prompts', prompt);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: promptKeys.lists() });
    },
  });
};

// Update prompt
export const useUpdatePrompt = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, prompt }: { id: number; prompt: PromptCreate }) => {
      const { data } = await apiClient.put<PromptRead>(`/api/v1/control/prompts/${id}`, prompt);
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: promptKeys.lists() });
      queryClient.invalidateQueries({ queryKey: promptKeys.detail(variables.id) });
    },
  });
};

// Delete prompt
export const useDeletePrompt = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/api/v1/control/prompts/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: promptKeys.lists() });
    },
  });
};

