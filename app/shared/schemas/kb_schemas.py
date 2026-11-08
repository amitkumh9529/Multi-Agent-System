import enum
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# Enum per lo stato del documento
class ProcessingStatus(str, enum.Enum):
    PENDING = "pending"  # Caricato, in attesa di elaborazione
    PROCESSING = "processing"  # Chunking/Embedding in corso
    COMPLETED = "completed"  # Pronto per il RAG
    FAILED = "failed"  # Errore durante l'ingestion


# --- DOCUMENT SCHEMAS ---

class DocumentBase(BaseModel):
    filename: str
    file_type: str
    file_size: int

class DocumentRead(DocumentBase):
    id: uuid.UUID
    status: ProcessingStatus

    class Config:
        from_attributes = True

class DocumentReadFull(DocumentBase):
    id: uuid.UUID

    #error_message: Optional[str] = None
    knowledge_base: Optional["KnowledgeBaseRead"]
    status: ProcessingStatus

    class Config:
        from_attributes = True


# --- KNOWLEDGE BASE SCHEMAS ---

class KnowledgeBaseSchema(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., min_length=5)


class KnowledgeBaseCreate(KnowledgeBaseSchema):
    pass


class KnowledgeBaseRead(KnowledgeBaseSchema):
    id: uuid.UUID

    class Config:
        from_attributes = True


class KnowledgeBaseReadFull(KnowledgeBaseSchema):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    # È utile restituire la lista dei documenti quando apri il dettaglio di una KB
    documents: List[DocumentRead] = []

    class Config:
        from_attributes = True