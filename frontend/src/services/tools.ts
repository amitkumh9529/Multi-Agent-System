import { useQuery } from '@tanstack/react-query';
import { apiClient } from './api';
import type { ToolRead } from '../types/api';

// Query keys
export const toolKeys = {
  all: ['tools'] as const,
  lists: () => [...toolKeys.all, 'list'] as const,
};

// Get all tools
export const useTools = () => {
  return useQuery({
    queryKey: toolKeys.lists(),
    queryFn: async () => {
      const { data } = await apiClient.get<ToolRead[]>('/api/v1/control/tools/tools');
      return data;
    },
  });
};

