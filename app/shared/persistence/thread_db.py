import uuid
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.shared.persistence.models.thread_model import ChatThreadModel
from app.shared.schemas.thread_schemas import ChatThreadCreate


def create_thread(db: Session, thread_data: ChatThreadCreate) -> Optional[ChatThreadModel]:
    """Crea il record del thread solo se non esiste già."""
    db_thread = ChatThreadModel(**thread_data.model_dump())
    db.add(db_thread)
    db.commit()
    db.refresh(db_thread)

    return db_thread


def get_all_threads(db: Session):
    """Restituisce le ultime chat ordinate per data."""
    return db.query(ChatThreadModel).all()


def get_thread(db: Session, thread_id: str) -> Optional[ChatThreadModel]:
    """Restituisce le ultime chat ordinate per data."""
    return db.query(ChatThreadModel) \
        .filter(ChatThreadModel.thread_id == thread_id).first()

def update_thread(db: Session, old_thread: ChatThreadModel) -> Optional[ChatThreadModel]:
    """
    Aggiorna il timestamp 'updated_at' del thread al momento corrente.
    Serve per far risalire la chat in cima alla lista quando arriva un nuovo messaggio.
    """
    old_thread.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(old_thread)

    return old_thread

def delete_thread(db: Session, db_thread: ChatThreadModel):
    """
    Elimina il thread dai metadati e pulisce la memoria di LangGraph.
    """
    db.delete(db_thread)

    # 2. PULIZIA PROFONDA LANGGRAPH (Raw SQL)
    # LangGraph non espone un metodo "delete" semplice, quindi puliamo le tabelle a mano.
    # Queste sono le tabelle standard create da PostgresSaver
    queries = [
        "DELETE FROM checkpoints WHERE thread_id = :tid",
        "DELETE FROM checkpoint_blobs WHERE thread_id = :tid",
        "DELETE FROM checkpoint_writes WHERE thread_id = :tid"
    ]

    for q in queries:
        db.execute(text(q), {"tid": db_thread.thread_id})

    db.commit()
    return True