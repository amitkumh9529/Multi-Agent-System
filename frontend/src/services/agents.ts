import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './api';
import type { AgentRead, AgentReadFull, AgentCreate } from '../types/api';

// Query keys
export const agentKeys = {
  all: ['agents'] as const,
  lists: () => [...agentKeys.all, 'list'] as const,
  list: (filters: string) => [...agentKeys.lists(), { filters }] as const,
  details: () => [...agentKeys.all, 'detail'] as const,
  detail: (id: number) => [...agentKeys.details(), id] as const,
};

// Get all agents
export const useAgents = () => {
  return useQuery({
    queryKey: agentKeys.lists(),
    queryFn: async () => {
      const { data } = await apiClient.get<AgentRead[]>('/api/v1/control/agents');
      return data;
    },
  });
};

// Get agent by ID
export const useAgent = (id: number) => {
  return useQuery({
    queryKey: agentKeys.detail(id),
    queryFn: async () => {
      const { data } = await apiClient.get<AgentReadFull>(`/api/v1/control/agents/${id}`);
      return data;
    },
    enabled: !!id,
  });
};

// Create agent
export const useCreateAgent = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (agent: AgentCreate) => {
      const { data } = await apiClient.post<AgentRead>('/api/v1/control/agents', agent);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: agentKeys.lists() });
    },
  });
};

// Update agent
export const useUpdateAgent = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, agent }: { id: number; agent: AgentCreate }) => {
      const { data } = await apiClient.put<AgentReadFull>(`/api/v1/control/agents/${id}`, agent);
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: agentKeys.lists() });
      queryClient.invalidateQueries({ queryKey: agentKeys.detail(variables.id) });
    },
  });
};

// Delete agent
export const useDeleteAgent = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/api/v1/control/agents/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: agentKeys.lists() });
    },
  });
};

