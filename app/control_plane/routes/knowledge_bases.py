import uuid

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session

from app.shared.persistence.db_client import get_db
from app.control_plane.services import kb_service, ingestion_service
from app.shared.schemas.kb_schemas import KnowledgeBaseRead, KnowledgeBaseCreate, KnowledgeBaseReadFull, DocumentRead, \
    DocumentReadFull

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=KnowledgeBaseRead)
def create_knowledge_base(
        kb_data: KnowledgeBaseCreate,
        db: Session = Depends(get_db)
):
    """
    Crea una nuova knowledge base nel sistema
    """
    try:
        created_kb = kb_service.create_local_kb(db, kb_data)
        return created_kb
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[KnowledgeBaseRead])
def read_kb(db: Session = Depends(get_db)):
    """
    Restituisce la lista di Knowledge Bases nel sistema
    """
    try:
        return kb_service.get_all_kbs(db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{kb_id}", response_model=KnowledgeBaseReadFull)
def read_kb(
        kb_id: uuid.UUID,
        db: Session = Depends(get_db),
):
    """
    Restituisce la lista di Knowledge Bases nel sistema
    """
    try:
        return kb_service.get_kb_by_id(db, kb_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{kb_id}", response_model=KnowledgeBaseReadFull)
def update_kb(
        kb_id: uuid.UUID,
        kb_data: KnowledgeBaseCreate,
        db: Session = Depends(get_db)
):
    """
    Applica update alla knowledge base selezionata nel sistema
    """
    try:
        return kb_service.update_kb(db, kb_id, kb_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_kb(
        kb_id: uuid.UUID,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    """
    Rimuove la knowledge base selezionata nel sistema: i file in locale, i vettori nel database
    """
    try:
        kb_service.delete_kb(db, kb_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))



# API DOCUMENTS

@router.post("/{kb_id}/documents", status_code=status.HTTP_201_CREATED, response_model=DocumentReadFull)
def upload_doc_to_kb(
    kb_id: uuid.UUID,
    background_tasks: BackgroundTasks,  # Per svolgere task di ingestion in Background
    file: UploadFile = File(...), # Multipart Form Data
    db: Session = Depends(get_db)
):
    """
    Carica un file (PDF, TXT, MD) nella Knowledge Base specificata.
    """

    # Validazione estensione opzionale
    allowed_types = ["application/pdf", "text/plain", "text/markdown"]
    if file.content_type not in allowed_types and not file.filename.endswith(('.md', '.txt', '.pdf')):
         # Nota: il content-type del browser a volte è inaffidabile, meglio controllare estensione
         pass

    try:
        # 1. Upload fisico del documento e creazione record nel db con status PENDING (Sincrono)
        new_doc = kb_service.upload_document_to_kb(db, kb_id, file)

        # 2. Pipeline di ingestion del documen per il RAG (Asincrono / Background)
        background_tasks.add_task(run_ingestion_background, new_doc.id, kb_id)

        return new_doc
    except ValueError as e:
        # Errori logici (duplicati, kb non trovata) -> 400 o 409
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # Errori di sistema (disco pieno, permessi) -> 500
        raise HTTPException(status_code=500, detail=str(e))


def run_ingestion_background(doc_id: uuid.UUID, kb_id: uuid.UUID):
    """
    Wrapper per avviare la pipeline di ingestion del documento
    e gestire la sessione DB in Background.
    """
    from app.shared.persistence.db_client import SessionLocal
    # Apriamo una sessione dedicata per il task in background
    db = SessionLocal()         # Dobbiamo creare una nuova sessione perchè quella dell'API verrà chiusa appena salvato il documento nel DB
    try:
        ingestion_service.process_document_task(db, doc_id, kb_id)
    finally:
        db.close()


@router.delete("/{kb_id}/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doc_from_kb(
    kb_id: uuid.UUID,
    doc_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Elimina definitivamente un documento e il file associato dal sistema.
    """
    try:
        kb_service.delete_document_from_kb(db, kb_id, doc_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))