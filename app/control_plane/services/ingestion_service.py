import uuid
import os
from sqlalchemy.orm import Session
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.shared.persistence.models.kb_model import DocumentModel, ProcessingStatus
from app.shared.persistence import vector_db, kb_db


def _get_loader(file_path: str):
    """Factory per scegliere il loader giusto in base all'estensione."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return PyPDFLoader(file_path)
    elif ext == ".txt":
        return TextLoader(file_path, encoding="utf-8")
    elif ext == ".md":
        return UnstructuredMarkdownLoader(file_path)
    else:
        # Fallback per file testuali generici
        return TextLoader(file_path, encoding="utf-8")


def process_document_task(db: Session, doc_id: uuid.UUID, kb_id: uuid.UUID):
    """
    Funzione eseguita in Background.
    1. Carica file
    2. Chunking
    3. Embedding & Salvataggio
    4. Aggiornamento Stato
    """
    print(f"⚙️ [Ingestion] Avvio processo per Doc {doc_id}")

    # 1. Recupera il documento dal DB
    doc = kb_db.get_doc_from_kb(db=db, doc_id=doc_id, kb_id=kb_id)
    if not doc:
        print(f"❌ [Ingestion] Documento {doc_id} non trovato nel DB.")
        return

    # Aggiorna stato a PROCESSING
    doc.status = ProcessingStatus.PROCESSING
    db.commit()

    try:
        # 2. Caricamento Testo (Loader)
        loader = _get_loader(doc.file_path)
        raw_docs = loader.load()

        # 3. Chunking (Splitter)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True
        )
        chunks = text_splitter.split_documents(raw_docs)

        # ARRICCHIMENTO METADATI
        # Aggiungiamo ai metadati di ogni chunk il riferimento al documento originale
        for chunk in chunks:
            chunk.metadata["source_doc_id"] = str(doc.id)
            chunk.metadata["filename"] = doc.filename

        print(f"📄 [Ingestion] Creati {len(chunks)} chunks per {doc.filename}")

        # 4. Salvataggio Vettoriale (Embedding)
        # Usiamo l'ID della KB come nome della collezione per isolare i dati
        vector_db.add_documents_to_vector_store(
            kb_id=str(kb_id),
            documents=chunks
        )

        # 5. Successo
        doc.status = ProcessingStatus.COMPLETED
        print(f"✅ [Ingestion] Completato {doc.filename}")

    except Exception as e:
        # Gestione Errori
        print(f"🔥 [Ingestion] Errore: {e}")
        doc.status = ProcessingStatus.FAILED

    finally:
        # Commit finale dello stato (Successo o Fallimento)
        db.commit()