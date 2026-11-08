import { useState, useEffect } from 'react';
import { useAgents, useCreateAgent, useUpdateAgent, useDeleteAgent, useAgent } from '../services/agents';
import { usePrompts } from '../services/prompts';
import { useLLMModels } from '../services/llm';
import { useTools } from '../services/tools';
import { useKnowledgeBases } from '../services/kb';
import { apiClient } from '../services/api';
import Header from '../components/Layout/Header';
import Button from '../components/common/Button';
import Modal from '../components/common/Modal';
import Input from '../components/common/Input';
import Textarea from '../components/common/Textarea';
import Select from '../components/common/Select';
import MultiSelect from '../components/common/MultiSelect';
import type { AgentCreate, AgentType, AgentReadFull } from '../types/api';

export default function AgentsLibrary() {
  const { data: agents, isLoading } = useAgents();
  const { data: prompts } = usePrompts();
  const { data: llmModels } = useLLMModels();
  const { data: tools } = useTools();
  const { data: knowledgeBases } = useKnowledgeBases();
  const createAgent = useCreateAgent();
  const updateAgent = useUpdateAgent();
  const deleteAgent = useDeleteAgent();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [viewingAgent, setViewingAgent] = useState<number | null>(null);
  const [editingAgent, setEditingAgent] = useState<number | null>(null);
  const [formData, setFormData] = useState<AgentCreate>({
    name: '',
    description: '',
    prompt_id: null,
    llm_model_id: 0,
    temperature: 0,
    agent_type: 'worker',
    tool_ids: [],
    kb_ids: [],
  });
  const [searchQuery, setSearchQuery] = useState('');

  const handleOpenModal = async (agentId?: number) => {
    if (agentId) {
      const agent = agents?.find((a) => a.id === agentId);
      if (agent) {
        setEditingAgent(agentId);
        console.log('Opening modal for editing agent:', agentId, '| Agent data:', agent);
        // Fetch full agent data to get tools and knowledge bases
        try {
          const { data: fullAgent } = await apiClient.get<AgentReadFull>(`/api/v1/control/agents/${agentId}`);
          const initialFormData = {
            name: agent.name,
            description: agent.description,
            prompt_id: agent.prompt_id,
            llm_model_id: agent.llm_model_id,
            temperature: agent.temperature,
            agent_type: agent.agent_type as AgentType,
            tool_ids: fullAgent.tools?.map((t) => t.id) || [],
            kb_ids: fullAgent.knowledge_bases?.map((kb) => kb.id).filter((id): id is string => id !== null) || [],
          };
          console.log('Setting form data (edit mode):', initialFormData);
          setFormData(initialFormData);
        } catch (error) {
          console.error('Error fetching full agent data:', error);
          // Fallback to basic agent data if fetch fails
          const fallbackFormData = {
            name: agent.name,
            description: agent.description,
            prompt_id: agent.prompt_id,
            llm_model_id: agent.llm_model_id,
            temperature: agent.temperature,
            agent_type: agent.agent_type as AgentType,
            tool_ids: [],
            kb_ids: [],
          };
          console.log('Setting form data (fallback):', fallbackFormData);
          setFormData(fallbackFormData);
        }
      }
    } else {
      console.log('Opening modal for creating new agent');
      setEditingAgent(null);
      const newFormData: AgentCreate = {
        name: '',
        description: '',
        prompt_id: null,
        llm_model_id: 0,
        temperature: 0,
        agent_type: 'worker',
        tool_ids: [],
        kb_ids: [],
      };
      console.log('Setting form data (create mode):', newFormData);
      setFormData(newFormData);
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingAgent(null);
    setViewingAgent(null);
  };

  // Auto-select first LLM model when creating a new agent
  useEffect(() => {
    if (isModalOpen && !editingAgent && !viewingAgent && llmModels && llmModels.length > 0) {
      // Only set if llm_model_id is 0 or invalid
      setFormData((prev) => {
        if (!prev.llm_model_id || prev.llm_model_id <= 0) {
          const firstModelId = llmModels[0].id;
          console.log('Auto-selecting first LLM model:', firstModelId);
          return { ...prev, llm_model_id: firstModelId };
        }
        return prev;
      });
    }
  }, [isModalOpen, editingAgent, viewingAgent, llmModels]);

  const handleViewAgent = (id: number) => {
    setViewingAgent(id);
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Debug: log all form data
    console.log('=== Form Validation Debug ===');
    console.log('Form Data:', formData);
    console.log('name:', formData.name, '| Valid:', !!formData.name);
    console.log('description:', formData.description, '| Valid:', !!formData.description);
    console.log('llm_model_id:', formData.llm_model_id, '| Type:', typeof formData.llm_model_id, '| Valid:', !!(formData.llm_model_id && formData.llm_model_id > 0));
    console.log('agent_type:', formData.agent_type);
    console.log('temperature:', formData.temperature);
    console.log('prompt_id:', formData.prompt_id);
    console.log('tool_ids:', formData.tool_ids);
    console.log('kb_ids:', formData.kb_ids);

    // Check each field individually
    const errors: string[] = [];
    if (!formData.name || formData.name.trim() === '') {
      errors.push('Name is required');
    }
    if (!formData.description || formData.description.trim() === '') {
      errors.push('Description is required');
    }
    if (!formData.llm_model_id || formData.llm_model_id <= 0) {
      errors.push(`LLM Model is required (current value: ${formData.llm_model_id})`);
    }

    if (errors.length > 0) {
      console.error('Validation errors:', errors);
      alert(`Please fill in all required fields:\n${errors.join('\n')}`);
      return;
    }

    try {
      if (editingAgent) {
        await updateAgent.mutateAsync({ id: editingAgent, agent: formData });
      } else {
        await createAgent.mutateAsync(formData);
      }
      handleCloseModal();
    } catch (error) {
      console.error('Error saving agent:', error);
      alert('Error saving agent. Please try again.');
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this agent?')) {
      try {
        await deleteAgent.mutateAsync(id);
      } catch (error) {
        console.error('Error deleting agent:', error);
        alert('Error deleting agent. Please try again.');
      }
    }
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <Header title="Agents Library" />
        <div className="mt-6 text-center">Loading...</div>
      </div>
    );
  }

  const filteredAgents = agents?.filter((agent) => {
    const query = searchQuery.toLowerCase();
    return (
      agent.name.toLowerCase().includes(query) ||
      agent.description.toLowerCase().includes(query)
    );
  }) || [];

  const supervisors = filteredAgents.filter((a) => a.agent_type === 'supervisor');
  const workers = filteredAgents.filter((a) => a.agent_type === 'worker');

  return (
    <div>
      <Header title="Agents Library" subtitle="Manage your AI agents" />
      <div className="p-6">
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:relative sm:justify-start sm:min-h-[40px]">
          <div className="w-full sm:max-w-xs sm:absolute sm:left-1/2 sm:-translate-x-1/2">
            <Input
              placeholder="Search agents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="w-full sm:w-auto sm:ml-auto">
            <Button onClick={() => handleOpenModal()}>Create Agent</Button>
          </div>
        </div>

        {/* Supervisors Section */}
        {supervisors.length > 0 && (
          <div className="mb-8">
            <h2 className="mb-4 text-lg font-semibold text-gray-900 border-b border-gray-200 pb-2">
              Supervisors
            </h2>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {supervisors.map((agent) => (
                <div key={agent.id} className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
                      <p className="mt-1 text-sm text-gray-600 line-clamp-2">{agent.description}</p>
                      <div className="mt-2 flex gap-2">
                        <span className="inline-flex items-center rounded-full bg-purple-100 px-2.5 py-0.5 text-xs font-medium text-purple-800">
                          {agent.agent_type}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 flex gap-2">
                    <Button size="sm" variant="secondary" onClick={() => handleViewAgent(agent.id)}>
                      View
                    </Button>
                    <Button size="sm" variant="secondary" onClick={() => handleOpenModal(agent.id)}>
                      Edit
                    </Button>
                    <Button size="sm" variant="danger" onClick={() => handleDelete(agent.id)}>
                      Delete
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Worker Agents Section */}
        {workers.length > 0 && (
          <div>
            <h2 className="mb-4 text-lg font-semibold text-gray-900 border-b border-gray-200 pb-2">
              Worker Agents
            </h2>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {workers.map((agent) => (
                <div key={agent.id} className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
                      <p className="mt-1 text-sm text-gray-600 line-clamp-2">{agent.description}</p>
                      <div className="mt-2 flex gap-2">
                        <span className="inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800">
                          {agent.agent_type}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 flex gap-2">
                    <Button size="sm" variant="secondary" onClick={() => handleViewAgent(agent.id)}>
                      View
                    </Button>
                    <Button size="sm" variant="secondary" onClick={() => handleOpenModal(agent.id)}>
                      Edit
                    </Button>
                    <Button size="sm" variant="danger" onClick={() => handleDelete(agent.id)}>
                      Delete
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {agents?.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            No agents found. Create your first agent to get started.
          </div>
        )}
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={
          viewingAgent
            ? 'Agent Details'
            : editingAgent
              ? 'Edit Agent'
              : 'Create Agent'
        }
        footer={
          viewingAgent ? (
            <Button onClick={handleCloseModal}>Close</Button>
          ) : (
            <>
              <Button variant="ghost" onClick={handleCloseModal}>
                Cancel
              </Button>
              <Button
                onClick={handleSubmit}
                disabled={createAgent.isPending || updateAgent.isPending}
              >
                {editingAgent ? 'Update' : 'Create'}
              </Button>
            </>
          )
        }
      >
        {viewingAgent ? (
          <AgentDetails agentId={viewingAgent} />
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Name *"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
            <Textarea
              label="Description *"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={3}
              required
            />
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Agent Type *"
                value={formData.agent_type}
                onChange={(e) => setFormData({ ...formData, agent_type: e.target.value as AgentType })}
                options={[
                  { value: 'worker', label: 'Worker' },
                  { value: 'supervisor', label: 'Supervisor' },
                ]}
                required
              />
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Temperature: {formData.temperature}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={formData.temperature}
                  onChange={(e) => setFormData({ ...formData, temperature: parseFloat(e.target.value) })}
                  className="w-full"
                />
              </div>
            </div>
            <Select
              label="LLM Model *"
              value={formData.llm_model_id > 0 ? String(formData.llm_model_id) : ''}
              onChange={(e) => {
                const selectedValue = e.target.value;
                console.log('LLM Model onChange - raw value:', selectedValue, '| type:', typeof selectedValue);

                if (selectedValue && selectedValue !== '') {
                  const parsedValue = parseInt(selectedValue, 10);
                  console.log('LLM Model onChange - parsed value:', parsedValue, '| isNaN:', isNaN(parsedValue));

                  if (!isNaN(parsedValue) && parsedValue > 0) {
                    console.log('LLM Model onChange - updating formData with:', parsedValue);
                    setFormData((prev) => {
                      const updated = { ...prev, llm_model_id: parsedValue };
                      console.log('LLM Model onChange - new formData:', updated);
                      return updated;
                    });
                  } else {
                    console.error('LLM Model onChange - invalid parsed value:', parsedValue);
                  }
                } else {
                  console.warn('LLM Model onChange - empty value selected');
                }
              }}
              options={llmModels?.map((m) => ({ value: String(m.id), label: `${m.name} (${m.provider})` })) || []}
              required
            />
            <Select
              label="Prompt (Optional)"
              value={formData.prompt_id ? String(formData.prompt_id) : ''}
              onChange={(e) => setFormData({ ...formData, prompt_id: e.target.value ? parseInt(e.target.value, 10) : null })}
              options={[
                { value: '', label: 'None' },
                ...(prompts?.map((p) => ({ value: p.id, label: p.name })) || []),
              ]}
            />
            <MultiSelect
              label="Tools"
              selected={formData.tool_ids || []}
              onChange={(selected) => setFormData({ ...formData, tool_ids: selected as number[] })}
              options={tools?.map((t) => ({ value: t.id, label: t.display_name })) || []}
              placeholder="Select tools"
            />
            <MultiSelect
              label="Knowledge Bases"
              selected={(formData.kb_ids || []).filter((id) => id !== null) as (string | number)[]}
              onChange={(selected) => setFormData({ ...formData, kb_ids: selected as (string | null)[] })}
              options={knowledgeBases?.map((kb) => ({ value: kb.id, label: kb.name })) || []}
              placeholder="Select knowledge bases"
            />
          </form>
        )}
      </Modal>
    </div>
  );
}

function AgentDetails({ agentId }: { agentId: number }) {
  const { data: agent, isLoading } = useAgent(agentId);

  if (isLoading) {
    return <div>Loading agent details...</div>;
  }

  if (!agent) {
    return <div>Agent not found</div>;
  }

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold">{agent.name}</h3>
        <p className="text-sm text-gray-600">{agent.description}</p>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <span className="text-sm font-medium text-gray-700">Type:</span>
          <span className="ml-2 text-sm text-gray-900">{agent.agent_type}</span>
        </div>
        <div>
          <span className="text-sm font-medium text-gray-700">Temperature:</span>
          <span className="ml-2 text-sm text-gray-900">{agent.temperature}</span>
        </div>
      </div>
      <div>
        <span className="text-sm font-medium text-gray-700">LLM Model:</span>
        <span className="ml-2 text-sm text-gray-900">
          {agent.llm_model.name} ({agent.llm_model.provider})
        </span>
      </div>
      {agent.prompt && (
        <div>
          <span className="text-sm font-medium text-gray-700">Prompt:</span>
          <span className="ml-2 text-sm text-gray-900">{agent.prompt.name}</span>
        </div>
      )}
      {agent.tools.length > 0 && (
        <div>
          <span className="text-sm font-medium text-gray-700">Tools:</span>
          <div className="mt-1 flex flex-wrap gap-2">
            {agent.tools.map((tool) => (
              <span
                key={tool.id}
                className="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-800"
              >
                {tool.display_name}
              </span>
            ))}
          </div>
        </div>
      )}
      {agent.knowledge_bases.length > 0 && (
        <div>
          <span className="text-sm font-medium text-gray-700">Knowledge Bases:</span>
          <div className="mt-1 flex flex-wrap gap-2">
            {agent.knowledge_bases.map((kb) => (
              <span
                key={kb.id}
                className="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-800"
              >
                {kb.name}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

