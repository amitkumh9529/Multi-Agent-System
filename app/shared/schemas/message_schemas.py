import uuid
from datetime import datetime
from pydantic import BaseModel, Field

from app.shared.persistence.models.message_model import MessageType


class ChatMessageRead(BaseModel):
    id: uuid.UUID
    # Non serve ritornare il thread_id, lo sappiamo già
    type: MessageType = Field(..., description="Tipo messaggio: 'human' o 'ai'")
    content: str
    created_at: datetime

    class Config:
        from_attributes = True