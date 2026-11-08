from datetime import datetime, timezone
import uuid
from typing import Optional, Any
from sqlalchemy.orm import Session
from app.shared.persistence.models import KnowledgeBaseModel, DocumentModel
from app.shared.schemas.kb_schemas import KnowledgeBaseCreate


def create_kb(db: Session, kb_schema: KnowledgeBaseCreate) -> KnowledgeBaseModel:
    """
    Salva una nuova kb nel DB.
    """

    db_kb = KnowledgeBaseModel(**kb_schema.model_dump())

    db.add(db_kb)
    db.commit()
    db.refresh(db_kb)

    return db_kb


def filter_kbs(db: Session, kb_ids: list) -> list:
    """
    Filtra la lista delle kb in ingresso restituendo la lista di quelle realmente esistenti nel db
    """
    return db.query(KnowledgeBaseModel).filter(KnowledgeBaseModel.id.in_(kb_ids)).all()


def get_kb_by_name(db: Session, name: str) -> Optional[KnowledgeBaseModel]:
    """
    Query per ottenere (e verificare) esistenza della kb con nome specificato
    """
    return db.query(KnowledgeBaseModel).filter(KnowledgeBaseModel.name == name).first()


def get_all_kbs(db: Session) -> list:
    """
    Restituisce la lista delle bd memorizzate nel db
    """
    return db.query(KnowledgeBaseModel).all()


def get_kb_by_id(db: Session, kb_id: uuid.UUID) -> Optional[KnowledgeBaseModel]:
    """
    Query per ottenere la kb con id specificato dal DB
    """
    return db.query(KnowledgeBaseModel).filter(KnowledgeBaseModel.id == kb_id).first()


def get_other_kb_with_name(db:Session, name: str, kb_id: uuid.UUID) -> Optional[KnowledgeBaseModel]:
    """
    Query per verificare se esiste già nel db una KB col nome specificato
    """
    return db.query(KnowledgeBaseModel).filter(KnowledgeBaseModel.name == name).first()


def update_kb(db: Session, kb_old_model: KnowledgeBaseModel, kb_data: KnowledgeBaseCreate, kb_id: uuid.UUID) -> KnowledgeBaseModel:
    """
    Funzione che aggiorna una KB nel DB.
    """
    for key, value in kb_data.model_dump(exclude_unset=True).items():
        setattr(kb_old_model, key, value)

    kb_old_model.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(kb_old_model)
    return kb_old_model


def delete_kb(db: Session, kb_model: KnowledgeBaseModel):
    """
    Elimina una KB e i relativi documenti dal DB
    """
    db.delete(kb_model)
    db.commit()

#------------------------------------- DOCUMENTI

def deduplication_check(db: Session, kb_id: uuid.UUID, file_hash: str) -> Optional[DocumentModel]:
    """
    Query al db che resistituisce un file con lo stesso contenuto hash dalla KB selezionata
    """
    return db.query(DocumentModel).filter(
        DocumentModel.knowledge_base_id == kb_id,
        DocumentModel.content_hash == file_hash
    ).first()


def upload_document(db: Session, file_model: DocumentModel) -> DocumentModel:
    """
    Aggiunge un nuovo documento caricato alla KB nel db
    """
    db.add(file_model)
    db.commit()
    db.refresh(file_model)
    return file_model


def get_doc_from_kb(db: Session, kb_id: uuid.UUID, doc_id: uuid.UUID) -> Optional[DocumentModel]:
    """
    Query per ottenere doc con id specificato dalla KB specificata
    """

    return db.query(DocumentModel).filter(
        DocumentModel.id == doc_id,
        DocumentModel.knowledge_base_id == kb_id
    ).first()


def delete_document(db: Session, doc: DocumentModel):
    """
    Elimina doc dalla KB sul DB
    """

    db.delete(doc)
    db.commit()
