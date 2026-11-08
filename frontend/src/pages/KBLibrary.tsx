import { useState } from 'react';
import { useKnowledgeBases, useCreateKnowledgeBase, useUpdateKnowledgeBase, useDeleteKnowledgeBase, useKnowledgeBase, useUploadDocument, useDeleteDocument } from '../services/kb';
import Header from '../components/Layout/Header';
import Button from '../components/common/Button';
import Modal from '../components/common/Modal';
import Input from '../components/common/Input';
import Textarea from '../components/common/Textarea';
import FileUpload from '../components/common/FileUpload';
import type { KnowledgeBaseCreate } from '../types/api';

export default function KBLibrary() {
  const { data: knowledgeBases, isLoading } = useKnowledgeBases();
  const createKB = useCreateKnowledgeBase();
  const updateKB = useUpdateKnowledgeBase();
  const deleteKB = useDeleteKnowledgeBase();
  const uploadDocument = useUploadDocument();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [viewingKB, setViewingKB] = useState<string | null>(null);
  const [editingKB, setEditingKB] = useState<string | null>(null);
  const [uploadingKB, setUploadingKB] = useState<string | null>(null);
  const [formData, setFormData] = useState<KnowledgeBaseCreate>({
    name: '',
    description: '',
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleOpenModal = (kbId?: string) => {
    if (kbId) {
      const kb = knowledgeBases?.find((k) => k.id === kbId);
      if (kb) {
        setEditingKB(kbId);
        setFormData({
          name: kb.name,
          description: kb.description || '',
        });
      }
    } else {
      setEditingKB(null);
      setFormData({
        name: '',
        description: '',
      });
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingKB(null);
    setViewingKB(null);
    setFormData({
      name: '',
      description: '',
    });
  };

  const handleViewKB = (id: string) => {
    setViewingKB(id);
    setIsModalOpen(true);
  };

  const handleOpenUploadModal = (kbId: string) => {
    setUploadingKB(kbId);
    setSelectedFile(null);
    setIsUploadModalOpen(true);
  };

  const handleCloseUploadModal = () => {
    setIsUploadModalOpen(false);
    setUploadingKB(null);
    setSelectedFile(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.description || formData.description.trim() === '') {
      alert('Please fill in all required fields');
      return;
    }

    try {
      if (editingKB) {
        await updateKB.mutateAsync({ id: editingKB, kb: formData });
      } else {
        await createKB.mutateAsync(formData);
      }
      handleCloseModal();
    } catch (error) {
      console.error('Error saving knowledge base:', error);
      alert('Error saving knowledge base. Please try again.');
    }
  };

  const handleUpload = async () => {
    if (!uploadingKB || !selectedFile) {
      alert('Please select a file');
      return;
    }

    try {
      await uploadDocument.mutateAsync({ kbId: uploadingKB, file: selectedFile });
      handleCloseUploadModal();
    } catch (error) {
      console.error('Error uploading document:', error);
      alert('Error uploading document. Please try again.');
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this knowledge base?')) {
      try {
        await deleteKB.mutateAsync(id);
      } catch (error) {
        console.error('Error deleting knowledge base:', error);
        alert('Error deleting knowledge base. Please try again.');
      }
    }
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <Header title="Knowledge Bases Library" />
        <div className="mt-6 text-center">Loading...</div>
      </div>
    );
  }

  return (
    <div>
      <Header title="Knowledge Bases Library" subtitle="Manage your knowledge bases and documents" />
      <div className="p-6">
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:relative sm:justify-start sm:min-h-[40px]">
          <div className="w-full sm:max-w-xs sm:absolute sm:left-1/2 sm:-translate-x-1/2">
            <Input
              placeholder="Search knowledge bases..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="w-full sm:w-auto sm:ml-auto">
            <Button onClick={() => handleOpenModal()}>Create Knowledge Base</Button>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {knowledgeBases
            ?.filter((kb) => {
              const query = searchQuery.toLowerCase();
              return (
                kb.name.toLowerCase().includes(query) ||
                (kb.description && kb.description.toLowerCase().includes(query))
              );
            })
            .map((kb) => (
              <div key={kb.id} className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
                <h3 className="text-lg font-semibold text-gray-900">{kb.name}</h3>
                {kb.description && (
                  <p className="mt-2 text-sm text-gray-600 line-clamp-2">{kb.description}</p>
                )}
                <div className="mt-4 flex gap-2">
                  <Button size="sm" variant="secondary" onClick={() => handleViewKB(kb.id)}>
                    View
                  </Button>
                  <Button size="sm" variant="secondary" onClick={() => handleOpenModal(kb.id)}>
                    Edit
                  </Button>
                  <Button size="sm" variant="secondary" onClick={() => handleOpenUploadModal(kb.id)}>
                    Upload
                  </Button>
                  <Button size="sm" variant="danger" onClick={() => handleDelete(kb.id)}>
                    Delete
                  </Button>
                </div>
              </div>
            ))}
        </div>

        {knowledgeBases?.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            No knowledge bases found. Create your first knowledge base to get started.
          </div>
        )}
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={
          viewingKB
            ? 'Knowledge Base Details'
            : editingKB
              ? 'Edit Knowledge Base'
              : 'Create Knowledge Base'
        }
        footer={
          viewingKB ? (
            <Button onClick={handleCloseModal}>Close</Button>
          ) : (
            <>
              <Button variant="ghost" onClick={handleCloseModal}>
                Cancel
              </Button>
              <Button
                onClick={handleSubmit}
                disabled={createKB.isPending || updateKB.isPending}
              >
                {editingKB ? 'Update' : 'Create'}
              </Button>
            </>
          )
        }
      >
        {viewingKB ? (
          <KBDetails kbId={viewingKB} onUpload={() => handleOpenUploadModal(viewingKB)} />
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Name *"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              minLength={3}
              maxLength={50}
            />
            <Textarea
              label="Description *"
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={3}
              required
              minLength={3}
            />
          </form>
        )}
      </Modal>

      <Modal
        isOpen={isUploadModalOpen}
        onClose={handleCloseUploadModal}
        title="Upload Document"
        footer={
          <>
            <Button variant="ghost" onClick={handleCloseUploadModal}>
              Cancel
            </Button>
            <Button
              onClick={handleUpload}
              disabled={!selectedFile || uploadDocument.isPending}
            >
              Upload
            </Button>
          </>
        }
      >
        <FileUpload
          onFileSelect={setSelectedFile}
          accept=".pdf,.txt,.md"
          maxSize={10 * 1024 * 1024}
        />
        {selectedFile && (
          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-700">
              <span className="font-medium">Selected:</span> {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
            </p>
          </div>
        )}
      </Modal>
    </div>
  );
}

function KBDetails({ kbId, onUpload }: { kbId: string; onUpload: () => void }) {
  const { data: kb, isLoading } = useKnowledgeBase(kbId);
  const deleteDocument = useDeleteDocument();

  const handleDeleteDoc = async (docId: string) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        await deleteDocument.mutateAsync({ kbId, docId });
      } catch (error) {
        console.error('Error deleting document:', error);
        alert('Error deleting document. Please try again.');
      }
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      case 'pending':
        return 'bg-gray-100 text-gray-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return <div>Loading knowledge base details...</div>;
  }

  if (!kb) {
    return <div>Knowledge base not found</div>;
  }

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold">{kb.name}</h3>
        {kb.description && <p className="text-sm text-gray-600">{kb.description}</p>}
      </div>
      <div className="flex justify-between items-center">
        <h4 className="text-md font-medium">Documents ({kb.documents.length})</h4>
        <Button size="sm" onClick={onUpload}>
          Upload Document
        </Button>
      </div>
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {kb.documents.length === 0 ? (
          <p className="text-sm text-gray-500">No documents uploaded yet.</p>
        ) : (
          kb.documents.map((doc) => (
            <div key={doc.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{doc.filename}</p>
                <p className="text-xs text-gray-500">
                  {(doc.file_size / 1024).toFixed(2)} KB • {doc.file_type}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getStatusColor(doc.status)}`}>
                  {doc.status}
                </span>
                <Button
                  size="sm"
                  variant="danger"
                  onClick={() => handleDeleteDoc(doc.id)}
                >
                  Delete
                </Button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

