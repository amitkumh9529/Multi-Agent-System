import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './api';
import type { TeamRead, TeamReadFull, TeamCreate } from '../types/api';

// Query keys
export const teamKeys = {
  all: ['teams'] as const,
  lists: () => [...teamKeys.all, 'list'] as const,
  list: (filters: string) => [...teamKeys.lists(), { filters }] as const,
  details: () => [...teamKeys.all, 'detail'] as const,
  detail: (id: number) => [...teamKeys.details(), id] as const,
};

// Get all teams
export const useTeams = () => {
  return useQuery({
    queryKey: teamKeys.lists(),
    queryFn: async () => {
      const { data } = await apiClient.get<TeamRead[]>('/api/v1/control/teams');
      return data;
    },
  });
};

// Get team by ID
export const useTeam = (id: number) => {
  return useQuery({
    queryKey: teamKeys.detail(id),
    queryFn: async () => {
      const { data } = await apiClient.get<TeamReadFull>(`/api/v1/control/teams/${id}`);
      return data;
    },
    enabled: !!id,
  });
};

// Create team
export const useCreateTeam = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (team: TeamCreate) => {
      const { data } = await apiClient.post<TeamRead>('/api/v1/control/teams', team);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: teamKeys.lists() });
    },
  });
};

// Update team
export const useUpdateTeam = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, team }: { id: number; team: TeamCreate }) => {
      const { data } = await apiClient.put<TeamRead>(`/api/v1/control/teams/${id}`, team);
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: teamKeys.lists() });
      queryClient.invalidateQueries({ queryKey: teamKeys.detail(variables.id) });
    },
  });
};

// Delete team
export const useDeleteTeam = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/api/v1/control/teams/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: teamKeys.lists() });
    },
  });
};

