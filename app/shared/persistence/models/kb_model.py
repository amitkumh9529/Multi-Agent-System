import uuid
from app.shared.schemas.kb_schemas import ProcessingStatus
from typing import List, Optional
from sqlalchemy import String, DateTime, ForeignKey, Text, Enum, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.shared.persistence.models import AgentModel
from ..db_client import Base



class KnowledgeBaseModel(Base):
    __tablename__ = "knowledge_bases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relazione: Una KB ha molti documenti
    # cascade="all, delete-orphan" assicura che se cancello la KB, cancello anche i record dei file
    documents: Mapped[List["DocumentModel"]] = relationship(
        "DocumentModel",
        back_populates="knowledge_base",
        cascade="all, delete-orphan"
    )


    agents: Mapped[List[AgentModel]] = relationship(
        "AgentModel",
        secondary="agent_kbs",
        back_populates="knowledge_bases"
    )


class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Collegamento alla KB padre
    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("knowledge_bases.id", ondelete="CASCADE"),
        index=True
    )

    filename: Mapped[str] = mapped_column(String(255))  # Nome originale file
    file_path: Mapped[str] = mapped_column(String)  # Path locale o S3 key
    file_type: Mapped[str] = mapped_column(String(50))  # es. application/pdf
    file_size: Mapped[int] = mapped_column(Integer, default=0)  # Bytes
    content_hash: Mapped[str] = mapped_column(String(64), index=True) # SHA-256 del contenuto per rilevare duplicati

    # Stato del processo RAG
    status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus),
        default=ProcessingStatus.PENDING
    )
    #error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relazione inversa: un documento appartiene a una KB
    knowledge_base: Mapped["KnowledgeBaseModel"] = relationship(
        "KnowledgeBaseModel",
        back_populates="documents"
    )