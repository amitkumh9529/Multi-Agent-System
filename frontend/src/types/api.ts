// Enums
export type AgentType = 'supervisor' | 'worker';
export type MessageType = 'human' | 'ai' | 'tool';
export type ProcessingStatus = 'pending' | 'processing' | 'completed' | 'failed';

// LLM Models
export interface LLMModelRead {
  id: number;
  name: string;
  api_model_name: string;
  provider: string;
}

// Tools
export interface ToolRead {
  id: number;
  name: string;
  display_name: string;
  description: string | null;
}

// Prompts
export interface PromptCreate {
  name: string;
  description: string | null;
  system_prompt: string;
}

export interface PromptRead {
  id: number;
  name: string;
  description: string | null;
  system_prompt: string;
}

// Knowledge Bases
export interface KnowledgeBaseCreate {
  name: string;
  description: string | null;
}

export interface KnowledgeBaseRead {
  id: string; // UUID
  name: string;
  description: string | null;
}

export interface KnowledgeBaseReadFull {
  id: string; // UUID
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
  documents: DocumentRead[];
}

export interface DocumentRead {
  id: string; // UUID
  filename: string;
  file_type: string;
  file_size: number;
  status: ProcessingStatus;
}

export interface DocumentReadFull {
  id: string; // UUID
  filename: string;
  file_type: string;
  file_size: number;
  status: ProcessingStatus;
  knowledge_base: KnowledgeBaseRead | null;
}

// Agents
export interface AgentCreate {
  name: string;
  description: string;
  prompt_id: number | null;
  llm_model_id: number;
  temperature?: number;
  agent_type?: AgentType;
  tool_ids?: number[];
  kb_ids?: (string | null)[];
}

export interface AgentRead {
  id: number;
  name: string;
  description: string;
  prompt_id: number | null;
  llm_model_id: number;
  temperature: number;
  agent_type: AgentType;
}

export interface AgentReadFull {
  id: number;
  name: string;
  description: string;
  llm_model_id: number;
  temperature: number;
  agent_type: AgentType;
  prompt: PromptRead | null;
  llm_model: LLMModelRead;
  tools: ToolRead[];
  knowledge_bases: KnowledgeBaseRead[];
}

// Teams
export interface TeamCreate {
  name: string;
  description: string | null;
  supervisor_id: number;
  worker_ids?: number[];
}

export interface TeamRead {
  id: number;
  name: string;
  description: string | null;
}

export interface TeamReadFull {
  id: number;
  name: string;
  description: string | null;
  supervisor: AgentRead;
  workers: AgentRead[];
}

// Validation Errors
export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}

export interface HTTPValidationError {
  detail: ValidationError[];
}

// Chat Threads
export interface ChatThreadRead {
  thread_id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}

export interface ToolCall {
  name: string;
  args: Record<string, any>;
  id: string;
}

export interface TextBlock {
  type: 'text';
  text: string;
}

export interface ToolUseBlock {
  type: 'tool_use';
  name: string;
  input: Record<string, any>;
  id: string;
}

export type ContentBlock = TextBlock | ToolUseBlock;



export interface ChatMessageRead {
  id: string; // UUID
  type: MessageType;
  content: string | ContentBlock[];
  created_at?: string;
  tool_calls?: ToolCall[];
  tool_call_id?: string;
  name?: string;

}

export interface ChatRequest {
  message: string;
  team_id: number;
}


export type StreamEventType = 'answer' | 'thought' | 'tool_output' | 'ai' | 'tool';
