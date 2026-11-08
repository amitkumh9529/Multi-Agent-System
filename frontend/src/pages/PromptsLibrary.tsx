import { useState } from 'react';
import { usePrompts, useCreatePrompt, useUpdatePrompt, useDeletePrompt } from '../services/prompts';
import Header from '../components/Layout/Header';
import Button from '../components/common/Button';
import Modal from '../components/common/Modal';
import Input from '../components/common/Input';
import Textarea from '../components/common/Textarea';
import type { PromptCreate } from '../types/api';

export default function PromptsLibrary() {
  const { data: prompts, isLoading } = usePrompts();
  const createPrompt = useCreatePrompt();
  const updatePrompt = useUpdatePrompt();
  const deletePrompt = useDeletePrompt();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<number | null>(null);
  const [formData, setFormData] = useState<PromptCreate>({
    name: '',
    description: '',
    system_prompt: '',
  });
  const [searchQuery, setSearchQuery] = useState('');

  const handleOpenModal = (promptId?: number) => {
    if (promptId) {
      const prompt = prompts?.find((p) => p.id === promptId);
      if (prompt) {
        setEditingPrompt(promptId);
        setFormData({
          name: prompt.name,
          description: prompt.description || '',
          system_prompt: prompt.system_prompt,
        });
      }
    } else {
      setEditingPrompt(null);
      setFormData({
        name: '',
        description: '',
        system_prompt: '',
      });
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingPrompt(null);
    setFormData({
      name: '',
      description: '',
      system_prompt: '',
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.system_prompt) {
      alert('Please fill in all required fields');
      return;
    }

    try {
      if (editingPrompt) {
        await updatePrompt.mutateAsync({ id: editingPrompt, prompt: formData });
      } else {
        await createPrompt.mutateAsync(formData);
      }
      handleCloseModal();
    } catch (error) {
      console.error('Error saving prompt:', error);
      alert('Error saving prompt. Please try again.');
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this prompt?')) {
      try {
        await deletePrompt.mutateAsync(id);
      } catch (error) {
        console.error('Error deleting prompt:', error);
        alert('Error deleting prompt. Please try again.');
      }
    }
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <Header title="Prompts Library" />
        <div className="mt-6 text-center">Loading...</div>
      </div>
    );
  }

  return (
    <div>
      <Header title="Prompts Library" subtitle="Manage your system prompts" />
      <div className="p-6">
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:relative sm:justify-start sm:min-h-[40px]">
          <div className="w-full sm:max-w-xs sm:absolute sm:left-1/2 sm:-translate-x-1/2">
            <Input
              placeholder="Search prompts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="w-full sm:w-auto sm:ml-auto">
            <Button onClick={() => handleOpenModal()}>Create Prompt</Button>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {prompts
            ?.filter((prompt) => {
              const query = searchQuery.toLowerCase();
              return (
                prompt.name.toLowerCase().includes(query) ||
                (prompt.description && prompt.description.toLowerCase().includes(query)) ||
                prompt.system_prompt.toLowerCase().includes(query)
              );
            })
            .map((prompt) => (
              <div key={prompt.id} className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
                <h3 className="text-lg font-semibold text-gray-900">{prompt.name}</h3>
                {prompt.description && (
                  <p className="mt-2 text-sm text-gray-600 line-clamp-2">{prompt.description}</p>
                )}
                <div className="mt-3">
                  <p className="text-xs text-gray-500 line-clamp-3">
                    {prompt.system_prompt.substring(0, 150)}
                    {prompt.system_prompt.length > 150 ? '...' : ''}
                  </p>
                </div>
                <div className="mt-4 flex gap-2">
                  <Button size="sm" variant="secondary" onClick={() => handleOpenModal(prompt.id)}>
                    Edit
                  </Button>
                  <Button size="sm" variant="danger" onClick={() => handleDelete(prompt.id)}>
                    Delete
                  </Button>
                </div>
              </div>
            ))}
        </div>

        {prompts?.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            No prompts found. Create your first prompt to get started.
          </div>
        )}
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingPrompt ? 'Edit Prompt' : 'Create Prompt'}
        footer={
          <>
            <Button variant="ghost" onClick={handleCloseModal}>
              Cancel
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={createPrompt.isPending || updatePrompt.isPending}
            >
              {editingPrompt ? 'Update' : 'Create'}
            </Button>
          </>
        }
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Name *"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />
          <Textarea
            label="Description"
            value={formData.description || ''}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows={2}
          />
          <Textarea
            label="System Prompt *"
            value={formData.system_prompt}
            onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
            rows={10}
            required
            className="font-mono text-sm"
          />
        </form>
      </Modal>
    </div>
  );
}

