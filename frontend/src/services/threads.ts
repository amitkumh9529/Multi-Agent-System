import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './api';
import type { ChatThreadRead, ChatMessageRead, ChatRequest } from '../types/api';

// Query keys
export const threadKeys = {
  all: ['threads'] as const,
  lists: () => [...threadKeys.all, 'list'] as const,
  details: () => [...threadKeys.all, 'detail'] as const,
  detail: (id: string) => [...threadKeys.details(), id] as const,
  messages: (id: string) => [...threadKeys.detail(id), 'messages'] as const,
};

// Get all threads
export const useThreads = () => {
  return useQuery({
    queryKey: threadKeys.lists(),
    queryFn: async () => {
      const { data } = await apiClient.get<ChatThreadRead[]>('/api/v1/execution/threads');
      return data;
    },
  });
};

// Get messages for a thread
export const useThreadMessages = (threadId: string | undefined) => {
  return useQuery({
    queryKey: threadKeys.messages(threadId || ''),
    queryFn: async () => {
      if (!threadId) return [];
      const { data } = await apiClient.get<ChatMessageRead[]>(
        `/api/v1/execution/threads/${threadId}/messages`
      );
      return data;
    },
    enabled: !!threadId,
  });
};

// Send message with streaming
export const useSendMessage = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      threadId,
      request,
      onChunk,
    }: {
      threadId: string;
      request: ChatRequest;
      onChunk?: (data: any) => void;
    }) => {
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/api/v1/execution/threads/${threadId}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }

      // Handle streaming response (Server-Sent Events)
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let fullContent = '';

      if (reader) {
        while (true) { // eslint-disable-line no-constant-condition
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // Parse SSE format: "data: {...}\n\n"
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep incomplete line in buffer

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const jsonStr = line.slice(6); // Remove "data: " prefix
                const data = JSON.parse(jsonStr);

                if (onChunk) {
                  onChunk(data);
                }

                // Keep tracking full content for return value if applicable
                if (data.type === 'answer' && data.content) {
                  fullContent += data.content;
                } else if (data.type === 'ai' && data.content) {
                  fullContent = data.content; // Legacy behavior or if not streaming delta
                }

              } catch (e) {
                console.error('Error parsing SSE data:', e, line);
              }
            }
          }
        }
      }

      // Invalidate messages query to refresh the list
      queryClient.invalidateQueries({ queryKey: threadKeys.messages(threadId) });
      queryClient.invalidateQueries({ queryKey: threadKeys.lists() });

      return fullContent;
    },
  });
};

// Delete thread
export const useDeleteThread = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (threadId: string) => {
      await apiClient.delete(`/api/v1/execution/threads/${threadId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: threadKeys.lists() });
    },
  });
};

