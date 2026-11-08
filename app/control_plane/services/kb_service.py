# Logica per l'upload e l'indicizzazione dei file
import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.shared.factories.vector_store_factory import VectorStoreFactory
from app.shared.persistence.models.kb_model import DocumentModel
from app.shared.schemas.kb_schemas import KnowledgeBaseCreate, ProcessingStatus
from app.shared.persistence.models import KnowledgeBaseModel
from app.shared.persistence import kb_db, vector_db
from app.shared.blob_storage import storage_provider
from app.shared.utility.hashing import calculate_file_hash


def create_local_kb(db: Session, kb_data: KnowledgeBaseCreate) -> KnowledgeBaseModel:
    """
    Logica di business per gestire la creazione di un kb in locale (ossia con memorizzazione file in locale)
    """

    # 1. Controllo nome kb univoco
    if kb_db.get_kb_by_name(db, kb_data.name):
        raise ValueError(f"Un agente con nome {kb_data.name} esiste già")

    db_kb = kb_db.create_kb(db, kb_data)
    if not db_kb:
        raise ValueError(f"Errore durante la creazione della Knowledge Base")

    # Creo KB in locale
    storage_provider.create_kb_folder(db_kb.id)

    return db_kb


def get_all_kbs(db: Session)-> list[KnowledgeBaseModel]:
    """
    Logica di business per ottenere tutte le kb dal database
    """
    return kb_db.get_all_kbs(db)


def get_kb_by_id(db: Session, kb_id: uuid.UUID ) -> KnowledgeBaseModel:
    db_kb = kb_db.get_kb_by_id(db, kb_id)
    if not db_kb:
        raise ValueError(f"La Knowledge Base con id='{kb_id}' non trovata")
    return db_kb


def update_kb(db: Session, kb_id: uuid.UUID, kb_data: KnowledgeBaseCreate) -> KnowledgeBaseModel:
    """
    Logica di business per consentire la modifica della kb specificata
    """

    # Controllo id esistente
    db_kb = kb_db.get_kb_by_id(db, kb_id)
    if not db_kb:
        raise ValueError(f"La Knowledge Base con id='{kb_id}' non trovata")

    # Verifico che il nome non sia già usato da un' altra kb
    if kb_data.name != db_kb.name:
        existing_kb = kb_db.get_other_kb_with_name(db, name=kb_data.name, kb_id=kb_id)
        if existing_kb:
            raise ValueError(f"Una KnowledgeBase con nome '{kb_data.name}' esiste già")

    # Aggiorno KB
    print(f"Servizio: Agiorno la KB con id='{kb_id}'...")
    return kb_db.update_kb(db=db, kb_old_model=db_kb, kb_data=kb_data, kb_id=kb_id)


def delete_kb(db:Session, kb_id: uuid.UUID):
    """
    Logica di business per eliminare kb specificata
    """
    # 1. Verifica esistenza KB
    db_kb = kb_db.get_kb_by_id(db, kb_id)
    if not db_kb:
        raise ValueError(f"La Knowledge Base con id='{kb_id}' non trovata")

    # 2. ELIMINAZIONE VETTORI (Vector DB)
    collection_name = str(kb_id)
    try:
        vector_db.delete_collection(collection_name)
    except Exception as e:
        raise RuntimeError(f"Errore critico rimozione Vector Store: {str(e)}")

    # 3. ELIMINAZIONE FILE FISICI (Storage)
    try:
        storage_provider.delete_kb_folder(db_kb.id)
    except Exception as e:
        raise RuntimeError(f"Errore durante la rimozione fisica del file: {str(e)}")

    # 4. ELIMINAZIONE KNOWLEDGE BASE e DOCUMENTI da SQL DB
    kb_db.delete_kb(db, db_kb)


def upload_document_to_kb(db: Session, kb_id: uuid.UUID, file: UploadFile) -> DocumentModel:
    """
    Gestisce l'upload: Hash -> Check Duplicati -> Storage Fisico -> DB Record.
    """

    # 1. Verifica esistenza Knowledge Base
    db_kb = kb_db.get_kb_by_id(db, kb_id)
    if not db_kb:
        raise ValueError(f"La Knowledge Base con id='{kb_id}' non trovata")

    # 2. Calcolo Hash per Deduplicazione (Evitiamo di salvare lo stesso file due volte)
    file_hash = calculate_file_hash(file.file)
    existing_doc = kb_db.deduplication_check(db=db, kb_id=kb_id, file_hash=file_hash)
    if existing_doc:
        raise ValueError(f"File duplicato: Il documento '{existing_doc.filename}' contiene gli stessi dati.")

    # 3. Salvataggio Fisico (Locale o S3 tramite astrazione)
    try:
        # storage_provider restituisce il path (o url) dove ha salvato il file
        saved_path = storage_provider.save_file(kb_id, file)
    except Exception as e:
        raise RuntimeError(f"Errore durante il salvataggio fisico del file: {str(e)}")

    # 4. Creazione Record nel DB
    new_doc = DocumentModel(
        id=uuid.uuid4(),
        knowledge_base_id=kb_id,
        filename=file.filename,
        file_path=saved_path,
        file_type=file.content_type or "application/octet-stream",  # se non trova il tipo come fallback usiamo estensione file binario generico
        file_size=file.size,
        content_hash=file_hash,
        status=ProcessingStatus.PENDING  # Status Pending: è pronto per essere indicizzato, ma non lo è ancora
    )

    return kb_db.upload_document(db=db, file_model=new_doc)


def delete_document_from_kb(db: Session, kb_id: uuid.UUID, doc_id: uuid.UUID):
    """
    Elimina un documento: DB Record -> Storage Fisico -> (Futuro: Vettori).
    """

    # 1. Recupera il documento assicurandosi che appartenga a QUELLA KB
    db_doc = kb_db.get_doc_from_kb(db=db, kb_id=kb_id, doc_id=doc_id)
    if not db_doc:
        raise ValueError(f"Documento '{doc_id}' non trovato nella KB '{kb_id}'")

    # 3. Elimina vettori relativi al file dal VectorStore
    try:
        vector_db.delete_documents_from_collection(
            kb_id=str(db_doc.knowledge_base_id),
            filename=db_doc.filename,
            )
    except Exception as e:
        raise RuntimeError(f"Errore critico rimozione Vector Store: {str(e)}")

    # 2. Eliminazione Fisica del File
    try:
        storage_provider.delete_file(db_doc.file_path)
    except Exception as e:
        print(f"⚠️ Warning: Impossibile eliminare il file fisico {db_doc.file_path}: {e}")

    # 4. Elimina entry dal DB SQL
    kb_db.delete_document(db, db_doc)
