import uuid
from typing import Optional

from sqlalchemy.orm import Session
from app.shared.persistence.models import ChatMessageModel
from app.shared.persistence.models.message_model import MessageType


def add_message(db: Session, thread_id: str, content: str, msg_type: MessageType, id: uuid.UUID = None) -> Optional[ChatMessageModel]:
    """Salva un messaggio nella cronologia leggibile."""

    if not id:
        id = uuid.uuid4()   # Crea un ID univoco
        new_msg = ChatMessageModel(
            id=id,
            thread_id=thread_id,
            content=content,
            type=msg_type
        )
    else:
        new_msg = ChatMessageModel(
            id=id,
            thread_id=thread_id,
            content=content,
            type=msg_type
        )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg

def get_thread_history(db: Session, thread_id: str):
    """Recupera tutti i messaggi ordinati per data."""
    return db.query(ChatMessageModel)\
             .filter(ChatMessageModel.thread_id == thread_id)\
             .order_by(ChatMessageModel.created_at.asc())\
             .all()