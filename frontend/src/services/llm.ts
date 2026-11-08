import { useQuery } from '@tanstack/react-query';
import { apiClient } from './api';
import type { LLMModelRead } from '../types/api';

// Query keys
export const llmKeys = {
  all: ['llm'] as const,
  lists: () => [...llmKeys.all, 'list'] as const,
  details: () => [...llmKeys.all, 'detail'] as const,
  detail: (id: number) => [...llmKeys.details(), id] as const,
};

// Get all LLM models
export const useLLMModels = () => {
  return useQuery({
    queryKey: llmKeys.lists(),
    queryFn: async () => {
      const { data } = await apiClient.get<LLMModelRead[]>('/api/v1/control/llm');
      return data;
    },
  });
};

// Get LLM model by ID
export const useLLMModel = (id: number) => {
  return useQuery({
    queryKey: llmKeys.detail(id),
    queryFn: async () => {
      const { data } = await apiClient.get<LLMModelRead>(`/api/v1/control/llm/${id}`);
      return data;
    },
    enabled: !!id,
  });
};

